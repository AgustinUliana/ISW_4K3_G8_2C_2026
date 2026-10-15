import re
from dataclasses import dataclass, field

from ecoharmony.horario import EstadoDeInscripcion
from ecoharmony.motivos import MotivoRechazo

MAXIMO_DE_PERSONAS = 10
EMAIL_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_MOTIVO_SEGUN_ESTADO = {
    EstadoDeInscripcion.CERRADA: MotivoRechazo.INSCRIPCION_CERRADA,
    EstadoDeInscripcion.ANTICIPADA: MotivoRechazo.FUERA_DE_VENTANA,
}


@dataclass
class Inscripcion:
    actividad: object
    horario: object
    visitantes: list = field(default_factory=list)
    email_de_contacto: str = ""
    terminos_aceptados: object = None

    def motivos_de_rechazo(self, parque, ahora):
        return [
            *self._motivos_de_actividad_y_terminos(),
            *self._motivos_de_horario(parque, ahora),
            *self._motivos_de_visitantes(),
            *self._motivos_de_contacto(),
        ]

    def errores_por_visitante(self):
        """Posicion (desde 1) de cada visitante invalido -> sus errores."""
        errores = {}
        if self.actividad is None:
            return errores  # sin actividad no se puede validar la talla ni la edad minima
        for posicion, visitante in enumerate(self.visitantes, start=1):
            errores_del_visitante = visitante.errores(self.actividad)
            if errores_del_visitante:
                errores[posicion] = errores_del_visitante
        return errores

    def _motivos_de_actividad_y_terminos(self):
        if self.actividad is None:
            return [MotivoRechazo.ACTIVIDAD_REQUERIDA]
        if self.terminos_aceptados is None:
            return [MotivoRechazo.TERMINOS_NO_ACEPTADOS]
        if self.terminos_aceptados != self.actividad.terminos:
            return [MotivoRechazo.TERMINOS_DE_OTRA_ACTIVIDAD]
        return []

    def _motivos_de_horario(self, parque, ahora):
        if self.horario is None:
            return [MotivoRechazo.HORARIO_REQUERIDO]
        if not self.horario.es_turno():
            return [MotivoRechazo.HORARIO_NO_DISPONIBLE]
        motivos = []
        if not parque.esta_abierto(self.horario):
            motivos.append(MotivoRechazo.PARQUE_CERRADO)
        else:
            motivo_de_ventana = _MOTIVO_SEGUN_ESTADO.get(self.horario.estado_de_inscripcion(ahora))
            if motivo_de_ventana:
                motivos.append(motivo_de_ventana)
        if self.actividad and not self.actividad.tiene_cupo(self.horario, len(self.visitantes)):
            motivos.append(MotivoRechazo.SIN_CUPO)
        return motivos

    def _motivos_de_visitantes(self):
        motivos = []
        if not self.visitantes or len(self.visitantes) > MAXIMO_DE_PERSONAS:
            motivos.append(MotivoRechazo.CANTIDAD_INVALIDA)
        if self.errores_por_visitante():
            motivos.append(MotivoRechazo.VISITANTE_INVALIDO)
        dnis = [visitante.dni for visitante in self.visitantes]
        if len(dnis) != len(set(dnis)):
            motivos.append(MotivoRechazo.DNI_DUPLICADO)
        return motivos

    def _motivos_de_contacto(self):
        if not EMAIL_VALIDO.match(self.email_de_contacto or ""):
            return [MotivoRechazo.EMAIL_INVALIDO]
        return []
