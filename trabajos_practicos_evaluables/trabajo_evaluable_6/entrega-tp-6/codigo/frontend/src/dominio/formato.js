const DIAS = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"];

export function fechaLegible(fechaIso) {
  const [anio, mes, dia] = fechaIso.split("-");
  return `${dia}/${mes}/${anio}`;
}

export function textoDeCupo(cupo) {
  return cupo === 1 ? "Queda 1 lugar" : `Quedan ${cupo} lugares`;
}

export function etiquetaDeDia(fecha) {
  return `${DIAS[fecha.getDay()]} ${fecha.getDate()}/${fecha.getMonth() + 1}`;
}
