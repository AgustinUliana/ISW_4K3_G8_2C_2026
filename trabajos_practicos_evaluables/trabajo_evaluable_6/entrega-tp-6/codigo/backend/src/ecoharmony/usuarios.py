import base64
import hashlib
import hmac
import re
from dataclasses import dataclass, field
from datetime import timedelta

from ecoharmony.contrasenas import hashear, verificar
from ecoharmony.errores import EmailYaRegistradoError
from ecoharmony.motivos import MotivoRechazo

EMAIL_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LARGO_MINIMO_DE_CONTRASENA = 6
DURACION_DE_SESION = timedelta(hours=8)


@dataclass
class Usuario:
    email: str
    contrasena_hash: str = None


@dataclass
class ResultadoRegistro:
    registrado: bool
    motivos: list = field(default_factory=list)
    usuario: Usuario = None


@dataclass
class ResultadoSesion:
    iniciada: bool
    token: str = None
    motivos: list = field(default_factory=list)


def _normalizar(email):
    return (email or "").strip().lower()


class ServicioUsuarios:
    """Registro e inicio de sesion con email y contrasena (lo mas simple posible).

    La sesion es un token firmado con HMAC-SHA256: `<email|vencimiento en base64>.<firma>`.
    """

    def __init__(self, repositorio, clave_secreta, reloj, duracion_de_sesion=DURACION_DE_SESION):
        self._repositorio = repositorio
        self._clave_secreta = clave_secreta.encode("utf-8")
        self._reloj = reloj
        self._duracion_de_sesion = duracion_de_sesion

    def registrar(self, email, contrasena):
        email = _normalizar(email)
        motivos = []
        if not EMAIL_VALIDO.match(email):
            motivos.append(MotivoRechazo.EMAIL_INVALIDO)
        if len(contrasena or "") < LARGO_MINIMO_DE_CONTRASENA:
            motivos.append(MotivoRechazo.CONTRASENA_INVALIDA)
        if motivos:
            return ResultadoRegistro(registrado=False, motivos=motivos)
        usuario = Usuario(email=email, contrasena_hash=hashear(contrasena))
        try:
            self._repositorio.guardar(usuario)
        except EmailYaRegistradoError:
            return ResultadoRegistro(registrado=False, motivos=[MotivoRechazo.EMAIL_YA_REGISTRADO])
        return ResultadoRegistro(registrado=True, usuario=usuario)

    def iniciar_sesion(self, email, contrasena):
        usuario = self._repositorio.buscar(_normalizar(email))
        # El mismo rechazo para "email inexistente" y "contrasena incorrecta": no revela cual fallo.
        if usuario is None or not verificar(contrasena or "", usuario.contrasena_hash):
            return ResultadoSesion(iniciada=False, motivos=[MotivoRechazo.CREDENCIALES_INVALIDAS])
        vence = self._reloj.ahora() + self._duracion_de_sesion
        return ResultadoSesion(iniciada=True, token=self._firmar(usuario.email, vence))

    def usuario_de_token(self, token):
        """El usuario al que pertenece el token, o None si es invalido, alterado o esta vencido."""
        try:
            carga_b64, firma = token.split(".")
            carga = base64.urlsafe_b64decode(carga_b64.encode("ascii")).decode("utf-8")
            email, vence = carga.rsplit("|", 1)
            vence = float(vence)
        except (ValueError, AttributeError, UnicodeError):
            return None
        if not hmac.compare_digest(firma, self._firma(carga)):
            return None
        if self._reloj.ahora().timestamp() > vence:
            return None
        return self._repositorio.buscar(email)

    def _firmar(self, email, vence):
        carga = f"{email}|{vence.timestamp()}"
        carga_b64 = base64.urlsafe_b64encode(carga.encode("utf-8")).decode("ascii")
        return f"{carga_b64}.{self._firma(carga)}"

    def _firma(self, carga):
        return hmac.new(self._clave_secreta, carga.encode("utf-8"), hashlib.sha256).hexdigest()
