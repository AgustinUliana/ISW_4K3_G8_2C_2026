// Ilustracion de cada actividad (archivos en public/actividades/, sin tildes en el nombre).
const ARCHIVOS = {
  Tirolesa: "tirolesa",
  Safari: "safari",
  Palestra: "palestra",
  Jardinería: "jardineria",
};

export function imagenDeActividad(nombre) {
  const archivo = ARCHIVOS[nombre];
  return archivo ? `/actividades/${archivo}.svg` : null;
}
