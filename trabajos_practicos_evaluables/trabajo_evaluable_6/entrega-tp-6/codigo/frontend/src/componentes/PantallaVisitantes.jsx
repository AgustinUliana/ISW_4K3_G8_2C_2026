import { useState } from "react";
import { mensajesPorCampo } from "../dominio/campos";
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
  const [problemas, setProblemas] = useState({}); // posicion -> { campo: mensaje }
  const [validando, setValidando] = useState(false);

  function cambiarCantidad(cantidad) {
    setVisitantes((actuales) => Array.from({ length: cantidad }, (_, i) => actuales[i] ?? visitanteVacio()));
  }

  function cambiar(indice, campo, valor) {
    setVisitantes((actuales) => actuales.map((v, i) => (i === indice ? { ...v, [campo]: valor } : v)));
    // al corregir un campo se le quita su mensaje de error
    setProblemas((actuales) => {
      const posicion = String(indice + 1);
      if (!actuales[posicion]?.[campo]) return actuales;
      const { [campo]: _corregido, ...resto } = actuales[posicion];
      return { ...actuales, [posicion]: resto };
    });
  }

  const contexto = { edadMinima: actividad.edad_minima };
  const marcado = (n, campo) => (problemas[String(n)]?.[campo] ? true : undefined);
  const descrito = (n, campo) => (problemas[String(n)]?.[campo] ? `error-${campo}-${n}` : undefined);

  function mostrarRechazo(cuerpo) {
    setErrores(mensajesDeRechazo(cuerpo, contexto));
    setProblemas(
      Object.fromEntries(
        Object.entries(cuerpo.visitantes ?? {}).map(([posicion, motivos]) => [
          posicion,
          mensajesPorCampo(motivos, contexto),
        ]),
      ),
    );
  }

  // Lo que le falta completar a un visitante, con los mismos motivos que usa la API.
  function motivosFaltantes(v) {
    return [
      !v.nombre.trim() && "nombre_requerido",
      !v.dni.trim() && "dni_requerido",
      v.edad === "" && "edad_requerida",
      actividad.requiere_talla && !v.talla && "talla_requerida",
    ].filter(Boolean);
  }

  async function continuar(evento) {
    evento.preventDefault();
    setProblemas({});
    const incompletos = Object.fromEntries(
      visitantes.map((v, i) => [String(i + 1), motivosFaltantes(v)]).filter(([, motivos]) => motivos.length > 0),
    );
    if (Object.keys(incompletos).length > 0) {
      mostrarRechazo({ motivos: ["visitante_invalido"], visitantes: incompletos });
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
      mostrarRechazo(respuesta.datos);
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
                aria-describedby={descrito(n, "nombre")}
                onChange={(e) => cambiar(indice, "nombre", e.target.value)}
              />
              <ErrorDeCampo id={`error-nombre-${n}`} texto={problemas[String(n)]?.nombre} />
              <label htmlFor={`dni-${n}`}>DNI</label>
              <input
                id={`dni-${n}`}
                inputMode="numeric"
                value={visitante.dni}
                aria-invalid={marcado(n, "dni")}
                aria-describedby={descrito(n, "dni")}
                onChange={(e) => cambiar(indice, "dni", e.target.value)}
              />
              <ErrorDeCampo id={`error-dni-${n}`} texto={problemas[String(n)]?.dni} />
              <label htmlFor={`edad-${n}`}>Edad</label>
              <input
                id={`edad-${n}`}
                type="number"
                inputMode="numeric"
                min="0"
                value={visitante.edad}
                aria-invalid={marcado(n, "edad")}
                aria-describedby={descrito(n, "edad")}
                onChange={(e) => cambiar(indice, "edad", e.target.value)}
              />
              <ErrorDeCampo id={`error-edad-${n}`} texto={problemas[String(n)]?.edad} />
              {actividad.requiere_talla && (
                <>
                  <label htmlFor={`talla-${n}`}>Talla</label>
                  <select
                    id={`talla-${n}`}
                    value={visitante.talla}
                    aria-invalid={marcado(n, "talla")}
                aria-describedby={descrito(n, "talla")}
                    onChange={(e) => cambiar(indice, "talla", e.target.value)}
                  >
                    <option value="">Elegí la talla</option>
                    {TALLAS.map((talla) => (
                      <option key={talla} value={talla}>
                        {talla}
                      </option>
                    ))}
                  </select>
                  <ErrorDeCampo id={`error-talla-${n}`} texto={problemas[String(n)]?.talla} />
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

function ErrorDeCampo({ id, texto }) {
  return texto ? (
    <p id={id} className="error-campo">
      {texto}
    </p>
  ) : null;
}
