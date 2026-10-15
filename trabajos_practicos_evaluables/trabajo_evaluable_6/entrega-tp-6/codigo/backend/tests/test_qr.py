from datetime import date, datetime, time

import pytest

from ecoharmony.catalogo import crear_actividades
from ecoharmony.errores import InscripcionNoConfirmada
from ecoharmony.horario import Horario
from ecoharmony.inscripcion import Inscripcion
from ecoharmony.qr import contenido_del_qr
from ecoharmony.visitante import Visitante

AHORA = datetime(2026, 11, 4, 8, 0)


def una_inscripcion_confirmada(codigo="INS-0001"):
    tirolesa = crear_actividades()["Tirolesa"]
    inscripcion = Inscripcion(
        actividad=tirolesa,
        horario=Horario(date(2026, 11, 4), time(10, 0)),
        visitantes=[
            Visitante("Ana Perez", "30123456", 30, talla="M"),
            Visitante("Luis Gomez", "28123456", 41, talla="L"),
        ],
        email_de_contacto="ana.perez@example.com",
        terminos_aceptados=tirolesa.terminos,
    )
    inscripcion.confirmar(codigo=codigo, ahora=AHORA)
    return inscripcion


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
