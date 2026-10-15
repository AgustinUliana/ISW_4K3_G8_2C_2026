from datetime import date, datetime, time

import pytest

from ecoharmony.catalogo import crear_actividades
from ecoharmony.horario import Horario
from ecoharmony.inscripcion import EstadoDeLaInscripcion, Inscripcion
from ecoharmony.motivos import MotivoRechazo
from ecoharmony.parque import Parque
from ecoharmony.visitante import Visitante

AHORA = datetime(2026, 11, 4, 8, 0)  # miercoles 08:00
H1 = Horario(date(2026, 11, 4), time(10, 0))
ANA = Visitante("Ana Perez", "30123456", 30, talla="M")


def una_inscripcion(**cambios):
    """Inscripcion valida (Tirolesa, H1, Ana) con los campos que se quieran pisar."""
    actividad = cambios.get("actividad", crear_actividades()["Tirolesa"])
    datos = {
        "actividad": actividad,
        "horario": H1,
        "visitantes": [ANA],
        "email_de_contacto": "ana.perez@example.com",
        "terminos_aceptados": actividad.terminos if actividad else None,
    }
    datos.update(cambios)
    return Inscripcion(**datos)


def motivos_de_una_inscripcion(ahora=AHORA, **cambios):
    return una_inscripcion(**cambios).motivos_de_rechazo(Parque(), ahora)


def test_se_confirma_con_todos_los_datos_validos():
    assert motivos_de_una_inscripcion() == []


def test_se_rechaza_sin_aceptar_los_terminos_y_condiciones():
    motivos = motivos_de_una_inscripcion(terminos_aceptados=None)

    assert motivos == [MotivoRechazo.TERMINOS_NO_ACEPTADOS]


def test_se_rechaza_si_se_aceptan_los_terminos_de_otra_actividad():
    terminos_de_jardineria = crear_actividades()["Jardinería"].terminos

    motivos = motivos_de_una_inscripcion(terminos_aceptados=terminos_de_jardineria)

    assert motivos == [MotivoRechazo.TERMINOS_DE_OTRA_ACTIVIDAD]


def test_se_confirma_cuando_se_aceptan_los_terminos_especificos_de_la_actividad():
    jardineria = crear_actividades()["Jardinería"]

    motivos = motivos_de_una_inscripcion(
        actividad=jardineria, terminos_aceptados=jardineria.terminos
    )

    assert motivos == []


def test_se_rechaza_sin_actividad():
    assert motivos_de_una_inscripcion(actividad=None) == [MotivoRechazo.ACTIVIDAD_REQUERIDA]


def test_se_rechaza_sin_horario():
    assert motivos_de_una_inscripcion(horario=None) == [MotivoRechazo.HORARIO_REQUERIDO]


def test_se_rechaza_sin_visitantes():
    assert motivos_de_una_inscripcion(visitantes=[]) == [MotivoRechazo.CANTIDAD_INVALIDA]


def n_visitantes(cantidad):
    return [
        Visitante(f"Persona {chr(65 + i)}", str(30000001 + i), 30, talla="M")
        for i in range(cantidad)
    ]


@pytest.mark.parametrize("cantidad, motivos", [(10, []), (11, [MotivoRechazo.CANTIDAD_INVALIDA])])
def test_se_rechaza_si_supera_el_maximo_de_10_personas_por_inscripcion(cantidad, motivos):
    palestra = crear_actividades()[
        "Palestra"
    ]  # cupo 12: el limite que actua es el de 10 por inscripcion

    resultado = motivos_de_una_inscripcion(actividad=palestra, visitantes=n_visitantes(cantidad))

    assert resultado == motivos


def test_se_rechaza_si_algun_visitante_es_invalido_e_indica_cual():
    sin_dni = Visitante("Luis Gomez", "", 41, talla="L")
    inscripcion = una_inscripcion(
        visitantes=[ANA, sin_dni, Visitante("Eva Soto", "30123457", 25, talla="S")]
    )

    assert inscripcion.motivos_de_rechazo(Parque(), AHORA) == [MotivoRechazo.VISITANTE_INVALIDO]
    assert inscripcion.errores_por_visitante() == {2: [MotivoRechazo.DNI_REQUERIDO]}


