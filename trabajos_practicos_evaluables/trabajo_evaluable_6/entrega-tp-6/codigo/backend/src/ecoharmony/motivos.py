from enum import Enum


class MotivoRechazo(Enum):
    NOMBRE_REQUERIDO = "nombre_requerido"
    DNI_REQUERIDO = "dni_requerido"
    DNI_INVALIDO = "dni_invalido"
    EDAD_REQUERIDA = "edad_requerida"
    EDAD_INVALIDA = "edad_invalida"
    EDAD_NO_PERMITIDA = "edad_no_permitida"
    TALLA_REQUERIDA = "talla_requerida"
    TALLA_INVALIDA = "talla_invalida"
    NOMBRE_INVALIDO = "nombre_invalido"
