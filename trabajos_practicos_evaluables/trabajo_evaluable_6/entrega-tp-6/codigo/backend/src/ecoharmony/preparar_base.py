from pathlib import Path

import psycopg

from ecoharmony.catalogo import crear_actividades
from ecoharmony.repositorio_postgres import RepositorioPostgres

ESQUEMA = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"


def preparar_base(url):
    """Crea las tablas que falten y carga el catalogo de actividades. Se puede repetir."""
    with psycopg.connect(url) as conexion:
        conexion.execute(ESQUEMA.read_text(encoding="utf-8"))
    RepositorioPostgres(url).cargar_actividades(crear_actividades())


if __name__ == "__main__":
    from ecoharmony.entorno import leer_env

    codigo = Path(__file__).resolve().parents[3]
    url = leer_env(codigo / ".env")["DATABASE_URL"]
    preparar_base(url)
    print("Base lista: esquema creado y actividades cargadas.")