def test_se_rechaza_si_hay_un_dni_repetido_dentro_de_la_misma_inscripcion():
    luis_con_el_dni_de_ana = Visitante("Luis Gomez", ANA.dni, 41, talla="L")

    motivos = motivos_de_una_inscripcion(visitantes=[ANA, luis_con_el_dni_de_ana])

    assert motivos == [MotivoRechazo.DNI_DUPLICADO]


def test_se_rechaza_si_no_hay_cupo():
    tirolesa = crear_actividades()["Tirolesa"]
    tirolesa.reservar(H1, cantidad=10)

    assert motivos_de_una_inscripcion(actividad=tirolesa) == [MotivoRechazo.SIN_CUPO]


def test_se_rechaza_si_el_cupo_alcanza_solo_para_parte_del_grupo():
    palestra = crear_actividades()["Palestra"]
    palestra.reservar(H1, cantidad=9)  # quedan 3

    motivos = motivos_de_una_inscripcion(actividad=palestra, visitantes=n_visitantes(4))

    assert motivos == [MotivoRechazo.SIN_CUPO]
    assert palestra.cupo_restante(H1) == 3  # no se reservo nada


@pytest.mark.parametrize("hora", [time(8, 0), time(10, 30), time(18, 0)])
def test_se_rechaza_si_el_horario_no_es_un_turno_de_la_actividad(hora):
    no_es_turno = Horario(date(2026, 11, 4), hora)

    assert motivos_de_una_inscripcion(horario=no_es_turno) == [MotivoRechazo.HORARIO_NO_DISPONIBLE]


def test_se_rechaza_si_el_parque_esta_cerrado_ese_dia():
    lunes = Horario(date(2026, 11, 2), time(10, 0))
    lunes_a_las_8 = datetime(2026, 11, 2, 8, 0)

    motivos = motivos_de_una_inscripcion(horario=lunes, ahora=lunes_a_las_8)

    assert motivos == [MotivoRechazo.PARQUE_CERRADO]


@pytest.mark.parametrize("ahora", [datetime(2026, 11, 4, 9, 46), datetime(2026, 11, 4, 10, 30)])
def test_se_rechaza_si_el_turno_es_dentro_de_menos_de_15_minutos_o_ya_paso(ahora):
    motivos = motivos_de_una_inscripcion(ahora=ahora)

    assert motivos == [MotivoRechazo.INSCRIPCION_CERRADA]


def test_se_rechaza_si_el_turno_esta_a_mas_de_24_horas():
    viernes = Horario(date(2026, 11, 6), time(10, 0))  # AHORA es el miercoles a las 8

    assert motivos_de_una_inscripcion(horario=viernes) == [MotivoRechazo.FUERA_DE_VENTANA]


@pytest.mark.parametrize(
    "email", ["", "ana", "ana@", "ana@dominio", "@dominio.com", "ana perez@dominio.com"]
)
def test_se_rechaza_sin_email_de_contacto_valido(email):
    assert motivos_de_una_inscripcion(email_de_contacto=email) == [MotivoRechazo.EMAIL_INVALIDO]


def test_se_acumulan_todos_los_motivos_de_rechazo():
    motivos = motivos_de_una_inscripcion(horario=None, terminos_aceptados=None)

    assert set(motivos) == {MotivoRechazo.HORARIO_REQUERIDO, MotivoRechazo.TERMINOS_NO_ACEPTADOS}


def test_la_inscripcion_confirmada_tiene_su_codigo_y_estado_confirmada():
    inscripcion = una_inscripcion()
    assert inscripcion.estado is EstadoDeLaInscripcion.PENDIENTE

    inscripcion.confirmar(codigo="INS-0001", ahora=AHORA)

    assert inscripcion.estado is EstadoDeLaInscripcion.CONFIRMADA
    assert inscripcion.codigo == "INS-0001"


def test_la_inscripcion_confirmada_registra_la_version_de_los_terminos_y_cuando_se_acepto():
    inscripcion = una_inscripcion()

    inscripcion.confirmar(codigo="INS-0001", ahora=AHORA)

    assert inscripcion.terminos_aceptados.version == "v1"
    assert inscripcion.confirmada_el == AHORA
