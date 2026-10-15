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

## 3. Preguntas que siguen abiertas

| ID | Prioridad | Pregunta | Si no responde, asumimos | Respuesta del PO |
|---|---|---|---|---|
| **P01** | Alta | ¿A **qué email** se envía? Los datos del visitante no incluyen email. ¿Se pide un email de contacto en el formulario? | Un **email de contacto** obligatorio en el formulario; un solo email por inscripción. | |
| **P02** | Alta | ¿El visitante debe estar **registrado / logueado** para inscribirse? | **No** requiere registro. | |
| **P07** | Media | Si piden 4 lugares y quedan 3, ¿se rechaza todo o se ofrecen 3? | **Todo o nada.** | |
| **P10b** | Media | **Menores de edad:** ¿necesitan adulto responsable inscripto? ¿Quién acepta los T&C por ellos? | Sin adulto responsable. | |
| **P13b** | Alta | Si el **envío del email falla**, ¿la inscripción queda confirmada? ¿Se muestra el QR en pantalla? | Queda confirmada, se informa el fallo y se muestran los QR en pantalla. | |
| **P12b** | Media | ¿Qué debe **codificar** el QR y quién lo valida? ¿Uso único? | Código de reserva + número de visitante, sin datos personales. | |
| **P15b** | Baja | ¿Los T&C se aceptan **una vez por inscripción** o por visitante? ¿Se guarda evidencia (versión y fecha)? | Una aceptación por inscripción; se guarda versión y momento. | |
| **P17** | Media | `[PO #18]` habla de "subtotales y total". ¿Las actividades **tienen costo**? | **Sin costo.** El email no lleva totales. | |
| **P18** | Baja | ¿Cómo se marca una actividad "no disponible" (clima, mantenimiento)? | No disponible = sin turno cargado. | |
| **P19b** | Baja | Un turno **sin cupo**: ¿se oculta o se muestra deshabilitado ("Agotado")? | Deshabilitado, mostrando `0` cupos. | |
| **P20** | Baja | ¿Se pueden cancelar / modificar inscripciones? | Fuera de alcance. | |
| **P21** | Baja | Al terminar, ¿pantalla de confirmación con qué datos? | Resumen + código de reserva + QR. | |
| **P22** | Media | `[PO #22]` "¿Pueden agregar el nombre de la persona de la actividad? Sí, **pero opcional**." Es ambiguo: ¿el **nombre del visitante** pasa a ser opcional, o es un dato adicional? | El **nombre del visitante sigue siendo obligatorio** (lo exige el criterio de aceptación). | |

## 4. Decisión técnica del grupo: el email

El PO pide email **real y gratuito** `[PO #5]`. Opciones (según el documento previo del grupo; **verificar
límites vigentes** al implementar):

- **Gmail SMTP** con contraseña de aplicación: lo más simple, sin registrarse en otro servicio, ~500 correos/día.
- **Brevo**: plan gratuito permanente, ~300 correos/día, SDK de Python.

Se decide al llegar al Grupo 7/10; hasta entonces `ServicioEmail` es una interfaz con dobles.
