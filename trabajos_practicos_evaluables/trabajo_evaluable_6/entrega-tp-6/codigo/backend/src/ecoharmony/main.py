"""Punto de arranque: arma los servicios reales a partir del entorno (.env) y crea la API.

uvicorn --factory ecoharmony.main:crear_aplicacion
"""

import logging
import os
from pathlib import Path

from ecoharmony.api import Servicios, crear_app
from ecoharmony.entorno import leer_env
from ecoharmony.generador_qr_local import GeneradorQRLocal
from ecoharmony.inscripcion_service import InscripcionService
from ecoharmony.parque import Parque
from ecoharmony.reloj import RelojSistema
from ecoharmony.repositorio_postgres import RepositorioPostgres
from ecoharmony.repositorio_usuarios_postgres import RepositorioDeUsuariosPostgres
from ecoharmony.servicio_email_en_carpeta import ServicioEmailEnCarpeta
from ecoharmony.servicio_email_smtp import (
    ConfiguracionIncompletaError,
    ConfiguracionSmtp,
    ServicioEmailSmtp,
)
from ecoharmony.usuarios import ServicioUsuarios

logger = logging.getLogger(__name__)

CODIGO = Path(__file__).resolve().parents[3]
VARIABLES_OBLIGATORIAS = ("DATABASE_URL", "SECRETO_DE_SESIONES")
ORIGEN_POR_DEFECTO_DEL_FRONT = "http://localhost:5173"


def _servicio_email(entorno):
    try:
        return ServicioEmailSmtp(ConfiguracionSmtp.desde_entorno(entorno))
    except ConfiguracionIncompletaError:
        logger.warning(
            "SMTP no configurado: los emails se guardan en salida_de_emails/ (solo desarrollo)"
        )
        return ServicioEmailEnCarpeta(CODIGO / "salida_de_emails")


def crear_servicios(entorno):
    faltantes = [variable for variable in VARIABLES_OBLIGATORIAS if not entorno.get(variable)]
    if faltantes:
        raise ConfiguracionIncompletaError(f"Falta configurar: {', '.join(faltantes)}")
    url = entorno["DATABASE_URL"]
    reloj, parque = RelojSistema(), Parque()
    repositorio = RepositorioPostgres(url)
    generador_qr = GeneradorQRLocal()
    servicio_email = _servicio_email(entorno)
    return Servicios(
        usuarios=ServicioUsuarios(
            RepositorioDeUsuariosPostgres(url), entorno["SECRETO_DE_SESIONES"], reloj
        ),
        inscripciones=InscripcionService(repositorio, parque, reloj, generador_qr, servicio_email),
        repositorio=repositorio,
        parque=parque,
        reloj=reloj,
        generador_qr=generador_qr,
        servicio_email=servicio_email,
    )


def crear_aplicacion(entorno=None):
    entorno = entorno if entorno is not None else {**leer_env(CODIGO / ".env"), **os.environ}
    origenes = entorno.get("ORIGENES_PERMITIDOS", ORIGEN_POR_DEFECTO_DEL_FRONT)
    return crear_app(
        crear_servicios(entorno),
        origenes_permitidos=[origen.strip() for origen in origenes.split(",") if origen.strip()],
    )
