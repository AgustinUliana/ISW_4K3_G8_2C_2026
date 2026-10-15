import { useState } from "react";
import { textoDeCupo } from "../dominio/formato";

const TALLAS = ["XS", "S", "M", "L", "XL", "XXL"];
const MAXIMO_POR_INSCRIPCION = 10; // regla del PO
const visitanteVacio = () => ({ nombre: "", dni: "", edad: "", talla: "" });

export function PantallaVisitantes({ actividad, turno, alContinuar, alVolver }) {
  const maximo = Math.min(MAXIMO_POR_INSCRIPCION, turno.cupo_restante);
  const [visitantes, setVisitantes] = useState([visitanteVacio()]);
  const [errores, setErrores] = useState([]);

  function cambiarCantidad(cantidad) {
    setVisitantes((actuales) => Array.from({ length: cantidad }, (_, i) => actuales[i] ?? visitanteVacio()));
  }

  function cambiar(indice, campo, valor) {
    setVisitantes((actuales) => actuales.map((v, i) => (i === indice ? { ...v, [campo]: valor } : v)));
  }

  function continuar(evento) {
    evento.preventDefault();
    const incompleto = visitantes.findIndex(
      (v) => !v.nombre.trim() || !v.dni.trim() || v.edad === "" || (actividad.requiere_talla && !v.talla),
    );
    if (incompleto >= 0) {
      setErrores([`Completá todos los datos del visitante ${incompleto + 1}.`]);
      return;
    }
    alContinuar(
      visitantes.map((v) => ({
        nombre: v.nombre.trim(),
        dni: v.dni.trim(),
        edad: Number(v.edad),
        talla: actividad.requiere_talla ? v.talla : null,
      })),
    );
  }

  return (
    <section className="pantalla" aria-labelledby="titulo-visitantes">
      <h2 id="titulo-visitantes">¿Quiénes participan?</h2>
      <form onSubmit={continuar} noValidate>
        <label htmlFor="cantidad">Cantidad de personas</label>
        <select id="cantidad" value={visitantes.length} onChange={(e) => cambiarCantidad(Number(e.target.value))}>
          {Array.from({ length: maximo }, (_, i) => (
            <option key={i + 1} value={i + 1}>
              {i + 1}
            </option>
          ))}
        </select>
        <p className="ayuda">{textoDeCupo(turno.cupo_restante)} en este turno.</p>
        <p className="ayuda">Máximo {MAXIMO_POR_INSCRIPCION} personas por inscripción.</p>
        {actividad.edad_minima > 0 && (
          <p className="ayuda">Edad mínima de la actividad: {actividad.edad_minima} años.</p>
        )}
        {visitantes.map((visitante, indice) => {
          const n = indice + 1;
          return (
            <fieldset key={n} className="visitante">
              <legend>Visitante {n}</legend>
              <label htmlFor={`nombre-${n}`}>Nombre</label>
              <input
                id={`nombre-${n}`}
                autoComplete="name"
                value={visitante.nombre}
                onChange={(e) => cambiar(indice, "nombre", e.target.value)}
              />
              <label htmlFor={`dni-${n}`}>DNI</label>
              <input
                id={`dni-${n}`}
                inputMode="numeric"
                value={visitante.dni}
                onChange={(e) => cambiar(indice, "dni", e.target.value)}
              />
              <label htmlFor={`edad-${n}`}>Edad</label>
              <input
                id={`edad-${n}`}
                type="number"
                inputMode="numeric"
                min="0"
                value={visitante.edad}
                onChange={(e) => cambiar(indice, "edad", e.target.value)}
              />
              {actividad.requiere_talla && (
                <>
                  <label htmlFor={`talla-${n}`}>Talla</label>
                  <select
                    id={`talla-${n}`}
                    value={visitante.talla}
                    onChange={(e) => cambiar(indice, "talla", e.target.value)}
                  >
                    <option value="">Elegí la talla</option>
                    {TALLAS.map((talla) => (
                      <option key={talla} value={talla}>
                        {talla}
                      </option>
                    ))}
                  </select>
                </>
              )}
            </fieldset>
          );
        })}
        {errores.length > 0 && (
          <div role="alert" className="aviso aviso-error">
            {errores.map((mensaje) => (
              <p key={mensaje}>{mensaje}</p>
            ))}
          </div>
        )}
        <div className="acciones">
          <button type="button" className="boton-secundario" onClick={alVolver}>
            Volver
          </button>
          <button type="submit" className="boton-principal">
            Continuar
          </button>
        </div>
      </form>
    </section>
  );
}
