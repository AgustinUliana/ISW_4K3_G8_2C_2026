from ecoharmony.entorno import leer_env


def test_leer_env_lee_pares_clave_valor_ignorando_comentarios_y_lineas_vacias(tmp_path):
    archivo = tmp_path / ".env"
    archivo.write_text(
        "# comentario\n\nUSUARIO=ecoharmony\nURL=postgresql://u:p@localhost:5433/db\n"
    )

    assert leer_env(archivo) == {
        "USUARIO": "ecoharmony",
        "URL": "postgresql://u:p@localhost:5433/db",
    }


def test_leer_env_de_un_archivo_inexistente_devuelve_un_diccionario_vacio(tmp_path):
    assert leer_env(tmp_path / "no-existe.env") == {}
