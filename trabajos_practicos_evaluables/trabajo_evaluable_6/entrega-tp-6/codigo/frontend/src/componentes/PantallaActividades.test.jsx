import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ACTIVIDADES, crearApiFalsa, falla, ok } from "../test/apiFalsa";
import { PantallaActividades } from "./PantallaActividades";

const tarjeta = (nombre) => screen.getByRole("article", { name: nombre });

describe("PantallaActividades", () => {
  it("lista las actividades con sus requisitos", async () => {
    render(<PantallaActividades api={crearApiFalsa()} alElegir={vi.fn()} />);

    expect(await screen.findByRole("heading", { name: "Tirolesa" })).toBeInTheDocument();
    expect(within(tarjeta("Tirolesa")).getByText("Desde 8 años")).toBeInTheDocument();
    expect(within(tarjeta("Tirolesa")).getByText("Requiere talla de vestimenta")).toBeInTheDocument();
    expect(within(tarjeta("Tirolesa")).getByText("Hasta 10 personas por turno")).toBeInTheDocument();
    expect(within(tarjeta("Safari")).getByText("Todas las edades")).toBeInTheDocument();
    expect(within(tarjeta("Safari")).queryByText("Requiere talla de vestimenta")).toBeNull();
  });

  it("mientras carga muestra un aviso", () => {
    render(<PantallaActividades api={crearApiFalsa({ actividades: () => new Promise(() => {}) })} alElegir={vi.fn()} />);

    expect(screen.getByText("Cargando actividades…")).toBeInTheDocument();
  });

  it("al elegir una actividad avisa cual", async () => {
    const usuario = userEvent.setup();
    const alElegir = vi.fn();
    render(<PantallaActividades api={crearApiFalsa()} alElegir={alElegir} />);

    await screen.findByRole("heading", { name: "Safari" });
    await usuario.click(within(tarjeta("Safari")).getByRole("button", { name: "Elegir" }));

    expect(alElegir).toHaveBeenCalledWith(ACTIVIDADES[1]);
  });

  it("una actividad sin turnos disponibles no se puede elegir", async () => {
    render(<PantallaActividades api={crearApiFalsa()} alElegir={vi.fn()} />);

    await screen.findByRole("heading", { name: "Palestra" });

    expect(within(tarjeta("Palestra")).getByRole("button", { name: "Elegir" })).toBeDisabled();
    expect(within(tarjeta("Palestra")).getByText("Sin turnos disponibles")).toBeInTheDocument();
  });

  it("si falla la carga avisa y permite reintentar", async () => {
    const usuario = userEvent.setup();
    const actividades = vi
      .fn()
      .mockResolvedValueOnce(falla(0, { motivos: ["sin_conexion"] }))
      .mockResolvedValueOnce({ ok: true, estado: 200, datos: ACTIVIDADES });
    render(<PantallaActividades api={crearApiFalsa({ actividades })} alElegir={vi.fn()} />);

    expect(await screen.findByRole("alert")).toHaveTextContent(/no pudimos conectarnos/i);
    await usuario.click(screen.getByRole("button", { name: "Reintentar" }));

    expect(await screen.findByRole("heading", { name: "Tirolesa" })).toBeInTheDocument();
  });

  it("cada tarjeta muestra la ilustracion de su actividad", async () => {
    render(<PantallaActividades api={crearApiFalsa()} alElegir={vi.fn()} />);

    await screen.findByRole("heading", { name: "Tirolesa" });

    for (const [nombre, archivo] of [
      ["Tirolesa", "tirolesa"],
      ["Safari", "safari"],
      ["Palestra", "palestra"],
      ["Jardinería", "jardineria"],
    ]) {
      const imagen = within(tarjeta(nombre)).getByRole("img", { name: `Ilustración de la actividad ${nombre}` });
      expect(imagen).toHaveAttribute("src", `/actividades/${archivo}.svg`);
    }
  });

  it("una actividad sin ilustracion se muestra igual, sin imagen", async () => {
    const nueva = { nombre: "Rafting", requiere_talla: false, edad_minima: 0, cupo_por_turno: 6, disponible: true };
    render(<PantallaActividades api={crearApiFalsa({ actividades: async () => ok([nueva]) })} alElegir={vi.fn()} />);

    await screen.findByRole("heading", { name: "Rafting" });

    expect(within(tarjeta("Rafting")).queryByRole("img")).toBeNull();
  });
});
