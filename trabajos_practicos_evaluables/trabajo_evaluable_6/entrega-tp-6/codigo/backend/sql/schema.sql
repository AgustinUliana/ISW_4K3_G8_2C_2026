-- Esquema de EcoHarmony Park: inscripcion a actividades.
-- SQL plano (sin ORM). Se lee tal cual en DBeaver.
-- Es reaplicable: crea solo lo que falta (la prueba REP-08 lo verifica sobre una base vacia).

-- Catalogo de actividades (Tirolesa, Safari, Palestra, Jardineria).
CREATE TABLE IF NOT EXISTS actividad (
    nombre           text PRIMARY KEY,
    cupo_por_turno   integer NOT NULL CHECK (cupo_por_turno > 0),
    edad_minima      integer NOT NULL DEFAULT 0 CHECK (edad_minima >= 0),
    requiere_talla   boolean NOT NULL DEFAULT false,
    terminos_version text NOT NULL,
    terminos_texto   text NOT NULL
);

-- Personas ya inscriptas por turno (actividad + fecha + hora). Es la fuente del cupo restante.
-- El control de cupo se hace en una sola sentencia atomica (ver RepositorioPostgres.guardar).
CREATE TABLE IF NOT EXISTS ocupacion (
    actividad text    NOT NULL REFERENCES actividad (nombre),
    fecha     date    NOT NULL,
    hora      time    NOT NULL,
    personas  integer NOT NULL CHECK (personas >= 0),
    PRIMARY KEY (actividad, fecha, hora)
);

CREATE SEQUENCE IF NOT EXISTS inscripcion_codigo_seq;

CREATE TABLE IF NOT EXISTS inscripcion (
    codigo            text PRIMARY KEY,
    actividad         text      NOT NULL REFERENCES actividad (nombre),
    fecha             date      NOT NULL,
    hora              time      NOT NULL,
    email_de_contacto text      NOT NULL,
    terminos_version  text      NOT NULL,
    confirmada_el     timestamp NOT NULL
);

-- Una fila por visitante. fecha y hora se repiten a proposito: la restriccion UNIQUE
-- impide que una misma persona (DNI) tenga dos turnos en el mismo horario, en cualquier
-- actividad (regla del PO).
CREATE TABLE IF NOT EXISTS visitante_inscripto (
    inscripcion text    NOT NULL REFERENCES inscripcion (codigo),
    posicion    integer NOT NULL,
    nombre      text    NOT NULL,
    dni         text    NOT NULL,
    edad        integer NOT NULL CHECK (edad >= 0),
    talla       text,
    fecha       date    NOT NULL,
    hora        time    NOT NULL,
    PRIMARY KEY (inscripcion, posicion),
    CONSTRAINT un_dni_por_horario UNIQUE (dni, fecha, hora)
);

-- Usuarios registrados: email + contrasena (guardada como hash con sal, nunca en texto plano).
CREATE TABLE IF NOT EXISTS usuario (
    email           text PRIMARY KEY CHECK (email = lower(email)),
    contrasena_hash text      NOT NULL,
    registrado_el   timestamp NOT NULL DEFAULT now()
);
