import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ACTIVIDADES, crearApiFalsa, falla, ok } from "../test/apiFalsa";
import { PantallaVisitantes } from "./PantallaVisitantes";

const TIROLESA = ACTIVIDADES[0]; // pide talla, desde 8 años
const SAFARI = ACTIVIDADES[1]; // no pide talla
const SESION = { token: "tok", email: "ana@example.com" };

function mostrar(actividad, cupoRestante, { api = crearApiFalsa(), visitantesIniciales } = {}) {
  const alContinuar = vi.fn();
  const alVolver = vi.fn();
  const alSesionVencida = vi.fn();
  render(
    <PantallaVisitantes
      api={api}
      sesion={SESION}
      actividad={actividad}
      fecha="2026-11-04"
      turno={{ hora: "10:00", cupo_restante: cupoRestante, agotado: false }}
      visitantesIniciales={visitantesIniciales}
      alContinuar={alContinuar}
      alVolver={alVolver}
      alSesionVencida={alSesionVencida}
    />,
  );
  return { api, alContinuar, alVolver, alSesionVencida };
}

const visitante = (numero) => within(screen.getByRole("group", { name: `Visitante ${numero}` }));
const continuar = (usuario) => usuario.click(screen.getByRole("button", { name: /Continuar|Revisando/ }));

async function completar(usuario, numero, { nombre, dni, edad, talla }) {
  const grupo = visitante(numero);
  await usuario.type(grupo.getByLabelText("Nombre"), nombre);
  await usuario.type(grupo.getByLabelText("DNI"), dni);
  await usuario.type(grupo.getByLabelText("Edad"), String(edad));
  if (talla) await usuario.selectOptions(grupo.getByLabelText("Talla"), talla);
}

const rechazoDeDniYEdad = () =>
  falla(422, { motivos: ["visitante_invalido"], visitantes: { 1: ["dni_invalido", "edad_invalida"] } });

describe("PantallaVisitantes", () => {
  it("la cantidad maxima es el cupo restante del turno", () => {
    mostrar(TIROLESA, 3);

    const opciones = within(screen.getByLabelText("Cantidad de personas")).getAllByRole("option");
    expect(opciones.map((o) => o.textContent)).toEqual(["1", "2", "3"]);
    expect(screen.getByText("Quedan 3 lugares en este turno.")).toBeInTheDocument();
  });

  it("nunca ofrece mas de 10 personas por inscripcion, aunque haya mas cupo", () => {
    mostrar(SAFARI, 12);

    const opciones = within(screen.getByLabelText("Cantidad de personas")).getAllByRole("option");
    expect(opciones).toHaveLength(10);
  });

  it("empieza con un visitante y agrega formularios al subir la cantidad", async () => {
    const usuario = userEvent.setup();
    mostrar(SAFARI, 8);

    expect(screen.getAllByRole("group", { name: /^Visitante/ })).toHaveLength(1);
    await usuario.selectOptions(screen.getByLabelText("Cantidad de personas"), "3");

    expect(screen.getAllByRole("group", { name: /^Visitante/ })).toHaveLength(3);
  });

  it("al bajar la cantidad conserva los datos de los visitantes que quedan", async () => {
    const usuario = userEvent.setup();
    mostrar(SAFARI, 8);
    await usuario.selectOptions(screen.getByLabelText("Cantidad de personas"), "2");
    await usuario.type(visitante(1).getByLabelText("Nombre"), "Ana Perez");

    await usuario.selectOptions(screen.getByLabelText("Cantidad de personas"), "1");

    expect(visitante(1).getByLabelText("Nombre")).toHaveValue("Ana Perez");
  });

  it("pide la talla solo si la actividad la requiere", () => {
    const { unmount } = render(
      <PantallaVisitantes
        api={crearApiFalsa()}
        sesion={SESION}
        actividad={TIROLESA}
        fecha="2026-11-04"
        turno={{ hora: "10:00", cupo_restante: 5 }}
        alContinuar={vi.fn()}
        alVolver={vi.fn()}
        alSesionVencida={vi.fn()}
      />,
    );
    expect(visitante(1).getByLabelText("Talla")).toBeInTheDocument();
    unmount();

    mostrar(SAFARI, 5);
    expect(visitante(1).queryByLabelText("Talla")).toBeNull();
  });

  it("informa la edad minima de la actividad", () => {
    mostrar(TIROLESA, 5);

    expect(screen.getByText("Edad mínima de la actividad: 8 años.")).toBeInTheDocument();
  });

  it("si falta algun dato indica de que visitante y no consulta a la API ni continua", async () => {
    const usuario = userEvent.setup();
    const { alContinuar, api } = mostrar(SAFARI, 5);
    await usuario.selectOptions(screen.getByLabelText("Cantidad de personas"), "2");
    await completar(usuario, 1, { nombre: "Luis Gomez", dni: "28123456", edad: 41 });
    await usuario.type(visitante(2).getByLabelText("Nombre"), "Eva Soto");

    await continuar(usuario);

    expect(screen.getByRole("alert")).toHaveTextContent("Completá todos los datos del visitante 2.");
    expect(alContinuar).not.toHaveBeenCalled();
    expect(api.validarInscripcion).not.toHaveBeenCalled();
  });

  it("si la actividad pide talla y no se eligio, no continua", async () => {
    const usuario = userEvent.setup();
    const { alContinuar } = mostrar(TIROLESA, 5);
    await completar(usuario, 1, { nombre: "Ana Perez", dni: "30123456", edad: 30 });

    await continuar(usuario);

    expect(screen.getByRole("alert")).toHaveTextContent("Completá todos los datos del visitante 1.");
    expect(alContinuar).not.toHaveBeenCalled();
  });

  it("permite volver a elegir el horario", async () => {
    const usuario = userEvent.setup();
    const { alVolver } = mostrar(SAFARI, 5);

    await usuario.click(screen.getByRole("button", { name: "Volver" }));

    expect(alVolver).toHaveBeenCalled();
  });
});

