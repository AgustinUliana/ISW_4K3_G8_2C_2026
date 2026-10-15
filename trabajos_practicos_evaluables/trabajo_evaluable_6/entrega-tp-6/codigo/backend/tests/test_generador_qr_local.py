"""Contrato del GeneradorQRLocal (categoria C: usa la libreria qrcode, sin red)."""
import pytest

from ecoharmony.generador_qr_local import GeneradorQRLocal

FIRMA_PNG = b"\x89PNG\r\n\x1a\n"

pytestmark = pytest.mark.local


def test_el_generador_local_devuelve_una_imagen_png_valida():
    imagen = GeneradorQRLocal().generar("INS-0001|V1")

    assert imagen.startswith(FIRMA_PNG)
    assert len(imagen) > len(FIRMA_PNG)


def test_el_generador_local_devuelve_imagenes_distintas_para_contenidos_distintos():
    generador = GeneradorQRLocal()

    assert generador.generar("INS-0001|V1") != generador.generar("INS-0001|V2")
