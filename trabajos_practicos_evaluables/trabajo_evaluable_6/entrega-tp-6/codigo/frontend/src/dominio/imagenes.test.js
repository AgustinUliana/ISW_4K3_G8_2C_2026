import { describe, expect, it } from "vitest";
import { imagenDeActividad } from "./imagenes";

describe("imagenDeActividad", () => {
  it("cada actividad del parque tiene su ilustracion", () => {
    expect(imagenDeActividad("Tirolesa")).toBe("/actividades/tirolesa.svg");
    expect(imagenDeActividad("Safari")).toBe("/actividades/safari.svg");
    expect(imagenDeActividad("Palestra")).toBe("/actividades/palestra.svg");
  });

  it("el archivo no lleva tildes aunque el nombre si", () => {
    expect(imagenDeActividad("Jardinería")).toBe("/actividades/jardineria.svg");
  });

  it("una actividad sin ilustracion devuelve null", () => {
    expect(imagenDeActividad("Rafting")).toBeNull();
  });
});
