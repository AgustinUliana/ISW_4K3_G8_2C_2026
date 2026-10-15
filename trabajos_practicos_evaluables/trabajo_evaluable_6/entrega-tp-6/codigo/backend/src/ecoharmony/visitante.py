from dataclasses import dataclass

from ecoharmony.motivos import MotivoRechazo

TALLAS = ("XS", "S", "M", "L", "XL", "XXL")


@dataclass
class Visitante:
    nombre: str
    dni: str
    edad: int
    talla: str = None

    def errores(self, actividad):
        errores = []
        if not self.nombre.strip():
            errores.append(MotivoRechazo.NOMBRE_REQUERIDO)
        elif len(self.nombre) > 30 or not all(c.isalpha() or c in " '-" for c in self.nombre):
            errores.append(MotivoRechazo.NOMBRE_INVALIDO)
        if not self.dni:
            errores.append(MotivoRechazo.DNI_REQUERIDO)
        elif not self.dni.isdigit() or not 7 <= len(self.dni) <= 8:
            errores.append(MotivoRechazo.DNI_INVALIDO)
        if self.edad is None:
            errores.append(MotivoRechazo.EDAD_REQUERIDA)
        elif not isinstance(self.edad, int) or not 0 <= self.edad <= 100:
            errores.append(MotivoRechazo.EDAD_INVALIDA)
        if isinstance(self.edad, int) and not actividad.admite_edad(self.edad):
            errores.append(MotivoRechazo.EDAD_NO_PERMITIDA)
        if actividad.requiere_talla and not self.talla:
            errores.append(MotivoRechazo.TALLA_REQUERIDA)
        elif actividad.requiere_talla and self.talla not in TALLAS:
            errores.append(MotivoRechazo.TALLA_INVALIDA)
        return errores
