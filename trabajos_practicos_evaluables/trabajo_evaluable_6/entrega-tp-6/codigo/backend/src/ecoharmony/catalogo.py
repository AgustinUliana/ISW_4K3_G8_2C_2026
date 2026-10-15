from ecoharmony.actividad import Actividad
from ecoharmony.terminos import TerminosYCondiciones
from ecoharmony.terminos_texto import VERSION_DE_LOS_TERMINOS, redactar_terminos


def _actividad(nombre, cupo_por_turno, edad_minima=0, requiere_talla=False):
    """Una actividad con sus reglas (las del PO) y sus propios terminos y condiciones."""
    terminos = TerminosYCondiciones(
        nombre,
        VERSION_DE_LOS_TERMINOS,
        redactar_terminos(nombre, edad_minima, requiere_talla, cupo_por_turno),
    )
    return Actividad(
        nombre,
        cupo_por_turno=cupo_por_turno,
        edad_minima=edad_minima,
        requiere_talla=requiere_talla,
        terminos=terminos,
    )


def crear_actividades():
    actividades = [
        _actividad("Tirolesa", cupo_por_turno=10, edad_minima=8, requiere_talla=True),
        _actividad("Safari", cupo_por_turno=8),
        _actividad("Palestra", cupo_por_turno=12, edad_minima=12, requiere_talla=True),
        _actividad("Jardinería", cupo_por_turno=12),
    ]
    return {actividad.nombre: actividad for actividad in actividades}
