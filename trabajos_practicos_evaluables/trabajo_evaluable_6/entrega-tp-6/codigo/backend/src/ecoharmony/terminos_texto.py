"""Terminos y condiciones de cada actividad (BORRADOR: el grupo los redacta y los revisa).

El PO pidio un texto distinto por actividad, disenado por el grupo y sin validacion de su parte.
Todos siguen el mismo modelo de 11 apartados (objeto, requisitos, normas de seguridad, equipo o
materiales, salud, responsabilidad, suspension, cuidado, datos, fotos y aceptacion). Cambian los
apartados propios de cada actividad (objeto, normas, equipo, salud y cuidado), que se redactaron a
partir de las practicas habituales de parques de aventura, rocodromos, zoologicos y huertas.
Las reglas que fija el PO (edad minima, talla, cupo, ventana de inscripcion, maximo de personas)
se toman de los datos de la actividad, asi nunca quedan numeros sueltos que se desactualicen.
"""

from ecoharmony.horario import ANTICIPACION_MAXIMA, CIERRE_PREVIO
from ecoharmony.inscripcion import MAXIMO_DE_PERSONAS

VERSION_DE_LOS_TERMINOS = "v1"

_HORAS_DE_ANTICIPACION = int(ANTICIPACION_MAXIMA.total_seconds() // 3600)
_MINUTOS_DE_CIERRE = int(CIERRE_PREVIO.total_seconds() // 60)

_INFORMAR_PELIGRO = (
    "Informar al personal sobre cualquier situación de peligro, accidente o incidente."
)
_SEGUIR_INSTRUCCIONES = "Seguir las instrucciones del personal responsable."

# Lo propio de cada actividad. "equipo" es (titulo del apartado 4, texto).
_DE_LA_ACTIVIDAD = {
    "Tirolesa": {
        "titulo": "Tirolesa",
        "objeto": (
            "La actividad consiste en recorrer en tirolesa el circuito aéreo del parque, "
            "descendiendo sujeto a una línea de vida, con el acompañamiento permanente de "
            "personal capacitado y con equipo de seguridad provisto por el parque. Busca ofrecer "
            "una experiencia de aventura y contacto con la naturaleza en condiciones controladas."
        ),
        "normas": [
            _SEGUIR_INSTRUCCIONES,
            "Esperar la autorización del personal antes de engancharse a la línea de vida y "
            "antes de cada descenso.",
            "No soltar, abrir ni modificar el equipo, ni desengancharse por cuenta propia.",
            "Mantener las manos, el cabello y la ropa lejos de la polea y del cable.",
            "Guardar antes de comenzar los objetos sueltos (celulares, cámaras, llaves) para "
            "que no caigan durante el recorrido.",
            "Usar calzado cerrado y sujeto al pie, y recogerse el cabello largo.",
            "No correr ni empujar en las plataformas.",
            _INFORMAR_PELIGRO,
        ],
        "equipo": (
            "Uso del equipo de seguridad",
            "El parque entrega a cada participante arnés, casco y polea. El personal los "
            "coloca y revisa antes de cada recorrido, y el participante debe mantenerlos "
            "puestos y ajustados hasta que el personal indique que puede retirarlos. Si el "
            "equipo no queda correctamente ajustado, la persona no podrá realizar el "
            "recorrido hasta que se corrija. La talla de vestimenta informada en la "
            "inscripción sirve para preparar el equipo con anticipación.",
        ),
        "salud": (
            "El participante debe comunicar al personal, antes de comenzar, cualquier "
            "condición que pueda comprometer su seguridad: problemas de espalda, cuello o "
            "corazón, epilepsia o convulsiones, vértigo o miedo a las alturas, lesiones "
            "recientes o embarazo. No se puede participar bajo los efectos del alcohol o de "
            "otras sustancias. El personal puede impedir la participación o interrumpir el "
            "recorrido cuando considere que existe un riesgo."
        ),
        "cuidado": (
            "Los participantes deberán respetar el circuito y las plataformas, no dañar el "
            "equipo ni las instalaciones, no arrojar objetos ni residuos desde las alturas, "
            "cuidar los árboles y la vegetación del recorrido y depositar los residuos en los "
            "lugares indicados."
        ),
    },
    "Safari": {
        "titulo": "Safari",
        "objeto": (
            "La actividad consiste en un recorrido guiado para observar a los animales del "
            "bioparque, conocer sus hábitos y promover el respeto y la conservación de la "
            "fauna, siempre a una distancia segura para las personas y para los animales."
        ),
        "normas": [
            "Seguir al guía y permanecer con el grupo durante todo el recorrido, sin "
            "adelantarse ni alejarse.",
            "Mantener la distancia que indique el guía y no cruzar vallas, cercos ni barreras.",
            "No alimentar a los animales ni arrojarles comida u objetos.",
            "No tocar, perseguir, llamar ni molestar a los animales, ni golpear vidrios o mallas.",
            "Hablar en voz baja y evitar los movimientos bruscos y los ruidos fuertes.",
            "No usar flash para sacar fotografías.",
            "Mantener a las niñas y los niños bajo la supervisión permanente de un adulto.",
            _INFORMAR_PELIGRO,
        ],
        "equipo": (
            "Contacto con los animales y alimentación",
            "Los animales son silvestres y su comportamiento puede ser impredecible. Su dieta "
            "está controlada por el personal, por lo que solo el personal del parque puede "
            "alimentarlos. Queda prohibido ingresar con alimentos fuera de las zonas "
            "habilitadas y dejar bolsas o envoltorios al alcance de los animales. Después de "
            "cualquier contacto con superficies del recorrido, se recomienda lavarse las manos.",
        ),
        "salud": (
            "El participante deberá comunicar al personal, antes de comenzar, cualquier alergia "
            "relevante (a picaduras de insectos, pelos, plumas o polen), así como cualquier "
            "condición que pueda ser un riesgo para el recorrido. Las personas con síntomas de "
            "enfermedades contagiosas deberán abstenerse de participar para cuidar a los "
            "demás visitantes y a los animales."
        ),
        "cuidado": (
            "Los participantes deberán respetar el hábitat de los animales y la señalización "
            "del recorrido, no extraer piedras, plumas ni otros elementos del entorno y "
            "depositar los residuos en los lugares indicados."
        ),
    },
    "Palestra": {
        "titulo": "Palestra (escalada en pared)",
        "objeto": (
            "La actividad consiste en escalar la pared de escalada del parque con guía y "
            "asegurado desde el suelo, para iniciarse en las técnicas básicas de escalada, "
            "el equilibrio y la confianza en uno mismo, en condiciones controladas."
        ),
        "normas": [
            "Escalar únicamente cuando el guía lo autorice y el asegurador esté listo.",
            "Respetar las vías y las alturas indicadas y no escalar sin asegurador.",
            "Comunicarse con el asegurador con las señales indicadas antes de subir y de bajar.",
            "No permanecer debajo de quien escala ni en la zona de caída.",
            "No trepar a la pared fuera del turno ni sin autorización del personal.",
            "Usar calzado cerrado (o de escalada), no escalar descalzo y recogerse el cabello "
            "largo.",
            "Sacarse anillos, pulseras, colgantes y todo objeto que pueda engancharse.",
            _INFORMAR_PELIGRO,
        ],
        "equipo": (
            "Uso del equipo de seguridad",
            "El parque entrega a cada participante arnés y casco, y asegura la escalada con "
            "cuerda y dispositivos de seguridad. El personal verifica el ajuste del equipo y "
            "el enganche a la cuerda antes de cada ascenso. El participante no debe "
            "modificarlos ni desengancharse por cuenta propia. La talla de vestimenta "
            "informada en la inscripción sirve para preparar el equipo con anticipación.",
        ),
        "salud": (
            "El participante debe comunicar al personal, antes de comenzar, cualquier "
            "condición que pueda comprometer su seguridad: lesiones en manos, muñecas, "
            "hombros o espalda, problemas cardíacos, epilepsia, vértigo o embarazo. No se "
            "puede participar bajo los efectos del alcohol o de otras sustancias. Se "
            "recomienda hidratarse antes y después de la actividad."
        ),
        "cuidado": (
            "Los participantes deberán respetar la pared y sus presas, no dañar el equipo ni "
            "las instalaciones, no dejar objetos personales en la zona de escalada y "
            "depositar los residuos en los lugares indicados."
        ),
    },
    "Jardinería": {
        "titulo": "Jardinería y cuidado de espacios verdes",
        "objeto": (
            "La actividad tiene como objetivo promover el contacto con la naturaleza, el "
            "aprendizaje de técnicas básicas de jardinería y el cuidado del medioambiente "
            "mediante actividades prácticas dentro de las instalaciones del parque."
        ),
        "normas": [
            _SEGUIR_INSTRUCCIONES,
            "Utilizar las herramientas y los materiales únicamente para los fines indicados.",
            "Utilizar los elementos de protección que se proporcionen cuando corresponda, "
            "como los guantes.",
            "Usar calzado cerrado y recogerse el cabello largo.",
            "No correr, jugar ni realizar acciones que puedan poner en riesgo a otros "
            "participantes.",
            _INFORMAR_PELIGRO,
        ],
        "equipo": (
            "Uso de herramientas y materiales",
            "Las herramientas, los fertilizantes, los sustratos y demás materiales deberán "
            "utilizarse de acuerdo con las indicaciones del personal, y las herramientas se "
            "devuelven al terminar. Queda prohibido manipular productos químicos o "
            "herramientas restringidas sin autorización y supervisión.",
        ),
        "salud": (
            "El participante deberá comunicar al personal, antes de comenzar, cuando sea "
            "pertinente para la seguridad de la actividad, cualquier alergia relevante a "
            "plantas, polen, tierra u otros materiales utilizados. La organización informará "
            "sobre los riesgos conocidos y las medidas preventivas correspondientes. Se "
            "recomienda usar protector solar y mantenerse hidratado."
        ),
        "cuidado": (
            "Los participantes deberán respetar los espacios verdes, evitar dañar plantas y "
            "árboles, no retirar materiales sin autorización y depositar los residuos en los "
            "lugares indicados."
        ),
    },
}

_RESPONSABILIDAD = (
    "El parque se compromete a adoptar medidas razonables de prevención, mantener los "
    "espacios de actividad en condiciones adecuadas y proporcionar instrucciones de "
    "seguridad. Estos términos no eximen al parque de las responsabilidades que legalmente "
    "le correspondan ni implican una renuncia general a los derechos del participante."
)

_MODIFICACIONES = (
    "La organización podrá modificar, reprogramar o suspender la actividad por condiciones "
    "climáticas, razones operativas o situaciones que comprometan la seguridad. Cuando "
    "corresponda, informará a los participantes sobre las alternativas disponibles."
)

_DATOS_PERSONALES = (
    "Los datos recabados durante la inscripción se utilizarán para gestionar la "
    "participación, comunicar información relacionada con la actividad (por ejemplo, el "
    "email de confirmación con los códigos QR) y atender cuestiones de seguridad. Su "
    "tratamiento deberá ajustarse a la normativa aplicable sobre protección de datos "
    "personales."
)

_FOTOGRAFIAS = (
    "La toma y utilización de fotografías o videos con fines promocionales se gestionará "
    "mediante una autorización específica, cuando corresponda. La aceptación de los términos "
    "generales no implica por sí sola la autorización para utilizar la imagen del "
    "participante."
)

_ACEPTACION = (
    "Declaro que he leído y comprendido estos términos y condiciones, que tuve la posibilidad "
    "de consultar las dudas que considere necesarias y que acepto cumplir las normas de "
    "participación y seguridad de la actividad. Al marcar «Acepto los términos y condiciones» "
    "en la inscripción, quien se inscribe deja constancia de su aceptación y, si inscribe a "
    "menores de edad, declara ser su madre, padre, tutor o representante legal."
)


def _lista(items):
    return "\n".join(f"- {item}" for item in items)


def _requisitos(edad_minima, requiere_talla, cupo_por_turno):
    edad = f"Desde {edad_minima} años." if edad_minima else "Todas las edades."
    if requiere_talla:
        talla = "Al inscribirte tenés que indicar la talla de vestimenta de cada visitante."
    else:
        talla = "No hace falta indicar la talla de vestimenta."
    condiciones = [
        f"Edad: {edad}",
        talla,
        f"Hay {cupo_por_turno} lugares por turno. Cada turno dura una hora.",
        f"Se puede reservar hasta {_HORAS_DE_ANTICIPACION} horas antes del turno. La "
        f"inscripción cierra {_MINUTOS_DE_CIERRE} minutos antes de que empiece.",
        f"Una misma inscripción puede incluir hasta {MAXIMO_DE_PERSONAS} personas.",
        "Una misma persona no puede tener dos turnos en el mismo horario.",
        "La reserva se confirma cuando se recibe el email con el código de reserva y un "
        "código QR por cada visitante. El día de la actividad hay que presentar el DNI y el "
        "código QR.",
    ]
    return (
        "El participante deberá completar el formulario de inscripción con información "
        "veraz (nombre, DNI de 7 u 8 dígitos y edad de cada visitante) y aceptar estos "
        "términos y condiciones antes de participar. Condiciones de esta actividad:\n"
        f"{_lista(condiciones)}\n"
        "En caso de menores de edad, la inscripción y autorización deberán ser realizadas por "
        "su madre, padre, tutor o representante legal, según corresponda."
    )


def _apartado(numero, titulo, contenido):
    return f"{numero}. {titulo}\n{contenido}"


def redactar_terminos(nombre, edad_minima, requiere_talla, cupo_por_turno):
    if nombre not in _DE_LA_ACTIVIDAD:
        raise ValueError(f"No hay texto de terminos y condiciones para la actividad {nombre}")
    propio = _DE_LA_ACTIVIDAD[nombre]
    titulo_del_equipo, texto_del_equipo = propio["equipo"]
    apartados = [
        _apartado(1, "Objeto de la actividad", propio["objeto"]),
        _apartado(
            2,
            "Requisitos de inscripción",
            _requisitos(edad_minima, requiere_talla, cupo_por_turno),
        ),
        _apartado(
            3,
            "Normas de seguridad",
            f"El participante se compromete a:\n{_lista(propio['normas'])}",
        ),
        _apartado(4, titulo_del_equipo, texto_del_equipo),
        _apartado(5, "Salud y condiciones de participación", propio["salud"]),
        _apartado(6, "Responsabilidad de la organización", _RESPONSABILIDAD),
        _apartado(7, "Modificaciones, suspensión o cancelación", _MODIFICACIONES),
        _apartado(8, "Cuidado de las instalaciones y del medioambiente", propio["cuidado"]),
        _apartado(9, "Datos personales", _DATOS_PERSONALES),
        _apartado(10, "Fotografías y videos", _FOTOGRAFIAS),
        _apartado(11, "Aceptación", _ACEPTACION),
    ]
    encabezado = f"TÉRMINOS Y CONDICIONES DE PARTICIPACIÓN\nActividad: {propio['titulo']}"
    return "\n\n".join([encabezado, *apartados]) + "\n"
