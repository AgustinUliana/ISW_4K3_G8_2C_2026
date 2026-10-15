"""API HTTP (FastAPI) probada con TestClient sobre los servicios reales y dobles en memoria."""

from collections import namedtuple
from datetime import date, time

import pytest
from fastapi.testclient import TestClient

from datos_de_prueba import AHORA
from dobles import EmailEnMemoria, EmailQueFalla, GeneradorQRFalso, RelojFijo
from ecoharmony.api import Servicios, crear_app
from ecoharmony.catalogo import crear_actividades
from ecoharmony.horario import Horario
from ecoharmony.inscripcion_service import InscripcionService
from ecoharmony.parque import Parque
from ecoharmony.repositorio_memoria import RepositorioEnMemoria
from ecoharmony.repositorio_usuarios_memoria import RepositorioDeUsuariosEnMemoria
from ecoharmony.usuarios import ServicioUsuarios

ORIGEN_DEL_FRONT = "http://localhost:5173"
Cliente = namedtuple("Cliente", "http email repositorio")


def armar_cliente(repositorio=None, email=None, intentos_de_email=1):
    repositorio = repositorio or RepositorioEnMemoria(crear_actividades())
    email = email or EmailEnMemoria()
    reloj, parque = RelojFijo(AHORA), Parque()
    servicios = Servicios(
        usuarios=ServicioUsuarios(RepositorioDeUsuariosEnMemoria(), "clave-de-prueba", reloj),
        inscripciones=InscripcionService(
            repositorio,
            parque,
            reloj,
            GeneradorQRFalso(),
            email,
            intentos_de_email=intentos_de_email,
            dormir=lambda segundos: None,
        ),
        repositorio=repositorio,
        parque=parque,
        reloj=reloj,
    )
    app = crear_app(servicios, origenes_permitidos=[ORIGEN_DEL_FRONT])
    return Cliente(TestClient(app, raise_server_exceptions=False), email, repositorio)


@pytest.fixture
def cliente():
    return armar_cliente()


def test_post_registro_con_datos_validos_responde_201(cliente):
    respuesta = cliente.http.post(
        "/registro", json={"email": "Ana@Example.com", "contrasena": "secreto1"}
    )

    assert respuesta.status_code == 201
    assert respuesta.json() == {"email": "ana@example.com"}


def test_post_registro_con_datos_invalidos_responde_422_con_los_motivos(cliente):
    respuesta = cliente.http.post("/registro", json={"email": "ana", "contrasena": "123"})

    assert respuesta.status_code == 422
    assert respuesta.json()["motivos"] == ["email_invalido", "contrasena_invalida"]


def test_post_registro_sin_cuerpo_responde_422_y_no_falla(cliente):
    respuesta = cliente.http.post("/registro", json={})

    assert respuesta.status_code == 422
    assert "email_invalido" in respuesta.json()["motivos"]


def test_post_registro_de_un_email_repetido_responde_409(cliente):
    datos = {"email": "ana@example.com", "contrasena": "secreto1"}
    cliente.http.post("/registro", json=datos)

    respuesta = cliente.http.post("/registro", json=datos)

    assert respuesta.status_code == 409
    assert respuesta.json()["motivos"] == ["email_ya_registrado"]


def test_post_sesion_con_credenciales_correctas_devuelve_un_token(cliente):
    datos = {"email": "ana@example.com", "contrasena": "secreto1"}
    cliente.http.post("/registro", json=datos)

    respuesta = cliente.http.post("/sesion", json=datos)

    assert respuesta.status_code == 200
    assert respuesta.json()["token"]


