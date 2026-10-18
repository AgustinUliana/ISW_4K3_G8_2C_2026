export function PantallaListo({ codigo, email, alOtra }) {
  return (
    <section className="pantalla pantalla-final" aria-labelledby="titulo-listo">
      <h2 id="titulo-listo">¡Inscripción confirmada!</h2>
      <p>Tu código de reserva es</p>
      <p className="codigo">{codigo}</p>
      <p>
        Te enviamos un email a <strong>{email}</strong> con el resumen y un código QR por cada visitante. Presentá el
        QR al llegar a la actividad.
      </p>
      <p className="ayuda">Si no lo ves en unos minutos, revisá la carpeta de spam o correo no deseado.</p>
      <button type="button" className="boton-principal" onClick={alOtra}>
        Hacer otra inscripción
      </button>
    </section>
  );
}
