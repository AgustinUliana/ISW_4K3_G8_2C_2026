import { describe, expect, it } from "vitest";
import { camposConError, mensajesPorCampo } from "./campos";

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

describe("mensajesPorCampo", () => {
  it("da un mensaje por campo, con el formato esperado", () => {
    expect(mensajesPorCampo(["dni_invalido", "edad_invalida"])).toEqual({
      dni: "El DNI debe tener 7 u 8 números sin puntos ni espacios (por ejemplo 30123456).",
      edad: "La edad debe ser un número entero entre 0 y 100.",
    });
  });

  it("si un campo tiene varios motivos usa el primero", () => {
    expect(mensajesPorCampo(["dni_requerido", "dni_invalido"])).toEqual({ dni: "Falta el DNI (7 u 8 números)." });
  });

  it("usa el contexto para la edad minima", () => {
    expect(mensajesPorCampo(["edad_no_permitida"], { edadMinima: 8 })).toEqual({
      edad: "No alcanza la edad mínima: la actividad es desde los 8 años.",
    });
  });

  it("reconoce los campos del acceso y no duplica el punto final", () => {
    expect(mensajesPorCampo(["email_invalido", "contrasena_invalida"])).toEqual({
      email: "El email no es válido. Escribilo con el formato nombre@dominio.com.",
      contrasena: "La contraseña es demasiado corta: tiene que tener al menos 6 caracteres.",
    });
  });

  it("ignora los motivos que no son de un campo", () => {
    expect(mensajesPorCampo(["sin_cupo"])).toEqual({});
  });
});
