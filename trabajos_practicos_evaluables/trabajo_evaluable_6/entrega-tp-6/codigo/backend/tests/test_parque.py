from datetime import date, time

import pytest

from ecoharmony.horario import Horario
from ecoharmony.parque import Parque

MIERCOLES = date(2026, 11, 4)


def test_el_parque_esta_abierto_un_dia_comun_dentro_de_su_horario():
    parque = Parque()

    assert parque.esta_abierto(Horario(MIERCOLES, time(10, 0)))


def test_el_parque_esta_cerrado_si_el_horario_empieza_antes_de_la_apertura():
    parque = Parque()

    assert not parque.esta_abierto(Horario(MIERCOLES, time(8, 0)))


def test_el_parque_esta_cerrado_si_el_horario_termina_despues_del_cierre():
    parque = Parque()

    assert not parque.esta_abierto(Horario(MIERCOLES, time(18, 30)))


@pytest.mark.parametrize("inicio", [time(8, 30), time(18, 0)])
def test_el_parque_esta_abierto_en_los_bordes_de_apertura_y_cierre(inicio):
    parque = Parque()

    assert parque.esta_abierto(Horario(MIERCOLES, inicio))


def test_el_parque_esta_cerrado_los_lunes():
    parque = Parque()
    lunes = date(2026, 11, 2)

    assert not parque.esta_abierto(Horario(lunes, time(10, 0)))


@pytest.mark.parametrize("feriado", [date(2026, 12, 25), date(2027, 1, 1)])
def test_el_parque_esta_cerrado_el_25_de_diciembre_y_el_1_de_enero(feriado):
    parque = Parque()

    assert not parque.esta_abierto(Horario(feriado, time(10, 0)))
