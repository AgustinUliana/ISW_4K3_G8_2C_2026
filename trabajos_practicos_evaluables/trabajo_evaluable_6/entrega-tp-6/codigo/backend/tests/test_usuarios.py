import pytest

from datos_de_prueba import AHORA
from dobles import RelojFijo
from ecoharmony.contrasenas import verificar
from ecoharmony.motivos import MotivoRechazo
from ecoharmony.repositorio_usuarios_memoria import RepositorioDeUsuariosEnMemoria
from ecoharmony.usuarios import ServicioUsuarios


def un_servicio(repositorio=None, ahora=AHORA, clave_secreta="clave-de-prueba"):
    return ServicioUsuarios(
        repositorio=repositorio or RepositorioDeUsuariosEnMemoria(),
        clave_secreta=clave_secreta,
        reloj=RelojFijo(ahora),
    )


def test_se_registra_un_usuario_con_email_y_contrasena_validos():
    repositorio = RepositorioDeUsuariosEnMemoria()

    resultado = un_servicio(repositorio).registrar("ana@example.com", "secreto1")

    assert resultado.registrado
    assert repositorio.buscar("ana@example.com").email == "ana@example.com"


def test_el_email_se_guarda_sin_espacios_ni_mayusculas():
    repositorio = RepositorioDeUsuariosEnMemoria()

    un_servicio(repositorio).registrar("  Ana@Example.COM ", "secreto1")

    assert repositorio.buscar("ana@example.com") is not None


@pytest.mark.parametrize("email", ["", "ana", "ana@", "ana@dominio", "@dominio.com", "a b@x.com"])
def test_no_se_registra_con_un_email_invalido(email):
    resultado = un_servicio().registrar(email, "secreto1")

    assert not resultado.registrado
    assert resultado.motivos == [MotivoRechazo.EMAIL_INVALIDO]


@pytest.mark.parametrize("contrasena, valida", [("12345", False), ("123456", True), ("", False)])
def test_la_contrasena_debe_tener_al_menos_6_caracteres(contrasena, valida):
    resultado = un_servicio().registrar("ana@example.com", contrasena)

    assert resultado.registrado is valida
    if not valida:
        assert resultado.motivos == [MotivoRechazo.CONTRASENA_INVALIDA]


def test_no_se_registra_dos_veces_el_mismo_email_sin_distinguir_mayusculas():
    servicio = un_servicio()
    servicio.registrar("ana@example.com", "secreto1")

    resultado = servicio.registrar("ANA@example.com", "otra-clave")

    assert not resultado.registrado
    assert resultado.motivos == [MotivoRechazo.EMAIL_YA_REGISTRADO]


def test_la_contrasena_se_guarda_como_hash_y_no_en_texto_plano():
    repositorio = RepositorioDeUsuariosEnMemoria()

    un_servicio(repositorio).registrar("ana@example.com", "secreto1")

    guardado = repositorio.buscar("ana@example.com").contrasena_hash
    assert guardado != "secreto1"
    assert verificar("secreto1", guardado)
