import { useCallback, useEffect, useState } from "react";
import { mensajesDeRechazo } from "../dominio/mensajes";

export function PantallaActividades({ api, alElegir }) {
  const [actividades, setActividades] = useState(null);
  const [errores, setErrores] = useState([]);

  const cargar = useCallback(async () => {
    setErrores([]);
    setActividades(null);
    const respuesta = await api.actividades();
    if (respuesta.ok) setActividades(respuesta.datos);
    else setErrores(mensajesDeRechazo(respuesta.datos));
  }, [api]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  if (errores.length > 0) {
    return (
      <section className="pantalla">
        <div role="alert" className="aviso aviso-error">
          {errores.map((mensaje) => (
            <p key={mensaje}>{mensaje}</p>
          ))}
        </div>
        <button type="button" className="boton-secundario" onClick={cargar}>
          Reintentar
        </button>
      </section>
    );
  }
  if (actividades === null) {
    return <p className="cargando">Cargando actividades…</p>;
  }
  return (
    <section className="pantalla" aria-labelledby="titulo-actividades">
      <h2 id="titulo-actividades">Elegí una actividad</h2>
      <div className="grilla-actividades">
        {actividades.map((actividad) => (
          <article key={actividad.nombre} className="tarjeta" aria-labelledby={`actividad-${actividad.nombre}`}>
            <h3 id={`actividad-${actividad.nombre}`}>{actividad.nombre}</h3>
            <ul className="requisitos">
              <li>{actividad.edad_minima > 0 ? `Desde ${actividad.edad_minima} años` : "Todas las edades"}</li>
              {actividad.requiere_talla && <li>Requiere talla de vestimenta</li>}
              <li>Hasta {actividad.cupo_por_turno} personas por turno</li>
            </ul>
            {!actividad.disponible && <p className="sin-turnos">Sin turnos disponibles</p>}
            <button
              type="button"
              className="boton-principal"
              disabled={!actividad.disponible}
              onClick={() => alElegir(actividad)}
            >
              Elegir
            </button>
          </article>
        ))}
      </div>
    </section>
  );
}