def test_post_sesion_con_credenciales_incorrectas_responde_401(cliente):
    cliente.http.post("/registro", json={"email": "ana@example.com", "contrasena": "secreto1"})

    respuesta = cliente.http.post(
        "/sesion", json={"email": "ana@example.com", "contrasena": "otra-clave"}
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["motivos"] == ["credenciales_invalidas"]


def test_el_front_react_puede_llamar_a_la_api_desde_su_origen(cliente):
    respuesta = cliente.http.options(
        "/sesion",
        headers={"Origin": ORIGEN_DEL_FRONT, "Access-Control-Request-Method": "POST"},
    )

    assert respuesta.headers["access-control-allow-origin"] == ORIGEN_DEL_FRONT


def test_get_actividades_devuelve_las_cuatro_con_sus_reglas_y_su_disponibilidad(cliente):
    respuesta = cliente.http.get("/actividades")

    assert respuesta.status_code == 200
    por_nombre = {actividad["nombre"]: actividad for actividad in respuesta.json()}
    assert set(por_nombre) == {"Tirolesa", "Safari", "Palestra", "Jardinería"}
    assert por_nombre["Tirolesa"] == {
        "nombre": "Tirolesa",
        "requiere_talla": True,
        "edad_minima": 8,
        "cupo_por_turno": 10,
        "disponible": True,
    }


def test_get_horarios_de_una_actividad_devuelve_los_turnos_con_su_cupo_restante(cliente):
    a_las_10 = Horario(date(2026, 11, 4), time(10, 0))
    cliente.repositorio.actividad("Tirolesa").reservar(a_las_10, cantidad=3)

    respuesta = cliente.http.get("/actividades/Tirolesa/horarios", params={"fecha": "2026-11-04"})

    assert respuesta.status_code == 200
    turnos = respuesta.json()["turnos"]
    assert [turno["hora"] for turno in turnos] == [f"{hora:02d}:00" for hora in range(9, 18)]
    assert {"hora": "10:00", "cupo_restante": 7, "agotado": False} in turnos


def test_get_horarios_con_una_fecha_invalida_o_ausente_responde_422(cliente):
    assert (
        cliente.http.get("/actividades/Tirolesa/horarios", params={"fecha": "ayer"}).status_code
        == 422
    )
    assert cliente.http.get("/actividades/Tirolesa/horarios").status_code == 422


def test_get_horarios_de_una_actividad_inexistente_responde_404(cliente):
    respuesta = cliente.http.get("/actividades/Rafting/horarios", params={"fecha": "2026-11-04"})

    assert respuesta.status_code == 404
    assert respuesta.json()["motivos"] == ["actividad_inexistente"]


def test_get_terminos_de_una_actividad_devuelve_los_de_esa_actividad(cliente):
    respuesta = cliente.http.get("/actividades/Safari/terminos")

    assert respuesta.status_code == 200
    assert respuesta.json()["actividad"] == "Safari"
    assert respuesta.json()["version"] == "v1"
    assert respuesta.json()["texto"]


def test_get_terminos_de_una_actividad_inexistente_responde_404(cliente):
    assert cliente.http.get("/actividades/Rafting/terminos").status_code == 404


VISITANTES = [
    {"nombre": "Ana Perez", "dni": "30123456", "edad": 30, "talla": "M"},
    {"nombre": "Luis Gomez", "dni": "28123456", "edad": 41, "talla": "L"},
]


def una_inscripcion_json(**cambios):
    datos = {
        "actividad": "Tirolesa",
        "fecha": "2026-11-04",
        "hora": "10:00",
        "visitantes": VISITANTES,
        "terminos_aceptados": "Tirolesa",
    }
    datos.update(cambios)
    return datos


def entrar(cliente, email="ana.perez@example.com", contrasena="secreto1"):
    """Registra a un usuario, inicia sesion y devuelve el encabezado Authorization."""
    cliente.http.post("/registro", json={"email": email, "contrasena": contrasena})
    token = cliente.http.post("/sesion", json={"email": email, "contrasena": contrasena}).json()
    return {"Authorization": f"Bearer {token['token']}"}


def test_post_inscripcion_valida_responde_201_y_envia_el_email_al_usuario(cliente):
    respuesta = cliente.http.post(
        "/inscripciones", json=una_inscripcion_json(), headers=entrar(cliente)
    )

    assert respuesta.status_code == 201
    assert respuesta.json() == {"codigo": "INS-0001"}
    (mensaje,) = cliente.email.enviados
    assert mensaje.destinatario == "ana.perez@example.com"
    assert len(mensaje.adjuntos) == 2  # un QR por visitante


@pytest.mark.parametrize("encabezados", [{}, {"Authorization": "Bearer token-falso"}])
def test_post_inscripcion_sin_sesion_valida_responde_401(cliente, encabezados):
    respuesta = cliente.http.post(
        "/inscripciones", json=una_inscripcion_json(), headers=encabezados
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["motivos"] == ["usuario_no_registrado"]  # y nada mas que eso
    assert cliente.email.enviados == []


def test_post_inscripcion_sin_cupo_responde_409(cliente):
    cliente.repositorio.actividad("Tirolesa").reservar(
        Horario(date(2026, 11, 4), time(10, 0)), cantidad=10
    )

    respuesta = cliente.http.post(
        "/inscripciones", json=una_inscripcion_json(), headers=entrar(cliente)
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["motivos"] == ["sin_cupo"]


def test_post_inscripcion_con_un_visitante_invalido_responde_422_indicando_cual(cliente):
    sin_dni = {"nombre": "Luis Gomez", "dni": "", "edad": 41, "talla": "L"}

    respuesta = cliente.http.post(
        "/inscripciones",
        json=una_inscripcion_json(visitantes=[VISITANTES[0], sin_dni]),
        headers=entrar(cliente),
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["motivos"] == ["visitante_invalido"]
    assert respuesta.json()["visitantes"] == {"2": ["dni_requerido"]}


def test_post_inscripcion_con_un_horario_que_no_es_fecha_responde_422(cliente):
    respuesta = cliente.http.post(
        "/inscripciones", json=una_inscripcion_json(fecha="no-es-fecha"), headers=entrar(cliente)
    )

    assert respuesta.status_code == 422
    assert "horario_requerido" in respuesta.json()["motivos"]


def test_post_inscripcion_con_tipos_inesperados_responde_422_y_no_falla(cliente):
    raro = {"nombre": None, "dni": 30123456, "edad": "treinta", "talla": 5}

    respuesta = cliente.http.post(
        "/inscripciones", json=una_inscripcion_json(visitantes=[raro]), headers=entrar(cliente)
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["motivos"] == ["visitante_invalido"]


def test_post_inscripcion_a_una_actividad_inexistente_responde_404(cliente):
    respuesta = cliente.http.post(
        "/inscripciones", json=una_inscripcion_json(actividad="Rafting"), headers=entrar(cliente)
    )

    assert respuesta.status_code == 404


def test_post_inscripcion_si_el_email_nunca_se_envia_responde_503_y_no_queda_confirmada():
    cliente = armar_cliente(email=EmailQueFalla())

    respuesta = cliente.http.post(
        "/inscripciones", json=una_inscripcion_json(), headers=entrar(cliente)
    )

    assert respuesta.status_code == 503
    assert respuesta.json()["motivos"] == ["email_no_enviado"]
    assert cliente.repositorio.inscripciones() == []


class RepositorioQueExplota(RepositorioEnMemoria):
    def guardar(self, inscripcion):
        raise RuntimeError("detalle interno que no debe filtrarse")


def test_un_error_inesperado_responde_500_sin_detalles_internos():
    cliente = armar_cliente(repositorio=RepositorioQueExplota(crear_actividades()))

    respuesta = cliente.http.post(
        "/inscripciones", json=una_inscripcion_json(), headers=entrar(cliente)
    )

    assert respuesta.status_code == 500
    assert respuesta.json() == {"detalle": "Error interno del servidor"}
    assert "detalle interno" not in respuesta.text


def test_post_validar_con_datos_correctos_responde_200_y_no_inscribe_ni_envia_email(cliente):
    respuesta = cliente.http.post(
        "/inscripciones/validar",
        json=una_inscripcion_json(terminos_aceptados=None),
        headers=entrar(cliente),
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {"valida": True}
    assert cliente.repositorio.inscripciones() == []
    assert cliente.email.enviados == []


def test_post_validar_con_un_visitante_invalido_responde_422_indicando_cual(cliente):
    sin_dni = {"nombre": "Luis Gomez", "dni": "", "edad": 41, "talla": "L"}

    respuesta = cliente.http.post(
        "/inscripciones/validar",
        json=una_inscripcion_json(visitantes=[VISITANTES[0], sin_dni]),
        headers=entrar(cliente),
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["motivos"] == ["visitante_invalido"]
    assert respuesta.json()["visitantes"] == {"2": ["dni_requerido"]}


def test_post_validar_sin_sesion_responde_401(cliente):
    respuesta = cliente.http.post("/inscripciones/validar", json=una_inscripcion_json())

    assert respuesta.status_code == 401
    assert respuesta.json()["motivos"] == ["usuario_no_registrado"]


def test_post_validar_sin_cupo_responde_409(cliente):
    cliente.repositorio.actividad("Tirolesa").reservar(
        Horario(date(2026, 11, 4), time(10, 0)), cantidad=10
    )

    respuesta = cliente.http.post(
        "/inscripciones/validar", json=una_inscripcion_json(), headers=entrar(cliente)
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["motivos"] == ["sin_cupo"]
