import psycopg

from ecoharmony.actividad import Actividad
from ecoharmony.errores import (
    ActividadNoEncontradaError,
    CupoInsuficienteError,
    DniYaInscriptoError,
)
from ecoharmony.horario import Horario
from ecoharmony.inscripcion import EstadoDeLaInscripcion, Inscripcion
from ecoharmony.terminos import TerminosYCondiciones
from ecoharmony.visitante import Visitante

# Reserva atomica del cupo: inserta el turno o suma las personas, pero solo si no se pasa del
# cupo. Si no hay lugar no devuelve ninguna fila. Al ser una unica sentencia, dos pedidos
# simultaneos por el ultimo lugar no pueden ganar los dos (el segundo espera el bloqueo de fila).
_RESERVAR_CUPO = """
INSERT INTO ocupacion (actividad, fecha, hora, personas)
SELECT a.nombre, %(fecha)s, %(hora)s, %(personas)s
  FROM actividad a
 WHERE a.nombre = %(actividad)s AND a.cupo_por_turno >= %(personas)s
ON CONFLICT (actividad, fecha, hora) DO UPDATE
   SET personas = ocupacion.personas + EXCLUDED.personas
 WHERE ocupacion.personas + EXCLUDED.personas
       <= (SELECT cupo_por_turno FROM actividad WHERE nombre = EXCLUDED.actividad)
RETURNING personas
"""


class RepositorioPostgres:
    """Repositorio de inscripciones sobre PostgreSQL (SQL plano con psycopg, sin ORM)."""

    def __init__(self, url):
        self._url = url

    def _conectar(self):
        return psycopg.connect(self._url)

    def cargar_actividades(self, actividades):
        """Carga (o actualiza) el catalogo de actividades."""
        with self._conectar() as conexion:
            for actividad in actividades.values():
                conexion.execute(
                    """
                    INSERT INTO actividad (nombre, cupo_por_turno, edad_minima, requiere_talla,
                                           terminos_version, terminos_texto)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (nombre) DO UPDATE SET
                        cupo_por_turno = EXCLUDED.cupo_por_turno,
                        edad_minima = EXCLUDED.edad_minima,
                        requiere_talla = EXCLUDED.requiere_talla,
                        terminos_version = EXCLUDED.terminos_version,
                        terminos_texto = EXCLUDED.terminos_texto
                    """,
                    (
                        actividad.nombre,
                        actividad.cupo_por_turno,
                        actividad.edad_minima,
                        actividad.requiere_talla,
                        actividad.terminos.version,
                        actividad.terminos.texto,
                    ),
                )

    def actividad(self, nombre):
        with self._conectar() as conexion:
            fila = conexion.execute(
                """
                SELECT cupo_por_turno, edad_minima, requiere_talla, terminos_version, terminos_texto
                  FROM actividad WHERE nombre = %s
                """,
                (nombre,),
            ).fetchone()
            if fila is None:
                raise ActividadNoEncontradaError(nombre)
            cupo, edad_minima, requiere_talla, version, texto = fila
            actividad = Actividad(
                nombre,
                cupo_por_turno=cupo,
                edad_minima=edad_minima,
                requiere_talla=requiere_talla,
                terminos=TerminosYCondiciones(nombre, version, texto),
            )
            ocupaciones = conexion.execute(
                "SELECT fecha, hora, personas FROM ocupacion WHERE actividad = %s", (nombre,)
            )
            for fecha, hora, personas in ocupaciones:
                actividad.registrar_ocupacion(Horario(fecha, hora), personas)
            return actividad

    def siguiente_codigo(self):
        with self._conectar() as conexion:
            numero = conexion.execute("SELECT nextval('inscripcion_codigo_seq')").fetchone()[0]
        return f"INS-{numero:04d}"

    def guardar(self, inscripcion):
        """Reserva el cupo y guarda la inscripcion y sus visitantes en una sola transaccion."""
        try:
            self._guardar(inscripcion)
        except psycopg.errors.UniqueViolation as error:
            if error.diag.constraint_name == "un_dni_por_horario":
                raise DniYaInscriptoError(error.diag.message_detail) from error
            raise

    def _guardar(self, inscripcion):
        horario = inscripcion.horario
        with self._conectar() as conexion:  # si algo falla se hace rollback de todo
            reserva = conexion.execute(
                _RESERVAR_CUPO,
                {
                    "actividad": inscripcion.actividad.nombre,
                    "fecha": horario.fecha,
                    "hora": horario.hora_inicio,
                    "personas": len(inscripcion.visitantes),
                },
            ).fetchone()
            if reserva is None:
                raise CupoInsuficienteError(inscripcion.actividad.nombre)
            conexion.execute(
                """
                INSERT INTO inscripcion (codigo, actividad, fecha, hora, email_de_contacto,
                                         terminos_version, confirmada_el)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    inscripcion.codigo,
                    inscripcion.actividad.nombre,
                    horario.fecha,
                    horario.hora_inicio,
                    inscripcion.email_de_contacto,
                    inscripcion.terminos_aceptados.version,
                    inscripcion.confirmada_el,
                ),
            )
            for posicion, visitante in enumerate(inscripcion.visitantes, start=1):
                conexion.execute(
                    """
                    INSERT INTO visitante_inscripto (inscripcion, posicion, nombre, dni, edad, talla,
                                                     fecha, hora)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        inscripcion.codigo,
                        posicion,
                        visitante.nombre,
                        visitante.dni,
                        visitante.edad,
                        visitante.talla,
                        horario.fecha,
                        horario.hora_inicio,
                    ),
                )

    def obtener(self, codigo):
        with self._conectar() as conexion:
            fila = conexion.execute(
                """
                SELECT actividad, fecha, hora, email_de_contacto, terminos_version, confirmada_el
                  FROM inscripcion WHERE codigo = %s
                """,
                (codigo,),
            ).fetchone()
            if fila is None:
                return None
            visitantes = conexion.execute(
                """
                SELECT nombre, dni, edad, talla FROM visitante_inscripto
                 WHERE inscripcion = %s ORDER BY posicion
                """,
                (codigo,),
            ).fetchall()
        nombre_actividad, fecha, hora, email, version, confirmada_el = fila
        actividad = self.actividad(nombre_actividad)
        inscripcion = Inscripcion(
            actividad=actividad,
            horario=Horario(fecha, hora),
            visitantes=[Visitante(*datos) for datos in visitantes],
            email_de_contacto=email,
            terminos_aceptados=TerminosYCondiciones(
                nombre_actividad, version, actividad.terminos.texto
            ),
        )
        inscripcion.codigo = codigo
        inscripcion.estado = EstadoDeLaInscripcion.CONFIRMADA
        inscripcion.confirmada_el = confirmada_el
        return inscripcion

    def dni_inscripto_en(self, dni, horario):
        with self._conectar() as conexion:
            fila = conexion.execute(
                "SELECT 1 FROM visitante_inscripto WHERE dni = %s AND fecha = %s AND hora = %s",
                (dni, horario.fecha, horario.hora_inicio),
            ).fetchone()
        return fila is not None

    def inscripciones(self):
        with self._conectar() as conexion:
            codigos = [
                fila[0]
                for fila in conexion.execute("SELECT codigo FROM inscripcion ORDER BY codigo")
            ]
        return [self.obtener(codigo) for codigo in codigos]
