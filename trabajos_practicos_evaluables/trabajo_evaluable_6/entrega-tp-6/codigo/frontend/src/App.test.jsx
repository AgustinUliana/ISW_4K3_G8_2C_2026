import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import App from "./App";
import { crearApiFalsa, falla } from "./test/apiFalsa";

const AHORA = new Date(2026, 10, 4, 10, 0); // miercoles 4/11/2026 10:00

function almacenamientoEnMemoria(inicial = {}) {
  const datos = { ...inicial };
  return {
    datos,
    getItem: (clave) => datos[clave] ?? null,
    setItem: (clave, valor) => {
      datos[clave] = valor;
    },
    removeItem: (clave) => {
      delete datos[clave];
    },
  };
}

function montar({ api = crearApiFalsa(), almacenamiento = almacenamientoEnMemoria() } = {}) {
  render(<App api={api} ahora={() => AHORA} almacenamiento={almacenamiento} />);
  return { api, almacenamiento };
}

const SESION_GUARDADA = { "ecoharmony.sesion": JSON.stringify({ token: "tok", email: "ana@example.com" }) };

async function entrar(usuario) {
  await usuario.type(screen.getByLabelText("Email"), "ana@example.com");
  await usuario.type(screen.getByLabelText("Contraseña"), "secreto1");
  await usuario.click(screen.getByRole("button", { name: "Iniciar sesión" }));
}

