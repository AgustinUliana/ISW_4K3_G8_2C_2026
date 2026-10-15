"""Terminos y condiciones de cada actividad (BORRADOR: el grupo los redacta y los revisa).

El PO pidio un texto distinto por actividad, disenado por el grupo y sin validacion de su parte.
Cada texto se arma con las reglas de la actividad (edad minima, talla, cupo) y con la ventana de
inscripcion, asi nunca quedan numeros sueltos que se desactualicen si el PO cambia una regla.
"""

from ecoharmony.horario import ANTICIPACION_MAXIMA, CIERRE_PREVIO
from ecoharmony.inscripcion import MAXIMO_DE_PERSONAS

VERSION_DE_LOS_TERMINOS = "v1"

_HORAS_DE_ANTICIPACION = int(ANTICIPACION_MAXIMA.total_seconds() // 3600)
_MINUTOS_DE_CIERRE = int(CIERRE_PREVIO.total_seconds() // 60)

# Lo propio de cada actividad: de que se trata y que hay que cumplir durante la actividad.
_DE_LA_ACTIVIDAD = {
    "Tirolesa": [
        "Es un recorrido en tirolesa por el circuito aéreo del parque.",
        "Es obligatorio usar el equipo de seguridad que entrega el personal y mantenerlo "
        "puesto durante todo el recorrido.",
        "Usá calzado cerrado y ropa cómoda. No se pueden llevar objetos sueltos.",
    ],
    "Safari": [
        "Es un recorrido guiado para observar a los animales del bioparque.",
        "Mantené la distancia que indique el guía y no toques ni alimentes a los animales.",
        "Hablá en voz baja y no uses flash para sacar fotos.",
    ],
    "Palestra": [
        "Es una actividad de escalada en pared con guía del parque.",
        "Es obligatorio usar el arnés y el casco que entrega el personal, y escalar solo "
        "con autorización del guía.",
        "Usá calzado cómodo, recogete el pelo largo y sacate anillos, pulseras y colgantes.",
    ],
    "Jardinería": [
        "Es una actividad guiada de cuidado de las plantas del parque.",
        "El personal entrega las herramientas y los guantes: devolvelos al terminar.",
        "Usá ropa que se pueda ensuciar y protector solar.",
    ],
}

_DIA_DE_LA_ACTIVIDAD = [
    "Presentate con tu DNI y con el código QR de cada visitante.",
    "Llegá con puntualidad: el turno empieza y termina en el horario reservado.",
    "El personal puede impedir la participación de quien no cumpla los requisitos de este texto.",
]

_SEGURIDAD = [
    "Seguí en todo momento las indicaciones del personal.",
    "El parque puede suspender o reprogramar la actividad por razones de seguridad o de clima.",
]

_DATOS_PERSONALES = [
    "Usamos tus datos solo para gestionar la inscripción y el ingreso a la actividad.",
    "Tu email se usa para enviarte la confirmación y los códigos QR.",
]

_CIERRE = (
    "Al aceptar confirmás que leíste estos términos y condiciones y que los aceptás "
    "para esta actividad."
)


def _apartado(numero, titulo, items):
    lineas = "\n".join(f"- {item}" for item in items)
    return f"{numero}. {titulo}\n{lineas}"


def _reserva(cupo_por_turno):
    return [
        f"La inscripción reserva un lugar por persona en el turno elegido. "
        f"Hay {cupo_por_turno} lugares por turno.",
        f"Podés reservar hasta {_HORAS_DE_ANTICIPACION} horas antes del turno. "
        f"La inscripción cierra {_MINUTOS_DE_CIERRE} minutos antes de que empiece.",
        f"Una misma inscripción puede incluir hasta {MAXIMO_DE_PERSONAS} personas.",
        "La reserva se confirma recién cuando recibís el email con el código de reserva "
        "y un código QR por cada visitante.",
    ]


def _requisitos(edad_minima, requiere_talla):
    edad = f"Desde {edad_minima} años." if edad_minima else "Todas las edades."
    if requiere_talla:
        talla = "Al inscribirte tenés que indicar la talla de vestimenta de cada visitante."
    else:
        talla = "No hace falta indicar la talla de vestimenta."
    return [
        f"Edad: {edad}",
        talla,
        "Cada visitante se carga con su nombre, su DNI (7 u 8 dígitos) y su edad. "
        "Los datos tienen que ser reales.",
        "Una misma persona no puede tener dos turnos en el mismo horario.",
    ]


def redactar_terminos(nombre, edad_minima, requiere_talla, cupo_por_turno):
    if nombre not in _DE_LA_ACTIVIDAD:
        raise ValueError(f"No hay texto de terminos y condiciones para la actividad {nombre}")
    apartados = [
        _apartado(1, "Reserva", _reserva(cupo_por_turno)),
        _apartado(2, "Quiénes pueden participar", _requisitos(edad_minima, requiere_talla)),
        _apartado(3, "La actividad", [*_DE_LA_ACTIVIDAD[nombre], "Cada turno dura una hora."]),
        _apartado(4, "El día de la actividad", _DIA_DE_LA_ACTIVIDAD),
        _apartado(5, "Seguridad", _SEGURIDAD),
        _apartado(6, "Datos personales", _DATOS_PERSONALES),
    ]
    titulo = f"TÉRMINOS Y CONDICIONES - {nombre.upper()} ({VERSION_DE_LOS_TERMINOS})"
    return "\n\n".join([titulo, *apartados, _CIERRE]) + "\n"
