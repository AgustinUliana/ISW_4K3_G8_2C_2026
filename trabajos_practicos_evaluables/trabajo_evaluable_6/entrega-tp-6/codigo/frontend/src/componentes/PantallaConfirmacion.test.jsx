import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ACTIVIDADES, crearApiFalsa, falla, ok } from "../test/apiFalsa";
import { PantallaConfirmacion } from "./PantallaConfirmacion";
import { PantallaListo } from "./PantallaListo";

const TIROLESA = ACTIVIDADES[0];
const VISITANTES = [
  { nombre: "Ana Perez", dni: "30123456", edad: 30, talla: "M" },
  { nombre: "Luis Gomez", dni: "28123456", edad: 41, talla: "L" },
];

function mostrar(api = crearApiFalsa()) {
  const alInscripto = vi.fn();
  const alVolver = vi.fn();
  const alSesionVencida = vi.fn();
  render(
    <PantallaConfirmacion
      api={api}
      sesion={{ token: "tok", email: "ana@example.com" }}
      actividad={TIROLESA}
      fecha="2026-11-04"
      turno={{ hora: "10:00", cupo_restante: 7, agotado: false }}
      visitantes={VISITANTES}
      alInscripto={alInscripto}
      alVolver={alVolver}
      alSesionVencida={alSesionVencida}
    />,
  );
  return { api, alInscripto, alVolver, alSesionVencida };
}

const botonConfirmar = () => screen.getByRole("button", { name: "Confirmar inscripción" });

