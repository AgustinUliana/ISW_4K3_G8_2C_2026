"""Armado de los servicios reales a partir del .env (sin conectarse a nada)."""

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ecoharmony.generador_qr_local import GeneradorQRLocal
from ecoharmony.main import crear_aplicacion, crear_servicios
from ecoharmony.repositorio_postgres import RepositorioPostgres
from ecoharmony.servicio_email_en_carpeta import ServicioEmailEnCarpeta
from ecoharmony.servicio_email_smtp import ConfiguracionIncompletaError, ServicioEmailSmtp

BASE = {
    "DATABASE_URL": "postgresql://usuario:clave@localhost:5433/ecoharmony",
    "SECRETO_DE_SESIONES": "una-clave-larga-de-prueba",
}
SMTP = {
    "SMTP_SERVIDOR": "smtp.ejemplo.com",
    "SMTP_PUERTO": "587",
    "SMTP_USUARIO": "usuario",
    "SMTP_CLAVE": "clave-de-prueba",
    "EMAIL_REMITENTE": "inscripciones@ecoharmony.example",
}


def test_con_la_configuracion_completa_se_arman_la_base_el_qr_y_el_email_reales():
    servicios = crear_servicios({**BASE, **SMTP})

    assert isinstance(servicios.repositorio, RepositorioPostgres)
    assert isinstance(servicios.servicio_email, ServicioEmailSmtp)
    assert isinstance(servicios.generador_qr, GeneradorQRLocal)


def test_sin_credenciales_smtp_el_email_se_guarda_en_una_carpeta_y_se_avisa(caplog):
    with caplog.at_level(logging.WARNING):
        servicios = crear_servicios(BASE)

    assert isinstance(servicios.servicio_email, ServicioEmailEnCarpeta)
    assert "SMTP no configurado" in caplog.text


@pytest.mark.parametrize("falta", list(BASE))
def test_falta_una_variable_obligatoria_falla_indicando_cual(falta):
    incompleto = {k: v for k, v in BASE.items() if k != falta}

    with pytest.raises(ConfiguracionIncompletaError, match=falta):
        crear_servicios(incompleto)


def test_crear_aplicacion_devuelve_la_api_con_sus_rutas():
    app = crear_aplicacion({**BASE, **SMTP})

    rutas = {ruta.path for ruta in app.routes}
    assert isinstance(app, FastAPI)
    assert {"/registro", "/sesion", "/actividades", "/inscripciones"} <= rutas


def _origenes_aceptados(app, origenes):
    cliente = TestClient(app)
    aceptados = []
    for origen in origenes:
        respuesta = cliente.options(
            "/sesion", headers={"Origin": origen, "Access-Control-Request-Method": "POST"}
        )
        if respuesta.headers.get("access-control-allow-origin") == origen:
            aceptados.append(origen)
    return aceptados


def test_por_defecto_la_api_acepta_al_front_en_localhost_y_en_127_0_0_1():
    app = crear_aplicacion({**BASE, **SMTP})

    origenes = ["http://localhost:5173", "http://127.0.0.1:5173", "https://otro-sitio.example"]

    assert _origenes_aceptados(app, origenes) == ["http://localhost:5173", "http://127.0.0.1:5173"]


def test_los_origenes_permitidos_se_pueden_configurar_con_una_variable():
    app = crear_aplicacion({**BASE, **SMTP, "ORIGENES_PERMITIDOS": "https://parque.example"})

    origenes = ["https://parque.example", "http://localhost:5173"]

    assert _origenes_aceptados(app, origenes) == ["https://parque.example"]
