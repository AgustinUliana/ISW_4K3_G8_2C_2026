from ecoharmony.errores import EmailYaRegistradoError


class RepositorioDeUsuariosEnMemoria:
    def __init__(self):
        self._usuarios = {}

    def guardar(self, usuario):
        if usuario.email in self._usuarios:
            raise EmailYaRegistradoError(usuario.email)
        self._usuarios[usuario.email] = usuario

    def buscar(self, email):
        return self._usuarios.get(email)
