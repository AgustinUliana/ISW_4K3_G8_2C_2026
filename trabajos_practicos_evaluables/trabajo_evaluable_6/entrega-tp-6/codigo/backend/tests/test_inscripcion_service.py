from datetime import date, datetime, time

import pytest

from datos_de_prueba import AHORA, ANA, EMAIL_DE_ANA, H1, LUIS, una_solicitud
from dobles import (
    EmailEnMemoria,
    EmailQueFalla,
    EmailQueFallaLasPrimeras,
    GeneradorQRFalso,
    GeneradorQRQueFalla,
    RelojFijo,
)
from ecoharmony.catalogo import crear_actividades
from ecoharmony.errores import CupoInsuficienteError, DniYaInscriptoError
from ecoharmony.horario import Horario
from ecoharmony.inscripcion_service import InscripcionService
from ecoharmony.motivos import MotivoRechazo
from ecoharmony.parque import Parque
from ecoharmony.repositorio_memoria import RepositorioEnMemoria
from ecoharmony.visitante import Visitante


def armar_servicio(
    repositorio=None,
    email=None,
    generador_qr=None,
    ahora=AHORA,
    intentos_de_email=3,
    dormir=None,
    pausa=0,
):
    return InscripcionService(
        repositorio=repositorio or RepositorioEnMemoria(crear_actividades()),
        parque=Parque(),
        reloj=RelojFijo(ahora),
        generador_qr=generador_qr or GeneradorQRFalso(),
        servicio_email=email or EmailEnMemoria(),
        intentos_de_email=intentos_de_email,
        dormir=dormir or (lambda segundos: None),
        pausa_entre_intentos=pausa,
    )


def test_inscripcion_valida_se_confirma_y_devuelve_el_codigo_de_reserva():
    resultado = armar_servicio().inscribir(una_solicitud())

    assert resultado.confirmada
    assert resultado.codigo == "INS-0001"


def test_sin_cupo_no_confirma():
    repositorio = RepositorioEnMemoria(crear_actividades())
    repositorio.actividad("Tirolesa").reservar(H1, cantidad=10)

    resultado = armar_servicio(repositorio).inscribir(una_solicitud())

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.SIN_CUPO]


def assert_sin_efectos(repositorio, email, cupo_de_tirolesa=10):
    """Un rechazo no deja rastro: nada guardado, cupo intacto y ningun email enviado."""
    assert repositorio.inscripciones() == []
    assert repositorio.actividad("Tirolesa").cupo_restante(H1) == cupo_de_tirolesa
    assert email.enviados == []


def test_sin_aceptar_los_terminos_no_confirma_ni_envia_email():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailEnMemoria()

    resultado = armar_servicio(repositorio, email).inscribir(una_solicitud(terminos_aceptados=None))

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.TERMINOS_NO_ACEPTADOS]
    assert_sin_efectos(repositorio, email)


def test_terminos_de_otra_actividad_no_confirman_ni_envian_email():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailEnMemoria()

    resultado = armar_servicio(repositorio, email).inscribir(
        una_solicitud(terminos_aceptados="Jardinería")
    )

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.TERMINOS_DE_OTRA_ACTIVIDAD]
    assert_sin_efectos(repositorio, email)


def test_inscripcion_valida_queda_persistida():
    repositorio = RepositorioEnMemoria(crear_actividades())

    resultado = armar_servicio(repositorio).inscribir(una_solicitud())

    guardada = repositorio.obtener(resultado.codigo)
    assert guardada.actividad.nombre == "Tirolesa"
    assert guardada.horario == H1
    assert [v.dni for v in guardada.visitantes] == [ANA.dni, LUIS.dni]


def test_inscripcion_valida_descuenta_el_cupo():
    repositorio = RepositorioEnMemoria(crear_actividades())

    armar_servicio(repositorio).inscribir(una_solicitud())  # Ana y Luis: 2 personas

    assert repositorio.actividad("Tirolesa").cupo_restante(H1) == 8


