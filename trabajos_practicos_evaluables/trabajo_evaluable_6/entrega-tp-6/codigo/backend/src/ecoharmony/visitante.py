from dataclasses import dataclass

from ecoharmony.motivos import MotivoRechazo

TALLAS = ("XS", "S", "M", "L", "XL", "XXL")
LARGO_MAXIMO_NOMBRE = 30
LARGOS_VALIDOS_DNI = (7, 8)
EDAD_MAXIMA = 100


@dataclass
class Visitante:
    nombre: str
    dni: str
    edad: int
    talla: str = None

    def errores(self, actividad):
        return [
            *self._errores_de_nombre(),
            *self._errores_de_dni(),
            *self._errores_de_edad(actividad),
            *self._errores_de_talla(actividad),
        ]

    def _errores_de_nombre(self):
        if not self.nombre.strip():
            return [MotivoRechazo.NOMBRE_REQUERIDO]
        solo_caracteres_validos = all(c.isalpha() or c in " '-" for c in self.nombre)
        if len(self.nombre) > LARGO_MAXIMO_NOMBRE or not solo_caracteres_validos:
            return [MotivoRechazo.NOMBRE_INVALIDO]
        return []

    def _errores_de_dni(self):
        if not self.dni:
            return [MotivoRechazo.DNI_REQUERIDO]
        if not self.dni.isdigit() or len(self.dni) not in LARGOS_VALIDOS_DNI:
            return [MotivoRechazo.DNI_INVALIDO]
        return []

    def _errores_de_edad(self, actividad):
        if self.edad is None:
            return [MotivoRechazo.EDAD_REQUERIDA]
        if not isinstance(self.edad, int) or not 0 <= self.edad <= EDAD_MAXIMA:
            return [MotivoRechazo.EDAD_INVALIDA]
        if not actividad.admite_edad(self.edad):
            return [MotivoRechazo.EDAD_NO_PERMITIDA]
        return []

    def _errores_de_talla(self, actividad):
        if not actividad.requiere_talla:
            return []
        if not self.talla:
            return [MotivoRechazo.TALLA_REQUERIDA]
        if self.talla not in TALLAS:
            return [MotivoRechazo.TALLA_INVALIDA]
        return []
