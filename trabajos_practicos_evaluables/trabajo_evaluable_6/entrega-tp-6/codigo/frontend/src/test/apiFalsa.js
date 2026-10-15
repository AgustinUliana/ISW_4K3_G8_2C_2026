// API falsa para probar las pantallas sin red (mismo contrato que src/api/cliente.js).
import { vi } from "vitest";

export const ok = (datos = {}, estado = 200) => ({ ok: true, estado, datos });
export const falla = (estado, datos = {}) => ({ ok: false, estado, datos });

export const ACTIVIDADES = [
  { nombre: "Tirolesa", requiere_talla: true, edad_minima: 8, cupo_por_turno: 10, disponible: true },
  { nombre: "Safari", requiere_talla: false, edad_minima: 0, cupo_por_turno: 8, disponible: true },
  { nombre: "Palestra", requiere_talla: true, edad_minima: 12, cupo_por_turno: 12, disponible: false },
  { nombre: "Jardinería", requiere_talla: false, edad_minima: 0, cupo_por_turno: 12, disponible: true },
];

export const TURNOS = {
  actividad: "Tirolesa",
  fecha: "2026-11-04",
  turnos: [
    { hora: "10:00", cupo_restante: 7, agotado: false },
    { hora: "11:00", cupo_restante: 0, agotado: true },
    { hora: "12:00", cupo_restante: 1, agotado: false },
  ],
};

export function crearApiFalsa(sobrescribir = {}) {
  return {
    registrar: vi.fn(async (email) => ok({ email }, 201)),
    iniciarSesion: vi.fn(async () => ok({ token: "token-de-prueba" })),
    actividades: vi.fn(async () => ok(ACTIVIDADES)),
    horarios: vi.fn(async () => ok(TURNOS)),
    terminos: vi.fn(async (nombre) =>
      ok({ actividad: nombre, version: "v1", texto: `Texto de los términos de ${nombre}.` }),
    ),
    inscribir: vi.fn(async () => ok({ codigo: "INS-0001" }, 201)),
    ...sobrescribir,
  };
}
