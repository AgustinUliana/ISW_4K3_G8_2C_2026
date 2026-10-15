from datetime import time

APERTURA = time(8, 30)
CIERRE = time(19, 0)
LUNES = 0
FERIADOS = ((12, 25), (1, 1))  # (mes, dia)


class Parque:
    def __init__(self, apertura=APERTURA, cierre=CIERRE):
        self.apertura = apertura
        self.cierre = cierre

    def esta_abierto(self, horario):
        if horario.fecha.weekday() == LUNES:
            return False
        if (horario.fecha.month, horario.fecha.day) in FERIADOS:
            return False
        return self.apertura <= horario.hora_inicio and horario.hora_fin <= self.cierre
