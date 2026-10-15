import psycopg

from ecoharmony.errores import EmailYaRegistradoError
from ecoharmony.usuarios import Usuario


class RepositorioDeUsuariosPostgres:
    def __init__(self, url):
        self._url = url

    def guardar(self, usuario):
        try:
            with psycopg.connect(self._url) as conexion:
                conexion.execute(
                    "INSERT INTO usuario (email, contrasena_hash) VALUES (%s, %s)",
                    (usuario.email, usuario.contrasena_hash),
                )
        except psycopg.errors.UniqueViolation as error:
            raise EmailYaRegistradoError(usuario.email) from error

    def buscar(self, email):
        with psycopg.connect(self._url) as conexion:
            fila = conexion.execute(
                "SELECT email, contrasena_hash FROM usuario WHERE email = %s", (email,)
            ).fetchone()
        return Usuario(*fila) if fila else None