def test_inscripcion_valida_envia_un_unico_email_al_contacto():
    email = EmailEnMemoria()

    armar_servicio(email=email).inscribir(una_solicitud())

    assert len(email.enviados) == 1
    assert email.enviados[0].destinatario == EMAIL_DE_ANA


def test_cada_qr_adjunto_al_email_es_el_que_entrego_el_generador():
    email = EmailEnMemoria()

    armar_servicio(email=email).inscribir(una_solicitud())

    adjuntos = email.enviados[0].adjuntos
    assert [adjunto.contenido for adjunto in adjuntos] == [b"QR[INS-0001|V1]", b"QR[INS-0001|V2]"]


def test_parque_cerrado_no_confirma_ni_envia_email():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailEnMemoria()
    lunes = Horario(date(2026, 11, 2), time(10, 0))
    lunes_a_las_8 = datetime(2026, 11, 2, 8, 0)

    resultado = armar_servicio(repositorio, email, ahora=lunes_a_las_8).inscribir(
        una_solicitud(horario=lunes)
    )

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.PARQUE_CERRADO]
    assert_sin_efectos(repositorio, email)


def test_turno_con_inscripcion_cerrada_no_confirma_ni_envia_email():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailEnMemoria()
    a_14_minutos = datetime(2026, 11, 4, 9, 46)

    resultado = armar_servicio(repositorio, email, ahora=a_14_minutos).inscribir(una_solicitud())

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.INSCRIPCION_CERRADA]
    assert_sin_efectos(repositorio, email)


def test_actividad_que_requiere_talla_sin_indicarla_no_confirma_ni_envia_email():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailEnMemoria()
    sin_talla = Visitante("Ana Perez", "30123456", 30)

    resultado = armar_servicio(repositorio, email).inscribir(una_solicitud(visitantes=[sin_talla]))

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.VISITANTE_INVALIDO]
    assert_sin_efectos(repositorio, email)


def test_actividad_que_no_requiere_talla_sin_indicarla_confirma_y_envia_email():
    email = EmailEnMemoria()
    sin_talla = Visitante("Ana Perez", "30123456", 30)
    solicitud = una_solicitud(
        actividad="Safari", terminos_aceptados="Safari", visitantes=[sin_talla]
    )

    resultado = armar_servicio(email=email).inscribir(solicitud)

    assert resultado.confirmada
    assert len(email.enviados) == 1


def test_el_ultimo_cupo_lo_obtiene_solo_la_primera_inscripcion():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailEnMemoria()
    repositorio.actividad("Tirolesa").reservar(H1, cantidad=9)  # queda 1
    servicio = armar_servicio(repositorio, email)

    primera = servicio.inscribir(una_solicitud(visitantes=[ANA]))
    segunda = servicio.inscribir(una_solicitud(visitantes=[LUIS]))

    assert primera.confirmada
    assert not segunda.confirmada
    assert segunda.motivos == [MotivoRechazo.SIN_CUPO]
    assert len(email.enviados) == 1


def test_dni_ya_inscripto_en_el_mismo_horario_no_confirma_ni_envia_email():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailEnMemoria()
    servicio = armar_servicio(repositorio, email)
    servicio.inscribir(una_solicitud(visitantes=[ANA]))  # Ana ya esta en Tirolesa a las 10:00

    en_safari_a_la_misma_hora = una_solicitud(
        actividad="Safari", terminos_aceptados="Safari", visitantes=[ANA]
    )
    resultado = servicio.inscribir(en_safari_a_la_misma_hora)

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.DNI_YA_INSCRIPTO]
    assert len(repositorio.inscripciones()) == 1
    assert repositorio.actividad("Safari").cupo_restante(H1) == 8
    assert len(email.enviados) == 1


def test_si_el_email_falla_se_reintenta_hasta_que_se_envia():
    email = EmailQueFallaLasPrimeras(fallos=2)

    resultado = armar_servicio(email=email).inscribir(una_solicitud())

    assert resultado.confirmada
    assert email.intentos == 3
    assert len(email.enviados) == 1