describe("App", () => {
  it("sin sesion empieza por el acceso", () => {
    montar();

    expect(screen.getByRole("heading", { name: "Ingresá para inscribirte" })).toBeInTheDocument();
  });

  it("recorre toda la inscripcion: acceso, actividad, horario, visitantes, terminos y confirmacion", async () => {
    const usuario = userEvent.setup();
    const { api } = montar();

    await entrar(usuario);
    const tirolesa = await screen.findByRole("article", { name: "Tirolesa" });
    await usuario.click(within(tirolesa).getByRole("button", { name: "Elegir" }));

    await usuario.click(await screen.findByRole("button", { name: /^10:00/ }));

    await usuario.selectOptions(await screen.findByLabelText("Cantidad de personas"), "2");
    for (const [numero, datos] of [
      [1, { nombre: "Ana Perez", dni: "30123456", edad: "30", talla: "M" }],
      [2, { nombre: "Luis Gomez", dni: "28123456", edad: "41", talla: "L" }],
    ]) {
      const grupo = within(screen.getByRole("group", { name: `Visitante ${numero}` }));
      await usuario.type(grupo.getByLabelText("Nombre"), datos.nombre);
      await usuario.type(grupo.getByLabelText("DNI"), datos.dni);
      await usuario.type(grupo.getByLabelText("Edad"), datos.edad);
      await usuario.selectOptions(grupo.getByLabelText("Talla"), datos.talla);
    }
    await usuario.click(screen.getByRole("button", { name: "Continuar" }));

    await screen.findByText("Texto de los términos de Tirolesa.");
    await usuario.click(screen.getByLabelText("Acepto los términos y condiciones de Tirolesa"));
    await usuario.click(screen.getByRole("button", { name: "Confirmar inscripción" }));

    expect(await screen.findByRole("heading", { name: "¡Inscripción confirmada!" })).toBeInTheDocument();
    expect(screen.getByText("INS-0001")).toBeInTheDocument();
    expect(api.inscribir).toHaveBeenCalledWith(
      expect.objectContaining({ actividad: "Tirolesa", fecha: "2026-11-04", hora: "10:00" }),
      "token-de-prueba",
    );
  });

  it("despues de inscribirse permite empezar otra inscripcion", async () => {
    const usuario = userEvent.setup();
    montar({ almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });
    const safari = await screen.findByRole("article", { name: "Safari" });
    await usuario.click(within(safari).getByRole("button", { name: "Elegir" }));
    await usuario.click(await screen.findByRole("button", { name: /^10:00/ }));
    const grupo = within(await screen.findByRole("group", { name: "Visitante 1" }));
    await usuario.type(grupo.getByLabelText("Nombre"), "Eva Soto");
    await usuario.type(grupo.getByLabelText("DNI"), "40123456");
    await usuario.type(grupo.getByLabelText("Edad"), "25");
    await usuario.click(screen.getByRole("button", { name: "Continuar" }));
    await screen.findByText("Texto de los términos de Safari.");
    await usuario.click(screen.getByLabelText("Acepto los términos y condiciones de Safari"));
    await usuario.click(screen.getByRole("button", { name: "Confirmar inscripción" }));

    await usuario.click(await screen.findByRole("button", { name: "Hacer otra inscripción" }));

    expect(await screen.findByRole("heading", { name: "Elegí una actividad" })).toBeInTheDocument();
  });

  it("con una sesion guardada salta el acceso y muestra el email en el encabezado", async () => {
    montar({ almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });

    expect(await screen.findByRole("heading", { name: "Elegí una actividad" })).toBeInTheDocument();
    expect(screen.getByRole("banner")).toHaveTextContent("ana@example.com");
  });

  it("al entrar guarda la sesion y al cerrar sesion la borra y vuelve al acceso", async () => {
    const usuario = userEvent.setup();
    const { almacenamiento } = montar();

    await entrar(usuario);
    await screen.findByRole("heading", { name: "Elegí una actividad" });
    expect(JSON.parse(almacenamiento.datos["ecoharmony.sesion"])).toEqual({
      token: "token-de-prueba",
      email: "ana@example.com",
    });

    await usuario.click(screen.getByRole("button", { name: "Cerrar sesión" }));

    expect(almacenamiento.datos["ecoharmony.sesion"]).toBeUndefined();
    expect(screen.getByRole("heading", { name: "Ingresá para inscribirte" })).toBeInTheDocument();
  });

  it("si la sesion vence al confirmar, vuelve al acceso con un aviso y borra la sesion", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({ inscribir: vi.fn(async () => falla(401, { motivos: ["usuario_no_registrado"] })) });
    const { almacenamiento } = montar({ api, almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });
    const safari = await screen.findByRole("article", { name: "Safari" });
    await usuario.click(within(safari).getByRole("button", { name: "Elegir" }));
    await usuario.click(await screen.findByRole("button", { name: /^10:00/ }));
    const grupo = within(await screen.findByRole("group", { name: "Visitante 1" }));
    await usuario.type(grupo.getByLabelText("Nombre"), "Eva Soto");
    await usuario.type(grupo.getByLabelText("DNI"), "40123456");
    await usuario.type(grupo.getByLabelText("Edad"), "25");
    await usuario.click(screen.getByRole("button", { name: "Continuar" }));
    await screen.findByText("Texto de los términos de Safari.");
    await usuario.click(screen.getByLabelText("Acepto los términos y condiciones de Safari"));
    await usuario.click(screen.getByRole("button", { name: "Confirmar inscripción" }));

    expect(await screen.findByRole("heading", { name: "Ingresá para inscribirte" })).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent(/tu sesión venció/i);
    expect(almacenamiento.datos["ecoharmony.sesion"]).toBeUndefined();
  });

  it("el boton volver del horario regresa a la lista de actividades", async () => {
    const usuario = userEvent.setup();
    montar({ almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });
    const safari = await screen.findByRole("article", { name: "Safari" });
    await usuario.click(within(safari).getByRole("button", { name: "Elegir" }));

    await usuario.click(await screen.findByRole("button", { name: "Volver" }));

    expect(await screen.findByRole("heading", { name: "Elegí una actividad" })).toBeInTheDocument();
  });

  it("marca en el indicador de pasos en cual esta", async () => {
    montar({ almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });
    await screen.findByRole("heading", { name: "Elegí una actividad" });

    const pasos = screen.getByRole("list", { name: "Pasos de la inscripción" });

    expect(within(pasos).getByText("Actividad").closest("li")).toHaveAttribute("aria-current", "step");
  });

  it("si el navegador no deja usar el almacenamiento, igual funciona", () => {
    const roto = {
      getItem: () => {
        throw new Error("bloqueado");
      },
      setItem: () => {
        throw new Error("bloqueado");
      },
      removeItem: () => {},
    };

    montar({ almacenamiento: roto });

    expect(screen.getByRole("heading", { name: "Ingresá para inscribirte" })).toBeInTheDocument();
  });
});


