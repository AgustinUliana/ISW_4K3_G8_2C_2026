import { describe, expect, it } from "vitest";
import { camposConError } from "./campos";

describe("camposConError", () => {
  it("indica que campos del visitante tienen problema segun los motivos de la API", () => {
    expect(camposConError(["dni_invalido", "edad_invalida"])).toEqual(["dni", "edad"]);
  });

  it("cada campo aparece una sola vez aunque tenga varios motivos", () => {
    expect(camposConError(["dni_requerido", "dni_invalido"])).toEqual(["dni"]);
  });

  it("reconoce los motivos del nombre, la edad y la talla", () => {
    expect(camposConError(["nombre_invalido"])).toEqual(["nombre"]);
    expect(camposConError(["edad_no_permitida"])).toEqual(["edad"]);
    expect(camposConError(["talla_requerida"])).toEqual(["talla"]);
  });

  it("ignora los motivos que no son de un campo concreto", () => {
    expect(camposConError(["sin_cupo", "algo_nuevo"])).toEqual([]);
  });
});
