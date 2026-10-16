import { capitalizar, mensajeDeMotivo } from "./mensajes";

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
  // acceso
  email_invalido: "email",
  email_ya_registrado: "email",
  contrasena_invalida: "contrasena",
};

export function camposConError(motivos) {
  const campos = motivos.map((motivo) => CAMPO_DEL_MOTIVO[motivo]).filter(Boolean);
  return [...new Set(campos)];
}

// Un mensaje por campo con problema (el del primer motivo), listo para mostrarlo debajo del campo.
export function mensajesPorCampo(motivos, contexto = {}) {
  const mensajes = {};
  for (const motivo of motivos) {
    const campo = CAMPO_DEL_MOTIVO[motivo];
    if (!campo || campo in mensajes) continue;
    const frase = capitalizar(mensajeDeMotivo(motivo, contexto));
    mensajes[campo] = frase.endsWith(".") ? frase : `${frase}.`;
  }
  return mensajes;
}
