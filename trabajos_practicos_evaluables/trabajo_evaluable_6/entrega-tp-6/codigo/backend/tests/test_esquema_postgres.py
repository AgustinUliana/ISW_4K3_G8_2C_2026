"""REP-08: el esquema SQL se crea desde cero y sus restricciones protegen los datos."""

import psycopg
import pytest

pytestmark = [pytest.mark.local, pytest.mark.db]


def _tablas(url):
    with psycopg.connect(url) as conexion:
        filas = conexion.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        ).fetchall()
    return {fila[0] for fila in filas}


def test_el_esquema_se_crea_desde_cero_en_una_base_vacia(base_vacia, base_con_esquema):
    assert _tablas(base_con_esquema) == {
        "actividad",
        "ocupacion",
        "inscripcion",
        "visitante_inscripto",
        "usuario",
    }


def test_la_base_rechaza_un_cupo_por_turno_que_no_sea_positivo(base_con_esquema):
    with psycopg.connect(base_con_esquema) as conexion:
        with pytest.raises(psycopg.errors.CheckViolation):
            conexion.execute("INSERT INTO actividad VALUES ('Rafting', 0, 0, false, 'v1', 'texto')")
