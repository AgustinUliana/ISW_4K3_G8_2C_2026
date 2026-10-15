import pytest

from ecoharmony.actividad import Actividad
from ecoharmony.motivos import MotivoRechazo
from ecoharmony.visitante import Visitante

safari = Actividad("Safari", cupo_por_turno=8)
tirolesa = Actividad("Tirolesa", cupo_por_turno=10, edad_minima=8, requiere_talla=True)


def un_visitante(**cambios):
    """Visitante valido (Ana Perez) con los campos que se quieran pisar."""
    datos = {"nombre": "Ana Perez", "dni": "30123456", "edad": 30, "talla": None}
    datos.update(cambios)
    return Visitante(**datos)


def test_visitante_con_nombre_dni_y_edad_es_valido_si_la_actividad_no_requiere_talla():
    assert un_visitante().errores(safari) == []


def test_visitante_sin_nombre_es_invalido():
    assert un_visitante(nombre="").errores(safari) == [MotivoRechazo.NOMBRE_REQUERIDO]


def test_visitante_con_nombre_de_solo_espacios_es_invalido():
    assert un_visitante(nombre="   ").errores(safari) == [MotivoRechazo.NOMBRE_REQUERIDO]


def test_visitante_sin_dni_es_invalido():
    assert un_visitante(dni="").errores(safari) == [MotivoRechazo.DNI_REQUERIDO]


def test_visitante_con_dni_no_numerico_es_invalido():
    assert un_visitante(dni="12A45678").errores(safari) == [MotivoRechazo.DNI_INVALIDO]


@pytest.mark.parametrize(
    "dni, es_valido",
    [("123456", False), ("1234567", True), ("12345678", True), ("123456789", False)],
)
def test_el_dni_valido_tiene_7_u_8_digitos(dni, es_valido):
    assert (un_visitante(dni=dni).errores(safari) == []) is es_valido


def test_visitante_sin_edad_es_invalido():
    assert un_visitante(edad=None).errores(safari) == [MotivoRechazo.EDAD_REQUERIDA]


@pytest.mark.parametrize("edad", ["abc", 12.5])
def test_visitante_con_edad_no_entera_es_invalido(edad):
    assert un_visitante(edad=edad).errores(safari) == [MotivoRechazo.EDAD_INVALIDA]


@pytest.mark.parametrize(
    "edad, es_valida",
    [(-1, False), (0, True), (100, True), (101, False)],
)
def test_la_edad_valida_esta_entre_0_y_100(edad, es_valida):
    assert (un_visitante(edad=edad).errores(safari) == []) is es_valida


def test_visitante_menor_a_la_edad_minima_de_la_actividad_es_invalido():
    nino = un_visitante(edad=7, talla="M")

    assert nino.errores(tirolesa) == [MotivoRechazo.EDAD_NO_PERMITIDA]


def test_visitante_sin_talla_es_invalido_si_la_actividad_la_requiere():
    assert un_visitante().errores(tirolesa) == [MotivoRechazo.TALLA_REQUERIDA]


def test_visitante_con_talla_es_valido_si_la_actividad_la_requiere():
    assert un_visitante(talla="M").errores(tirolesa) == []


@pytest.mark.parametrize("talla", ["XXXXL", "ancha", "m"])
def test_visitante_con_talla_fuera_de_los_valores_permitidos_es_invalido(talla):
    assert un_visitante(talla=talla).errores(tirolesa) == [MotivoRechazo.TALLA_INVALIDA]


def test_visitante_con_talla_es_valido_aunque_la_actividad_no_la_requiera():
    assert un_visitante(talla="M").errores(safari) == []


@pytest.mark.parametrize(
    "nombre, es_valido",
    [("A", True), ("A" * 30, True), ("A" * 31, False)],
)
def test_el_nombre_tiene_como_maximo_30_caracteres(nombre, es_valido):
    assert (un_visitante(nombre=nombre).errores(safari) == []) is es_valido


@pytest.mark.parametrize(
    "nombre, es_valido",
    [
        ("Maria José", True),
        ("D'Angelo", True),
        ("Pérez-Núñez", True),
        ("Ana2", False),
        ("Ana@", False),
    ],
)
def test_el_nombre_solo_admite_letras_espacios_apostrofe_y_guion(nombre, es_valido):
    assert (un_visitante(nombre=nombre).errores(safari) == []) is es_valido


@pytest.mark.parametrize("nombre", [None, 123])
def test_visitante_con_nombre_nulo_o_que_no_es_texto_es_invalido(nombre):
    assert un_visitante(nombre=nombre).errores(safari) == [MotivoRechazo.NOMBRE_REQUERIDO]


def test_visitante_con_dni_que_no_es_texto_es_invalido():
    assert un_visitante(dni=30123456).errores(safari) == [MotivoRechazo.DNI_INVALIDO]
