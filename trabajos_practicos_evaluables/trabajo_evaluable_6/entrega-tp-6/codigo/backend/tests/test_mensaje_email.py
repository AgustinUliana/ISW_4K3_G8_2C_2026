import pytest
from datos_de_prueba import EMAIL_DE_ANA, una_inscripcion_confirmada

from ecoharmony.mensaje_email import armar_mensaje

QRS = [b"qr-del-visitante-1", b"qr-del-visitante-2"]


def test_el_destinatario_es_el_email_de_contacto():
    mensaje = armar_mensaje(una_inscripcion_confirmada(), QRS)

    assert mensaje.destinatario == EMAIL_DE_ANA


def test_el_asunto_incluye_la_actividad():
    mensaje = armar_mensaje(una_inscripcion_confirmada(), QRS)

    assert "Tirolesa" in mensaje.asunto


def test_el_cuerpo_incluye_actividad_fecha_horario_y_cantidad_de_personas():
    cuerpo = armar_mensaje(una_inscripcion_confirmada(), QRS).cuerpo

    assert "Tirolesa" in cuerpo
    assert "04/11/2026" in cuerpo
    assert "10:00" in cuerpo
    assert "2 personas" in cuerpo


def test_el_cuerpo_incluye_el_nombre_de_cada_visitante():
    cuerpo = armar_mensaje(una_inscripcion_confirmada(), QRS).cuerpo

    assert "Ana Perez" in cuerpo
    assert "Luis Gomez" in cuerpo


def test_el_cuerpo_incluye_el_codigo_de_reserva_en_texto():
    cuerpo = armar_mensaje(una_inscripcion_confirmada("INS-0007"), QRS).cuerpo

    assert "INS-0007" in cuerpo


def test_el_mensaje_adjunta_un_qr_png_por_visitante():
    mensaje = armar_mensaje(una_inscripcion_confirmada(), QRS)

    assert [adjunto.contenido for adjunto in mensaje.adjuntos] == QRS
    assert all(adjunto.tipo == "image/png" for adjunto in mensaje.adjuntos)
    assert [adjunto.nombre for adjunto in mensaje.adjuntos] == ["qr-visitante-1.png", "qr-visitante-2.png"]


def test_no_se_arma_el_mensaje_de_una_inscripcion_no_confirmada():
    from ecoharmony.errores import InscripcionNoConfirmada
    from ecoharmony.inscripcion import EstadoDeLaInscripcion

    pendiente = una_inscripcion_confirmada()
    pendiente.estado = EstadoDeLaInscripcion.PENDIENTE

    with pytest.raises(InscripcionNoConfirmada):
        armar_mensaje(pendiente, QRS)
