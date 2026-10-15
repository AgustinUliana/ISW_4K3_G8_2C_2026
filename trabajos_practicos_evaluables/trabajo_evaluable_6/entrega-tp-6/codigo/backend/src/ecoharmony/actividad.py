from ecoharmony.errores import CupoInsuficiente


class Actividad:
    def __init__(self, nombre, cupo_por_turno):
        self.nombre = nombre
        self.cupo_por_turno = cupo_por_turno
        self._ocupados = {}

    def tiene_cupo(self, horario, cantidad):
        return cantidad <= self.cupo_restante(horario)

    def reservar(self, horario, cantidad):
        if not self.tiene_cupo(horario, cantidad):
            raise CupoInsuficiente(self.nombre)
        self._ocupados[horario] = self._ocupados.get(horario, 0) + cantidad

    def cupo_restante(self, horario):
        return self.cupo_por_turno - self._ocupados.get(horario, 0)
