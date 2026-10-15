import io

import qrcode


class GeneradorQRLocal:
    """Dibuja el QR con la libreria `qrcode`: local, gratuita y sin internet."""

    def generar(self, contenido):
        imagen = qrcode.make(contenido)
        buffer = io.BytesIO()
        imagen.save(buffer, format="PNG")
        return buffer.getvalue()
