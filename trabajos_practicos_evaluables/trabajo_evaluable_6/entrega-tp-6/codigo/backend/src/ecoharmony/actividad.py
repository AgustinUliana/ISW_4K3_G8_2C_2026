from ecoharmony.errores import CupoInsuficienteError


class Actividad:
    def __init__(self, nombre, cupo_por_turno, edad_minima=0, requiere_talla=False, terminos=None):
        self.nombre = nombre
        self.cupo_por_turno = cupo_por_turno
        self.edad_minima = edad_minima
        self.requiere_talla = requiere_talla
        self.terminos = terminos
        self._ocupados = {}

    def tiene_cupo(self, horario, cantidad):
        return horario.es_turno() and cantidad <= self.cupo_restante(horario)

    def reservar(self, horario, cantidad):
        if not self.tiene_cupo(horario, cantidad):
            raise CupoInsuficienteError(self.nombre)
        self._ocupados[horario] = self._ocupados.get(horario, 0) + cantidad

    def cupo_restante(self, horario):
        return self.cupo_por_turno - self._ocupados.get(horario, 0)

    def admite_edad(self, edad):
        return edad >= self.edad_minima
