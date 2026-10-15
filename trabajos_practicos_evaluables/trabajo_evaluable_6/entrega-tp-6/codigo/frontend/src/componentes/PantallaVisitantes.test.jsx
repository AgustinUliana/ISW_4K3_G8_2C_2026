import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ACTIVIDADES } from "../test/apiFalsa";
import { PantallaVisitantes } from "./PantallaVisitantes";

const TIROLESA = ACTIVIDADES[0]; // pide talla, desde 8 años
const SAFARI = ACTIVIDADES[1]; // no pide talla

function mostrar(actividad, cupoRestante) {
  const alContinuar = vi.fn();
  const alVolver = vi.fn();
  render(
    <PantallaVisitantes
      actividad={actividad}
      fecha="2026-11-04"
      turno={{ hora: "10:00", cupo_restante: cupoRestante, agotado: false }}
      alContinuar={alContinuar}
      alVolver={alVolver}
    />,
  );
  return { alContinuar, alVolver };
}

const visitante = (numero) => within(screen.getByRole("group", { name: `Visitante ${numero}` }));

async function completar(usuario, numero, { nombre, dni, edad, talla }) {
  const grupo = visitante(numero);
  await usuario.type(grupo.getByLabelText("Nombre"), nombre);
  await usuario.type(grupo.getByLabelText("DNI"), dni);
  await usuario.type(grupo.getByLabelText("Edad"), String(edad));
  if (talla) await usuario.selectOptions(grupo.getByLabelText("Talla"), talla);
}

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
      <PantallaVisitantes actividad={TIROLESA} fecha="2026-11-04" turno={{ hora: "10:00", cupo_restante: 5 }} alContinuar={vi.fn()} alVolver={vi.fn()} />,
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

  it("al continuar entrega los datos de los visitantes (edad como numero)", async () => {
    const usuario = userEvent.setup();
    const { alContinuar } = mostrar(TIROLESA, 5);

    await completar(usuario, 1, { nombre: " Ana Perez ", dni: "30123456", edad: 30, talla: "M" });
    await usuario.click(screen.getByRole("button", { name: "Continuar" }));

    expect(alContinuar).toHaveBeenCalledWith([{ nombre: "Ana Perez", dni: "30123456", edad: 30, talla: "M" }]);
  });

  it("en una actividad sin talla no manda la talla", async () => {
    const usuario = userEvent.setup();
    const { alContinuar } = mostrar(SAFARI, 5);

    await completar(usuario, 1, { nombre: "Luis Gomez", dni: "28123456", edad: 41 });
    await usuario.click(screen.getByRole("button", { name: "Continuar" }));

    expect(alContinuar).toHaveBeenCalledWith([{ nombre: "Luis Gomez", dni: "28123456", edad: 41, talla: null }]);
  });

  it("si falta algun dato indica de que visitante y no continua", async () => {
    const usuario = userEvent.setup();
    const { alContinuar } = mostrar(SAFARI, 5);
    await usuario.selectOptions(screen.getByLabelText("Cantidad de personas"), "2");
    await completar(usuario, 1, { nombre: "Luis Gomez", dni: "28123456", edad: 41 });
    await usuario.type(visitante(2).getByLabelText("Nombre"), "Eva Soto");

    await usuario.click(screen.getByRole("button", { name: "Continuar" }));

    expect(screen.getByRole("alert")).toHaveTextContent("Completá todos los datos del visitante 2.");
    expect(alContinuar).not.toHaveBeenCalled();
  });

  it("si la actividad pide talla y no se eligio, no continua", async () => {
    const usuario = userEvent.setup();
    const { alContinuar } = mostrar(TIROLESA, 5);
    await completar(usuario, 1, { nombre: "Ana Perez", dni: "30123456", edad: 30 });

    await usuario.click(screen.getByRole("button", { name: "Continuar" }));

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
