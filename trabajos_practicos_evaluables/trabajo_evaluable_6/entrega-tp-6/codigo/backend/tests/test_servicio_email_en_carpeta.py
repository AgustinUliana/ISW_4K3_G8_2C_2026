"""Email para desarrollo sin credenciales: guarda el texto y los QR en una carpeta."""

from ecoharmony.mensaje_email import Adjunto, MensajeEmail
from ecoharmony.servicio_email_en_carpeta import ServicioEmailEnCarpeta

MENSAJE = MensajeEmail(
    destinatario="ana.perez@example.com",
    asunto="Inscripción confirmada: Tirolesa",
    cuerpo="Tu inscripción a Tirolesa está confirmada.",
    adjuntos=(
        Adjunto("qr-visitante-1.png", "image/png", b"png-1"),
        Adjunto("qr-visitante-2.png", "image/png", b"png-2"),
    ),
)


def test_guarda_el_texto_del_email_y_cada_qr_como_png(tmp_path):
    ServicioEmailEnCarpeta(tmp_path).enviar(MENSAJE)

    (texto,) = tmp_path.glob("*.txt")
    contenido = texto.read_text(encoding="utf-8")
    assert "ana.perez@example.com" in contenido
    assert "Inscripción confirmada: Tirolesa" in contenido
    assert "Tu inscripción a Tirolesa está confirmada." in contenido
    assert [png.read_bytes() for png in sorted(tmp_path.glob("*.png"))] == [b"png-1", b"png-2"]


def test_crea_la_carpeta_si_no_existe_y_dos_emails_no_se_pisan(tmp_path):
    carpeta = tmp_path / "salida" / "de" / "emails"
    servicio = ServicioEmailEnCarpeta(carpeta)

    servicio.enviar(MENSAJE)
    servicio.enviar(MENSAJE)

    assert len(list(carpeta.glob("*.txt"))) == 2
