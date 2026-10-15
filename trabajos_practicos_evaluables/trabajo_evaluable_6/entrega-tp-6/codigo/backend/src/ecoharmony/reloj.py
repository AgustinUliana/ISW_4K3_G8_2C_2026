from datetime import datetime


class RelojSistema:
    """Hora local del servidor (el parque opera en un unico huso horario)."""

    def ahora(self):
        return datetime.now()
