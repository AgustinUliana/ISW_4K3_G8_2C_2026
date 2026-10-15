# TP6 – Preguntas para el Product Owner

**User Story:** Inscribirme a actividad (EcoHarmony Park) · **Grupo 8** · ISW 4K3 · 2026
**Estado:** respuestas del PO recibidas el 2026-10-15 · algunas preguntas siguen abiertas
**Documento hermano:** [plan-pruebas-tdd-tp-6.md](plan-pruebas-tdd-tp-6.md)

Los IDs `P01…P21` son los del plan de pruebas (columna *PO*). Las respuestas del PO vienen numeradas con
la lista de consultas del grupo; acá se indica entre paréntesis como `[PO #n]`.

## 1. Respuestas recibidas

| ID | Tema | Respuesta del PO | Efecto en las pruebas |
|---|---|---|---|
| **P03** | Fecha de la inscripción | `[PO #23]` Solo se puede reservar **dentro de las 24 h previas al turno**. No se puede inscribir a una actividad del viernes un martes. `[PO #2]` Un día de parque cerrado se muestra **deshabilitado** en el calendario. | Ventana de inscripción (HOR-04..06, INS-06, INS-06b, CAT-06). |
| **P04** | Horarios y días | `[PO #1]` Abre todos los días **menos lunes, 25/12 y 1/1**. `[PO #11]` Parque **8:30 a 19:00**. `[PO #12]` Actividades **9 a 18**, un turno por hora; **a las 18:00 no hay turno** (es la cota superior). Turnos: 9, 10, …, 17. | PAR-01..07, HOR-01..03, ACT-05. |
| **P05** | Cierre de inscripción | `[PO #30]` Se cierra **15 minutos antes** del inicio del turno. | HOR-04..06, INS-06b, SRV-08. |
| **P06** | Cupos | `[PO #13]` **Safari 8, Palestra 12, Jardinería 12, Tirolesa 10** (por turno). `[PO #20]` No hay máximo de visitantes por día. Cupos visibles para el usuario. | Fixtures §3, CAT-08. |
| **P08** | Máximo por inscripción | `[PO #31]` **10 personas.** | INS-10. |
| **P09** | Tallas | `[PO #9]` Requieren vestimenta **Palestra y Tirolesa**. `[PO #14]` Talles **XS, S, M, L, XL, XXL**. | ACT-10, VIS-10..13. |
| **P10** (edad) | Edades mínimas | `[PO #15]` Jardinería y Safari: **todas las edades**. Palestra: **12 o más**. Tirolesa: **8 o más**. | ACT-12, VIS-09. |
| **P11** | Documento | `[PO #32]` **Solo DNI** (7 u 8 dígitos). | VIS-05, VIS-06. |
| **P12** | QR | `[PO #28]` **Un QR por cada entrada (visitante)**, todos **dentro del mismo email**. | QR-01..06, EML-06, SRV-04. |
| **P13** (canal) | Email | `[PO #5]` El email debe estar **desarrollado, no simulado**: "simple y gratuito". | Ver §3 (decisión técnica del grupo). |
| **P14** | Contenido del email | `[PO #28]` Resumen de la inscripción y los QR. `[PO #18]` (pregunta genérica) menciona "subtotales y total": **las actividades no tienen precio definido**, ver P17. | EML-02..06. |
| **P15** (parcial) | T&C | `[PO #16]` **Uno distinto por actividad**; los diseña el grupo y **no se envían a validar** `[PO #17]`. | ACT-11, INS-14. |
| **P16** | Duplicados | `[PO #29]` Una persona **no puede tener inscripciones en otros turnos del mismo horario** (en ninguna actividad). | INS-12, REP-07, SRV-13. |
| **P19** (parcial) | Flujo | Primero actividad, después horario (decisión del grupo). Visibilidad de cupos: "el usuario puede ver cupos disponibles". | CAT-04, CAT-07, CAT-08. |
| – | Dispositivo | `[PO #24]` App **mobile**; el grupo la hace **web responsive con React**. | Fuera de este plan (front). |
| – | Identidad visual | `[PO #3]` Paleta `386641 · 6A994E · A7C957 · F2E8CF · BC4749`, fuente **Lato**. `[PO #17]` El logo lo diseña el grupo. | Fuera de este plan (front). |

