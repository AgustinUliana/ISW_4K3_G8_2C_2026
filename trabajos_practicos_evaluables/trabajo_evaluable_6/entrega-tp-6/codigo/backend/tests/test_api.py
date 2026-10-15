"""API HTTP (FastAPI) probada con TestClient sobre los servicios reales y dobles en memoria."""

from collections import namedtuple

import pytest
from fastapi.testclient import TestClient

from datos_de_prueba import AHORA
from dobles import EmailEnMemoria, GeneradorQRFalso, RelojFijo
from ecoharmony.api import Servicios, crear_app
from ecoharmony.catalogo import crear_actividades
from ecoharmony.inscripcion_service import InscripcionService
from ecoharmony.parque import Parque
from ecoharmony.repositorio_memoria import RepositorioEnMemoria
from ecoharmony.repositorio_usuarios_memoria import RepositorioDeUsuariosEnMemoria
from ecoharmony.usuarios import ServicioUsuarios

ORIGEN_DEL_FRONT = "http://localhost:5173"
Cliente = namedtuple("Cliente", "http email repositorio")


def armar_cliente(repositorio=None, email=None, intentos_de_email=1):
    repositorio = repositorio or RepositorioEnMemoria(crear_actividades())
    email = email or EmailEnMemoria()
    reloj, parque = RelojFijo(AHORA), Parque()
    servicios = Servicios(
        usuarios=ServicioUsuarios(RepositorioDeUsuariosEnMemoria(), "clave-de-prueba", reloj),
        inscripciones=InscripcionService(
            repositorio,
            parque,
            reloj,
            GeneradorQRFalso(),
            email,
            intentos_de_email=intentos_de_email,
            dormir=lambda segundos: None,
        ),
        repositorio=repositorio,
        parque=parque,
        reloj=reloj,
    )
    app = crear_app(servicios, origenes_permitidos=[ORIGEN_DEL_FRONT])
    return Cliente(TestClient(app, raise_server_exceptions=False), email, repositorio)


@pytest.fixture
def cliente():
    return armar_cliente()


def test_post_registro_con_datos_validos_responde_201(cliente):
    respuesta = cliente.http.post(
        "/registro", json={"email": "Ana@Example.com", "contrasena": "secreto1"}
    )

    assert respuesta.status_code == 201
    assert respuesta.json() == {"email": "ana@example.com"}


def test_post_registro_con_datos_invalidos_responde_422_con_los_motivos(cliente):
    respuesta = cliente.http.post("/registro", json={"email": "ana", "contrasena": "123"})

    assert respuesta.status_code == 422
    assert respuesta.json()["motivos"] == ["email_invalido", "contrasena_invalida"]


def test_post_registro_sin_cuerpo_responde_422_y_no_falla(cliente):
    respuesta = cliente.http.post("/registro", json={})

    assert respuesta.status_code == 422
    assert "email_invalido" in respuesta.json()["motivos"]


def test_post_registro_de_un_email_repetido_responde_409(cliente):
    datos = {"email": "ana@example.com", "contrasena": "secreto1"}
    cliente.http.post("/registro", json=datos)

    respuesta = cliente.http.post("/registro", json=datos)

    assert respuesta.status_code == 409
    assert respuesta.json()["motivos"] == ["email_ya_registrado"]


def test_post_sesion_con_credenciales_correctas_devuelve_un_token(cliente):
    datos = {"email": "ana@example.com", "contrasena": "secreto1"}
    cliente.http.post("/registro", json=datos)

    respuesta = cliente.http.post("/sesion", json=datos)

    assert respuesta.status_code == 200
    assert respuesta.json()["token"]


def test_post_sesion_con_credenciales_incorrectas_responde_401(cliente):
    cliente.http.post("/registro", json={"email": "ana@example.com", "contrasena": "secreto1"})

    respuesta = cliente.http.post(
        "/sesion", json={"email": "ana@example.com", "contrasena": "otra-clave"}
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["motivos"] == ["credenciales_invalidas"]


def test_el_front_react_puede_llamar_a_la_api_desde_su_origen(cliente):
    respuesta = cliente.http.options(
        "/sesion",
        headers={"Origin": ORIGEN_DEL_FRONT, "Access-Control-Request-Method": "POST"},
    )

    assert respuesta.headers["access-control-allow-origin"] == ORIGEN_DEL_FRONT
