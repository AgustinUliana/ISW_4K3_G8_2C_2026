import { describe, expect, it } from "vitest";
import { etiquetaDeDia, fechaLegible, textoDeCupo } from "./formato";

describe("formato", () => {
  it("fechaLegible pasa de AAAA-MM-DD a DD/MM/AAAA", () => {
    expect(fechaLegible("2026-11-04")).toBe("04/11/2026");
  });

  it("textoDeCupo usa singular y plural", () => {
    expect(textoDeCupo(1)).toBe("Queda 1 lugar");
    expect(textoDeCupo(7)).toBe("Quedan 7 lugares");
  });

  it("etiquetaDeDia muestra el dia de la semana abreviado y la fecha", () => {
    expect(etiquetaDeDia(new Date(2026, 10, 4))).toBe("mié 4/11");
    expect(etiquetaDeDia(new Date(2026, 10, 7))).toBe("sáb 7/11");
  });
});
