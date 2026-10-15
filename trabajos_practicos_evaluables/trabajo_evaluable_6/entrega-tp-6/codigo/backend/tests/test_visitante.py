import pytest

from ecoharmony.actividad import Actividad
from ecoharmony.motivos import MotivoRechazo
from ecoharmony.visitante import Visitante

safari = Actividad("Safari", cupo_por_turno=8)


def test_visitante_con_nombre_dni_y_edad_es_valido_si_la_actividad_no_requiere_talla():
    ana = Visitante("Ana Perez", "30123456", 30)

    assert ana.errores(safari) == []


def test_visitante_sin_nombre_es_invalido():
    sin_nombre = Visitante("", "30123456", 30)

    assert sin_nombre.errores(safari) == [MotivoRechazo.NOMBRE_REQUERIDO]


def test_visitante_con_nombre_de_solo_espacios_es_invalido():
    solo_espacios = Visitante("   ", "30123456", 30)

    assert solo_espacios.errores(safari) == [MotivoRechazo.NOMBRE_REQUERIDO]


def test_visitante_sin_dni_es_invalido():
    sin_dni = Visitante("Ana Perez", "", 30)

    assert sin_dni.errores(safari) == [MotivoRechazo.DNI_REQUERIDO]


def test_visitante_con_dni_no_numerico_es_invalido():
    dni_con_letra = Visitante("Ana Perez", "12A45678", 30)

    assert dni_con_letra.errores(safari) == [MotivoRechazo.DNI_INVALIDO]


@pytest.mark.parametrize(
    "dni, es_valido",
    [("123456", False), ("1234567", True), ("12345678", True), ("123456789", False)],
)
def test_el_dni_valido_tiene_7_u_8_digitos(dni, es_valido):
    visitante = Visitante("Ana Perez", dni, 30)

    assert (visitante.errores(safari) == []) is es_valido


def test_visitante_sin_edad_es_invalido():
    sin_edad = Visitante("Ana Perez", "30123456", None)

    assert sin_edad.errores(safari) == [MotivoRechazo.EDAD_REQUERIDA]


@pytest.mark.parametrize("edad", ["abc", 12.5])
def test_visitante_con_edad_no_entera_es_invalido(edad):
    visitante = Visitante("Ana Perez", "30123456", edad)

    assert visitante.errores(safari) == [MotivoRechazo.EDAD_INVALIDA]


@pytest.mark.parametrize(
    "edad, es_valida",
    [(-1, False), (0, True), (100, True), (101, False)],
)
def test_la_edad_valida_esta_entre_0_y_100(edad, es_valida):
    visitante = Visitante("Ana Perez", "30123456", edad)

    assert (visitante.errores(safari) == []) is es_valida


def test_visitante_menor_a_la_edad_minima_de_la_actividad_es_invalido():
    tirolesa = Actividad("Tirolesa", cupo_por_turno=10, edad_minima=8)
    nino = Visitante("Tomas Perez", "50123456", 7)

    assert nino.errores(tirolesa) == [MotivoRechazo.EDAD_NO_PERMITIDA]


tirolesa = Actividad("Tirolesa", cupo_por_turno=10, requiere_talla=True)


def test_visitante_sin_talla_es_invalido_si_la_actividad_la_requiere():
    sin_talla = Visitante("Ana Perez", "30123456", 30)

    assert sin_talla.errores(tirolesa) == [MotivoRechazo.TALLA_REQUERIDA]


def test_visitante_con_talla_es_valido_si_la_actividad_la_requiere():
    con_talla = Visitante("Ana Perez", "30123456", 30, talla="M")

    assert con_talla.errores(tirolesa) == []


@pytest.mark.parametrize("talla", ["XXXXL", "ancha", "m"])
def test_visitante_con_talla_fuera_de_los_valores_permitidos_es_invalido(talla):
    visitante = Visitante("Ana Perez", "30123456", 30, talla=talla)

    assert visitante.errores(tirolesa) == [MotivoRechazo.TALLA_INVALIDA]


def test_visitante_con_talla_es_valido_aunque_la_actividad_no_la_requiera():
    con_talla = Visitante("Ana Perez", "30123456", 30, talla="M")

    assert con_talla.errores(safari) == []


@pytest.mark.parametrize(
    "nombre, es_valido",
    [("A", True), ("A" * 30, True), ("A" * 31, False)],
)
def test_el_nombre_tiene_como_maximo_30_caracteres(nombre, es_valido):
    visitante = Visitante(nombre, "30123456", 30)

    assert (visitante.errores(safari) == []) is es_valido


@pytest.mark.parametrize(
    "nombre, es_valido",
    [("Maria José", True), ("D'Angelo", True), ("Pérez-Núñez", True), ("Ana2", False), ("Ana@", False)],
)
def test_el_nombre_solo_admite_letras_espacios_apostrofe_y_guion(nombre, es_valido):
    visitante = Visitante(nombre, "30123456", 30)

    assert (visitante.errores(safari) == []) is es_valido
