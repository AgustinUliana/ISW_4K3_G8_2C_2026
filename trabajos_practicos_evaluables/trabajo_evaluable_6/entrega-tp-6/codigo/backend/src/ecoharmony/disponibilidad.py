"""Consultas de disponibilidad: lo que la pantalla le muestra al visitante."""

from dataclasses import dataclass

from ecoharmony.horario import Horario, turnos_del_dia


@dataclass(frozen=True)
class TurnoDisponible:
    horario: Horario
    cupo_restante: int

    @property
    def agotado(self):
        return self.cupo_restante == 0


def turnos_disponibles(actividad, fecha, parque, ahora):
    """Turnos de la fecha en los que hoy se puede inscribir (con su cupo, aunque sea 0)."""
    return [
        TurnoDisponible(horario, actividad.cupo_restante(horario))
        for horario in turnos_del_dia(fecha)
        if parque.esta_abierto(horario) and horario.admite_inscripcion(ahora)
    ]
