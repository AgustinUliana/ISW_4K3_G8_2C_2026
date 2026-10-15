import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Vidrio } from "./Vidrio";

describe("Vidrio", () => {
  it("muestra su contenido dentro del vidrio", () => {
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

    expect(container.querySelector(".panel")).not.toBeNull();
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
});
