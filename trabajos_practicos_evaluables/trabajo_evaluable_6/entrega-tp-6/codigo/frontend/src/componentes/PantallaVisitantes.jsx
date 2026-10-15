import { useState } from "react";
import { camposConError } from "../dominio/campos";
import { textoDeCupo } from "../dominio/formato";
import { mensajesDeRechazo } from "../dominio/mensajes";

const TALLAS = ["XS", "S", "M", "L", "XL", "XXL"];
const MAXIMO_POR_INSCRIPCION = 10; // regla del PO
const visitanteVacio = () => ({ nombre: "", dni: "", edad: "", talla: "" });
const aFormulario = (v) => ({ nombre: v.nombre, dni: v.dni, edad: String(v.edad), talla: v.talla ?? "" });
const SESION_VENCIDA = "Tu sesión venció. Iniciá sesión de nuevo para inscribirte.";

export function PantallaVisitantes({
  api,
  sesion,
  actividad,
  fecha,
  turno,
  visitantesIniciales,
  alContinuar,
  alVolver,
  alSesionVencida,
}) {
  const maximo = Math.min(MAXIMO_POR_INSCRIPCION, turno.cupo_restante);
  const [visitantes, setVisitantes] = useState(() =>
    visitantesIniciales?.length > 0
      ? visitantesIniciales.slice(0, maximo).map(aFormulario)
      : [visitanteVacio()],
  );
  const [errores, setErrores] = useState([]);
  const [marcas, setMarcas] = useState({}); // posicion -> campos con error segun la API
  const [validando, setValidando] = useState(false);

  function cambiarCantidad(cantidad) {
    setVisitantes((actuales) => Array.from({ length: cantidad }, (_, i) => actuales[i] ?? visitanteVacio()));
  }

  function cambiar(indice, campo, valor) {
    setVisitantes((actuales) => actuales.map((v, i) => (i === indice ? { ...v, [campo]: valor } : v)));
    // al corregir un campo se le quita la marca de error
    setMarcas((actuales) => {
      const posicion = String(indice + 1);
      if (!actuales[posicion]?.includes(campo)) return actuales;
      return { ...actuales, [posicion]: actuales[posicion].filter((c) => c !== campo) };
    });
  }

  const marcado = (n, campo) => (marcas[String(n)]?.includes(campo) ? true : undefined);

  async function continuar(evento) {
    evento.preventDefault();
    setMarcas({});
    const incompleto = visitantes.findIndex(
      (v) => !v.nombre.trim() || !v.dni.trim() || v.edad === "" || (actividad.requiere_talla && !v.talla),
    );
    if (incompleto >= 0) {
      setErrores([`Completá todos los datos del visitante ${incompleto + 1}.`]);
      return;
    }
    setErrores([]);
    const datos = visitantes.map((v) => ({
      nombre: v.nombre.trim(),
      dni: v.dni.trim(),
      edad: Number(v.edad),
      talla: actividad.requiere_talla ? v.talla : null,
    }));
    setValidando(true);
    // Las reglas (DNI, edad, cupo...) las aplica el backend: se revisan aca, antes de seguir.
    const respuesta = await api.validarInscripcion(
      { actividad: actividad.nombre, fecha, hora: turno.hora, visitantes: datos },
      sesion.token,
    );
    setValidando(false);
    if (respuesta.ok) {
      alContinuar(datos);
    } else if (respuesta.estado === 401) {
      setErrores([SESION_VENCIDA]);
      alSesionVencida();
    } else {
      setErrores(mensajesDeRechazo(respuesta.datos));
      setMarcas(
        Object.fromEntries(
          Object.entries(respuesta.datos.visitantes ?? {}).map(([posicion, motivos]) => [
            posicion,
            camposConError(motivos),
          ]),
        ),
      );
    }
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
                aria-invalid={marcado(n, "nombre")}
                onChange={(e) => cambiar(indice, "nombre", e.target.value)}
              />
              <label htmlFor={`dni-${n}`}>DNI</label>
              <input
                id={`dni-${n}`}
                inputMode="numeric"
                value={visitante.dni}
                aria-invalid={marcado(n, "dni")}
                onChange={(e) => cambiar(indice, "dni", e.target.value)}
              />
              <label htmlFor={`edad-${n}`}>Edad</label>
              <input
                id={`edad-${n}`}
                type="number"
                inputMode="numeric"
                min="0"
                value={visitante.edad}
                aria-invalid={marcado(n, "edad")}
                onChange={(e) => cambiar(indice, "edad", e.target.value)}
              />
              {actividad.requiere_talla && (
                <>
                  <label htmlFor={`talla-${n}`}>Talla</label>
                  <select
                    id={`talla-${n}`}
                    value={visitante.talla}
                    aria-invalid={marcado(n, "talla")}
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
          <button type="submit" className="boton-principal" disabled={validando}>
            {validando ? "Revisando…" : "Continuar"}
          </button>
        </div>
      </form>
    </section>
  );
}
