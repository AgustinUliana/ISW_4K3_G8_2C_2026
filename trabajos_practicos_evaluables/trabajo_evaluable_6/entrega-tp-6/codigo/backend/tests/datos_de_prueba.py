"""Datos de prueba compartidos (Evident Data)."""

from datetime import date, datetime, time

from ecoharmony.catalogo import crear_actividades
from ecoharmony.horario import Horario
from ecoharmony.inscripcion import Inscripcion
from ecoharmony.inscripcion_service import SolicitudInscripcion
from ecoharmony.usuarios import Usuario
from ecoharmony.visitante import Visitante

AHORA = datetime(2026, 11, 4, 8, 0)  # miercoles 08:00
H1 = Horario(date(2026, 11, 4), time(10, 0))
ANA = Visitante("Ana Perez", "30123456", 30, talla="M")
LUIS = Visitante("Luis Gomez", "28123456", 41, talla="L")
EMAIL_DE_ANA = "ana.perez@example.com"
TITULAR = Usuario(EMAIL_DE_ANA)  # Ana, registrada


def una_inscripcion_confirmada(codigo="INS-0001", visitantes=None):
    """Inscripcion a Tirolesa, H1, con Ana y Luis (o los visitantes dados), ya confirmada."""
    tirolesa = crear_actividades()["Tirolesa"]
    inscripcion = Inscripcion(
        actividad=tirolesa,
        horario=H1,
        visitantes=visitantes or [ANA, LUIS],
        titular=TITULAR,
        terminos_aceptados=tirolesa.terminos,
    )
    inscripcion.confirmar(codigo=codigo, ahora=AHORA)
    return inscripcion


def n_visitantes(cantidad, primer_dni=30000001):
    """`cantidad` visitantes validos para Tirolesa, con DNIs distintos."""
    return [
        Visitante(f"Persona {chr(65 + i)}", str(primer_dni + i), 30, talla="M")
        for i in range(cantidad)
    ]


def una_solicitud(**cambios):
    """Solicitud valida: Tirolesa, H1, Ana y Luis, con los T&C de Tirolesa."""
    datos = {
        "actividad": "Tirolesa",
        "horario": H1,
        "visitantes": [ANA, LUIS],
        "titular": TITULAR,
        "terminos_aceptados": "Tirolesa",
    }
    datos.update(cambios)
    return SolicitudInscripcion(**datos)
