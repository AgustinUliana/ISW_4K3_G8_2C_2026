"""Pruebas de CONTRATO del repositorio.

El mismo conjunto debe pasar con RepositorioEnMemoria (el fake que usan las
unitarias) y, mas adelante, con RepositorioPostgres: asi el fake no se aparta
del comportamiento real (Beck, patron Mock Object).
"""
import pytest
from datos_de_prueba import ANA, H1, LUIS, una_inscripcion_confirmada

from ecoharmony.catalogo import crear_actividades
from ecoharmony.errores import ActividadNoEncontrada, CupoInsuficiente
from ecoharmony.repositorio_memoria import RepositorioEnMemoria


@pytest.fixture(params=["memoria"])
def repositorio(request):
    return RepositorioEnMemoria(crear_actividades())


def test_buscar_una_actividad_por_nombre_devuelve_la_actividad(repositorio):
    assert repositorio.actividad("Safari").nombre == "Safari"


def test_buscar_una_actividad_inexistente_falla(repositorio):
    with pytest.raises(ActividadNoEncontrada):
        repositorio.actividad("Rafting")


def test_recuperar_un_codigo_inexistente_devuelve_none(repositorio):
    assert repositorio.obtener("INS-9999") is None


def test_se_guarda_y_se_recupera_una_inscripcion_por_codigo(repositorio):
    inscripcion = una_inscripcion_confirmada(repositorio.siguiente_codigo())

    repositorio.guardar(inscripcion)

    recuperada = repositorio.obtener(inscripcion.codigo)
    assert recuperada.actividad.nombre == "Tirolesa"
    assert recuperada.horario == H1
    assert [v.dni for v in recuperada.visitantes] == [ANA.dni, LUIS.dni]
    assert recuperada.email_de_contacto == inscripcion.email_de_contacto
    assert recuperada.terminos_aceptados == inscripcion.terminos_aceptados


def test_el_cupo_reservado_se_conserva_al_volver_a_pedir_la_actividad(repositorio):
    inscripcion = una_inscripcion_confirmada(repositorio.siguiente_codigo())  # 2 personas

    repositorio.guardar(inscripcion)

    assert repositorio.actividad("Tirolesa").cupo_restante(H1) == 8


def test_guardar_la_inscripcion_y_reservar_el_cupo_es_todo_o_nada(repositorio):
    repositorio.actividad("Tirolesa").reservar(H1, cantidad=9)  # queda 1
    inscripcion = una_inscripcion_confirmada(repositorio.siguiente_codigo())  # pide 2

    with pytest.raises(CupoInsuficiente):
        repositorio.guardar(inscripcion)

    assert repositorio.obtener(inscripcion.codigo) is None
    assert repositorio.actividad("Tirolesa").cupo_restante(H1) == 1


def test_se_puede_consultar_si_un_dni_ya_esta_inscripto_en_una_fecha_y_hora(repositorio):
    from datetime import date, time

    from ecoharmony.horario import Horario

    repositorio.guardar(una_inscripcion_confirmada(repositorio.siguiente_codigo()))
    a_las_11 = Horario(date(2026, 11, 4), time(11, 0))

    assert repositorio.dni_inscripto_en(ANA.dni, H1)
    assert not repositorio.dni_inscripto_en(ANA.dni, a_las_11)
    assert not repositorio.dni_inscripto_en("99999999", H1)
