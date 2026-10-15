"""Consultas que alimentan la pantalla: que turnos se ofrecen y cuanto cupo queda."""

from datetime import date, datetime, time

from ecoharmony.catalogo import crear_actividades
from ecoharmony.disponibilidad import turnos_disponibles
from ecoharmony.horario import Horario
from ecoharmony.parque import Parque

MIERCOLES = date(2026, 11, 4)
JUEVES = date(2026, 11, 5)
VIERNES = date(2026, 11, 6)
MIERCOLES_12 = datetime(2026, 11, 4, 12, 0)


def horas(turnos):
    return [turno.horario.hora_inicio.hour for turno in turnos]


def test_hoy_solo_se_ofrecen_los_turnos_cuya_inscripcion_sigue_abierta():
    tirolesa = crear_actividades()["Tirolesa"]

    turnos = turnos_disponibles(tirolesa, MIERCOLES, Parque(), ahora=MIERCOLES_12)

    # a las 12:00 el turno de las 12 ya cerro (cierra 15 minutos antes) y el de las 13 sigue abierto
    assert horas(turnos) == [13, 14, 15, 16, 17]


def test_manana_solo_se_ofrecen_los_turnos_que_estan_dentro_de_las_proximas_24_horas():
    tirolesa = crear_actividades()["Tirolesa"]

    turnos = turnos_disponibles(tirolesa, JUEVES, Parque(), ahora=MIERCOLES_12)

    assert horas(turnos) == [9, 10, 11, 12]  # el jueves a las 13 faltarian mas de 24 horas


def test_un_dia_a_mas_de_24_horas_no_ofrece_turnos():
    tirolesa = crear_actividades()["Tirolesa"]

    assert turnos_disponibles(tirolesa, VIERNES, Parque(), ahora=MIERCOLES_12) == []


def test_un_dia_con_el_parque_cerrado_no_ofrece_turnos():
    tirolesa = crear_actividades()["Tirolesa"]
    domingo_a_las_12 = datetime(2026, 11, 1, 12, 0)
    lunes = date(2026, 11, 2)

    assert turnos_disponibles(tirolesa, lunes, Parque(), ahora=domingo_a_las_12) == []


def test_cada_turno_muestra_el_cupo_restante():
    tirolesa = crear_actividades()["Tirolesa"]
    tirolesa.reservar(Horario(MIERCOLES, time(13, 0)), cantidad=3)

    turnos = turnos_disponibles(tirolesa, MIERCOLES, Parque(), ahora=MIERCOLES_12)

    assert [turno.cupo_restante for turno in turnos] == [7, 10, 10, 10, 10]


def test_un_turno_sin_cupo_figura_como_agotado_con_cero_lugares():
    tirolesa = crear_actividades()["Tirolesa"]
    tirolesa.reservar(Horario(MIERCOLES, time(13, 0)), cantidad=10)

    turnos = turnos_disponibles(tirolesa, MIERCOLES, Parque(), ahora=MIERCOLES_12)

    assert turnos[0].cupo_restante == 0
    assert turnos[0].agotado
    assert not turnos[1].agotado
