import { useState } from "react";
import { mensajesPorCampo } from "../dominio/campos";
import { mensajesDeRechazo } from "../dominio/mensajes";
import { OjoAbierto, OjoTachado } from "./Iconos";

export function PantallaAcceso({ api, alEntrar, aviso = null }) {
  const [modo, setModo] = useState("ingresar"); // "ingresar" | "registrar"
  const [email, setEmail] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [errores, setErrores] = useState([]);
  const [problemas, setProblemas] = useState({}); // campo -> mensaje
  const [enviando, setEnviando] = useState(false);
  const [verContrasena, setVerContrasena] = useState(false);
  const registrando = modo === "registrar";

  function cambiarModo(nuevo) {
    setModo(nuevo);
    setErrores([]);
    setProblemas({});
    setVerContrasena(false);
  }

  function rechazar(datos) {
    setErrores(mensajesDeRechazo(datos));
    setProblemas(mensajesPorCampo(datos.motivos ?? []));
  }

  // al corregir un campo se le quita su mensaje de error
  function escribir(campo, valor, guardar) {
    guardar(valor);
    setProblemas(({ [campo]: _corregido, ...resto }) => resto);
  }

  async function enviar(evento) {
    evento.preventDefault();
    setEnviando(true);
    setErrores([]);
    setProblemas({});
    try {
      if (registrando) {
        const alta = await api.registrar(email, contrasena);
        if (!alta.ok) return rechazar(alta.datos);
      }
      const sesion = await api.iniciarSesion(email, contrasena);
      if (!sesion.ok) return rechazar(sesion.datos);
      alEntrar({ token: sesion.datos.token, email: email.trim().toLowerCase() });
    } finally {
      setEnviando(false);
    }
  }

  const textoDelBoton = registrando ? "Crear cuenta" : "Iniciar sesión";
  return (
    <section className="pantalla" aria-labelledby="titulo-acceso">
      <h2 id="titulo-acceso">{registrando ? "Creá tu cuenta" : "Ingresá para inscribirte"}</h2>
      {aviso && (
        <p role="status" className="aviso aviso-info">
          {aviso}
        </p>
      )}
      <p className="ayuda">Solo necesitás un email y una contraseña.</p>
      <div role="tablist" className="pestanas">
        <button type="button" role="tab" aria-selected={!registrando} onClick={() => cambiarModo("ingresar")}>
          Iniciar sesión
        </button>
        <button type="button" role="tab" aria-selected={registrando} onClick={() => cambiarModo("registrar")}>
          Crear cuenta
        </button>
      </div>
      <form onSubmit={enviar} noValidate>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          value={email}
          aria-invalid={problemas.email ? true : undefined}
          aria-describedby={problemas.email ? "error-email" : undefined}
          onChange={(e) => escribir("email", e.target.value, setEmail)}
        />
        <ErrorDeCampo id="error-email" texto={problemas.email} />
        <label htmlFor="contrasena">Contraseña</label>
        <div className="campo-clave">
          <input
            id="contrasena"
            type={verContrasena ? "text" : "password"}
            autoComplete={registrando ? "new-password" : "current-password"}
            value={contrasena}
            aria-invalid={problemas.contrasena ? true : undefined}
            aria-describedby={problemas.contrasena ? "error-contrasena" : undefined}
            onChange={(e) => escribir("contrasena", e.target.value, setContrasena)}
          />
          <button
            type="button"
            className="boton-ojo"
            aria-label={verContrasena ? "Ocultar la contraseña" : "Mostrar la contraseña"}
            aria-pressed={verContrasena}
            title={verContrasena ? "Ocultar la contraseña" : "Mostrar la contraseña"}
            onClick={() => setVerContrasena((visible) => !visible)}
          >
            {verContrasena ? <OjoTachado /> : <OjoAbierto />}
          </button>
        </div>
        <ErrorDeCampo id="error-contrasena" texto={problemas.contrasena} />
        {errores.length > 0 && (
          <div role="alert" className="aviso aviso-error">
            {errores.map((mensaje) => (
              <p key={mensaje}>{mensaje}</p>
            ))}
          </div>
        )}
        <button type="submit" className="boton-principal" disabled={enviando}>
          {enviando ? "Ingresando…" : textoDelBoton}
        </button>
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
