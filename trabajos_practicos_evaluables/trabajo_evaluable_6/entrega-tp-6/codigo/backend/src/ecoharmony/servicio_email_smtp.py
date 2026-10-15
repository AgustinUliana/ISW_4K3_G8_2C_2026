import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

TIEMPO_LIMITE_EN_SEGUNDOS = 10
SERVIDOR_DE_GMAIL = "smtp.gmail.com"
VARIABLES = ("SMTP_SERVIDOR", "SMTP_PUERTO", "SMTP_USUARIO", "SMTP_CLAVE", "EMAIL_REMITENTE")


class ConfiguracionIncompletaError(Exception):
    """Falta alguna variable de entorno de la configuracion SMTP."""


@dataclass(frozen=True)
class ConfiguracionSmtp:
    servidor: str
    puerto: int
    usuario: str
    clave: str
    remitente: str

    @classmethod
    def desde_entorno(cls, entorno):
        faltantes = [v for v in VARIABLES if not entorno.get(v)]
        if faltantes:
            raise ConfiguracionIncompletaError(f"Falta configurar: {', '.join(faltantes)}")
        servidor = entorno["SMTP_SERVIDOR"]
        clave = entorno["SMTP_CLAVE"]
        if servidor == SERVIDOR_DE_GMAIL:
            clave = clave.replace(" ", "")  # Google muestra la clave en 4 grupos separados
        return cls(
            servidor=servidor,
            puerto=int(entorno["SMTP_PUERTO"]),
            usuario=entorno["SMTP_USUARIO"],
            clave=clave,
            remitente=entorno["EMAIL_REMITENTE"],
        )


class ServicioEmailSmtp:
    """Envia por SMTP con STARTTLS. Sirve para Gmail (contrasena de aplicacion) o Brevo."""

    def __init__(self, configuracion, smtp_factory=smtplib.SMTP):
        self._configuracion = configuracion
        self._smtp_factory = smtp_factory

    def enviar(self, mensaje):
        configuracion = self._configuracion
        mime = a_mime(mensaje, remitente=configuracion.remitente)
        with self._smtp_factory(
            configuracion.servidor, configuracion.puerto, timeout=TIEMPO_LIMITE_EN_SEGUNDOS
        ) as smtp:
            smtp.starttls()
            smtp.login(configuracion.usuario, configuracion.clave)
            smtp.send_message(mime)


def a_mime(mensaje, remitente):
    mime = EmailMessage()
    mime["From"] = remitente
    mime["To"] = mensaje.destinatario
    mime["Subject"] = mensaje.asunto
    mime["Date"] = formatdate(localtime=True)
    mime["Message-ID"] = make_msgid(domain=remitente.rpartition("@")[2] or None)
    mime.set_content(mensaje.cuerpo)
    if mensaje.cuerpo_html:
        mime.add_alternative(mensaje.cuerpo_html, subtype="html")
        html = mime.get_body(preferencelist=("html",))
        for imagen in mensaje.imagenes_en_linea:
            tipo_principal, subtipo = imagen.tipo.split("/")
            html.add_related(
                imagen.contenido, maintype=tipo_principal, subtype=subtipo, cid=f"<{imagen.cid}>"
            )
    for adjunto in mensaje.adjuntos:
        tipo_principal, subtipo = adjunto.tipo.split("/")
        mime.add_attachment(
            adjunto.contenido, maintype=tipo_principal, subtype=subtipo, filename=adjunto.nombre
        )
    return mime
