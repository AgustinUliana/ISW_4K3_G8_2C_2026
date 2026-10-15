class CupoInsuficiente(Exception):
    """Se pidieron mas lugares que los que quedan en el turno."""


class InscripcionNoConfirmada(Exception):
    """Se intento armar un QR o un email de una inscripcion que no esta confirmada."""
