"""T&C propios de cada actividad: texto real (borrador), armado con las reglas del PO."""

import re

import pytest

from ecoharmony.catalogo import crear_actividades
from ecoharmony.terminos_texto import VERSION_DE_LOS_TERMINOS, redactar_terminos

ACTIVIDADES = ["Tirolesa", "Safari", "Palestra", "Jardinería"]
TITULOS_DE_APARTADOS = [
    "Objeto de la actividad",
    "Requisitos de inscripción",
    "Normas de seguridad",
    None,  # el cuarto apartado es propio de cada actividad
    "Salud y condiciones de participación",
    "Responsabilidad de la organización",
    "Modificaciones, suspensión o cancelación",
    "Cuidado de las instalaciones y del medioambiente",
    "Datos personales",
    "Fotografías y videos",
    "Aceptación",
]


@pytest.fixture
def terminos():
    return {nombre: actividad.terminos for nombre, actividad in crear_actividades().items()}


def _apartados(texto):
    """Devuelve {numero: (titulo, contenido)} de los apartados numerados del texto."""
    partes = re.split(r"^(\d+)\. (.+)$", texto, flags=re.MULTILINE)
    return {int(partes[i]): (partes[i + 1], partes[i + 2]) for i in range(1, len(partes), 3)}


def test_ninguna_actividad_conserva_el_texto_provisorio(terminos):
    for t in terminos.values():
        assert "provisorio" not in t.texto.lower()
        assert "a redactar" not in t.texto.lower()
        assert len(t.texto) > 2500


def test_los_terminos_tienen_version(terminos):
    assert VERSION_DE_LOS_TERMINOS == "v1"
    assert all(t.version == "v1" for t in terminos.values())


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_el_encabezado_dice_de_participacion_y_nombra_la_actividad(terminos, nombre):
    primeras = terminos[nombre].texto.splitlines()[:2]

    assert primeras[0] == "TÉRMINOS Y CONDICIONES DE PARTICIPACIÓN"
    assert primeras[1].startswith("Actividad: ")
    assert nombre in primeras[1]


def test_la_jardineria_se_presenta_como_jardineria_y_cuidado_de_espacios_verdes(terminos):
    assert "Actividad: Jardinería y cuidado de espacios verdes" in terminos["Jardinería"].texto


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_tiene_los_once_apartados_en_orden(terminos, nombre):
    apartados = _apartados(terminos[nombre].texto)

    assert sorted(apartados) == list(range(1, 12))
    for numero, titulo in enumerate(TITULOS_DE_APARTADOS, start=1):
        if titulo is not None:
            assert apartados[numero][0] == titulo


@pytest.mark.parametrize(
    "nombre, titulo_del_cuarto",
    [
        ("Tirolesa", "Uso del equipo de seguridad"),
        ("Safari", "Contacto con los animales y alimentación"),
        ("Palestra", "Uso del equipo de seguridad"),
        ("Jardinería", "Uso de herramientas y materiales"),
    ],
)
def test_el_cuarto_apartado_es_propio_de_la_actividad(terminos, nombre, titulo_del_cuarto):
    assert _apartados(terminos[nombre].texto)[4][0] == titulo_del_cuarto


def test_cada_actividad_tiene_sus_propias_normas_y_los_demas_no_las_comparten(terminos):
    propias = {
        "Tirolesa": "línea de vida",
        "Safari": "alimentar a los animales",
        "Palestra": "pared de escalada",
        "Jardinería": "sustratos",
    }
    for nombre, marca in propias.items():
        assert marca in terminos[nombre].texto
        for otra in propias:
            if otra != nombre:
                assert marca not in terminos[otra].texto


def test_las_normas_de_seguridad_son_distintas_en_cada_actividad(terminos):
    normas = [_apartados(terminos[nombre].texto)[3][1] for nombre in ACTIVIDADES]

    assert len(set(normas)) == 4


@pytest.mark.parametrize("nombre", ["Tirolesa", "Palestra"])
def test_en_altura_se_exige_arnes_casco_y_calzado_cerrado(terminos, nombre):
    texto = terminos[nombre].texto.lower()

    assert "arnés" in texto
    assert "casco" in texto
    assert "calzado cerrado" in texto


def test_en_el_safari_no_se_toca_ni_se_usa_flash(terminos):
    texto = terminos["Safari"].texto.lower()

    assert "no tocar" in texto
    assert "flash" in texto


def test_en_la_jardineria_se_usan_guantes_y_calzado_cerrado(terminos):
    texto = terminos["Jardinería"].texto.lower()

    assert "guantes" in texto
    assert "calzado cerrado" in texto
    assert "alergia" in texto


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_la_salud_pide_avisar_al_personal_antes_de_comenzar(terminos, nombre):
    salud = _apartados(terminos[nombre].texto)[5][1]

    assert "personal" in salud
    assert "antes de comenzar" in salud


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_los_menores_se_inscriben_a_traves_de_su_madre_padre_tutor_o_representante(
    terminos, nombre
):
    requisitos = _apartados(terminos[nombre].texto)[2][1]

    assert "menores de edad" in requisitos
    assert "madre, padre, tutor o representante legal" in requisitos


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_la_responsabilidad_del_parque_no_es_una_renuncia_general(terminos, nombre):
    responsabilidad = _apartados(terminos[nombre].texto)[6][1]

    assert "ni implican una renuncia general" in responsabilidad


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_el_parque_puede_suspender_por_clima_o_seguridad(terminos, nombre):
    modificaciones = _apartados(terminos[nombre].texto)[7][1]

    assert "condiciones climáticas" in modificaciones
    assert "seguridad" in modificaciones


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_las_fotos_requieren_una_autorizacion_especifica(terminos, nombre):
    fotos = _apartados(terminos[nombre].texto)[10][1]

    assert "autorización específica" in fotos
    assert "no implica por sí sola" in fotos


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_la_aceptacion_se_hace_marcando_la_casilla_y_no_con_firma(terminos, nombre):
    aceptacion = _apartados(terminos[nombre].texto)[11][1]

    assert "Declaro que he leído y comprendido" in aceptacion
    assert "Acepto los términos y condiciones" in aceptacion
    assert "Firma" not in aceptacion


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
    requisitos = _apartados(terminos[nombre].texto)[2][1]

    assert "24 horas" in requisitos  # se reserva hasta 24 horas antes
    assert "15 minutos" in requisitos  # la inscripcion cierra 15 minutos antes
    assert "10 personas" in requisitos  # maximo por inscripcion
    assert "QR" in requisitos
    assert "DNI" in requisitos


def test_el_texto_se_arma_con_las_reglas_de_la_actividad_y_no_con_numeros_fijos():
    texto = redactar_terminos("Tirolesa", edad_minima=10, requiere_talla=False, cupo_por_turno=5)

    assert "Desde 10 años" in texto
    assert "5 lugares por turno" in texto
    assert "no hace falta indicar la talla" in texto.lower()


def test_una_actividad_sin_texto_propio_no_se_puede_redactar():
    with pytest.raises(ValueError, match="Rafting"):
        redactar_terminos("Rafting", edad_minima=0, requiere_talla=False, cupo_por_turno=5)


@pytest.mark.parametrize("nombre", ACTIVIDADES)
def test_el_texto_no_muestra_la_version(terminos, nombre):
    texto = terminos[nombre].texto.lower()

    assert "versión" not in texto
    assert "version" not in texto
    assert not re.search(r"\bv\d+\b", texto)
