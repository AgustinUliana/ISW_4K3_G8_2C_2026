import { describe, expect, it } from "vitest";
import { diasParaElegir, estaAbierto } from "./calendario";

const fecha = (anio, mes, dia) => new Date(anio, mes - 1, dia);

describe("estaAbierto", () => {
  it("el parque abre un dia comun", () => {
    expect(estaAbierto(fecha(2026, 11, 4))).toBe(true); // miercoles
  });

  it("el parque cierra los lunes", () => {
    expect(estaAbierto(fecha(2026, 11, 2))).toBe(false);
  });

  it("el parque cierra el 25 de diciembre y el 1 de enero", () => {
    expect(estaAbierto(fecha(2026, 12, 25))).toBe(false);
    expect(estaAbierto(fecha(2027, 1, 1))).toBe(false);
  });
});

describe("diasParaElegir", () => {
  const miercoles10hs = new Date(2026, 10, 4, 10, 0);

  it("ofrece los proximos 7 dias empezando hoy, con la fecha en formato AAAA-MM-DD", () => {
    const dias = diasParaElegir(miercoles10hs);

    expect(dias).toHaveLength(7);
    expect(dias[0].fecha).toBe("2026-11-04");
    expect(dias[6].fecha).toBe("2026-11-10");
  });

  it("solo hoy y manana se pueden elegir: la inscripcion abre 24 horas antes del turno", () => {
    const dias = diasParaElegir(miercoles10hs);

    expect(dias.map((d) => d.seleccionable)).toEqual([true, true, false, false, false, false, false]);
    expect(dias[2].motivo).toBe("fuera_de_ventana"); // viernes
  });

  it("un dia con el parque cerrado se muestra deshabilitado, con el motivo 'cerrado'", () => {
    const domingo = new Date(2026, 10, 1, 10, 0); // manana es lunes
    const dias = diasParaElegir(domingo);

    expect(dias[1]).toMatchObject({ fecha: "2026-11-02", abierto: false, seleccionable: false, motivo: "cerrado" });
    expect(dias[0].seleccionable).toBe(true);
  });

  it("cruza el fin de mes y de año sin romperse", () => {
    const dias = diasParaElegir(new Date(2026, 11, 30, 10, 0)); // 30 de diciembre

    expect(dias.map((d) => d.fecha).slice(0, 3)).toEqual(["2026-12-30", "2026-12-31", "2027-01-01"]);
    expect(dias[2].abierto).toBe(false); // 1 de enero
  });
});
