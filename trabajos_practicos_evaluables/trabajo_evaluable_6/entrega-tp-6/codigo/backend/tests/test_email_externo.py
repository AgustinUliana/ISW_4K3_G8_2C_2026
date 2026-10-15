"""Prueba EXTERNA (categoria X, marcador `externa`): manda un email real con QR a una casilla.

No corre con `pytest` a secas: se pide a proposito con `pytest -m externa`. Si falta la
configuracion SMTP en el `.env` (o `EMAIL_DE_PRUEBA`, la casilla que recibe el mensaje), se
saltea con un aviso que dice que falta. Verificar a mano que el mensaje llega a la BANDEJA DE
ENTRADA (no a spam) y que los QR adjuntos se ven.
"""

import os
from pathlib import Path

import pytest

from ecoharmony.entorno import leer_env
from ecoharmony.generador_qr_local import GeneradorQRLocal
from ecoharmony.mensaje_email import Adjunto, MensajeEmail
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
    mensaje = MensajeEmail(
        destinatario=destinatario,
        asunto="[PRUEBA] Inscripción confirmada: Tirolesa - EcoHarmony Park",
        cuerpo=(
            "Este es un email de prueba del sistema de inscripciones de EcoHarmony Park.\n\n"
            "Código de reserva: PRUEBA-0001\nPersonas: 2 personas\n"
            "Si lo ves en tu bandeja de entrada con dos códigos QR adjuntos, el envío funciona."
        ),
        adjuntos=(
            Adjunto("qr-visitante-1.png", "image/png", generador.generar("PRUEBA-0001|V1")),
            Adjunto("qr-visitante-2.png", "image/png", generador.generar("PRUEBA-0001|V2")),
        ),
    )

    ServicioEmailSmtp(configuracion).enviar(mensaje)  # si falla la conexion o el login, lanza error
