import { useEffect, useState } from "react";
import { diasParaElegir } from "../dominio/calendario";
import { etiquetaDeDia, textoDeCupo } from "../dominio/formato";
import { mensajesDeRechazo } from "../dominio/mensajes";

const TEXTO_DEL_MOTIVO = { cerrado: "Cerrado", fuera_de_ventana: "Aún no disponible" };

export function PantallaHorario({ api, actividad, ahora, alElegir, alVolver }) {
  const dias = diasParaElegir(ahora);
  const primerElegible = dias.find((dia) => dia.seleccionable)?.fecha ?? null;
  const [fecha, setFecha] = useState(primerElegible);
  const [turnos, setTurnos] = useState(null);
  const [errores, setErrores] = useState([]);

  useEffect(() => {
    if (!fecha) return undefined;
    let vigente = true;
    setTurnos(null);
    setErrores([]);
    api.horarios(actividad.nombre, fecha).then((respuesta) => {
      if (!vigente) return;
      if (respuesta.ok) setTurnos(respuesta.datos.turnos);
      else setErrores(mensajesDeRechazo(respuesta.datos));
    });
    return () => {
      vigente = false;
    };
  }, [api, actividad.nombre, fecha]);

  return (
    <section className="pantalla" aria-labelledby="titulo-horario">
      <h2 id="titulo-horario">{actividad.nombre}: elegí el día y el horario</h2>
      <p className="ayuda">Podés reservar hasta 24 horas antes del turno. La inscripción cierra 15 minutos antes.</p>
      <div className="dias">
        {dias.map((dia) => (
          <button
            key={dia.fecha}
            type="button"
            className="dia"
            aria-pressed={dia.fecha === fecha}
            disabled={!dia.seleccionable}
            onClick={() => setFecha(dia.fecha)}
          >
            <span>{etiquetaDeDia(dia.fechaDate)}</span>
            {dia.motivo && <small>{TEXTO_DEL_MOTIVO[dia.motivo]}</small>}
          </button>
        ))}
      </div>
      {errores.length > 0 && (
        <div role="alert" className="aviso aviso-error">
          {errores.map((mensaje) => (
            <p key={mensaje}>{mensaje}</p>
          ))}
        </div>
      )}
      {turnos === null && errores.length === 0 && <p className="cargando">Cargando horarios…</p>}
      {turnos !== null && turnos.length === 0 && <p className="ayuda">No quedan turnos para este día.</p>}
      {turnos !== null && turnos.length > 0 && (
        <div className="turnos">
          {turnos.map((turno) => (
            <button
              key={turno.hora}
              type="button"
              className="turno"
              disabled={turno.agotado}
              onClick={() => alElegir({ fecha, turno })}
            >
              <span className="hora">{turno.hora}</span>
              <small>{turno.agotado ? "Agotado" : textoDeCupo(turno.cupo_restante)}</small>
            </button>
          ))}
        </div>
      )}
      <button type="button" className="boton-secundario" onClick={alVolver}>
        Volver
      </button>
    </section>
  );
}