## 2. Supuestos que tomamos sobre las respuestas (confirmar si hay dudas)

| Tema | Supuesto | Motivo |
|---|---|---|
| Borde de las 24 h | Se puede inscribir **exactamente** 24 h antes (límite inclusivo). | "Dentro de las 24 h antes". |
| Borde de los 15 min | Se puede inscribir **hasta exactamente** 15 min antes (inclusivo); 14 min antes ya no. | "De 15 minutos antes del inicio". |
| Turno del día en curso | El horario "ya comenzó" cae dentro de la regla de los 15 min (queda cerrado). | Un turno pasado está a menos de 15 min. |
| Conflicto de horario `[PO #29]` | Se compara por **DNI** y por **fecha + hora** de inicio, en cualquier actividad, y también dentro de la misma inscripción. | "No tenga inscripciones en otros turnos del mismo horario". |
| Cupo | Se mide en **personas**, por actividad + fecha + hora. | `[PO #13]`. |

## 3. Decisiones del grupo sobre las preguntas pendientes (2026-10-15)

Quedaron resueltas por decisión del grupo (no por el PO). Si el PO contradice alguna, se ajusta el dato o la
prueba correspondiente.

| ID | Decisión | Efecto |
|---|---|---|
| **P01** | El email de contacto es **el email con el que se registró el usuario**. | La solicitud lleva al usuario; el formulario no pide email. INS-16 se reemplaza por una regla sobre el usuario. |
| **P02** | **Sí hay registro e inicio de sesión, pero simple**: email + contraseña que coincidan, y nada más. | Nuevo grupo de pruebas USU (registro, login, sesión) y tabla de usuarios. INS-20 pasa a ser obligatoria. |
| **P07** | **Todo o nada**: si no entra todo el grupo, no se inscribe. La pantalla debería permitir elegir solo hasta el cupo disponible. | Ya implementado (`SIN_CUPO`). CAT-08 (cupo restante visible) lo necesita el front para limitar la cantidad. |
| **P13b** | El email "no tendría por qué fallar". Se mantiene la defensa actual: si fallara, la inscripción queda confirmada y se informa `email_enviado=False`. | Sin cambios (SRV-15). |
| **P17** | **Sin costo.** El email no lleva totales. | Sin cambios. |
| **P22** | **El nombre del visitante no es opcional.** Se revisará más adelante. | Sin cambios (VIS-02/03). |

### Siguen abiertas (baja prioridad)

| ID | Pregunta | Si no responde, asumimos |
|---|---|---|
| **P10b** | Menores de edad: ¿adulto responsable? ¿quién acepta los T&C? | Sin adulto responsable. |
| **P12b** | ¿Qué codifica el QR y quién lo valida? | Código de reserva + número de visitante. |
| **P15b** | ¿T&C una vez por inscripción o por visitante? | Una por inscripción, con versión y momento. |
| **P18** | ¿Cómo se marca una actividad "no disponible"? | Sin turno cargado. |
| **P19b** | Turno sin cupo: ¿oculto o deshabilitado? | Deshabilitado, mostrando `0`. |
| **P20** | ¿Cancelar o modificar inscripciones? | Fuera de alcance. |
| **P21** | ¿Pantalla de confirmación con qué datos? | Resumen, código de reserva y QR. |

## 4. Decisión técnica del grupo: el email

El PO pide email **real y gratuito** `[PO #5]`. Opciones (según el documento previo del grupo; **verificar
límites vigentes** al implementar):

- **Gmail SMTP** con contraseña de aplicación: lo más simple, sin registrarse en otro servicio, ~500 correos/día.
- **Brevo**: plan gratuito permanente, ~300 correos/día, SDK de Python.

Se decide al llegar al Grupo 7/10; hasta entonces `ServicioEmail` es una interfaz con dobles.
