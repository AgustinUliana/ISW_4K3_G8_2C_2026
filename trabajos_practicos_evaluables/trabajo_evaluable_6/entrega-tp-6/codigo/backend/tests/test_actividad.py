from datetime import date, time

import pytest

from ecoharmony.actividad import Actividad
from ecoharmony.errores import CupoInsuficiente
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

    with pytest.raises(CupoInsuficiente):
        tirolesa.reservar(H1, cantidad=3)

    assert tirolesa.cupo_restante(H1) == 2


def test_el_cupo_de_un_horario_no_afecta_a_otro_horario(tirolesa):
    tirolesa.reservar(H1, cantidad=3)

    assert tirolesa.cupo_restante(H2) == 10
