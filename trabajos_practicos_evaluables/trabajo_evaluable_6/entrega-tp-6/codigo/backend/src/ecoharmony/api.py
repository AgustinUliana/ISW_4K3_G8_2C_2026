"""API HTTP de EcoHarmony Park (FastAPI). Es una capa delgada: traduce JSON <-> servicios."""

import logging
from dataclasses import dataclass
from datetime import date, time
from typing import Any

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ecoharmony.disponibilidad import resumen_de_actividades, turnos_disponibles
from ecoharmony.errores import ActividadNoEncontradaError
from ecoharmony.horario import Horario
from ecoharmony.inscripcion_service import SolicitudInscripcion
from ecoharmony.motivos import MotivoRechazo
from ecoharmony.visitante import Visitante

logger = logging.getLogger(__name__)

# Estado HTTP segun el motivo; si hay varios, gana el primero de esta lista.
_ESTADO_POR_MOTIVO = [
    (MotivoRechazo.USUARIO_NO_REGISTRADO, 401),
    (MotivoRechazo.CREDENCIALES_INVALIDAS, 401),
    (MotivoRechazo.ACTIVIDAD_INEXISTENTE, 404),
    (MotivoRechazo.EMAIL_YA_REGISTRADO, 409),
    (MotivoRechazo.SIN_CUPO, 409),
    (MotivoRechazo.DNI_YA_INSCRIPTO, 409),
    (MotivoRechazo.EMAIL_NO_ENVIADO, 503),
]


@dataclass
class Servicios:
    usuarios: Any
    inscripciones: Any
    repositorio: Any
    parque: Any
    reloj: Any
    generador_qr: Any = None  # solo informativo: lo usa el servicio de inscripcion
    servicio_email: Any = None  # solo informativo: lo usa el servicio de inscripcion


class Credenciales(BaseModel):
    email: Any = None
    contrasena: Any = None


class VisitanteEntrada(BaseModel):
    nombre: Any = None
    dni: Any = None
    edad: Any = None
    talla: Any = None


class InscripcionEntrada(BaseModel):
    actividad: Any = None
    fecha: Any = None
    hora: Any = None
    visitantes: list[VisitanteEntrada] = []
    terminos_aceptados: Any = None


def _token_de(encabezado):
    if encabezado and encabezado.startswith("Bearer "):
        return encabezado[len("Bearer ") :]
    return None


def _horario(fecha, hora):
    try:
        return Horario(date.fromisoformat(fecha), time.fromisoformat(hora))
    except (TypeError, ValueError):
        return None


def _texto(valor):
    return valor if isinstance(valor, str) else None


def _estado_http(motivos):
    for motivo, estado in _ESTADO_POR_MOTIVO:
        if motivo in motivos:
            return estado
    return 422


def _rechazo(motivos, **extra):
    cuerpo = {"motivos": [motivo.value for motivo in motivos], **extra}
    return JSONResponse(status_code=_estado_http(motivos), content=cuerpo)


def crear_app(servicios, origenes_permitidos=()):
    app = FastAPI(title="EcoHarmony Park - Inscripcion a actividades")
    if origenes_permitidos:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(origenes_permitidos),
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.exception_handler(Exception)
    async def error_inesperado(solicitud, error):
        logger.exception("Error inesperado en %s", solicitud.url.path)
        return JSONResponse(status_code=500, content={"detalle": "Error interno del servidor"})

    @app.post("/registro", status_code=201)
    def registrar(datos: Credenciales):
        resultado = servicios.usuarios.registrar(_texto(datos.email), _texto(datos.contrasena))
        if not resultado.registrado:
            return _rechazo(resultado.motivos)
        return {"email": resultado.usuario.email}

    @app.post("/sesion")
    def iniciar_sesion(datos: Credenciales):
        sesion = servicios.usuarios.iniciar_sesion(_texto(datos.email), _texto(datos.contrasena))
        if not sesion.iniciada:
            return _rechazo(sesion.motivos)
        return {"token": sesion.token}

    @app.get("/actividades")
    def listar_actividades():
        resumen = resumen_de_actividades(
            servicios.repositorio.actividades(), servicios.parque, servicios.reloj.ahora()
        )
        return [
            {
                "nombre": item.actividad.nombre,
                "requiere_talla": item.actividad.requiere_talla,
                "edad_minima": item.actividad.edad_minima,
                "cupo_por_turno": item.actividad.cupo_por_turno,
                "disponible": item.disponible,
            }
            for item in sorted(resumen, key=lambda item: item.actividad.nombre)
        ]

    @app.get("/actividades/{nombre}/horarios")
    def horarios_de_una_actividad(nombre: str, fecha: str | None = None):
        try:
            actividad = servicios.repositorio.actividad(nombre)
        except ActividadNoEncontradaError:
            return _rechazo([MotivoRechazo.ACTIVIDAD_INEXISTENTE])
        try:
            dia = date.fromisoformat(fecha)
        except (TypeError, ValueError):
            return _rechazo([MotivoRechazo.FECHA_INVALIDA])
        turnos = turnos_disponibles(actividad, dia, servicios.parque, servicios.reloj.ahora())
        return {
            "actividad": nombre,
            "fecha": dia.isoformat(),
            "turnos": [
                {
                    "hora": turno.horario.hora_inicio.strftime("%H:%M"),
                    "cupo_restante": turno.cupo_restante,
                    "agotado": turno.agotado,
                }
                for turno in turnos
            ],
        }

    @app.get("/actividades/{nombre}/terminos")
    def terminos_de_una_actividad(nombre: str):
        try:
            terminos = servicios.repositorio.actividad(nombre).terminos
        except ActividadNoEncontradaError:
            return _rechazo([MotivoRechazo.ACTIVIDAD_INEXISTENTE])
        return {"actividad": nombre, "version": terminos.version, "texto": terminos.texto}

    @app.post("/inscripciones", status_code=201)
    def inscribir(datos: InscripcionEntrada, authorization: str | None = Header(default=None)):
        solicitud = SolicitudInscripcion(
            actividad=_texto(datos.actividad),
            horario=_horario(datos.fecha, datos.hora),
            visitantes=[Visitante(v.nombre, v.dni, v.edad, v.talla) for v in datos.visitantes],
            titular=servicios.usuarios.usuario_de_token(_token_de(authorization)),
            terminos_aceptados=_texto(datos.terminos_aceptados),
        )
        resultado = servicios.inscripciones.inscribir(solicitud)
        if not resultado.confirmada:
            visitantes = {
                str(posicion): [motivo.value for motivo in motivos]
                for posicion, motivos in resultado.errores_por_visitante.items()
            }
            return _rechazo(resultado.motivos, visitantes=visitantes)
        return {"codigo": resultado.codigo}

    return app
