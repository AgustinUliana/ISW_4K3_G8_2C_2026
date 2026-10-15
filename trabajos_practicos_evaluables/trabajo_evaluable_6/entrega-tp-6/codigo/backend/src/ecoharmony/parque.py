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
        return self._abre_ese_dia(horario.fecha) and self._entra_en_el_horario(horario)

    def _abre_ese_dia(self, fecha):
        es_feriado = (fecha.month, fecha.day) in FERIADOS
        return fecha.weekday() != LUNES and not es_feriado

    def _entra_en_el_horario(self, horario):
        return self.apertura <= horario.hora_inicio and horario.hora_fin <= self.cierre
