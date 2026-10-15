import logging
import time
from dataclasses import dataclass, field

from ecoharmony.errores import (
    ActividadNoEncontradaError,
    CupoInsuficienteError,
    DniYaInscriptoError,
)
from ecoharmony.inscripcion import Inscripcion
from ecoharmony.mensaje_email import armar_mensaje
from ecoharmony.motivos import MotivoRechazo
from ecoharmony.qr import contenido_del_qr

logger = logging.getLogger(__name__)


@dataclass
class SolicitudInscripcion:
    actividad: str
    horario: object
    visitantes: list
    titular: object  # el Usuario autenticado (None si no inicio sesion)
    terminos_aceptados: str = None


@dataclass
class ResultadoInscripcion:
    confirmada: bool
    codigo: str = None
    motivos: list = field(default_factory=list)
    errores_por_visitante: dict = field(default_factory=dict)  # posicion -> motivos


class InscripcionService:
    def __init__(
        self,
        repositorio,
        parque,
        reloj,
        generador_qr,
        servicio_email,
        intentos_de_email=3,
        pausa_entre_intentos=1.0,
        dormir=time.sleep,
    ):
        self._repositorio = repositorio
        self._parque = parque
        self._reloj = reloj
        self._generador_qr = generador_qr
        self._servicio_email = servicio_email
        self._intentos_de_email = intentos_de_email
        self._pausa_entre_intentos = pausa_entre_intentos
        self._dormir = dormir

    def inscribir(self, solicitud):
        try:
            actividad = self._repositorio.actividad(solicitud.actividad)
        except ActividadNoEncontradaError:
            return ResultadoInscripcion(
                confirmada=False, motivos=[MotivoRechazo.ACTIVIDAD_INEXISTENTE]
            )
        inscripcion = Inscripcion(
            actividad=actividad,
            horario=solicitud.horario,
            visitantes=solicitud.visitantes,
            titular=solicitud.titular,
            terminos_aceptados=self._terminos_aceptados(solicitud.terminos_aceptados),
        )
        motivos = inscripcion.motivos_de_rechazo(self._parque, self._reloj.ahora())
        if self._hay_dni_ya_inscripto(inscripcion):
            motivos.append(MotivoRechazo.DNI_YA_INSCRIPTO)
        if motivos:
            return ResultadoInscripcion(
                confirmada=False,
                motivos=motivos,
                errores_por_visitante=inscripcion.errores_por_visitante(),
            )
        inscripcion.confirmar(self._repositorio.siguiente_codigo(), self._reloj.ahora())
        qrs = self._generar_qrs(inscripcion)
        try:
            self._repositorio.guardar(inscripcion)
        except CupoInsuficienteError:
            return ResultadoInscripcion(confirmada=False, motivos=[MotivoRechazo.SIN_CUPO])
        except DniYaInscriptoError:
            return ResultadoInscripcion(confirmada=False, motivos=[MotivoRechazo.DNI_YA_INSCRIPTO])
        if not self._enviar_email_con_reintentos(armar_mensaje(inscripcion, qrs)):
            # Sin email no hay confirmacion: se deshace la reserva (cupo y DNI quedan libres).
            self._repositorio.anular(inscripcion.codigo)
            return ResultadoInscripcion(confirmada=False, motivos=[MotivoRechazo.EMAIL_NO_ENVIADO])
        return ResultadoInscripcion(confirmada=True, codigo=inscripcion.codigo)

    def _terminos_aceptados(self, nombre_de_la_actividad):
        if nombre_de_la_actividad is None:
            return None
        return self._repositorio.actividad(nombre_de_la_actividad).terminos

    def _generar_qrs(self, inscripcion):
        cantidad = len(inscripcion.visitantes)
        return [
            self._generador_qr.generar(contenido_del_qr(inscripcion, n))
            for n in range(1, cantidad + 1)
        ]

    def _hay_dni_ya_inscripto(self, inscripcion):
        return any(
            self._repositorio.dni_inscripto_en(visitante.dni, inscripcion.horario)
            for visitante in inscripcion.visitantes
        )

    def _enviar_email_con_reintentos(self, mensaje):
        for intento in range(1, self._intentos_de_email + 1):
            try:
                self._servicio_email.enviar(mensaje)
                return True
            except Exception:  # cualquier falla del correo se reintenta
                logger.exception(
                    "Fallo el envio del email (intento %s de %s)", intento, self._intentos_de_email
                )
                if intento < self._intentos_de_email:
                    self._dormir(self._pausa_entre_intentos)
        return False
