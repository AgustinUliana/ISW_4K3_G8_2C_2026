import { describe, expect, it, vi } from "vitest";
import { crearCliente } from "./cliente";

const respuesta = (estado, cuerpo) => ({
  ok: estado >= 200 && estado < 300,
  status: estado,
  json: async () => cuerpo,
});

const clienteCon = (fetchFalso) => crearCliente({ baseUrl: "http://api.test", fetchImpl: fetchFalso });
const JSON_HEADERS = expect.objectContaining({ "Content-Type": "application/json" });

describe("cliente de la API", () => {
  it("registrar hace POST /registro con el email y la contraseña en JSON", async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respuesta(201, { email: "ana@example.com" }));

    const resultado = await clienteCon(fetchFalso).registrar("ana@example.com", "secreto1");

    expect(fetchFalso).toHaveBeenCalledWith(
      "http://api.test/registro",
      expect.objectContaining({
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({ email: "ana@example.com", contrasena: "secreto1" }),
      }),
    );
    expect(resultado).toEqual({ ok: true, estado: 201, datos: { email: "ana@example.com" } });
  });

  it("iniciarSesion hace POST /sesion y devuelve el token", async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respuesta(200, { token: "abc" }));

    const resultado = await clienteCon(fetchFalso).iniciarSesion("ana@example.com", "secreto1");

    expect(fetchFalso.mock.calls[0][0]).toBe("http://api.test/sesion");
    expect(resultado.datos.token).toBe("abc");
  });

  it("actividades hace GET /actividades", async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respuesta(200, []));

    await clienteCon(fetchFalso).actividades();

    expect(fetchFalso).toHaveBeenCalledWith("http://api.test/actividades", expect.objectContaining({ method: "GET" }));
  });

  it("horarios codifica el nombre de la actividad (tildes) y agrega la fecha", async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respuesta(200, { turnos: [] }));

    await clienteCon(fetchFalso).horarios("Jardinería", "2026-11-04");

    expect(fetchFalso.mock.calls[0][0]).toBe(
      "http://api.test/actividades/Jardiner%C3%ADa/horarios?fecha=2026-11-04",
    );
  });

  it("terminos hace GET /actividades/{nombre}/terminos", async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respuesta(200, { texto: "..." }));

    await clienteCon(fetchFalso).terminos("Safari");

    expect(fetchFalso.mock.calls[0][0]).toBe("http://api.test/actividades/Safari/terminos");
  });

  it("inscribir envia el token como Bearer y el cuerpo en JSON", async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respuesta(201, { codigo: "INS-0001" }));
    const datos = { actividad: "Tirolesa", fecha: "2026-11-04", hora: "10:00", visitantes: [] };

    await clienteCon(fetchFalso).inscribir(datos, "mi-token");

    const [url, opciones] = fetchFalso.mock.calls[0];
    expect(url).toBe("http://api.test/inscripciones");
    expect(opciones.headers.Authorization).toBe("Bearer mi-token");
    expect(opciones.body).toBe(JSON.stringify(datos));
  });

  it("una respuesta de error conserva el estado y los motivos para mostrarlos", async () => {
    const fetchFalso = vi.fn().mockResolvedValue(respuesta(409, { motivos: ["sin_cupo"] }));

    const resultado = await clienteCon(fetchFalso).inscribir({}, "t");

    expect(resultado).toEqual({ ok: false, estado: 409, datos: { motivos: ["sin_cupo"] } });
  });

  it("si no hay conexion con el servidor, devuelve un error con el motivo sin_conexion", async () => {
    const fetchFalso = vi.fn().mockRejectedValue(new TypeError("Failed to fetch"));

    const resultado = await clienteCon(fetchFalso).actividades();

    expect(resultado).toEqual({ ok: false, estado: 0, datos: { motivos: ["sin_conexion"] } });
  });

  it("si el servidor responde algo que no es JSON no se rompe", async () => {
    const sinJson = { ok: false, status: 502, json: async () => { throw new SyntaxError("no es json"); } };

    const resultado = await clienteCon(vi.fn().mockResolvedValue(sinJson)).actividades();

    expect(resultado).toEqual({ ok: false, estado: 502, datos: {} });
  });
});
