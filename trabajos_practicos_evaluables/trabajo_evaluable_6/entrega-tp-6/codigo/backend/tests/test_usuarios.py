from datetime import timedelta

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


def un_servicio_con_ana_registrada(**opciones):
    servicio = un_servicio(**opciones)
    servicio.registrar("ana@example.com", "secreto1")
    return servicio


def test_el_inicio_de_sesion_con_credenciales_correctas_devuelve_un_token_del_usuario():
    servicio = un_servicio_con_ana_registrada()

    sesion = servicio.iniciar_sesion("ana@example.com", "secreto1")

    assert sesion.iniciada
    assert servicio.usuario_de_token(sesion.token).email == "ana@example.com"


def test_el_email_del_inicio_de_sesion_no_distingue_mayusculas():
    servicio = un_servicio_con_ana_registrada()

    assert servicio.iniciar_sesion(" ANA@example.com", "secreto1").iniciada


@pytest.mark.parametrize(
    "email, contrasena",
    [("ana@example.com", "otra-clave"), ("nadie@example.com", "secreto1")],
)
def test_el_inicio_de_sesion_falla_igual_con_contrasena_incorrecta_o_email_inexistente(
    email, contrasena
):
    sesion = un_servicio_con_ana_registrada().iniciar_sesion(email, contrasena)

    assert not sesion.iniciada
    assert sesion.token is None
    assert sesion.motivos == [MotivoRechazo.CREDENCIALES_INVALIDAS]


def test_un_token_alterado_o_firmado_con_otra_clave_no_identifica_a_nadie():
    repositorio = RepositorioDeUsuariosEnMemoria()
    servicio = un_servicio_con_ana_registrada(repositorio=repositorio)
    token = servicio.iniciar_sesion("ana@example.com", "secreto1").token

    otro_servidor = un_servicio(repositorio, clave_secreta="otra-clave")

    assert servicio.usuario_de_token(token + "x") is None
    assert servicio.usuario_de_token("basura") is None
    assert servicio.usuario_de_token(None) is None
    assert otro_servidor.usuario_de_token(token) is None


def test_un_token_vence_a_las_8_horas():
    repositorio = RepositorioDeUsuariosEnMemoria()
    servicio = un_servicio_con_ana_registrada(repositorio=repositorio)
    token = servicio.iniciar_sesion("ana@example.com", "secreto1").token

    antes_de_vencer = un_servicio(repositorio, ahora=AHORA + timedelta(hours=7, minutes=59))
    vencido = un_servicio(repositorio, ahora=AHORA + timedelta(hours=8, minutes=1))

    assert antes_de_vencer.usuario_de_token(token) is not None
    assert vencido.usuario_de_token(token) is None
