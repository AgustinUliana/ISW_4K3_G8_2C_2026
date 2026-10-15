import logging
from dataclasses import dataclass, field

from ecoharmony.errores import ActividadNoEncontrada, CupoInsuficiente
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
    email_de_contacto: str
    terminos_aceptados: str = None


@dataclass
class ResultadoInscripcion:
    confirmada: bool
    codigo: str = None
    motivos: list = field(default_factory=list)
    email_enviado: bool = False


class InscripcionService:
    def __init__(self, repositorio, parque, reloj, generador_qr, servicio_email):
        self._repositorio = repositorio
        self._parque = parque
        self._reloj = reloj
        self._generador_qr = generador_qr
        self._servicio_email = servicio_email

    def inscribir(self, solicitud):
        try:
            actividad = self._repositorio.actividad(solicitud.actividad)
        except ActividadNoEncontrada:
            return ResultadoInscripcion(confirmada=False, motivos=[MotivoRechazo.ACTIVIDAD_INEXISTENTE])
        inscripcion = Inscripcion(
            actividad=actividad,
            horario=solicitud.horario,
            visitantes=solicitud.visitantes,
            email_de_contacto=solicitud.email_de_contacto,
            terminos_aceptados=self._terminos_aceptados(solicitud.terminos_aceptados),
        )
        motivos = inscripcion.motivos_de_rechazo(self._parque, self._reloj.ahora())
        if self._hay_dni_ya_inscripto(inscripcion):
            motivos.append(MotivoRechazo.DNI_YA_INSCRIPTO)
        if motivos:
            return ResultadoInscripcion(confirmada=False, motivos=motivos)
        inscripcion.confirmar(self._repositorio.siguiente_codigo(), self._reloj.ahora())
        qrs = self._generar_qrs(inscripcion)
        try:
            self._repositorio.guardar(inscripcion)
        except CupoInsuficiente:
            return ResultadoInscripcion(confirmada=False, motivos=[MotivoRechazo.SIN_CUPO])
        email_enviado = self._enviar_email(armar_mensaje(inscripcion, qrs))
        return ResultadoInscripcion(confirmada=True, codigo=inscripcion.codigo, email_enviado=email_enviado)

    def _terminos_aceptados(self, nombre_de_la_actividad):
        if nombre_de_la_actividad is None:
            return None
        return self._repositorio.actividad(nombre_de_la_actividad).terminos

    def _generar_qrs(self, inscripcion):
        cantidad = len(inscripcion.visitantes)
        return [self._generador_qr.generar(contenido_del_qr(inscripcion, n)) for n in range(1, cantidad + 1)]

    def _hay_dni_ya_inscripto(self, inscripcion):
        return any(
            self._repositorio.dni_inscripto_en(visitante.dni, inscripcion.horario)
            for visitante in inscripcion.visitantes
        )

    def _enviar_email(self, mensaje):
        try:
            self._servicio_email.enviar(mensaje)
        except Exception:  # la inscripcion ya esta confirmada: un fallo de correo no la deshace
            logger.exception("No se pudo enviar el email de confirmacion")
            return False
        return True