def test_si_el_email_nunca_se_envia_la_inscripcion_no_queda_confirmada():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailQueFalla()

    resultado = armar_servicio(repositorio, email).inscribir(una_solicitud())

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.EMAIL_NO_ENVIADO]
    assert email.intentos == 3
    assert_sin_efectos(repositorio, email)


def test_la_cantidad_de_intentos_de_email_es_configurable():
    email = EmailQueFalla()

    armar_servicio(email=email, intentos_de_email=5).inscribir(una_solicitud())

    assert email.intentos == 5


def test_entre_un_intento_de_email_y_el_siguiente_se_espera():
    esperas = []

    armar_servicio(email=EmailQueFalla(), dormir=esperas.append, pausa=0.5).inscribir(
        una_solicitud()
    )

    assert esperas == [0.5, 0.5]  # 3 intentos: 2 esperas


def test_tras_anularse_por_el_email_se_puede_volver_a_intentar_la_inscripcion():
    repositorio = RepositorioEnMemoria(crear_actividades())
    armar_servicio(repositorio, EmailQueFalla()).inscribir(una_solicitud())

    de_nuevo = armar_servicio(repositorio, EmailEnMemoria()).inscribir(una_solicitud())

    assert de_nuevo.confirmada  # el cupo y los DNI quedaron libres


def test_si_falla_la_generacion_del_qr_no_se_confirma_ni_se_descuenta_cupo():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailEnMemoria()
    servicio = armar_servicio(repositorio, email, generador_qr=GeneradorQRQueFalla())

    with pytest.raises(RuntimeError):
        servicio.inscribir(una_solicitud())

    assert_sin_efectos(repositorio, email)


class RepositorioQueFallaAlGuardar(RepositorioEnMemoria):
    def guardar(self, inscripcion):
        raise ConnectionError("la base de datos no responde")


def test_si_falla_la_persistencia_no_se_envia_ningun_email():
    repositorio, email = RepositorioQueFallaAlGuardar(crear_actividades()), EmailEnMemoria()

    with pytest.raises(ConnectionError):
        armar_servicio(repositorio, email).inscribir(una_solicitud())

    assert_sin_efectos(repositorio, email)


class RepositorioQuePierdeLaCarrera(RepositorioEnMemoria):
    """Otro usuario se llevo el ultimo cupo entre la validacion y el guardado."""

    def guardar(self, inscripcion):
        raise CupoInsuficienteError(inscripcion.actividad.nombre)


def test_si_el_cupo_se_agota_justo_al_guardar_se_rechaza_por_falta_de_cupo():
    repositorio, email = RepositorioQuePierdeLaCarrera(crear_actividades()), EmailEnMemoria()

    resultado = armar_servicio(repositorio, email).inscribir(una_solicitud())

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.SIN_CUPO]
    assert email.enviados == []


def test_inscribirse_a_una_actividad_inexistente_no_confirma_ni_envia_email():
    repositorio, email = RepositorioEnMemoria(crear_actividades()), EmailEnMemoria()

    resultado = armar_servicio(repositorio, email).inscribir(una_solicitud(actividad="Rafting"))

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.ACTIVIDAD_INEXISTENTE]
    assert_sin_efectos(repositorio, email)


class RepositorioQuePierdeLaCarreraDelDni(RepositorioEnMemoria):
    """Otro pedido inscribio al mismo DNI entre la validacion y el guardado."""

    def guardar(self, inscripcion):
        raise DniYaInscriptoError(inscripcion.visitantes[0].dni)


def test_si_el_dni_se_inscribe_en_paralelo_se_rechaza_por_dni_ya_inscripto():
    repositorio, email = RepositorioQuePierdeLaCarreraDelDni(crear_actividades()), EmailEnMemoria()

    resultado = armar_servicio(repositorio, email).inscribir(una_solicitud())

    assert not resultado.confirmada
    assert resultado.motivos == [MotivoRechazo.DNI_YA_INSCRIPTO]
    assert email.enviados == []
