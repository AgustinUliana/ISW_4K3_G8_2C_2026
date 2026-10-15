"""Contratos que el servicio de inscripcion necesita del mundo exterior.

Se extrajeron cuando aparecio la segunda implementacion de cada uno (Beck, Extract
Interface): un fake para las pruebas y la implementacion real.
"""

from typing import Protocol


class Reloj(Protocol):
    def ahora(self): ...


class GeneradorQR(Protocol):
    def generar(self, contenido: str) -> bytes: ...


class ServicioEmail(Protocol):
    def enviar(self, mensaje) -> None: ...


class RepositorioDeInscripciones(Protocol):
    def actividad(self, nombre): ...

    def siguiente_codigo(self) -> str: ...

    def guardar(self, inscripcion) -> None: ...

    def obtener(self, codigo): ...

    def dni_inscripto_en(self, dni, horario) -> bool: ...
