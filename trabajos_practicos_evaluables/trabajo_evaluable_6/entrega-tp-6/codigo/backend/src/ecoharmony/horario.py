from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import Enum

PRIMER_TURNO = time(9, 0)
ULTIMO_TURNO = time(17, 0)
DURACION = timedelta(hours=1)
CIERRE_PREVIO = timedelta(minutes=15)
ANTICIPACION_MAXIMA = timedelta(hours=24)


class EstadoDeInscripcion(Enum):
    ABIERTA = "abierta"
    CERRADA = "cerrada"  # faltan menos de 15 minutos, o el turno ya paso
    ANTICIPADA = "anticipada"  # faltan mas de 24 horas


@dataclass(frozen=True)
class Horario:
    fecha: date
    hora_inicio: time

    @property
    def inicio(self):
        return datetime.combine(self.fecha, self.hora_inicio)

    @property
    def hora_fin(self):
        return (self.inicio + DURACION).time()

    def es_turno(self, primer_turno=PRIMER_TURNO, ultimo_turno=ULTIMO_TURNO):
        en_punto = self.hora_inicio.minute == 0
        return en_punto and primer_turno <= self.hora_inicio <= ultimo_turno

    def estado_de_inscripcion(self, ahora):
        if ahora > self.inicio - CIERRE_PREVIO:
            return EstadoDeInscripcion.CERRADA
        if ahora < self.inicio - ANTICIPACION_MAXIMA:
            return EstadoDeInscripcion.ANTICIPADA
        return EstadoDeInscripcion.ABIERTA

    def admite_inscripcion(self, ahora):
        return self.estado_de_inscripcion(ahora) is EstadoDeInscripcion.ABIERTA


def turnos_del_dia(fecha):
    """Los turnos de un dia: uno por hora en punto, del primero al ultimo."""
    return [Horario(fecha, time(hora)) for hora in range(PRIMER_TURNO.hour, ULTIMO_TURNO.hour + 1)]
