import pytest

from ecoharmony.catalogo import crear_actividades

# nombre: (cupo por turno, requiere talla, edad minima)  -- respuestas del PO
REGLAS_DEL_PO = {
    "Tirolesa": (10, True, 8),
    "Safari": (8, False, 0),
    "Palestra": (12, True, 12),
    "Jardinería": (12, False, 0),
}


@pytest.mark.parametrize("nombre", REGLAS_DEL_PO)
def test_el_catalogo_tiene_cada_actividad_con_su_cupo_talla_y_edad_minima(nombre):
    actividad = crear_actividades()[nombre]

    reglas = (actividad.cupo_por_turno, actividad.requiere_talla, actividad.edad_minima)
    assert reglas == REGLAS_DEL_PO[nombre]


def test_el_catalogo_contiene_exactamente_las_cuatro_actividades():
    assert set(crear_actividades()) == set(REGLAS_DEL_PO)


def test_cada_actividad_tiene_sus_propios_terminos_y_condiciones():
    actividades = crear_actividades()
    textos = {a.terminos.texto for a in actividades.values()}

    assert len(textos) == 4
    assert all(a.terminos.actividad == a.nombre for a in actividades.values())
    assert all(a.terminos.texto.strip() for a in actividades.values())
