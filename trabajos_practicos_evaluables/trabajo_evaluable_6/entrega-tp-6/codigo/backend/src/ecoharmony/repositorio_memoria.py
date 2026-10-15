from ecoharmony.errores import ActividadNoEncontradaError, DniYaInscriptoError


class RepositorioEnMemoria:
    def __init__(self, actividades):
        self._actividades = actividades
        self._inscripciones = {}

    def actividad(self, nombre):
        if nombre not in self._actividades:
            raise ActividadNoEncontradaError(nombre)
        return self._actividades[nombre]

    def siguiente_codigo(self):
        return f"INS-{len(self._inscripciones) + 1:04d}"

    def guardar(self, inscripcion):
        """Reserva el cupo y guarda la inscripcion (en Postgres sera una sola transaccion)."""
        for visitante in inscripcion.visitantes:
            if self.dni_inscripto_en(visitante.dni, inscripcion.horario):
                raise DniYaInscriptoError(visitante.dni)
        actividad = self._actividades[inscripcion.actividad.nombre]
        actividad.reservar(inscripcion.horario, len(inscripcion.visitantes))
        self._inscripciones[inscripcion.codigo] = inscripcion

    def obtener(self, codigo):
        return self._inscripciones.get(codigo)

    def dni_inscripto_en(self, dni, horario):
        return any(
            inscripcion.horario == horario and dni in [v.dni for v in inscripcion.visitantes]
            for inscripcion in self._inscripciones.values()
        )

    def inscripciones(self):
        return list(self._inscripciones.values())
