class CupoInsuficienteError(Exception):
    """Se pidieron mas lugares que los que quedan en el turno."""


class InscripcionNoConfirmadaError(Exception):
    """Se intento armar un QR o un email de una inscripcion que no esta confirmada."""


class ActividadNoEncontradaError(Exception):
    """No existe una actividad con ese nombre."""


class DniYaInscriptoError(Exception):
    """Algun DNI ya tiene un turno en esa fecha y hora."""