describe("App: los datos de los visitantes se validan en su propio paso", () => {
  async function llegarAlPasoDeVisitantes(usuario) {
    const safari = await screen.findByRole("article", { name: "Safari" });
    await usuario.click(within(safari).getByRole("button", { name: "Elegir" }));
    await usuario.click(await screen.findByRole("button", { name: /^10:00/ }));
    return within(await screen.findByRole("group", { name: "Visitante 1" }));
  }

  it("si los datos no son validos el error aparece en el paso 3 y se corrige ahi mismo", async () => {
    const usuario = userEvent.setup();
    const validarInscripcion = vi
      .fn()
      .mockResolvedValueOnce(
        falla(422, { motivos: ["visitante_invalido"], visitantes: { 1: ["dni_invalido", "edad_invalida"] } }),
      )
      .mockResolvedValueOnce({ ok: true, estado: 200, datos: { valida: true } });
    montar({ api: crearApiFalsa({ validarInscripcion }), almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });
    const grupo = await llegarAlPasoDeVisitantes(usuario);
    await usuario.type(grupo.getByLabelText("Nombre"), "Eva Soto");
    await usuario.type(grupo.getByLabelText("DNI"), "123");
    await usuario.type(grupo.getByLabelText("Edad"), "150");

    await usuario.click(screen.getByRole("button", { name: "Continuar" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Visitante 1: el DNI debe tener 7 u 8 números sin puntos ni espacios (por ejemplo 30123456), la edad debe ser un número entero entre 0 y 100.",
    );
    expect(screen.getByRole("heading", { name: "¿Quiénes participan?" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "Revisá y confirmá" })).toBeNull();

    await usuario.clear(grupo.getByLabelText("DNI"));
    await usuario.type(grupo.getByLabelText("DNI"), "40123456");
    await usuario.clear(grupo.getByLabelText("Edad"));
    await usuario.type(grupo.getByLabelText("Edad"), "25");
    await usuario.click(screen.getByRole("button", { name: "Continuar" }));

    expect(await screen.findByRole("heading", { name: "Revisá y confirmá" })).toBeInTheDocument();
  });

  it("al volver desde la confirmacion encuentra los datos que habia cargado", async () => {
    const usuario = userEvent.setup();
    montar({ almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });
    const grupo = await llegarAlPasoDeVisitantes(usuario);
    await usuario.type(grupo.getByLabelText("Nombre"), "Eva Soto");
    await usuario.type(grupo.getByLabelText("DNI"), "40123456");
    await usuario.type(grupo.getByLabelText("Edad"), "25");
    await usuario.click(screen.getByRole("button", { name: "Continuar" }));
    await screen.findByRole("heading", { name: "Revisá y confirmá" });

    await usuario.click(screen.getByRole("button", { name: "Volver" }));

    const otraVez = within(await screen.findByRole("group", { name: "Visitante 1" }));
    expect(otraVez.getByLabelText("Nombre")).toHaveValue("Eva Soto");
    expect(otraVez.getByLabelText("DNI")).toHaveValue("40123456");
  });

  it("si la sesion vence al validar, vuelve al acceso con un aviso", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      validarInscripcion: vi.fn(async () => falla(401, { motivos: ["usuario_no_registrado"] })),
    });
    montar({ api, almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });
    const grupo = await llegarAlPasoDeVisitantes(usuario);
    await usuario.type(grupo.getByLabelText("Nombre"), "Eva Soto");
    await usuario.type(grupo.getByLabelText("DNI"), "40123456");
    await usuario.type(grupo.getByLabelText("Edad"), "25");

    await usuario.click(screen.getByRole("button", { name: "Continuar" }));

    expect(await screen.findByRole("heading", { name: "Ingresá para inscribirte" })).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent(/tu sesión venció/i);
  });

  it("sin sesion el acceso muestra el logo grande y el lema, sin el encabezado de la aplicacion", () => {
    montar();

    const logo = screen.getByRole("img", { name: /^Logo de EcoHarmony Park$/i });
    expect(logo).toHaveAttribute("src", "/logo.png");
    expect(screen.getByText("Reservá tu lugar en las actividades del parque")).toBeInTheDocument();
    expect(screen.queryByRole("banner")).toBeNull();
    expect(screen.getByRole("heading", { name: "Ingresá para inscribirte" })).toBeInTheDocument();
  });

  it("con la sesion iniciada el logo pasa al encabezado, en su version chica", () => {
    montar({ almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });

    const logo = within(screen.getByRole("banner")).getByRole("img", { name: /^Logo de EcoHarmony Park$/i });
    expect(logo).toHaveAttribute("src", "/logo-emblema.png");
    expect(screen.queryByText("Reservá tu lugar en las actividades del parque")).toBeNull();
  });

  it("cerrar sesion es un boton con icono, sin texto visible, y conserva su nombre accesible", () => {
    montar({ almacenamiento: almacenamientoEnMemoria(SESION_GUARDADA) });

    const boton = within(screen.getByRole("banner")).getByRole("button", { name: "Cerrar sesión" });

    expect(boton.textContent).toBe("");
    expect(boton.querySelector("svg")).not.toBeNull();
    expect(boton).toHaveAttribute("title", "Cerrar sesión");
  });
});
