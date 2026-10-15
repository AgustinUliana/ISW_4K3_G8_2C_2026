import uuid
from datetime import datetime
from pathlib import Path


class ServicioEmailEnCarpeta:
    """Para desarrollo sin credenciales SMTP: guarda cada email (texto y QR) en una carpeta.

    No reemplaza al envio real (ServicioEmailSmtp), que es lo que pide el PO.
    """

    def __init__(self, carpeta):
        self._carpeta = Path(carpeta)

    def enviar(self, mensaje):
        self._carpeta.mkdir(parents=True, exist_ok=True)
        base = f"{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}"
        texto = (
            f"Para: {mensaje.destinatario}\n"
            f"Asunto: {mensaje.asunto}\n\n"
            f"{mensaje.cuerpo}\n"
            f"Adjuntos: {', '.join(a.nombre for a in mensaje.adjuntos)}\n"
        )
        (self._carpeta / f"{base}.txt").write_text(texto, encoding="utf-8")
        for adjunto in mensaje.adjuntos:
            (self._carpeta / f"{base}-{adjunto.nombre}").write_bytes(adjunto.contenido)
