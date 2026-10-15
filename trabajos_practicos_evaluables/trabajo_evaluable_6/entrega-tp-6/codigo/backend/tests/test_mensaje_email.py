import pytest

from datos_de_prueba import EMAIL_DE_ANA, una_inscripcion_confirmada
from ecoharmony.mensaje_email import armar_mensaje
from ecoharmony.visitante import Visitante

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
    assert [adjunto.nombre for adjunto in mensaje.adjuntos] == [
        "qr-visitante-1.png",
        "qr-visitante-2.png",
    ]


def test_no_se_arma_el_mensaje_de_una_inscripcion_no_confirmada():
    from ecoharmony.errores import InscripcionNoConfirmadaError
    from ecoharmony.inscripcion import EstadoDeLaInscripcion

    pendiente = una_inscripcion_confirmada()
    pendiente.estado = EstadoDeLaInscripcion.PENDIENTE

    with pytest.raises(InscripcionNoConfirmadaError):
        armar_mensaje(pendiente, QRS)


def _html(inscripcion=None):
    return armar_mensaje(inscripcion or una_inscripcion_confirmada("INS-0007"), QRS).cuerpo_html


def test_el_mensaje_trae_una_version_html_ademas_del_texto():
    mensaje = armar_mensaje(una_inscripcion_confirmada(), QRS)

    assert mensaje.cuerpo_html.lstrip().lower().startswith("<!doctype html")
    assert mensaje.cuerpo  # el texto plano se conserva para clientes sin HTML


def test_el_html_usa_la_paleta_de_ecoharmony():
    html = _html().lower()

    for color in ("#386641", "#6a994e", "#a7c957", "#f2e8cf", "#bc4749"):
        assert color in html


def test_el_html_usa_la_fuente_lato_con_alternativas():
    assert "font-family: lato," in _html().lower()


def test_el_html_incluye_el_logo_como_imagen_en_linea():
    mensaje = armar_mensaje(una_inscripcion_confirmada(), QRS)

    assert 'src="cid:logo"' in mensaje.cuerpo_html
    (logo,) = [i for i in mensaje.imagenes_en_linea if i.cid == "logo"]
    assert logo.tipo == "image/png"
    assert logo.contenido.startswith(b"\x89PNG")


def test_el_html_muestra_el_qr_de_cada_visitante_junto_a_su_nombre():
    mensaje = armar_mensaje(una_inscripcion_confirmada(), QRS)

    for numero, qr in enumerate(QRS, start=1):
        assert f'src="cid:qr-visitante-{numero}"' in mensaje.cuerpo_html
        (imagen,) = [i for i in mensaje.imagenes_en_linea if i.cid == f"qr-visitante-{numero}"]
        assert imagen.contenido == qr
    assert mensaje.cuerpo_html.index("Ana Perez") < mensaje.cuerpo_html.index("qr-visitante-1")


def test_el_html_incluye_codigo_actividad_fecha_horario_y_personas():
    html = _html()

    assert "INS-0007" in html
    assert "Tirolesa" in html
    assert "04/11/2026" in html
    assert "10:00" in html
    assert "2 personas" in html


def test_el_html_recuerda_presentar_el_dni_y_el_qr():
    html = _html()

    assert "DNI" in html
    assert "QR" in html


def test_el_html_escapa_los_datos_del_usuario():
    hostil = una_inscripcion_confirmada(
        visitantes=[Visitante("<script>alert(1)</script>", "30123456", 30, talla="M")]
    )

    html = armar_mensaje(hostil, [b"qr"]).cuerpo_html

    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_el_html_muestra_el_dni_debajo_del_nombre_de_cada_visitante():
    html = _html()

    assert html.index("Ana Perez") < html.index("DNI 30123456") < html.index("qr-visitante-1")
    assert html.index("Luis Gomez") < html.index("DNI 28123456") < html.index("qr-visitante-2")


def test_el_texto_plano_tambien_incluye_el_dni_de_cada_visitante():
    cuerpo = armar_mensaje(una_inscripcion_confirmada(), QRS).cuerpo

    assert "1. Ana Perez (DNI 30123456)" in cuerpo
    assert "2. Luis Gomez (DNI 28123456)" in cuerpo


def test_el_email_nunca_dice_prueba():
    mensaje = armar_mensaje(una_inscripcion_confirmada(), QRS)

    for texto in (mensaje.asunto, mensaje.cuerpo, mensaje.cuerpo_html):
        assert "prueba" not in texto.lower()


def test_el_asunto_incluye_el_codigo_fecha_y_horario_para_que_cada_inscripcion_sea_un_mail_aparte():
    asunto = armar_mensaje(una_inscripcion_confirmada("INS-0007"), QRS).asunto

    assert "INS-0007" in asunto
    assert "Tirolesa" in asunto
    assert "04/11/2026" in asunto
    assert "10:00" in asunto


def test_dos_inscripciones_a_la_misma_actividad_no_tienen_el_mismo_asunto():
    uno = armar_mensaje(una_inscripcion_confirmada("INS-0001"), QRS).asunto
    otro = armar_mensaje(una_inscripcion_confirmada("INS-0002"), QRS).asunto

    assert uno != otro
