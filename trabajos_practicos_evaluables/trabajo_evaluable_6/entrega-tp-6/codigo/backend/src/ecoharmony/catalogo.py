from ecoharmony.actividad import Actividad
from ecoharmony.terminos import TerminosYCondiciones

# TODO: reemplazar por los T&C reales que redacta el grupo (el PO no los valida).
_TEXTO_PROVISORIO = "Terminos y condiciones de {}: texto provisorio a redactar por el grupo."


def _terminos(nombre):
    return TerminosYCondiciones(nombre, "v1", _TEXTO_PROVISORIO.format(nombre))


def crear_actividades():
    actividades = [
        Actividad(
            "Tirolesa",
            cupo_por_turno=10,
            edad_minima=8,
            requiere_talla=True,
            terminos=_terminos("Tirolesa"),
        ),
        Actividad("Safari", cupo_por_turno=8, terminos=_terminos("Safari")),
        Actividad(
            "Palestra",
            cupo_por_turno=12,
            edad_minima=12,
            requiere_talla=True,
            terminos=_terminos("Palestra"),
        ),
        Actividad("Jardinería", cupo_por_turno=12, terminos=_terminos("Jardinería")),
    ]
    return {actividad.nombre: actividad for actividad in actividades}
