"""Consultas de disponibilidad: lo que la pantalla le muestra al visitante."""

from dataclasses import dataclass

from ecoharmony.horario import ANTICIPACION_MAXIMA, Horario, turnos_del_dia


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


@dataclass(frozen=True)
class ResumenDeActividad:
    actividad: object
    disponible: bool  # tiene al menos un turno con lugar dentro de la ventana de inscripcion


def resumen_de_actividades(actividades, parque, ahora):
    """Cada actividad con su disponibilidad. La ventana de 24 horas toca como mucho dos fechas."""
    fechas = {ahora.date(), (ahora + ANTICIPACION_MAXIMA).date()}
    return [
        ResumenDeActividad(
            actividad,
            disponible=any(
                not turno.agotado
                for fecha in sorted(fechas)
                for turno in turnos_disponibles(actividad, fecha, parque, ahora)
            ),
        )
        for actividad in actividades
    ]
