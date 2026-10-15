"""Pruebas de aceptacion (ACE): las pruebas de usuario de la consigna.

Se escribieron primero (ATDD) y estuvieron en xfail hasta que el sistema se construyo
ciclo a ciclo desde las pruebas unitarias. Corren dos veces:
- "memoria": con los fakes (rapido, sin dependencias);
- "postgres": con la base PostgreSQL real y el generador de QR real (libreria qrcode).
El email se captura en memoria: el envio real a una casilla es una prueba externa (X).
"""

from collections import namedtuple
from datetime import date, datetime, time

import pytest

from datos_de_prueba import AHORA, H1, n_visitantes, una_inscripcion_confirmada, una_solicitud
from dobles import EmailEnMemoria, GeneradorQRFalso, RelojFijo
from ecoharmony.catalogo import crear_actividades
from ecoharmony.generador_qr_local import GeneradorQRLocal
from ecoharmony.horario import Horario
from ecoharmony.inscripcion_service import InscripcionService
from ecoharmony.motivos import MotivoRechazo
from ecoharmony.parque import Parque
from ecoharmony.repositorio_memoria import RepositorioEnMemoria
from ecoharmony.repositorio_postgres import RepositorioPostgres
from ecoharmony.visitante import Visitante

Sistema = namedtuple("Sistema", "servicio repositorio email")
FIRMA_PNG = b"\x89PNG\r\n\x1a\n"


def armar_sistema(repositorio, generador_qr, ahora=AHORA):
    email = EmailEnMemoria()
    servicio = InscripcionService(
        repositorio=repositorio,
        parque=Parque(),
        reloj=RelojFijo(ahora),
        generador_qr=generador_qr,
        servicio_email=email,
    )
    return Sistema(servicio, repositorio, email)


@pytest.fixture(
    params=[
        "memoria",
        pytest.param("postgres", marks=[pytest.mark.local, pytest.mark.db]),
    ]
)
def sistema(request):
    if request.param == "memoria":
        return armar_sistema(RepositorioEnMemoria(crear_actividades()), GeneradorQRFalso())
    repositorio = RepositorioPostgres(request.getfixturevalue("base_con_esquema"))
    repositorio.cargar_actividades(crear_actividades())
    return armar_sistema(repositorio, GeneradorQRLocal())


def test_ace_01_inscribirse_con_cupo_horario_datos_y_terminos_confirma_y_envia_un_qr_por_visitante(
    sistema,
):
    resultado = sistema.servicio.inscribir(una_solicitud())

    assert resultado.confirmada
    (mensaje,) = sistema.email.enviados
    assert mensaje.destinatario == "ana.perez@example.com"
    assert len(mensaje.adjuntos) == 2  # un QR por visitante
    assert all(adjunto.contenido for adjunto in mensaje.adjuntos)
    assert sistema.repositorio.obtener(resultado.codigo) is not None
    assert sistema.repositorio.actividad("Tirolesa").cupo_restante(H1) == 8


def test_ace_02_inscribirse_a_una_actividad_sin_cupo_para_el_horario_falla(sistema):
    sistema.repositorio.guardar(
        una_inscripcion_confirmada(sistema.repositorio.siguiente_codigo(), n_visitantes(10))
    )  # Tirolesa 10:00 queda en 0

    resultado = sistema.servicio.inscribir(
        una_solicitud(visitantes=[Visitante("Eva Soto", "40123456", 25, talla="S")])
    )

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.SIN_CUPO]
    assert sistema.email.enviados == []


def test_ace_03_inscribirse_sin_talle_porque_la_actividad_no_lo_requiere_pasa(sistema):
    sin_talla = Visitante("Ana Perez", "30123456", 30)

    resultado = sistema.servicio.inscribir(
        una_solicitud(
            actividad="Jardinería", terminos_aceptados="Jardinería", visitantes=[sin_talla]
        )
    )

    assert resultado.confirmada
    assert len(sistema.email.enviados) == 1


@pytest.mark.parametrize(
    "horario, ahora, motivo",
    [
        # lunes: el parque esta cerrado
        (
            Horario(date(2026, 11, 2), time(10, 0)),
            datetime(2026, 11, 2, 8, 0),
            MotivoRechazo.PARQUE_CERRADO,
        ),
        # 18:00 es la cota superior: la actividad no tiene turno
        (Horario(date(2026, 11, 4), time(18, 0)), AHORA, MotivoRechazo.HORARIO_NO_DISPONIBLE),
    ],
)
def test_ace_04_inscribirse_en_un_horario_con_el_parque_cerrado_o_sin_turno_falla(
    sistema, horario, ahora, motivo
):
    sistema_con_reloj = armar_sistema(sistema.repositorio, GeneradorQRFalso(), ahora=ahora)

    resultado = sistema_con_reloj.servicio.inscribir(una_solicitud(horario=horario))

    assert not resultado.confirmada
    assert resultado.motivos == [motivo]
    assert sistema_con_reloj.email.enviados == []


def test_ace_05_inscribirse_sin_aceptar_los_terminos_de_la_actividad_falla(sistema):
    resultado = sistema.servicio.inscribir(una_solicitud(terminos_aceptados=None))

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.TERMINOS_NO_ACEPTADOS]
    assert sistema.email.enviados == []


def test_ace_06_inscribirse_sin_el_talle_que_la_actividad_requiere_falla(sistema):
    sin_talla = Visitante("Ana Perez", "30123456", 30)

    resultado = sistema.servicio.inscribir(una_solicitud(visitantes=[sin_talla]))

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.VISITANTE_INVALIDO]
    assert sistema.email.enviados == []


def test_ace_07_inscribirse_aceptando_los_terminos_de_otra_actividad_falla(sistema):
    resultado = sistema.servicio.inscribir(una_solicitud(terminos_aceptados="Safari"))

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.TERMINOS_DE_OTRA_ACTIVIDAD]
    assert sistema.email.enviados == []


def test_ace_08_inscribirse_sin_haber_iniciado_sesion_falla(sistema):
    resultado = sistema.servicio.inscribir(una_solicitud(titular=None))

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.USUARIO_NO_REGISTRADO]
    assert sistema.email.enviados == []
