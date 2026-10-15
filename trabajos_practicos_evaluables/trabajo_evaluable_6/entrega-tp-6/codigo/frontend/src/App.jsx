import { useState } from "react";
import { crearCliente } from "./api/cliente";
import { PantallaAcceso } from "./componentes/PantallaAcceso";
import { PantallaActividades } from "./componentes/PantallaActividades";
import { PantallaConfirmacion } from "./componentes/PantallaConfirmacion";
import { PantallaHorario } from "./componentes/PantallaHorario";
import { PantallaListo } from "./componentes/PantallaListo";
import { PantallaVisitantes } from "./componentes/PantallaVisitantes";
import { Vidrio } from "./componentes/Vidrio";

const CLAVE_DE_SESION = "ecoharmony.sesion";
const PASOS = [
  ["actividades", "Actividad"],
  ["horario", "Horario"],
  ["visitantes", "Visitantes"],
  ["confirmacion", "Confirmar"],
];
const AVISO_SESION_VENCIDA = "Tu sesión venció. Iniciá sesión de nuevo para inscribirte.";
const apiPorDefecto = crearCliente();

function almacenamientoDelNavegador() {
  try {
    return window.localStorage;
  } catch {
    return null; // el navegador lo bloquea (modo privado, cookies deshabilitadas)
  }
}

function leerSesion(almacenamiento) {
  try {
    const guardada = almacenamiento?.getItem(CLAVE_DE_SESION);
    return guardada ? JSON.parse(guardada) : null;
  } catch {
    return null;
  }
}

function recordarSesion(almacenamiento, sesion) {
  try {
    if (sesion) almacenamiento?.setItem(CLAVE_DE_SESION, JSON.stringify(sesion));
    else almacenamiento?.removeItem(CLAVE_DE_SESION);
  } catch {
    // sin almacenamiento la sesion dura hasta cerrar la pestaña: no es un error
  }
}

export default function App({
  api = apiPorDefecto,
  ahora = () => new Date(),
  almacenamiento = almacenamientoDelNavegador(),
}) {
  const [sesion, setSesion] = useState(() => leerSesion(almacenamiento));
  const [paso, setPaso] = useState("actividades");
  const [eleccion, setEleccion] = useState({});
  const [codigo, setCodigo] = useState(null);
  const [aviso, setAviso] = useState(null);

  function entrar(nuevaSesion) {
    recordarSesion(almacenamiento, nuevaSesion);
    setSesion(nuevaSesion);
    setAviso(null);
    setPaso("actividades");
  }

  function salir(motivo = null) {
    recordarSesion(almacenamiento, null);
    setSesion(null);
    setEleccion({});
    setAviso(motivo);
  }

  function empezarDeNuevo() {
    setEleccion({});
    setCodigo(null);
    setPaso("actividades");
  }

  let pantalla;
  if (!sesion) {
    pantalla = <PantallaAcceso api={api} alEntrar={entrar} aviso={aviso} />;
  } else if (paso === "actividades") {
    pantalla = (
      <PantallaActividades
        api={api}
        alElegir={(actividad) => {
          setEleccion({ actividad });
          setPaso("horario");
        }}
      />
    );
  } else if (paso === "horario") {
    pantalla = (
      <PantallaHorario
        api={api}
        actividad={eleccion.actividad}
        ahora={ahora()}
        alElegir={({ fecha, turno }) => {
          setEleccion((actual) => ({ ...actual, fecha, turno }));
          setPaso("visitantes");
        }}
        alVolver={() => setPaso("actividades")}
      />
    );
  } else if (paso === "visitantes") {
    pantalla = (
      <PantallaVisitantes
        actividad={eleccion.actividad}
        fecha={eleccion.fecha}
        turno={eleccion.turno}
        alContinuar={(visitantes) => {
          setEleccion((actual) => ({ ...actual, visitantes }));
          setPaso("confirmacion");
        }}
        alVolver={() => setPaso("horario")}
      />
    );
  } else if (paso === "confirmacion") {
    pantalla = (
      <PantallaConfirmacion
        api={api}
        sesion={sesion}
        actividad={eleccion.actividad}
        fecha={eleccion.fecha}
        turno={eleccion.turno}
        visitantes={eleccion.visitantes}
        alInscripto={(nuevoCodigo) => {
          setCodigo(nuevoCodigo);
          setPaso("listo");
        }}
        alVolver={() => setPaso("visitantes")}
        alSesionVencida={() => salir(AVISO_SESION_VENCIDA)}
      />
    );
  } else {
    pantalla = <PantallaListo codigo={codigo} email={sesion.email} alOtra={empezarDeNuevo} />;
  }

  return (
    <div className="aplicacion">
      <header className="encabezado">
        <Vidrio radio={22} relleno="10px 20px" className="encabezado-vidrio">
          <div className="encabezado-contenido">
            <div className="marca">
              <span className="marca-nombre">EcoHarmony Park</span>
              <span className="marca-detalle">Inscripción a actividades</span>
            </div>
            {sesion && (
              <div className="usuario">
                <span>{sesion.email}</span>
                <button type="button" className="boton-secundario" onClick={() => salir()}>
                  Cerrar sesión
                </button>
              </div>
            )}
          </div>
        </Vidrio>
      </header>
      <main className="contenido">
        {sesion && paso !== "listo" && (
          <ol className="pasos" aria-label="Pasos de la inscripción">
            {PASOS.map(([clave, titulo]) => (
              <li key={clave} aria-current={clave === paso ? "step" : undefined}>
                {titulo}
              </li>
            ))}
          </ol>
        )}
        <Vidrio radio={32} relleno="28px" className="panel">
          {pantalla}
        </Vidrio>
      </main>
    </div>
  );
}
