import { describe, expect, it } from "vitest";
import { mensajeDeMotivo, mensajesDeRechazo } from "./mensajes";

describe("mensajeDeMotivo", () => {
  it("traduce los motivos que devuelve la API a frases para el visitante", () => {
    expect(mensajeDeMotivo("sin_cupo")).toBe("No quedan lugares suficientes en ese horario.");
    expect(mensajeDeMotivo("credenciales_invalidas")).toBe("El email o la contraseña no son correctos.");
    expect(mensajeDeMotivo("email_ya_registrado")).toBe("Ese email ya está registrado. Iniciá sesión.");
  });

  it("si el motivo no se conoce, da un mensaje generico en lugar de mostrar el codigo", () => {
    expect(mensajeDeMotivo("algo_nuevo")).toBe("No se pudo completar la operación. Probá de nuevo.");
  });

  it("explica que sin el email no se confirma la inscripcion", () => {
    expect(mensajeDeMotivo("email_no_enviado")).toMatch(/no pudimos enviar el email/i);
  });
});

describe("mensajesDeRechazo", () => {
  it("devuelve una frase por cada motivo", () => {
    expect(mensajesDeRechazo({ motivos: ["sin_cupo", "terminos_no_aceptados"] })).toEqual([
      "No quedan lugares suficientes en ese horario.",
      "Tenés que aceptar los términos y condiciones.",
    ]);
  });

  it("en lugar del aviso general de visitante invalido, indica cual visitante y que le falta", () => {
    const cuerpo = { motivos: ["visitante_invalido"], visitantes: { 2: ["dni_requerido", "talla_requerida"] } };

    expect(mensajesDeRechazo(cuerpo)).toEqual(["Visitante 2: falta el DNI, falta elegir la talla."]);
  });

  it("tolera una respuesta sin motivos", () => {
    expect(mensajesDeRechazo({})).toEqual(["No se pudo completar la operación. Probá de nuevo."]);
  });
});
