// A que campo del formulario del visitante corresponde cada motivo de rechazo de la API.
const CAMPO_DEL_MOTIVO = {
  nombre_requerido: "nombre",
  nombre_invalido: "nombre",
  dni_requerido: "dni",
  dni_invalido: "dni",
  edad_requerida: "edad",
  edad_invalida: "edad",
  edad_no_permitida: "edad",
  talla_requerida: "talla",
  talla_invalida: "talla",
};

export function camposConError(motivos) {
  const campos = motivos.map((motivo) => CAMPO_DEL_MOTIVO[motivo]).filter(Boolean);
  return [...new Set(campos)];
}
