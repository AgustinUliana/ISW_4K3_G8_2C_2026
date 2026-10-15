import { useState } from "react";
import { mensajesDeRechazo } from "../dominio/mensajes";

export function PantallaAcceso({ api, alEntrar }) {
  const [modo, setModo] = useState("ingresar"); // "ingresar" | "registrar"
  const [email, setEmail] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [errores, setErrores] = useState([]);
  const [enviando, setEnviando] = useState(false);
  const registrando = modo === "registrar";

  function cambiarModo(nuevo) {
    setModo(nuevo);
    setErrores([]);
  }

  async function enviar(evento) {
    evento.preventDefault();
    setEnviando(true);
    setErrores([]);
    try {
      if (registrando) {
        const alta = await api.registrar(email, contrasena);
        if (!alta.ok) return setErrores(mensajesDeRechazo(alta.datos));
      }
      const sesion = await api.iniciarSesion(email, contrasena);
      if (!sesion.ok) return setErrores(mensajesDeRechazo(sesion.datos));
      alEntrar({ token: sesion.datos.token, email: email.trim().toLowerCase() });
    } finally {
      setEnviando(false);
    }
  }

  const textoDelBoton = registrando ? "Crear cuenta" : "Iniciar sesión";
  return (
    <section className="pantalla" aria-labelledby="titulo-acceso">
      <h2 id="titulo-acceso">{registrando ? "Creá tu cuenta" : "Ingresá para inscribirte"}</h2>
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
          onChange={(e) => setEmail(e.target.value)}
        />
        <label htmlFor="contrasena">Contraseña</label>
        <input
          id="contrasena"
          type="password"
          autoComplete={registrando ? "new-password" : "current-password"}
          value={contrasena}
          onChange={(e) => setContrasena(e.target.value)}
        />
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