describe("PantallaConfirmacion", () => {
  it("muestra los terminos y condiciones propios de la actividad", async () => {
    const { api } = mostrar();

    expect(await screen.findByText("Texto de los términos de Tirolesa.")).toBeInTheDocument();
    expect(api.terminos).toHaveBeenCalledWith("Tirolesa");
    expect(screen.getByRole("heading", { name: "Términos y condiciones de Tirolesa" })).toBeInTheDocument();
  });

  it("resume la inscripcion y dice a que email llegan los QR", async () => {
    mostrar();
    await screen.findByText("Texto de los términos de Tirolesa.");

    const resumen = screen.getByRole("region", { name: "Resumen de tu inscripción" });
    expect(resumen).toHaveTextContent("Tirolesa");
    expect(resumen).toHaveTextContent("04/11/2026");
    expect(resumen).toHaveTextContent("10:00");
    expect(resumen).toHaveTextContent("2 personas");
    expect(resumen).toHaveTextContent("Ana Perez");
    expect(resumen).toHaveTextContent("Luis Gomez");
    expect(resumen).toHaveTextContent("ana@example.com");
  });

  it("no se puede confirmar sin aceptar los terminos", async () => {
    mostrar();
    await screen.findByText("Texto de los términos de Tirolesa.");

    expect(botonConfirmar()).toBeDisabled();
  });

  it("al aceptar y confirmar envia la inscripcion con la sesion y avisa el codigo", async () => {
    const usuario = userEvent.setup();
    const { api, alInscripto } = mostrar();
    await screen.findByText("Texto de los términos de Tirolesa.");

    await usuario.click(screen.getByLabelText("Acepto los términos y condiciones de Tirolesa"));
    await usuario.click(botonConfirmar());

    expect(api.inscribir).toHaveBeenCalledWith(
      {
        actividad: "Tirolesa",
        fecha: "2026-11-04",
        hora: "10:00",
        visitantes: VISITANTES,
        terminos_aceptados: "Tirolesa",
      },
      "tok",
    );
    expect(alInscripto).toHaveBeenCalledWith("INS-0001");
  });

  it("si no hay cupo lo explica y permite elegir otro horario", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({ inscribir: vi.fn(async () => falla(409, { motivos: ["sin_cupo"] })) });
    const { alInscripto } = mostrar(api);
    await screen.findByText("Texto de los términos de Tirolesa.");

    await usuario.click(screen.getByLabelText("Acepto los términos y condiciones de Tirolesa"));
    await usuario.click(botonConfirmar());

    expect(await screen.findByRole("alert")).toHaveTextContent("No quedan lugares suficientes en ese horario.");
    expect(alInscripto).not.toHaveBeenCalled();
    expect(botonConfirmar()).toBeEnabled();
  });

  it("indica cual visitante tiene un problema y cual es", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      inscribir: vi.fn(async () =>
        falla(422, { motivos: ["visitante_invalido"], visitantes: { 2: ["dni_invalido"] } }),
      ),
    });
    mostrar(api);
    await screen.findByText("Texto de los términos de Tirolesa.");

    await usuario.click(screen.getByLabelText("Acepto los términos y condiciones de Tirolesa"));
    await usuario.click(botonConfirmar());

    expect(await screen.findByRole("alert")).toHaveTextContent("Visitante 2: el DNI debe tener 7 u 8 números sin puntos ni espacios (por ejemplo 30123456).");
  });

  it("si el email no se pudo enviar explica que la inscripcion no se confirmo", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({ inscribir: vi.fn(async () => falla(503, { motivos: ["email_no_enviado"] })) });
    mostrar(api);
    await screen.findByText("Texto de los términos de Tirolesa.");

    await usuario.click(screen.getByLabelText("Acepto los términos y condiciones de Tirolesa"));
    await usuario.click(botonConfirmar());

    expect(await screen.findByRole("alert")).toHaveTextContent(/la inscripción no se confirmó/i);
  });

  it("si la sesion vencio avisa para que se vuelva a iniciar sesion", async () => {
    const usuario = userEvent.setup();
    const api = crearApiFalsa({
      inscribir: vi.fn(async () => falla(401, { motivos: ["usuario_no_registrado"] })),
    });
    const { alSesionVencida } = mostrar(api);
    await screen.findByText("Texto de los términos de Tirolesa.");

    await usuario.click(screen.getByLabelText("Acepto los términos y condiciones de Tirolesa"));
    await usuario.click(botonConfirmar());

    expect(alSesionVencida).toHaveBeenCalled();
  });

  it("mientras se envia no deja confirmar dos veces", async () => {
    const usuario = userEvent.setup();
    let responder;
    const api = crearApiFalsa({ inscribir: vi.fn(() => new Promise((resolver) => { responder = resolver; })) });
    mostrar(api);
    await screen.findByText("Texto de los términos de Tirolesa.");

    await usuario.click(screen.getByLabelText("Acepto los términos y condiciones de Tirolesa"));
    await usuario.click(botonConfirmar());

    expect(screen.getByRole("button", { name: /Enviando/ })).toBeDisabled();
    expect(api.inscribir).toHaveBeenCalledTimes(1);
    responder(ok({ codigo: "INS-0001" }, 201));
  });

  it("si no se pueden cargar los terminos no deja confirmar", async () => {
    const api = crearApiFalsa({ terminos: vi.fn(async () => falla(0, { motivos: ["sin_conexion"] })) });
    mostrar(api);

    expect(await screen.findByRole("alert")).toHaveTextContent(/no pudimos conectarnos/i);
    expect(botonConfirmar()).toBeDisabled();
  });
});

describe("PantallaListo", () => {
  it("muestra el codigo de reserva y a que email llega la confirmacion", () => {
    render(<PantallaListo codigo="INS-0007" email="ana@example.com" alOtra={vi.fn()} />);

    expect(screen.getByRole("heading", { name: "¡Inscripción confirmada!" })).toBeInTheDocument();
    expect(screen.getByText("INS-0007")).toBeInTheDocument();
    expect(screen.getByText(/ana@example\.com/)).toBeInTheDocument();
  });

  it("permite hacer otra inscripcion", async () => {
    const alOtra = vi.fn();
    render(<PantallaListo codigo="INS-0007" email="ana@example.com" alOtra={alOtra} />);

    await userEvent.click(screen.getByRole("button", { name: "Hacer otra inscripción" }));

    expect(alOtra).toHaveBeenCalled();
  });
});
