"""Fixtures de la base PostgreSQL de pruebas (categoria C, marcador `db`).

Si la base no esta levantada, las pruebas que la usan se saltean con un mensaje que
explica como levantarla (docker compose up -d); no fallan por infraestructura.
"""

import os
from pathlib import Path

import psycopg
import pytest

from ecoharmony.entorno import leer_env

BACKEND = Path(__file__).resolve().parents[1]
CODIGO = BACKEND.parent
ESQUEMA = BACKEND / "sql" / "schema.sql"


def _url_de_pruebas():
    return os.environ.get("DATABASE_URL_TEST") or leer_env(CODIGO / ".env").get("DATABASE_URL_TEST")


@pytest.fixture(scope="session")
def url_base_de_pruebas():
    url = _url_de_pruebas()
    if not url:
        pytest.skip("Falta DATABASE_URL_TEST: copiar .env.example a .env")
    try:
        psycopg.connect(url, connect_timeout=3).close()
    except psycopg.OperationalError:
        pytest.skip("PostgreSQL de pruebas no responde: ejecutar `docker compose up -d`")
    return url


@pytest.fixture
def base_vacia(url_base_de_pruebas):
    """La base de pruebas sin ninguna tabla."""
    with psycopg.connect(url_base_de_pruebas) as conexion:
        conexion.execute("DROP SCHEMA public CASCADE")
        conexion.execute("CREATE SCHEMA public")
    return url_base_de_pruebas


@pytest.fixture
def base_con_esquema(base_vacia):
    """La base de pruebas con el esquema recien creado desde schema.sql."""
    with psycopg.connect(base_vacia) as conexion:
        conexion.execute(ESQUEMA.read_text(encoding="utf-8"))
    return base_vacia
