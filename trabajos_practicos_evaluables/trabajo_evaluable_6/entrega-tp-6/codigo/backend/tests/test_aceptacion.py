"""Pruebas de aceptacion (ACE): las pruebas de usuario de la consigna.

Se escribieron primero (ATDD) y estuvieron en xfail hasta que el sistema se
construyo ciclo a ciclo desde las pruebas unitarias. ACE-01 paso a verde con
SRV-04 (dobles en memoria); luego se apunta a Postgres y al QR real.
"""

from datetime import date, datetime, time


def test_inscribirse_a_una_actividad_con_cupo_confirma_y_envia_un_email_con_un_qr_por_visitante():
    from dobles import EmailEnMemoria, GeneradorQRFalso, RelojFijo
    from ecoharmony.catalogo import crear_actividades
    from ecoharmony.horario import Horario
    from ecoharmony.inscripcion_service import InscripcionService, SolicitudInscripcion
    from ecoharmony.parque import Parque
    from ecoharmony.repositorio_memoria import RepositorioEnMemoria
    from ecoharmony.visitante import Visitante

    email = EmailEnMemoria()
    servicio = InscripcionService(
        repositorio=RepositorioEnMemoria(crear_actividades()),
        parque=Parque(),
        reloj=RelojFijo(datetime(2026, 11, 4, 8, 0)),
        generador_qr=GeneradorQRFalso(),
        servicio_email=email,
    )
    solicitud = SolicitudInscripcion(
        actividad="Tirolesa",
        horario=Horario(date(2026, 11, 4), time(10, 0)),
        visitantes=[
            Visitante("Ana Perez", "30123456", 30, "M"),
            Visitante("Luis Gomez", "28123456", 41, "L"),
        ],
        email_de_contacto="ana.perez@example.com",
        terminos_aceptados="Tirolesa",
    )

    resultado = servicio.inscribir(solicitud)

    assert resultado.confirmada
    assert len(email.enviados) == 1
    assert email.enviados[0].destinatario == "ana.perez@example.com"
    assert len(email.enviados[0].adjuntos) == 2
