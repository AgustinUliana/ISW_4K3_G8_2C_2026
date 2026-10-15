// Cliente HTTP de la API. Siempre devuelve { ok, estado, datos }: nunca lanza.
const URL_POR_DEFECTO = import.meta.env?.VITE_API_URL ?? "http://localhost:8000";

export function crearCliente({ baseUrl = URL_POR_DEFECTO, fetchImpl = (...args) => fetch(...args) } = {}) {
  async function pedir(ruta, { metodo = "GET", cuerpo, token } = {}) {
    const headers = {};
    if (cuerpo !== undefined) headers["Content-Type"] = "application/json";
    if (token) headers.Authorization = `Bearer ${token}`;
    const opciones = { method: metodo, headers };
    if (cuerpo !== undefined) opciones.body = JSON.stringify(cuerpo);
    let respuesta;
    try {
      respuesta = await fetchImpl(`${baseUrl}${ruta}`, opciones);
    } catch {
      return { ok: false, estado: 0, datos: { motivos: ["sin_conexion"] } };
    }
    let datos = {};
    try {
      datos = await respuesta.json();
    } catch {
      // el servidor no devolvio JSON: se informa solo el estado
    }
    return { ok: respuesta.ok, estado: respuesta.status, datos };
  }

  const nombre = (texto) => encodeURIComponent(texto);

  return {
    registrar: (email, contrasena) => pedir("/registro", { metodo: "POST", cuerpo: { email, contrasena } }),
    iniciarSesion: (email, contrasena) => pedir("/sesion", { metodo: "POST", cuerpo: { email, contrasena } }),
    actividades: () => pedir("/actividades"),
    horarios: (actividad, fecha) => pedir(`/actividades/${nombre(actividad)}/horarios?fecha=${fecha}`),
    terminos: (actividad) => pedir(`/actividades/${nombre(actividad)}/terminos`),
    inscribir: (datos, token) => pedir("/inscripciones", { metodo: "POST", cuerpo: datos, token }),
  };
}
