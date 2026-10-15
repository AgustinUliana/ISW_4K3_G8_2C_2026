"""Dobles de prueba (politica del plan, seccion 2.2.1).

- Reloj, generador de QR: consultas  -> stub / fake (se verifica el estado).
- Servicio de email: accion          -> mock (se verifica que se envio).
- Fallas: Crash Test Dummy (lanzan la excepcion).
"""


class RelojFijo:
    def __init__(self, ahora):
        self._ahora = ahora

    def ahora(self):
        return self._ahora


class GeneradorQRFalso:
    """Stub: devuelve bytes distintos para cada contenido."""

    def generar(self, contenido):
        return f"QR[{contenido}]".encode()


class GeneradorQRQueFalla:
    def generar(self, contenido):
        raise RuntimeError("no se pudo generar el QR")


class EmailEnMemoria:
    """Mock: recuerda los mensajes enviados."""

    def __init__(self):
        self.enviados = []

    def enviar(self, mensaje):
        self.enviados.append(mensaje)


class EmailQueFalla:
    """Crash Test Dummy: siempre falla (y cuenta los intentos)."""

    def __init__(self):
        self.intentos = 0
        self.enviados = []

    def enviar(self, mensaje):
        self.intentos += 1
        raise ConnectionError("el servidor de correo no responde")


class EmailQueFallaLasPrimeras:
    """Falla las primeras `fallos` veces y despues funciona."""

    def __init__(self, fallos):
        self.fallos = fallos
        self.intentos = 0
        self.enviados = []

    def enviar(self, mensaje):
        self.intentos += 1
        if self.intentos <= self.fallos:
            raise ConnectionError("el servidor de correo no responde")
        self.enviados.append(mensaje)
