import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { crearApiFalsa, falla, ok } from "../test/apiFalsa";
import { PantallaAcceso } from "./PantallaAcceso";

async function completar(usuario, email, contrasena) {
  await usuario.type(screen.getByLabelText("Email"), email);
  await usuario.type(screen.getByLabelText("Contraseña"), contrasena);
}

describe("PantallaAcceso", () => {
  it("inicia sesion con el email y la contraseña y avisa quien entro", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa();
    const alEntrar = vi.fn();
    render(<PantallaAcceso api={api} alEntrar={alEntrar} />);

    await completar(usuario, "ana@example.com", "secreto1");
    await usuario.click(screen.getByRole("button", { name: "Iniciar sesión" }));

    expect(api.iniciarSesion).toHaveBeenCalledWith("ana@example.com", "secreto1");
    expect(alEntrar).toHaveBeenCalledWith({ token: "token-de-prueba", email: "ana@example.com" });
  });

  it("si las credenciales son incorrectas muestra el motivo y no entra", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      iniciarSesion: vi.fn(async () => falla(401, { motivos: ["credenciales_invalidas"] })),
    });
    const alEntrar = vi.fn();
    render(<PantallaAcceso api={api} alEntrar={alEntrar} />);

    await completar(usuario, "ana@example.com", "mala");
    await usuario.click(screen.getByRole("button", { name: "Iniciar sesión" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("El email o la contraseña no son correctos.");
    expect(alEntrar).not.toHaveBeenCalled();
  });

  it("crear cuenta registra al usuario y despues inicia sesion", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa();
    const alEntrar = vi.fn();
    render(<PantallaAcceso api={api} alEntrar={alEntrar} />);

    await usuario.click(screen.getByRole("tab", { name: "Crear cuenta" }));
    await completar(usuario, "Nueva@Example.com", "secreto1");
    await usuario.click(screen.getByRole("button", { name: "Crear cuenta" }));

    expect(api.registrar).toHaveBeenCalledWith("Nueva@Example.com", "secreto1");
    expect(api.iniciarSesion).toHaveBeenCalledWith("Nueva@Example.com", "secreto1");
    expect(alEntrar).toHaveBeenCalledWith({ token: "token-de-prueba", email: "nueva@example.com" });
  });

  it("si el email ya esta registrado lo dice y no inicia sesion", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      registrar: vi.fn(async () => falla(409, { motivos: ["email_ya_registrado"] })),
    });
    render(<PantallaAcceso api={api} alEntrar={vi.fn()} />);

    await usuario.click(screen.getByRole("tab", { name: "Crear cuenta" }));
    await completar(usuario, "ana@example.com", "secreto1");
    await usuario.click(screen.getByRole("button", { name: "Crear cuenta" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Ese email ya está registrado. Iniciá sesión.");
    expect(api.iniciarSesion).not.toHaveBeenCalled();
  });

  it("muestra todos los motivos si los datos del registro no son validos", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      registrar: vi.fn(async () => falla(422, { motivos: ["email_invalido", "contrasena_invalida"] })),
    });
    render(<PantallaAcceso api={api} alEntrar={vi.fn()} />);

    await usuario.click(screen.getByRole("tab", { name: "Crear cuenta" }));
    await completar(usuario, "ana", "123");
    await usuario.click(screen.getByRole("button", { name: "Crear cuenta" }));

    const aviso = await screen.findByRole("alert");
    expect(aviso).toHaveTextContent("El email no es válido.");
    expect(aviso).toHaveTextContent("La contraseña es demasiado corta: tiene que tener al menos 6 caracteres.");
  });

  it("mientras espera la respuesta deshabilita el boton para no enviar dos veces", async () => {
    const usuario = userEvent.setup();
    let responder;
    const api = crearApiFalsa({
      iniciarSesion: vi.fn(() => new Promise((resolver) => { responder = resolver; })),
    });
    render(<PantallaAcceso api={api} alEntrar={vi.fn()} />);

    await completar(usuario, "ana@example.com", "secreto1");
    await usuario.click(screen.getByRole("button", { name: "Iniciar sesión" }));

    expect(screen.getByRole("button", { name: /Ingresando/ })).toBeDisabled();
    responder(ok({ token: "t" }));
  });

  it("si no hay conexion avisa que no se pudo contactar al servidor", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      iniciarSesion: vi.fn(async () => falla(0, { motivos: ["sin_conexion"] })),
    });
    render(<PantallaAcceso api={api} alEntrar={vi.fn()} />);

    await completar(usuario, "ana@example.com", "secreto1");
    await usuario.click(screen.getByRole("button", { name: "Iniciar sesión" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/no pudimos conectarnos con el servidor/i);
  });
});

