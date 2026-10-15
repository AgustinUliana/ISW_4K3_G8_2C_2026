from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

PRIMER_TURNO = time(9, 0)
ULTIMO_TURNO = time(17, 0)
DURACION = timedelta(hours=1)
CIERRE_PREVIO = timedelta(minutes=15)
ANTICIPACION_MAXIMA = timedelta(hours=24)


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

    def admite_inscripcion(self, ahora):
        return self.inicio - ANTICIPACION_MAXIMA <= ahora <= self.inicio - CIERRE_PREVIO
