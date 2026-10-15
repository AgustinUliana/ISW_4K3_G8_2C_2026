"""T&C propios de cada actividad: texto real (borrador), armado con las reglas del PO."""

import pytest

from ecoharmony.catalogo import crear_actividades
from ecoharmony.terminos_texto import VERSION_DE_LOS_TERMINOS, redactar_terminos

ACTIVIDADES = ["Tirolesa", "Safari", "Palestra", "Jardinería"]


@pytest.fixture
def terminos():
    return {nombre: actividad.terminos for nombre, actividad in crear_actividades().items()}


def test_ninguna_actividad_conserva_el_texto_provisorio(terminos):
    for t in terminos.values():
        assert "provisorio" not in t.texto.lower()
        assert "a redactar" not in t.texto.lower()
        assert len(t.texto) > 600


def test_los_terminos_tienen_version(terminos):
    assert VERSION_DE_LOS_TERMINOS == "v1"
    assert all(t.version == "v1" for t in terminos.values())


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_el_titulo_nombra_la_actividad(terminos, nombre):
    titulo = terminos[nombre].texto.splitlines()[0]

    assert nombre.upper() in titulo.upper()


def test_cada_actividad_tiene_su_propio_apartado_y_los_demas_no_lo_comparten(terminos):
    propias = {
        "Tirolesa": "equipo de seguridad",
        "Safari": "animales",
        "Palestra": "arnés",
        "Jardinería": "plantas",
    }
    for nombre, marca in propias.items():
        assert marca in terminos[nombre].texto
        for otra, _ in propias.items():
            if otra != nombre:
                assert marca not in terminos[otra].texto


@pytest.mark.parametrize(
    "nombre, edad", [("Tirolesa", "Desde 8 años"), ("Palestra", "Desde 12 años")]
)
def test_exige_la_edad_minima_de_la_actividad(terminos, nombre, edad):
    assert edad in terminos[nombre].texto


@pytest.mark.parametrize("nombre", ["Safari", "Jardinería"])
def test_sin_edad_minima_dice_que_es_para_todas_las_edades(terminos, nombre):
    assert "Todas las edades" in terminos[nombre].texto


@pytest.mark.parametrize("nombre", ["Tirolesa", "Palestra"])
def test_donde_se_requiere_la_talla_se_explica_que_hay_que_indicarla(terminos, nombre):
    texto = terminos[nombre].texto.lower()

    assert "indicar la talla de vestimenta de cada visitante" in texto
    assert "no hace falta" not in texto


@pytest.mark.parametrize("nombre", ["Safari", "Jardinería"])
def test_donde_no_se_requiere_la_talla_se_aclara_que_no_hace_falta(terminos, nombre):
    assert "no hace falta indicar la talla" in terminos[nombre].texto.lower()


@pytest.mark.parametrize(
    "nombre, cupo", [("Tirolesa", 10), ("Safari", 8), ("Palestra", 12), ("Jardinería", 12)]
)
def test_informa_el_cupo_por_turno_de_la_actividad(terminos, nombre, cupo):
    assert f"{cupo} lugares por turno" in terminos[nombre].texto


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_incluye_las_reglas_de_reserva_del_po(terminos, nombre):
    texto = terminos[nombre].texto

    assert "24 horas" in texto  # se reserva hasta 24 horas antes
    assert "15 minutos" in texto  # la inscripcion cierra 15 minutos antes
    assert "10 personas" in texto  # maximo por inscripcion
    assert "QR" in texto
    assert "DNI" in texto


def test_el_texto_se_arma_con_las_reglas_de_la_actividad_y_no_con_numeros_fijos():
    texto = redactar_terminos("Tirolesa", edad_minima=10, requiere_talla=False, cupo_por_turno=5)

    assert "Desde 10 años" in texto
    assert "5 lugares por turno" in texto
    assert "no hace falta indicar la talla" in texto.lower()


def test_una_actividad_sin_texto_propio_no_se_puede_redactar():
    with pytest.raises(ValueError, match="Rafting"):
        redactar_terminos("Rafting", edad_minima=0, requiere_talla=False, cupo_por_turno=5)
