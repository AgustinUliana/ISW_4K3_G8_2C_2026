from datetime import date, time

import pytest

from ecoharmony.actividad import Actividad
from ecoharmony.errores import CupoInsuficienteError
from ecoharmony.horario import Horario

H1 = Horario(date(2026, 11, 4), time(10, 0))
H2 = Horario(date(2026, 11, 4), time(11, 0))


@pytest.fixture
def tirolesa():
    return Actividad("Tirolesa", cupo_por_turno=10)


def test_hay_cupo_si_se_piden_menos_personas_que_el_cupo_restante(tirolesa):
    assert tirolesa.tiene_cupo(H1, cantidad=3)


def test_hay_cupo_si_se_piden_exactamente_las_personas_del_cupo_restante(tirolesa):
    assert tirolesa.tiene_cupo(H1, cantidad=10)


def test_no_hay_cupo_si_se_piden_mas_personas_que_el_cupo_restante(tirolesa):
    assert not tirolesa.tiene_cupo(H1, cantidad=11)


def test_no_hay_cupo_si_el_cupo_esta_agotado(tirolesa):
    tirolesa.reservar(H1, cantidad=10)

    assert not tirolesa.tiene_cupo(H1, cantidad=1)


def test_reservar_descuenta_del_cupo_restante(tirolesa):
    tirolesa.reservar(H1, cantidad=3)

    assert tirolesa.cupo_restante(H1) == 7


def test_reservas_sucesivas_se_acumulan(tirolesa):
    tirolesa.reservar(H1, cantidad=3)
    tirolesa.reservar(H1, cantidad=4)

    assert tirolesa.cupo_restante(H1) == 3


def test_reservar_mas_que_el_restante_falla_sin_modificar_el_cupo(tirolesa):
    tirolesa.reservar(H1, cantidad=8)

    with pytest.raises(CupoInsuficienteError):
        tirolesa.reservar(H1, cantidad=3)

    assert tirolesa.cupo_restante(H1) == 2


def test_el_cupo_de_un_horario_no_afecta_a_otro_horario(tirolesa):
    tirolesa.reservar(H1, cantidad=3)

    assert tirolesa.cupo_restante(H2) == 10


@pytest.mark.parametrize("hora", [time(8, 0), time(10, 30), time(18, 0)])
def test_no_hay_cupo_en_un_horario_que_no_es_turno_de_la_actividad(tirolesa, hora):
    no_es_turno = Horario(date(2026, 11, 4), hora)

    assert not tirolesa.tiene_cupo(no_es_turno, cantidad=1)


@pytest.mark.parametrize("edad, admitida", [(7, False), (8, True), (30, True)])
def test_actividad_con_edad_minima_rechaza_a_los_menores(edad, admitida):
    tirolesa = Actividad("Tirolesa", cupo_por_turno=10, edad_minima=8)

    assert tirolesa.admite_edad(edad) is admitida


def test_actividad_sin_edad_minima_admite_todas_las_edades():
    safari = Actividad("Safari", cupo_por_turno=8)

    assert safari.admite_edad(0)


def test_liberar_devuelve_lugares_al_cupo_restante(tirolesa):
    tirolesa.reservar(H1, cantidad=5)

    tirolesa.liberar(H1, cantidad=3)

    assert tirolesa.cupo_restante(H1) == 8


def test_liberar_mas_de_lo_reservado_nunca_supera_el_cupo_maximo(tirolesa):
    tirolesa.reservar(H1, cantidad=2)

    tirolesa.liberar(H1, cantidad=5)

    assert tirolesa.cupo_restante(H1) == 10