describe("PantallaAcceso con aviso", () => {
  it("muestra el aviso que se le pasa, por ejemplo cuando la sesion vencio", () => {
    render(<PantallaAcceso api={crearApiFalsa()} alEntrar={vi.fn()} aviso="Tu sesión venció." />);

    expect(screen.getByRole("status")).toHaveTextContent("Tu sesión venció.");
  });

  it("marca el campo con problema y explica el formato debajo", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      registrar: vi.fn(async () => falla(422, { motivos: ["email_invalido", "contrasena_invalida"] })),
    });
    render(<PantallaAcceso api={api} alEntrar={vi.fn()} />);
    await usuario.click(screen.getByRole("tab", { name: "Crear cuenta" }));
    await completar(usuario, "ana", "123");

    await usuario.click(screen.getByRole("button", { name: "Crear cuenta" }));
    await screen.findByRole("alert");

    const email = screen.getByLabelText("Email");
    const contrasena = screen.getByLabelText("Contraseña");
    expect(email).toHaveAttribute("aria-invalid", "true");
    expect(email).toHaveAccessibleDescription("El email no es válido. Escribilo con el formato nombre@dominio.com.");
    expect(contrasena).toHaveAttribute("aria-invalid", "true");
    expect(contrasena).toHaveAccessibleDescription(
      "La contraseña es demasiado corta: tiene que tener al menos 6 caracteres.",
    );
  });

  it("al corregir un campo se le quita la marca y el otro la conserva", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      registrar: vi.fn(async () => falla(422, { motivos: ["email_invalido", "contrasena_invalida"] })),
    });
    render(<PantallaAcceso api={api} alEntrar={vi.fn()} />);
    await usuario.click(screen.getByRole("tab", { name: "Crear cuenta" }));
    await completar(usuario, "ana", "123");
    await usuario.click(screen.getByRole("button", { name: "Crear cuenta" }));
    await screen.findByRole("alert");

    await usuario.type(screen.getByLabelText("Email"), "@example.com");

    expect(screen.getByLabelText("Email")).not.toHaveAttribute("aria-invalid");
    expect(screen.getByLabelText("Contraseña")).toHaveAttribute("aria-invalid", "true");
  });

  it("si las credenciales no coinciden no marca ningun campo", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      iniciarSesion: vi.fn(async () => falla(401, { motivos: ["credenciales_invalidas"] })),
    });
    render(<PantallaAcceso api={api} alEntrar={vi.fn()} />);
    await completar(usuario, "ana@example.com", "equivocada");

    await usuario.click(screen.getByRole("button", { name: "Iniciar sesión" }));
    await screen.findByRole("alert");

    expect(screen.getByLabelText("Email")).not.toHaveAttribute("aria-invalid");
    expect(screen.getByLabelText("Contraseña")).not.toHaveAttribute("aria-invalid");
  });

  it("si el email ya esta registrado lo marca en el campo del email", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      registrar: vi.fn(async () => falla(409, { motivos: ["email_ya_registrado"] })),
    });
    render(<PantallaAcceso api={api} alEntrar={vi.fn()} />);
    await usuario.click(screen.getByRole("tab", { name: "Crear cuenta" }));
    await completar(usuario, "ana@example.com", "secreto1");

    await usuario.click(screen.getByRole("button", { name: "Crear cuenta" }));
    await screen.findByRole("alert");

    expect(screen.getByLabelText("Email")).toHaveAccessibleDescription("Ese email ya está registrado. Iniciá sesión.");
  });

  it("la contraseña empieza oculta y el ojo la muestra y la vuelve a ocultar", async () => {
    const usuario = userEvent.setup();
    render(<PantallaAcceso api={crearApiFalsa()} alEntrar={vi.fn()} />);
    await usuario.type(screen.getByLabelText("Contraseña"), "secreto1");

    expect(screen.getByLabelText("Contraseña")).toHaveAttribute("type", "password");

    await usuario.click(screen.getByRole("button", { name: "Mostrar la contraseña" }));

    expect(screen.getByLabelText("Contraseña")).toHaveAttribute("type", "text");
    expect(screen.getByLabelText("Contraseña")).toHaveValue("secreto1");
    const ocultar = screen.getByRole("button", { name: "Ocultar la contraseña" });
    expect(ocultar).toHaveAttribute("aria-pressed", "true");

    await usuario.click(ocultar);

    expect(screen.getByLabelText("Contraseña")).toHaveAttribute("type", "password");
  });

  it("el ojo tambien esta al crear la cuenta y vuelve a ocultar la contraseña al cambiar de pestaña", async () => {
    const usuario = userEvent.setup();
    render(<PantallaAcceso api={crearApiFalsa()} alEntrar={vi.fn()} />);

    await usuario.click(screen.getByRole("tab", { name: "Crear cuenta" }));
    await usuario.click(screen.getByRole("button", { name: "Mostrar la contraseña" }));
    expect(screen.getByLabelText("Contraseña")).toHaveAttribute("type", "text");

    await usuario.click(screen.getByRole("tab", { name: "Iniciar sesión" }));

    expect(screen.getByLabelText("Contraseña")).toHaveAttribute("type", "password");
  });

  it("tocar el ojo no envia el formulario", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa();
    render(<PantallaAcceso api={api} alEntrar={vi.fn()} />);
    await completar(usuario, "ana@example.com", "secreto1");

    await usuario.click(screen.getByRole("button", { name: "Mostrar la contraseña" }));

    expect(api.iniciarSesion).not.toHaveBeenCalled();
  });
});
