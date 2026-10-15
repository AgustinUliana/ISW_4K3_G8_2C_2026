"""PREP: dejar lista la base (esquema + las cuatro actividades), p. ej. la de DBeaver."""

import psycopg
import pytest

from ecoharmony.preparar_base import preparar_base
from ecoharmony.repositorio_postgres import RepositorioPostgres

pytestmark = [pytest.mark.local, pytest.mark.db]

ACTIVIDADES = {"Tirolesa", "Safari", "Palestra", "Jardinería"}


def test_preparar_una_base_vacia_crea_el_esquema_y_carga_las_cuatro_actividades(base_vacia):
    preparar_base(base_vacia)

    repositorio = RepositorioPostgres(base_vacia)
    assert {repositorio.actividad(nombre).nombre for nombre in ACTIVIDADES} == ACTIVIDADES


def test_preparar_dos_veces_no_falla_ni_duplica_las_actividades(base_vacia):
    preparar_base(base_vacia)

    preparar_base(base_vacia)

    repositorio = RepositorioPostgres(base_vacia)
    assert repositorio.actividad("Tirolesa").cupo_por_turno == 10


def test_preparar_agrega_las_tablas_nuevas_a_una_base_ya_preparada(base_vacia):
    preparar_base(base_vacia)
    with psycopg.connect(base_vacia) as conexion:
        conexion.execute("DROP TABLE usuario")  # como una base creada antes de existir los usuarios

    preparar_base(base_vacia)

    with psycopg.connect(base_vacia) as conexion:
        assert conexion.execute("SELECT to_regclass('public.usuario')").fetchone()[0] is not None
