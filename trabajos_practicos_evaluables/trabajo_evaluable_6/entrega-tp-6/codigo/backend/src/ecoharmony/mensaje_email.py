from dataclasses import dataclass

from ecoharmony.errores import InscripcionNoConfirmadaError
from ecoharmony.inscripcion import EstadoDeLaInscripcion


@dataclass(frozen=True)
class Adjunto:
    nombre: str
    tipo: str
    contenido: bytes


@dataclass(frozen=True)
class MensajeEmail:
    destinatario: str
    asunto: str = ""
    cuerpo: str = ""
    adjuntos: tuple = ()


def armar_mensaje(inscripcion, qrs):
    if inscripcion.estado is not EstadoDeLaInscripcion.CONFIRMADA:
        raise InscripcionNoConfirmadaError(inscripcion.codigo)
    horario = inscripcion.horario
    cuerpo = (
        f"Tu inscripción a {inscripcion.actividad.nombre} está confirmada.\n\n"
        f"Código de reserva: {inscripcion.codigo}\n"
        f"Fecha: {horario.fecha:%d/%m/%Y}\n"
        f"Horario: {horario.hora_inicio:%H:%M} a {horario.hora_fin:%H:%M}\n"
        f"Personas: {len(inscripcion.visitantes)} personas\n"
        f"{_lista_de_visitantes(inscripcion)}\n"
    )
    return MensajeEmail(
        destinatario=inscripcion.email_de_contacto,
        asunto=f"Inscripción confirmada: {inscripcion.actividad.nombre}",
        cuerpo=cuerpo,
        adjuntos=tuple(_adjuntos_de_qr(qrs)),
    )


def _lista_de_visitantes(inscripcion):
    lineas = [
        f"{numero}. {visitante.nombre}"
        for numero, visitante in enumerate(inscripcion.visitantes, start=1)
    ]
    return "\n".join(lineas)


def _adjuntos_de_qr(qrs):
    for numero, qr in enumerate(qrs, start=1):
        yield Adjunto(f"qr-visitante-{numero}.png", "image/png", qr)
