import { useEffect, useState } from "react";
import { fechaLegible } from "../dominio/formato";
import { mensajesDeRechazo } from "../dominio/mensajes";

export function PantallaConfirmacion({
  api,
  sesion,
  actividad,
  fecha,
  turno,
  visitantes,
  alInscripto,
  alVolver,
  alSesionVencida,
}) {
  const [terminos, setTerminos] = useState(null);
  const [aceptados, setAceptados] = useState(false);
  const [errores, setErrores] = useState([]);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    let vigente = true;
    api.terminos(actividad.nombre).then((respuesta) => {
      if (!vigente) return;
      if (respuesta.ok) setTerminos(respuesta.datos);
      else setErrores(mensajesDeRechazo(respuesta.datos));
    });
    return () => {
      vigente = false;
    };
  }, [api, actividad.nombre]);

  async function confirmar() {
    setEnviando(true);
    setErrores([]);
    const respuesta = await api.inscribir(
      {
        actividad: actividad.nombre,
        fecha,
        hora: turno.hora,
        visitantes,
        terminos_aceptados: aceptados ? actividad.nombre : null,
      },
      sesion.token,
    );
    setEnviando(false);
    if (respuesta.ok) {
      alInscripto(respuesta.datos.codigo);
    } else if (respuesta.estado === 401) {
      setErrores(["Tu sesión venció. Iniciá sesión de nuevo para inscribirte."]);
      alSesionVencida();
    } else {
      setErrores(mensajesDeRechazo(respuesta.datos));
    }
  }

  const puedeConfirmar = terminos !== null && aceptados && !enviando;
  return (
    <section className="pantalla" aria-labelledby="titulo-confirmacion">
      <h2 id="titulo-confirmacion">Revisá y confirmá</h2>
      <section aria-labelledby="titulo-resumen" className="resumen">
        <h3 id="titulo-resumen">Resumen de tu inscripción</h3>
        <dl>
          <dt>Actividad</dt>
          <dd>{actividad.nombre}</dd>
          <dt>Día y horario</dt>
          <dd>
            {fechaLegible(fecha)} a las {turno.hora}
          </dd>
          <dt>Personas</dt>
          <dd>
            {visitantes.length} {visitantes.length === 1 ? "persona" : "personas"}:{" "}
            {visitantes.map((v) => v.nombre).join(", ")}
          </dd>
        </dl>
        <p className="ayuda">
          Te enviaremos la confirmación con un QR por visitante a {sesion.email}.
        </p>
      </section>
      <section aria-labelledby="titulo-terminos" className="terminos">
        <h3 id="titulo-terminos">Términos y condiciones de {actividad.nombre}</h3>
        {terminos && <div className="texto-terminos">{terminos.texto}</div>}
        <label className="casilla">
          <input type="checkbox" checked={aceptados} onChange={(e) => setAceptados(e.target.checked)} />
          Acepto los términos y condiciones de {actividad.nombre}
        </label>
      </section>
      {errores.length > 0 && (
        <div role="alert" className="aviso aviso-error">
          {errores.map((mensaje) => (
            <p key={mensaje}>{mensaje}</p>
          ))}
        </div>
      )}
      <div className="acciones">
        <button type="button" className="boton-secundario" onClick={alVolver} disabled={enviando}>
          Volver
        </button>
        <button type="button" className="boton-principal" disabled={!puedeConfirmar} onClick={confirmar}>
          {enviando ? "Enviando…" : "Confirmar inscripción"}
        </button>
      </div>
    </section>
  );
}
