"""Adaptador SMTP del servicio de email (Gmail o Brevo: solo cambia la configuracion).

Se prueba con un SMTP falso: sin red. El envio real a una casilla del grupo es una
prueba externa (categoria X) que se ejecuta aparte.
"""

import pytest

from ecoharmony.mensaje_email import Adjunto, MensajeEmail
from ecoharmony.servicio_email_smtp import (
    ConfiguracionIncompletaError,
    ConfiguracionSmtp,
    ServicioEmailSmtp,
    a_mime,
)

MENSAJE = MensajeEmail(
    destinatario="ana.perez@example.com",
    asunto="Inscripción confirmada: Tirolesa",
    cuerpo="Tu inscripción a Tirolesa está confirmada.",
    adjuntos=(
        Adjunto("qr-visitante-1.png", "image/png", b"png-1"),
        Adjunto("qr-visitante-2.png", "image/png", b"png-2"),
    ),
)
CONFIGURACION = ConfiguracionSmtp(
    servidor="smtp.ejemplo.com",
    puerto=587,
    usuario="usuario",
    clave="clave-de-prueba",
    remitente="inscripciones@ecoharmony.example",
)


def test_el_mime_tiene_remitente_destinatario_y_asunto():
    mime = a_mime(MENSAJE, remitente="inscripciones@ecoharmony.example")

    assert mime["From"] == "inscripciones@ecoharmony.example"
    assert mime["To"] == "ana.perez@example.com"
    assert mime["Subject"] == "Inscripción confirmada: Tirolesa"


def test_el_mime_lleva_el_cuerpo_del_mensaje():
    mime = a_mime(MENSAJE, remitente="inscripciones@ecoharmony.example")

    assert mime.get_body(preferencelist=("plain",)).get_content().strip() == MENSAJE.cuerpo


def test_el_mime_adjunta_cada_qr_como_png():
    mime = a_mime(MENSAJE, remitente="inscripciones@ecoharmony.example")

    adjuntos = list(mime.iter_attachments())
    assert [a.get_filename() for a in adjuntos] == ["qr-visitante-1.png", "qr-visitante-2.png"]
    assert [a.get_content_type() for a in adjuntos] == ["image/png", "image/png"]
    assert [a.get_content() for a in adjuntos] == [b"png-1", b"png-2"]


class SmtpFalso:
    """Registra lo que se le pide, como el servidor SMTP real, pero sin red."""

    instancias = []

    def __init__(self, servidor, puerto, timeout=None):
        self.conexion = (servidor, puerto)
        self.timeout = timeout
        self.llamadas = []
        self.enviado = None
        SmtpFalso.instancias.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.llamadas.append("quit")

    def starttls(self):
        self.llamadas.append("starttls")

    def login(self, usuario, clave):
        self.llamadas.append(("login", usuario, clave))

    def send_message(self, mime):
        self.llamadas.append("send_message")
        self.enviado = mime


def test_el_servicio_smtp_se_conecta_cifrado_se_autentica_y_envia_el_mensaje():
    SmtpFalso.instancias.clear()
    servicio = ServicioEmailSmtp(CONFIGURACION, smtp_factory=SmtpFalso)

    servicio.enviar(MENSAJE)

    (smtp,) = SmtpFalso.instancias
    assert smtp.conexion == ("smtp.ejemplo.com", 587)
    assert smtp.llamadas == [
        "starttls",
        ("login", "usuario", "clave-de-prueba"),
        "send_message",
        "quit",
    ]
    assert smtp.enviado["To"] == "ana.perez@example.com"
    assert smtp.enviado["From"] == "inscripciones@ecoharmony.example"


ENTORNO = {
    "SMTP_SERVIDOR": "smtp.ejemplo.com",
    "SMTP_PUERTO": "587",
    "SMTP_USUARIO": "usuario",
    "SMTP_CLAVE": "clave-de-prueba",
    "EMAIL_REMITENTE": "inscripciones@ecoharmony.example",
}


def test_la_configuracion_se_lee_de_las_variables_de_entorno():
    assert ConfiguracionSmtp.desde_entorno(ENTORNO) == CONFIGURACION


@pytest.mark.parametrize("falta", list(ENTORNO))
def test_falta_una_variable_de_entorno_falla_indicando_cual(falta):
    incompleto = {k: v for k, v in ENTORNO.items() if k != falta}

    with pytest.raises(ConfiguracionIncompletaError, match=falta):
        ConfiguracionSmtp.desde_entorno(incompleto)


def test_la_conexion_smtp_tiene_un_tiempo_limite_para_no_colgar_la_inscripcion():
    SmtpFalso.instancias.clear()

    ServicioEmailSmtp(CONFIGURACION, smtp_factory=SmtpFalso).enviar(MENSAJE)

    (smtp,) = SmtpFalso.instancias
    assert smtp.timeout == 10
