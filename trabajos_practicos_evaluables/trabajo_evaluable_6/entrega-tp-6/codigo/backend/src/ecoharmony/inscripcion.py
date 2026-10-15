import re
from dataclasses import dataclass, field

from ecoharmony.horario import ANTICIPACION_MAXIMA, CIERRE_PREVIO
from ecoharmony.motivos import MotivoRechazo

MAXIMO_DE_PERSONAS = 10
EMAIL_VALIDO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Inscripcion:
    actividad: object
    horario: object
    visitantes: list = field(default_factory=list)
    email_de_contacto: str = ""
    terminos_aceptados: object = None

    def motivos_de_rechazo(self, parque, ahora):
        motivos = []
        if self.actividad is None:
            motivos.append(MotivoRechazo.ACTIVIDAD_REQUERIDA)
        else:
            motivos.extend(self._motivos_de_terminos())
        if self.horario is None:
            motivos.append(MotivoRechazo.HORARIO_REQUERIDO)
        elif not self.horario.es_turno():
            motivos.append(MotivoRechazo.HORARIO_NO_DISPONIBLE)
        elif not parque.esta_abierto(self.horario):
            motivos.append(MotivoRechazo.PARQUE_CERRADO)
        elif ahora > self.horario.inicio - CIERRE_PREVIO:
            motivos.append(MotivoRechazo.INSCRIPCION_CERRADA)
        elif ahora < self.horario.inicio - ANTICIPACION_MAXIMA:
            motivos.append(MotivoRechazo.FUERA_DE_VENTANA)
        if not self.visitantes or len(self.visitantes) > MAXIMO_DE_PERSONAS:
            motivos.append(MotivoRechazo.CANTIDAD_INVALIDA)
        if self.errores_por_visitante():
            motivos.append(MotivoRechazo.VISITANTE_INVALIDO)
        if self._horario_es_turno() and self.actividad and not self.actividad.tiene_cupo(self.horario, len(self.visitantes)):
            motivos.append(MotivoRechazo.SIN_CUPO)
        if not EMAIL_VALIDO.match(self.email_de_contacto or ""):
            motivos.append(MotivoRechazo.EMAIL_INVALIDO)
        dnis = [visitante.dni for visitante in self.visitantes]
        if len(dnis) != len(set(dnis)):
            motivos.append(MotivoRechazo.DNI_DUPLICADO)
        return motivos

    def _horario_es_turno(self):
        return self.horario is not None and self.horario.es_turno()

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

    def _motivos_de_terminos(self):
        if self.terminos_aceptados is None:
            return [MotivoRechazo.TERMINOS_NO_ACEPTADOS]
        if self.terminos_aceptados != self.actividad.terminos:
            return [MotivoRechazo.TERMINOS_DE_OTRA_ACTIVIDAD]
        return []
