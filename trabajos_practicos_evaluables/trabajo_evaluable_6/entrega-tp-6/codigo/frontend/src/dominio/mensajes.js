// Traduce los motivos de rechazo de la API (codigos) a frases para el visitante.
const GENERICO = "No se pudo completar la operación. Probá de nuevo.";

const MENSAJES = {
  sin_conexion: "No pudimos conectarnos con el servidor. Revisá tu conexión y probá de nuevo.",
  // sesion y registro
  email_invalido: "El email no es válido. Escribilo con el formato nombre@dominio.com.",
  contrasena_invalida: "La contraseña es demasiado corta: tiene que tener al menos 6 caracteres.",
  email_ya_registrado: "Ese email ya está registrado. Iniciá sesión.",
  credenciales_invalidas: "El email o la contraseña no son correctos. Revisá que estén bien escritos.",
  usuario_no_registrado: "Iniciá sesión para inscribirte.",
  // eleccion de actividad y horario
  actividad_requerida: "Elegí una actividad.",
  actividad_inexistente: "Esa actividad no existe.",
  horario_requerido: "Elegí un día y un horario.",
  fecha_invalida: "La fecha no es válida.",
  horario_no_disponible: "Ese horario no está disponible.",
  parque_cerrado: "El parque está cerrado ese día.",
  inscripcion_cerrada: "La inscripción para ese turno ya cerró (cierra 15 minutos antes).",
  fuera_de_ventana: "Solo se puede reservar dentro de las 24 horas previas al turno.",
  sin_cupo: "No quedan lugares suficientes en ese horario.",
  // visitantes
  cantidad_invalida: "La cantidad de personas debe ser de 1 a 10.",
  visitante_invalido: "Revisá los datos de los visitantes.",
  dni_duplicado: "Hay un DNI repetido en la inscripción: cada visitante necesita un DNI distinto.",
  dni_ya_inscripto: "Alguno de los DNI ya tiene una inscripción en ese horario.",
  nombre_requerido: "falta el nombre y apellido",
  nombre_invalido: "el nombre solo admite letras, espacios, apóstrofes y guiones (hasta 30 caracteres)",
  dni_requerido: "falta el DNI (7 u 8 números)",
  dni_invalido: "el DNI debe tener 7 u 8 números sin puntos ni espacios (por ejemplo 30123456)",
  edad_requerida: "falta la edad",
  edad_invalida: "la edad debe ser un número entero entre 0 y 100",
  edad_no_permitida: ({ edadMinima } = {}) =>
    edadMinima
      ? `no alcanza la edad mínima: la actividad es desde los ${edadMinima} años`
      : "no alcanza la edad mínima de la actividad",
  talla_requerida: "falta elegir la talla (XS, S, M, L, XL o XXL)",
  talla_invalida: "la talla no es válida: elegí una de la lista",
  // cierre
  terminos_no_aceptados: "Tenés que aceptar los términos y condiciones.",
  terminos_de_otra_actividad: "Los términos aceptados no son los de esta actividad.",
  email_no_enviado:
    "No pudimos enviar el email de confirmación, por eso la inscripción no se confirmó. Probá de nuevo en unos minutos.",
};

// `contexto` aporta datos de la pantalla que el motivo no trae (por ejemplo { edadMinima: 8 }).
export function mensajeDeMotivo(motivo, contexto = {}) {
  const mensaje = MENSAJES[motivo] ?? GENERICO;
  return typeof mensaje === "function" ? mensaje(contexto) : mensaje;
}

export const capitalizar = (texto) => texto.charAt(0).toUpperCase() + texto.slice(1);

export function mensajesDeRechazo(cuerpo, contexto = {}) {
  const motivos = cuerpo?.motivos ?? [];
  const porVisitante = Object.entries(cuerpo?.visitantes ?? {});
  const frases = motivos
    .filter((motivo) => !(motivo === "visitante_invalido" && porVisitante.length > 0))
    .map((motivo) => mensajeDeMotivo(motivo, contexto));
  for (const [posicion, errores] of porVisitante) {
    frases.push(`Visitante ${posicion}: ${errores.map((motivo) => mensajeDeMotivo(motivo, contexto)).join(", ")}.`);
  }
  // "Visitante 2: falta el DNI..." ya empieza con mayuscula; los demas detalles se escriben en minuscula.
  return frases.length > 0 ? frases.map((frase) => capitalizar(frase)) : [GENERICO];
}