describe("PantallaVisitantes: validacion en este mismo paso", () => {
  it("antes de continuar valida los datos con la API y recien entonces avanza (edad como numero)", async () => {
    const usuario = userEvent.setup();
    const { alContinuar, api } = mostrar(TIROLESA, 5);
    const datos = [{ nombre: "Ana Perez", dni: "30123456", edad: 30, talla: "M" }];

    await completar(usuario, 1, { nombre: " Ana Perez ", dni: "30123456", edad: 30, talla: "M" });
    await continuar(usuario);

    await waitFor(() => expect(alContinuar).toHaveBeenCalledWith(datos));
    expect(api.validarInscripcion).toHaveBeenCalledWith(
      { actividad: "Tirolesa", fecha: "2026-11-04", hora: "10:00", visitantes: datos },
      "tok",
    );
  });

  it("en una actividad sin talla no manda la talla", async () => {
    const usuario = userEvent.setup();
    const { alContinuar } = mostrar(SAFARI, 5);

    await completar(usuario, 1, { nombre: "Luis Gomez", dni: "28123456", edad: 41 });
    await continuar(usuario);

    await waitFor(() =>
      expect(alContinuar).toHaveBeenCalledWith([{ nombre: "Luis Gomez", dni: "28123456", edad: 41, talla: null }]),
    );
  });

  it("si la API rechaza los datos, el error aparece aca indicando visitante y motivos, y no avanza", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({ validarInscripcion: vi.fn(async () => rechazoDeDniYEdad()) });
    const { alContinuar } = mostrar(SAFARI, 5, { api });
    await completar(usuario, 1, { nombre: "Eva Soto", dni: "123", edad: 150 });

    await continuar(usuario);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Visitante 1: el DNI debe tener 7 u 8 números sin puntos ni espacios (por ejemplo 30123456), la edad debe ser un número entero entre 0 y 100.",
    );
    expect(alContinuar).not.toHaveBeenCalled();
  });

  it("marca los campos con problema y deja sin marcar los que estan bien", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({ validarInscripcion: vi.fn(async () => rechazoDeDniYEdad()) });
    mostrar(SAFARI, 5, { api });
    await completar(usuario, 1, { nombre: "Eva Soto", dni: "123", edad: 150 });

    await continuar(usuario);
    await screen.findByRole("alert");

    expect(visitante(1).getByLabelText("DNI")).toHaveAttribute("aria-invalid", "true");
    expect(visitante(1).getByLabelText("Edad")).toHaveAttribute("aria-invalid", "true");
    expect(visitante(1).getByLabelText("Nombre")).not.toHaveAttribute("aria-invalid");
  });

  it("conserva lo escrito y al corregir un campo se le quita la marca de error", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({ validarInscripcion: vi.fn(async () => rechazoDeDniYEdad()) });
    mostrar(SAFARI, 5, { api });
    await completar(usuario, 1, { nombre: "Eva Soto", dni: "123", edad: 150 });
    await continuar(usuario);
    await screen.findByRole("alert");

    expect(visitante(1).getByLabelText("DNI")).toHaveValue("123");
    await usuario.type(visitante(1).getByLabelText("DNI"), "45678");

    expect(visitante(1).getByLabelText("DNI")).not.toHaveAttribute("aria-invalid");
    expect(visitante(1).getByLabelText("Edad")).toHaveAttribute("aria-invalid", "true");
  });

  it("despues de corregir se puede volver a continuar y esta vez avanza", async () => {
    const usuario = userEvent.setup();
    const validarInscripcion = vi
      .fn()
      .mockResolvedValueOnce(rechazoDeDniYEdad())
      .mockResolvedValueOnce(ok({ valida: true }));
    const { alContinuar } = mostrar(SAFARI, 5, { api: crearApiFalsa({ validarInscripcion }) });
    await completar(usuario, 1, { nombre: "Eva Soto", dni: "123", edad: 150 });
    await continuar(usuario);
    await screen.findByRole("alert");

    await usuario.clear(visitante(1).getByLabelText("DNI"));
    await usuario.type(visitante(1).getByLabelText("DNI"), "40123456");
    await usuario.clear(visitante(1).getByLabelText("Edad"));
    await usuario.type(visitante(1).getByLabelText("Edad"), "25");
    await continuar(usuario);

    await waitFor(() =>
      expect(alContinuar).toHaveBeenCalledWith([{ nombre: "Eva Soto", dni: "40123456", edad: 25, talla: null }]),
    );
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("tambien muestra los problemas que no son de un visitante, como la falta de cupo", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({ validarInscripcion: vi.fn(async () => falla(409, { motivos: ["sin_cupo"] })) });
    mostrar(SAFARI, 5, { api });
    await completar(usuario, 1, { nombre: "Eva Soto", dni: "40123456", edad: 25 });

    await continuar(usuario);

    expect(await screen.findByRole("alert")).toHaveTextContent("No quedan lugares suficientes en ese horario.");
  });

  it("mientras revisa los datos deshabilita el boton", async () => {
    const usuario = userEvent.setup();
    let responder;
    const api = crearApiFalsa({ validarInscripcion: vi.fn(() => new Promise((resolver) => { responder = resolver; })) });
    mostrar(SAFARI, 5, { api });
    await completar(usuario, 1, { nombre: "Eva Soto", dni: "40123456", edad: 25 });

    await continuar(usuario);

    expect(screen.getByRole("button", { name: /Revisando/ })).toBeDisabled();
    responder(ok({ valida: true }));
  });

  it("si la sesion vencio avisa para volver a iniciar sesion", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      validarInscripcion: vi.fn(async () => falla(401, { motivos: ["usuario_no_registrado"] })),
    });
    const { alSesionVencida } = mostrar(SAFARI, 5, { api });
    await completar(usuario, 1, { nombre: "Eva Soto", dni: "40123456", edad: 25 });

    await continuar(usuario);

    await waitFor(() => expect(alSesionVencida).toHaveBeenCalled());
  });

  it("si se vuelve a este paso, arranca con los datos que ya se habian cargado", () => {
    mostrar(TIROLESA, 5, {
      visitantesIniciales: [
        { nombre: "Ana Perez", dni: "30123456", edad: 30, talla: "M" },
        { nombre: "Luis Gomez", dni: "28123456", edad: 41, talla: "L" },
      ],
    });

    expect(screen.getByLabelText("Cantidad de personas")).toHaveValue("2");
    expect(visitante(1).getByLabelText("Nombre")).toHaveValue("Ana Perez");
    expect(visitante(2).getByLabelText("DNI")).toHaveValue("28123456");
    expect(visitante(2).getByLabelText("Edad")).toHaveValue(41);
    expect(visitante(2).getByLabelText("Talla")).toHaveValue("L");
  });

  it("los datos cargados nunca superan el cupo actual del turno", () => {
    mostrar(SAFARI, 1, {
      visitantesIniciales: [
        { nombre: "Ana Perez", dni: "30123456", edad: 30, talla: null },
        { nombre: "Luis Gomez", dni: "28123456", edad: 41, talla: null },
      ],
    });

    expect(screen.getAllByRole("group", { name: /^Visitante/ })).toHaveLength(1);
  });
});
