import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Vidrio } from "./Vidrio";

// La libreria se reemplaza por un doble que deja ver con que props la usamos.
vi.mock("liquid-glass-react", () => ({
  default: ({ children, cornerRadius, elasticity, padding, displacementScale, style }) => (
    <div
      data-testid="liquid-glass"
      data-radio={cornerRadius}
      data-elasticidad={elasticity}
      data-relleno={padding}
      data-refraccion={displacementScale}
      data-style={JSON.stringify(style)}
    >
      {children}
    </div>
  ),
}));

afterEach(() => {
  vi.unstubAllGlobals();
  delete HTMLElement.prototype.offsetWidth;
  delete HTMLElement.prototype.offsetHeight;
});

function simularNavegadorConMedicion({ ancho, alto }) {
  vi.stubGlobal(
    "ResizeObserver",
    class {
      constructor(alCambiar) {
        this.alCambiar = alCambiar;
      }
      observe() {
        this.alCambiar([]);
      }
      disconnect() {}
    },
  );
  Object.defineProperty(HTMLElement.prototype, "offsetWidth", { configurable: true, get: () => ancho });
  Object.defineProperty(HTMLElement.prototype, "offsetHeight", { configurable: true, get: () => alto });
}

describe("Vidrio", () => {
  it("muestra su contenido", () => {
    render(
      <Vidrio>
        <p>Hola desde el vidrio</p>
      </Vidrio>,
    );

    expect(screen.getByText("Hola desde el vidrio")).toBeInTheDocument();
  });

  it("deja ponerle una clase para darle estilo", () => {
    const { container } = render(
      <Vidrio className="panel">
        <p>contenido</p>
      </Vidrio>,
    );

    expect(container.querySelector(".vidrio.panel")).not.toBeNull();
  });

  it("si se le pasa alClick, responde al click como un boton", async () => {
    const alClick = vi.fn();
    render(
      <Vidrio alClick={alClick}>
        <span>Tocar</span>
      </Vidrio>,
    );

    await userEvent.click(screen.getByText("Tocar"));

    expect(alClick).toHaveBeenCalledTimes(1);
  });

  it("si el navegador no puede medir (sin ResizeObserver) igual muestra el contenido, sin la capa", () => {
    render(
      <Vidrio>
        <p>contenido</p>
      </Vidrio>,
    );

    expect(screen.queryByTestId("liquid-glass")).toBeNull();
    expect(screen.getByText("contenido")).toBeInTheDocument();
  });

  it("dibuja la capa de vidrio del mismo tamaño que el contenido, detras de el", () => {
    simularNavegadorConMedicion({ ancho: 300, alto: 120 });
    const { container } = render(
      <Vidrio radio={28}>
        <p>contenido</p>
      </Vidrio>,
    );

    const vidrio = screen.getByTestId("liquid-glass");
    expect(vidrio.firstChild).toHaveStyle({ width: "300px", height: "120px" });
    expect(vidrio).toHaveAttribute("data-radio", "28");
    expect(JSON.parse(vidrio.dataset.style)).toMatchObject({ position: "absolute", top: "50%", left: "50%" });
    expect(container.querySelector(".vidrio-capa")).toHaveAttribute("aria-hidden", "true");
  });

  it("la capa no se mueve con el mouse: la elasticidad es 0 salvo que se pida", () => {
    simularNavegadorConMedicion({ ancho: 200, alto: 80 });
    render(
      <Vidrio>
        <p>contenido</p>
      </Vidrio>,
    );

    expect(screen.getByTestId("liquid-glass")).toHaveAttribute("data-elasticidad", "0");
  });

  it("no le suma relleno propio a la libreria: si no, el vidrio quedaria mas grande que el panel", () => {
    simularNavegadorConMedicion({ ancho: 300, alto: 120 });
    render(
      <Vidrio>
        <p>contenido</p>
      </Vidrio>,
    );

    expect(screen.getByTestId("liquid-glass")).toHaveAttribute("data-relleno", "0px");
  });

  it("la intensidad de la refraccion es configurable: los paneles grandes la piden mas suave", () => {
    simularNavegadorConMedicion({ ancho: 800, alto: 400 });
    render(
      <Vidrio refraccion={24}>
        <p>contenido</p>
      </Vidrio>,
    );

    expect(screen.getByTestId("liquid-glass")).toHaveAttribute("data-refraccion", "24");
  });

  it("sin indicarla usa una refraccion moderada por defecto", () => {
    simularNavegadorConMedicion({ ancho: 200, alto: 80 });
    render(
      <Vidrio>
        <p>contenido</p>
      </Vidrio>,
    );

    expect(screen.getByTestId("liquid-glass")).toHaveAttribute("data-refraccion", "40");
  });
});
