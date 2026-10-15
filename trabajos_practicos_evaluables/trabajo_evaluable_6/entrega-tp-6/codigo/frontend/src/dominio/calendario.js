// Regla del PO: el parque cierra los lunes, el 25 de diciembre y el 1 de enero.
// Y solo se puede reservar dentro de las 24 horas previas al turno (hoy y manana).
const FERIADOS = [
  [12, 25],
  [1, 1],
];
const LUNES = 1;
const DIAS_QUE_SE_MUESTRAN = 7;
const ULTIMO_DIA_RESERVABLE = 1; // 0 = hoy, 1 = manana

const dosDigitos = (numero) => String(numero).padStart(2, "0");

export function aFechaIso(fecha) {
  return `${fecha.getFullYear()}-${dosDigitos(fecha.getMonth() + 1)}-${dosDigitos(fecha.getDate())}`;
}

export function estaAbierto(fecha) {
  const esFeriado = FERIADOS.some(([mes, dia]) => fecha.getMonth() + 1 === mes && fecha.getDate() === dia);
  return fecha.getDay() !== LUNES && !esFeriado;
}

export function diasParaElegir(ahora, cantidad = DIAS_QUE_SE_MUESTRAN) {
  return Array.from({ length: cantidad }, (_, desdeHoy) => {
    const fecha = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate() + desdeHoy);
    const abierto = estaAbierto(fecha);
    const enVentana = desdeHoy <= ULTIMO_DIA_RESERVABLE;
    let motivo = null;
    if (!abierto) motivo = "cerrado";
    else if (!enVentana) motivo = "fuera_de_ventana";
    return { fecha: aFechaIso(fecha), fechaDate: fecha, abierto, enVentana, seleccionable: abierto && enVentana, motivo };
  });
}
