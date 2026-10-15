from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class Horario:
    fecha: date
    hora_inicio: time
