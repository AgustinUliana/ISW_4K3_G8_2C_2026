"""Pruebas de CONTRATO del repositorio.

El mismo conjunto debe pasar con RepositorioEnMemoria (el fake que usan las
unitarias) y, mas adelante, con RepositorioPostgres: asi el fake no se aparta
del comportamiento real (Beck, patron Mock Object).
"""

import pytest

from datos_de_prueba import ANA, H1, LUIS, n_visitantes, una_inscripcion_confirmada
from ecoharmony.catalogo import crear_actividades
from ecoharmony.errores import (
    ActividadNoEncontradaError,
    CupoInsuficienteError,
    DniYaInscriptoError,
)
from ecoharmony.repositorio_memoria import RepositorioEnMemoria
from ecoharmony.repositorio_postgres import RepositorioPostgres


@pytest.fixture(
    params=[
        "memoria",
        pytest.param("postgres", marks=[pytest.mark.local, pytest.mark.db]),
    ]
)
def repositorio(request):
    if request.param == "memoria":
        return RepositorioEnMemoria(crear_actividades())
    repositorio = RepositorioPostgres(request.getfixturevalue("base_con_esquema"))
    repositorio.cargar_actividades(crear_actividades())
    return repositorio


def test_buscar_una_actividad_por_nombre_devuelve_la_actividad(repositorio):
    assert repositorio.actividad("Safari").nombre == "Safari"


def test_buscar_una_actividad_inexistente_falla(repositorio):
    with pytest.raises(ActividadNoEncontradaError):
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
    nueve = una_inscripcion_confirmada(repositorio.siguiente_codigo(), visitantes=n_visitantes(9))
    repositorio.guardar(nueve)  # queda 1 lugar
    inscripcion = una_inscripcion_confirmada(repositorio.siguiente_codigo())  # pide 2

    with pytest.raises(CupoInsuficienteError):
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


@pytest.mark.parametrize("nombre", ["Tirolesa", "Safari", "Palestra", "Jardinería"])
def test_la_carga_inicial_deja_cada_actividad_con_sus_reglas_y_terminos(repositorio, nombre):
    esperada = crear_actividades()[nombre]

    cargada = repositorio.actividad(nombre)

    assert cargada.cupo_por_turno == esperada.cupo_por_turno
    assert cargada.edad_minima == esperada.edad_minima
    assert cargada.requiere_talla == esperada.requiere_talla
    assert cargada.terminos == esperada.terminos


def test_guardar_con_un_dni_ya_inscripto_en_ese_horario_falla_sin_dejar_rastro(repositorio):
    repositorio.guardar(una_inscripcion_confirmada(repositorio.siguiente_codigo(), [ANA]))
    de_ana_otra_vez = una_inscripcion_confirmada(repositorio.siguiente_codigo(), [ANA, LUIS])

    with pytest.raises(DniYaInscriptoError):
        repositorio.guardar(de_ana_otra_vez)

    assert repositorio.obtener(de_ana_otra_vez.codigo) is None
    assert repositorio.actividad("Tirolesa").cupo_restante(H1) == 9  # solo cuenta la 1ra


@pytest.mark.local
@pytest.mark.db
def test_dos_reservas_simultaneas_del_ultimo_cupo_solo_dejan_pasar_una(base_con_esquema):
    import threading

    repositorio = RepositorioPostgres(base_con_esquema)
    repositorio.cargar_actividades(crear_actividades())
    repositorio.guardar(
        una_inscripcion_confirmada(repositorio.siguiente_codigo(), n_visitantes(9))
    )  # queda 1 lugar
    pedidos = [
        una_inscripcion_confirmada(repositorio.siguiente_codigo(), [ANA]),
        una_inscripcion_confirmada(repositorio.siguiente_codigo(), [LUIS]),
    ]
    arrancan_juntos = threading.Barrier(2)
    resultados = []

    def intentar(inscripcion):
        arrancan_juntos.wait()
        try:
            repositorio.guardar(inscripcion)
            resultados.append("guardada")
        except CupoInsuficienteError:
            resultados.append("sin cupo")

    hilos = [threading.Thread(target=intentar, args=(pedido,)) for pedido in pedidos]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()

    assert sorted(resultados) == ["guardada", "sin cupo"]
    assert repositorio.actividad("Tirolesa").cupo_restante(H1) == 0


def test_anular_una_inscripcion_libera_el_cupo_y_el_dni(repositorio):
    inscripcion = una_inscripcion_confirmada(repositorio.siguiente_codigo())  # Ana y Luis
    repositorio.guardar(inscripcion)

    repositorio.anular(inscripcion.codigo)

    assert repositorio.obtener(inscripcion.codigo) is None
    assert repositorio.actividad("Tirolesa").cupo_restante(H1) == 10
    assert not repositorio.dni_inscripto_en(ANA.dni, H1)


def test_anular_un_codigo_inexistente_no_falla(repositorio):
    repositorio.anular("INS-9999")


def test_se_listan_todas_las_actividades_del_catalogo(repositorio):
    nombres = {actividad.nombre for actividad in repositorio.actividades()}

    assert nombres == {"Tirolesa", "Safari", "Palestra", "Jardinería"}
