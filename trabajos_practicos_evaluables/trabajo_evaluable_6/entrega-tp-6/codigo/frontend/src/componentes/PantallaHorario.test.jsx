import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ACTIVIDADES, crearApiFalsa, falla, ok } from "../test/apiFalsa";
import { PantallaHorario } from "./PantallaHorario";

const TIROLESA = ACTIVIDADES[0];
const MIERCOLES_10HS = new Date(2026, 10, 4, 10, 0);

function mostrar(api = crearApiFalsa(), props = {}) {
  const alElegir = vi.fn();
  const alVolver = vi.fn();
  render(
    <PantallaHorario
      api={api}
      actividad={TIROLESA}
      ahora={MIERCOLES_10HS}
      alElegir={alElegir}
      alVolver={alVolver}
      {...props}
    />,
  );
  return { alElegir, alVolver };
}

describe("PantallaHorario", () => {
  it("ofrece los proximos dias y deshabilita los que no se pueden elegir, con el motivo", async () => {
    mostrar();

    await screen.findByRole("button", { name: /^10:00/ });
    expect(screen.getByRole("button", { name: /^mié 4\/11/ })).toBeEnabled();
    expect(screen.getByRole("button", { name: /^jue 5\/11/ })).toBeEnabled();
    expect(screen.getByRole("button", { name: /^vie 6\/11/ })).toBeDisabled();
    expect(screen.getByRole("button", { name: /^vie 6\/11/ })).toHaveTextContent("Aún no disponible");
    expect(screen.getByRole("button", { name: /^lun 9\/11/ })).toBeDisabled();
    expect(screen.getByRole("button", { name: /^lun 9\/11/ })).toHaveTextContent("Cerrado");
  });

  it("carga los horarios del primer dia elegible y muestra el cupo restante", async () => {
    const api = crearApiFalsa();
    mostrar(api);

    expect(await screen.findByRole("button", { name: /^10:00/ })).toHaveTextContent("Quedan 7 lugares");
    expect(api.horarios).toHaveBeenCalledWith("Tirolesa", "2026-11-04");
    expect(screen.getByRole("button", { name: /^12:00/ })).toHaveTextContent("Queda 1 lugar");
  });

  it("un horario agotado figura deshabilitado", async () => {
    mostrar();

    const agotado = await screen.findByRole("button", { name: /^11:00/ });

    expect(agotado).toBeDisabled();
    expect(agotado).toHaveTextContent("Agotado");
  });

  it("al elegir un horario avisa el dia y el turno", async () => {
    const usuario = userEvent.setup();
    const { alElegir } = mostrar();

    await usuario.click(await screen.findByRole("button", { name: /^10:00/ }));

    expect(alElegir).toHaveBeenCalledWith({
      fecha: "2026-11-04",
      turno: { hora: "10:00", cupo_restante: 7, agotado: false },
    });
  });

  it("al cambiar de dia pide los horarios de ese dia", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa();
    mostrar(api);

    await screen.findByRole("button", { name: /^10:00/ });
    await usuario.click(screen.getByRole("button", { name: /^jue 5\/11/ }));

    expect(api.horarios).toHaveBeenLastCalledWith("Tirolesa", "2026-11-05");
  });

  it("si el dia no tiene turnos lo dice", async () => {
    const api = crearApiFalsa({ horarios: vi.fn(async () => ok({ turnos: [] })) });
    mostrar(api);

    expect(await screen.findByText("No quedan turnos para este día.")).toBeInTheDocument();
  });

  it("si falla la carga muestra el motivo", async () => {
    const api = crearApiFalsa({ horarios: vi.fn(async () => falla(0, { motivos: ["sin_conexion"] })) });
    mostrar(api);

    expect(await screen.findByRole("alert")).toHaveTextContent(/no pudimos conectarnos/i);
  });

  it("permite volver a elegir otra actividad", async () => {
    const usuario = userEvent.setup();
    const { alVolver } = mostrar();

    await usuario.click(screen.getByRole("button", { name: "Volver" }));

    expect(alVolver).toHaveBeenCalled();
  });
});
