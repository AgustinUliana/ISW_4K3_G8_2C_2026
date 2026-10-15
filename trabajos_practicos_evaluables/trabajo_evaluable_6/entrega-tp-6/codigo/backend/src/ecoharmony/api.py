"""API HTTP de EcoHarmony Park (FastAPI). Es una capa delgada: traduce JSON <-> servicios."""

import logging
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ecoharmony.motivos import MotivoRechazo

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


class Credenciales(BaseModel):
    email: Any = None
    contrasena: Any = None


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

    return app
