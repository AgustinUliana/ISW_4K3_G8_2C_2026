from ecoharmony.errores import InscripcionNoConfirmadaError
from ecoharmony.inscripcion import EstadoDeLaInscripcion


def contenido_del_qr(inscripcion, numero_de_visitante):
    if inscripcion.estado is not EstadoDeLaInscripcion.CONFIRMADA:
        raise InscripcionNoConfirmadaError(inscripcion.codigo)
    return f"{inscripcion.codigo}|V{numero_de_visitante}"
