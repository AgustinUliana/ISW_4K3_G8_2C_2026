from dataclasses import dataclass


@dataclass(frozen=True)
class TerminosYCondiciones:
    actividad: str
    version: str
    texto: str
