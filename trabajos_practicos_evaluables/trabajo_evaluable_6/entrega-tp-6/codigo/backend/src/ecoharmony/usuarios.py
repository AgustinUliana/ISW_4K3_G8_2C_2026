import re
from dataclasses import dataclass, field

from ecoharmony.contrasenas import hashear
from ecoharmony.errores import EmailYaRegistradoError
from ecoharmony.motivos import MotivoRechazo

EMAIL_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LARGO_MINIMO_DE_CONTRASENA = 6


@dataclass
class Usuario:
    email: str
    contrasena_hash: str = None


@dataclass
class ResultadoRegistro:
    registrado: bool
    motivos: list = field(default_factory=list)
    usuario: Usuario = None


class ServicioUsuarios:
    """Registro de usuarios con email y contrasena (lo mas simple posible)."""

    def __init__(self, repositorio, clave_secreta, reloj):
        self._repositorio = repositorio
        self._clave_secreta = clave_secreta
        self._reloj = reloj

    def registrar(self, email, contrasena):
        email = (email or "").strip().lower()
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
