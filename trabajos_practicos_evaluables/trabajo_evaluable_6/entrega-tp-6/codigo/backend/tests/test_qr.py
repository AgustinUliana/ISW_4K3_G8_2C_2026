import pytest
from datos_de_prueba import una_inscripcion_confirmada

from ecoharmony.errores import InscripcionNoConfirmada
from ecoharmony.qr import contenido_del_qr

def test_el_contenido_del_qr_incluye_el_codigo_de_la_inscripcion():
    inscripcion = una_inscripcion_confirmada("INS-0001")

    assert "INS-0001" in contenido_del_qr(inscripcion, numero_de_visitante=1)


def test_el_contenido_del_qr_es_distinto_para_cada_visitante_y_para_cada_inscripcion():
    primera = una_inscripcion_confirmada("INS-0001")
    segunda = una_inscripcion_confirmada("INS-0002")

    contenidos = {
        contenido_del_qr(primera, 1),
        contenido_del_qr(primera, 2),
        contenido_del_qr(segunda, 1),
    }

    assert len(contenidos) == 3


def test_el_contenido_del_qr_es_el_mismo_para_el_mismo_visitante():
    inscripcion = una_inscripcion_confirmada()

    assert contenido_del_qr(inscripcion, 2) == contenido_del_qr(inscripcion, 2)


def test_el_contenido_del_qr_no_expone_datos_personales():
    inscripcion = una_inscripcion_confirmada()

    contenido = contenido_del_qr(inscripcion, 1)

    assert "30123456" not in contenido
    assert "Ana" not in contenido
    assert "ana.perez@example.com" not in contenido


def test_no_se_arma_el_qr_de_una_inscripcion_no_confirmada():
    pendiente = una_inscripcion_confirmada()
    pendiente.estado = type(pendiente.estado).PENDIENTE

    with pytest.raises(InscripcionNoConfirmada):
        contenido_del_qr(pendiente, 1)
