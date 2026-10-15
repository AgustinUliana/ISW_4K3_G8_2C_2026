"""Contrato del repositorio de usuarios: el mismo conjunto para el fake y para PostgreSQL."""

import pytest

from ecoharmony.errores import EmailYaRegistradoError
from ecoharmony.repositorio_usuarios_memoria import RepositorioDeUsuariosEnMemoria
from ecoharmony.repositorio_usuarios_postgres import RepositorioDeUsuariosPostgres
from ecoharmony.usuarios import Usuario


@pytest.fixture(
    params=[
        "memoria",
        pytest.param("postgres", marks=[pytest.mark.local, pytest.mark.db]),
    ]
)
def repositorio(request):
    if request.param == "memoria":
        return RepositorioDeUsuariosEnMemoria()
    return RepositorioDeUsuariosPostgres(request.getfixturevalue("base_con_esquema"))


def test_se_guarda_y_se_busca_un_usuario_por_email(repositorio):
    repositorio.guardar(Usuario("ana@example.com", "hash-de-prueba"))

    encontrado = repositorio.buscar("ana@example.com")

    assert encontrado.email == "ana@example.com"
    assert encontrado.contrasena_hash == "hash-de-prueba"


def test_buscar_un_email_inexistente_devuelve_none(repositorio):
    assert repositorio.buscar("nadie@example.com") is None


def test_guardar_dos_veces_el_mismo_email_falla(repositorio):
    repositorio.guardar(Usuario("ana@example.com", "hash-1"))

    with pytest.raises(EmailYaRegistradoError):
        repositorio.guardar(Usuario("ana@example.com", "hash-2"))
