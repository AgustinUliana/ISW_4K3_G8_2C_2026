"""Prueba EXTERNA (categoria X, marcador `externa`): manda un email real con QR a una casilla.

No corre con `pytest` a secas: se pide a proposito con `pytest -m externa`. Si falta la
configuracion SMTP en el `.env` (o `EMAIL_DE_PRUEBA`, la casilla que recibe el mensaje), se
saltea con un aviso que dice que falta. Verificar a mano que el mensaje llega a la BANDEJA DE
ENTRADA (no a spam) y que los QR adjuntos se ven.
"""

import os
from dataclasses import replace
from pathlib import Path

import pytest

from datos_de_prueba import una_inscripcion_confirmada
from ecoharmony.entorno import leer_env
from ecoharmony.generador_qr_local import GeneradorQRLocal
from ecoharmony.mensaje_email import armar_mensaje
from ecoharmony.servicio_email_smtp import (
    ConfiguracionIncompletaError,
    ConfiguracionSmtp,
    ServicioEmailSmtp,
)

CODIGO = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.externa


def _entorno():
    return {**leer_env(CODIGO / ".env"), **os.environ}


def test_se_envia_un_email_real_con_un_qr_por_visitante_a_la_casilla_de_prueba():
    entorno = _entorno()
    destinatario = entorno.get("EMAIL_DE_PRUEBA")
    if not destinatario:
        pytest.skip("Falta EMAIL_DE_PRUEBA en el .env: la casilla que recibe el email de prueba")
    try:
        configuracion = ConfiguracionSmtp.desde_entorno(entorno)
    except ConfiguracionIncompletaError as error:
        pytest.skip(str(error))
    generador = GeneradorQRLocal()
    inscripcion = una_inscripcion_confirmada("INS-0001")
    qrs = [generador.generar(f"INS-0001|V{n}") for n in (1, 2)]
    real = armar_mensaje(inscripcion, qrs)  # el mismo mensaje que arma el sistema al inscribir
    mensaje = replace(real, destinatario=destinatario, asunto=real.asunto)

    ServicioEmailSmtp(configuracion).enviar(mensaje)  # si falla la conexion o el login, lanza error
