from datetime import date, datetime, time

import pytest

from ecoharmony.horario import Horario


def test_un_horario_dura_una_hora():
    horario = Horario(date(2026, 11, 4), time(10, 0))

    assert horario.hora_fin == time(11, 0)


def test_dos_horarios_con_la_misma_fecha_e_inicio_son_iguales():
    assert Horario(date(2026, 11, 4), time(10, 0)) == Horario(date(2026, 11, 4), time(10, 0))
    assert Horario(date(2026, 11, 4), time(10, 0)) != Horario(date(2026, 11, 4), time(11, 0))


@pytest.mark.parametrize(
    "hora, es_turno",
    [
        (time(9, 0), True),
        (time(17, 0), True),
        (time(18, 0), False),  # cota superior: a las 18:00 no hay turno
        (time(8, 0), False),
        (time(10, 30), False),
    ],
)
def test_un_horario_es_turno_si_empieza_en_punto_entre_las_9_y_las_17(hora, es_turno):
    assert Horario(date(2026, 11, 4), hora).es_turno() is es_turno


def test_se_puede_inscribir_exactamente_15_minutos_antes_del_turno():
    turno = Horario(date(2026, 11, 4), time(10, 0))

    assert turno.admite_inscripcion(ahora=datetime(2026, 11, 4, 9, 45))


@pytest.mark.parametrize(
    "ahora",
    [
        datetime(2026, 11, 4, 9, 46),  # a 14 minutos: ya cerro
        datetime(2026, 11, 4, 10, 0),  # justo al inicio
        datetime(2026, 11, 4, 10, 30),  # turno ya comenzado
    ],
)
def test_no_se_puede_inscribir_con_menos_de_15_minutos_de_anticipacion(ahora):
    turno = Horario(date(2026, 11, 4), time(10, 0))

    assert not turno.admite_inscripcion(ahora=ahora)


def test_no_se_puede_inscribir_con_mas_de_24_horas_de_anticipacion():
    turno = Horario(date(2026, 11, 5), time(10, 0))

    assert not turno.admite_inscripcion(ahora=datetime(2026, 11, 4, 9, 59))


def test_se_puede_inscribir_exactamente_24_horas_antes_del_turno():
    turno = Horario(date(2026, 11, 5), time(10, 0))

    assert turno.admite_inscripcion(ahora=datetime(2026, 11, 4, 10, 0))
