import { describe, expect, it } from "vitest";
import { mensajeDeMotivo, mensajesDeRechazo } from "./mensajes";

describe("mensajeDeMotivo", () => {
  it("traduce los motivos que devuelve la API a frases para el visitante", () => {
    expect(mensajeDeMotivo("sin_cupo")).toBe("No quedan lugares suficientes en ese horario.");
    expect(mensajeDeMotivo("credenciales_invalidas")).toBe("El email o la contraseña no son correctos. Revisá que estén bien escritos.");
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

    expect(mensajesDeRechazo(cuerpo)).toEqual([
      "Visitante 2: falta el DNI (7 u 8 números), falta elegir la talla (XS, S, M, L, XL o XXL).",
    ]);
  });

  it("tolera una respuesta sin motivos", () => {
    expect(mensajesDeRechazo({})).toEqual(["No se pudo completar la operación. Probá de nuevo."]);
  });
});

describe("sin conexion", () => {
  it("avisa que no se pudo conectar con el servidor", () => {
    expect(mensajeDeMotivo("sin_conexion")).toMatch(/no pudimos conectarnos con el servidor/i);
  });
});

describe("mensajes que explican el formato esperado", () => {
  it("el email indica la forma de escribirlo", () => {
    expect(mensajeDeMotivo("email_invalido")).toBe("El email no es válido. Escribilo con el formato nombre@dominio.com.");
  });

  it("la contraseña dice cuanto le falta", () => {
    expect(mensajeDeMotivo("contrasena_invalida")).toBe(
      "La contraseña es demasiado corta: tiene que tener al menos 6 caracteres.",
    );
  });

  it("el DNI explica la cantidad de digitos y da un ejemplo", () => {
    expect(mensajeDeMotivo("dni_invalido")).toBe(
      "el DNI debe tener 7 u 8 números sin puntos ni espacios (por ejemplo 30123456)",
    );
    expect(mensajeDeMotivo("dni_requerido")).toBe("falta el DNI (7 u 8 números)");
  });

  it("la edad pide un numero entero dentro del rango", () => {
    expect(mensajeDeMotivo("edad_invalida")).toBe("la edad debe ser un número entero entre 0 y 100");
  });

  it("el nombre dice que caracteres admite", () => {
    expect(mensajeDeMotivo("nombre_invalido")).toBe(
      "el nombre solo admite letras, espacios, apóstrofes y guiones (hasta 30 caracteres)",
    );
    expect(mensajeDeMotivo("nombre_requerido")).toBe("falta el nombre y apellido");
  });

  it("la talla lista las opciones", () => {
    expect(mensajeDeMotivo("talla_requerida")).toBe("falta elegir la talla (XS, S, M, L, XL o XXL)");
    expect(mensajeDeMotivo("talla_invalida")).toBe("la talla no es válida: elegí una de la lista");
  });

  it("un DNI repetido explica que cada visitante necesita uno distinto", () => {
    expect(mensajeDeMotivo("dni_duplicado")).toBe(
      "Hay un DNI repetido en la inscripción: cada visitante necesita un DNI distinto.",
    );
  });

  it("la edad minima dice cual es cuando se conoce la actividad", () => {
    expect(mensajeDeMotivo("edad_no_permitida", { edadMinima: 8 })).toBe(
      "no alcanza la edad mínima: la actividad es desde los 8 años",
    );
    expect(mensajeDeMotivo("edad_no_permitida")).toBe("no alcanza la edad mínima de la actividad");
  });

  it("mensajesDeRechazo pasa el contexto a cada motivo", () => {
    const cuerpo = { motivos: ["visitante_invalido"], visitantes: { 1: ["edad_no_permitida"] } };

    expect(mensajesDeRechazo(cuerpo, { edadMinima: 12 })).toEqual([
      "Visitante 1: no alcanza la edad mínima: la actividad es desde los 12 años.",
    ]);
  });
});
