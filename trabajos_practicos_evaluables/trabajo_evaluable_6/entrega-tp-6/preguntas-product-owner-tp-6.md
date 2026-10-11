# TP6 – Preguntas para el Product Owner

**User Story:** Inscribirme a actividad (EcoHarmony Park) · **Grupo 8** · ISW 4K3 · 2026
**Estado:** lista para llevar a la consulta · 2026-10-11
**Documento hermano:** [plan-pruebas-tdd-tp-6.md](plan-pruebas-tdd-tp-6.md)

Cada pregunta tiene: qué hay que decidir, **por qué importa** (qué pruebas cambian) y **qué vamos a
asumir si no hay respuesta**, para no quedar bloqueados. La última columna queda vacía para anotar lo
que conteste el PO. Los IDs (`P01`…) son los que aparecen en la columna *PO* del plan de pruebas.

## Si hay poco tiempo: las 8 imprescindibles

**P01, P02, P03, P04, P05, P09, P12, P13.** Son las que cambian el resultado esperado de más pruebas
o la forma del sistema (a quién se manda el email, cuándo se puede inscribir, qué contiene el QR).

## Lo que ya está claro (no hace falta preguntar)

Tomado del enunciado del TP2 y de los criterios de aceptación:

- Las actividades son **Tirolesa, Safari, Palestra y Jardinería**, de **una hora** de duración.
- Los datos por visitante son **nombre, DNI, edad y talla** (esta última solo si la actividad la pide).
- Hay que **aceptar los T&C específicos de la actividad**.
- Al terminar se envía un **email con el resumen y un QR**.
- Los **cupos son limitados** y los **administradores** los mantienen **por fuera de la aplicación**.
- El flujo es **primero la actividad, después el horario** (decisión del grupo, 2026-10-11).

---

## Prioridad alta

| ID | Pregunta | Por qué importa / pruebas afectadas | Si no responde, asumimos | Respuesta del PO |
|---|---|---|---|---|
| **P01** | Los datos que se piden del visitante son nombre, DNI, edad y talla, pero **no hay email**. Sin embargo, el resumen se envía "al mail del visitante". ¿**De dónde sale el email**? ¿Se pide un email de contacto en el formulario de inscripción, o sale de la cuenta del usuario? Si se inscriben 4 personas, ¿se manda **un solo email** a quien inscribe o **uno por persona**? | Define el destinatario y si hay un campo más en el formulario. INS-16, EML-01, SRV-05. | Se pide **un email de contacto** al inscribir, y se manda **un solo email** con toda la inscripción. | |
| **P02** | Para **comprar entradas** hay que estar registrado (mail y contraseña). Para **inscribirse a una actividad**, ¿el visitante también debe estar **registrado / logueado**, o puede inscribirse sin cuenta? ¿Hace falta haber **comprado la entrada** del día? | Si exige registro, se agrega una regla y una dependencia con la US de compra. INS-20. | **No** requiere registro ni entrada comprada. | |
| **P03** | ¿La inscripción es **solo para el día actual** o se puede elegir una **fecha futura**? Si es futura, ¿**con cuánta anticipación máxima**? (Miguel dijo que sirve "para planificarlas con anterioridad".) | Cambia si el horario incluye fecha y qué rango se valida. Afecta `Horario`, CAT-04..06 y todos los datos de prueba. | Se elige **fecha desde hoy**, **sin límite superior** de anticipación. | |
| **P04** | ¿Cuál es el **horario de apertura y cierre** del parque, y **qué días está cerrado**? Las actividades duran 1 hora: ¿las franjas son **fijas e iguales para todas** (por ejemplo 09:00, 10:00, 11:00…) o **cada actividad tiene sus propios horarios**? | Es la base de "parque cerrado" y de los valores límite. PAR-01..06, HOR-01..03, CAT-05, INS-05. | Abre **09:00**, cierra **18:00**, cerrado los **lunes**; franjas de 1 h en punto, iguales para todas. | |
| **P05** | ¿**Hasta cuándo** se puede inscribir a un horario? ¿Hasta que **comienza**, hasta **X minutos antes**, o solo se permite inscribirse **el día anterior**? ¿Se puede inscribir a un horario que ya pasó el mismo día? | Define el borde exacto de "horario pasado". HOR-04, INS-06, CAT-06, SRV-08. | Se puede hasta el **instante de inicio** (a las 10:00 ya no se puede para las 10:00). | |
| **P09** | ¿**Qué actividades piden talla** de vestimenta? ¿Qué **talles** son válidos (XS–XL, numéricos, talles infantiles)? Si una actividad no la pide pero el usuario carga una talla, ¿se **ignora** o se **rechaza**? | Define `requiere_talla` y los valores permitidos. ACT-10, VIS-10..13, SRV-11..12, ACE-03, ACE-06. | Tirolesa y Palestra sí; Safari y Jardinería no. Talles `XS, S, M, L, XL`. Si sobra, se ignora. | |
| **P12** | El QR: ¿**un QR por inscripción o uno por persona**? ¿**Qué debe codificar** (un código de reserva, o datos de las personas)? ¿**Quién lo escanea** y para qué (control de ingreso a la actividad)? ¿Debe ser de **uso único**? | Define el contenido del QR y cuántos se generan. QR-01..05, SRV-04. | **Un QR por inscripción**, con un código de reserva opaco (sin datos personales) que el personal valida contra el sistema. | |
| **P13** | Si la inscripción es válida pero **falla el envío del email** (servidor caído, mail inexistente): ¿la inscripción **queda confirmada igual**? ¿Se muestra el QR **en pantalla** o se ofrece **reenviar** el email? | Define el comportamiento ante fallas. SRV-15, SRV-16. | La inscripción **queda confirmada**, se informa que el email no pudo enviarse y el QR se muestra en pantalla. | |

## Prioridad media

| ID | Pregunta | Por qué importa / pruebas afectadas | Si no responde, asumimos | Respuesta del PO |
|---|---|---|---|---|
| **P06** | ¿Cuál es el **cupo** por actividad y horario? ¿Es el **mismo para todas** o distinto por actividad? ¿El cupo se cuenta en **personas** (no en inscripciones)? | Datos de ACT-01..09 y del *seed* (REP-06). | **10 personas** por actividad y horario, contadas por persona. | |
| **P07** | Si un grupo pide **4 lugares y quedan 3**, ¿se **rechaza toda la inscripción** o se ofrece inscribir a 3? | INS-08, ACT-03. | **Todo o nada:** se rechaza y se informa cuántos lugares quedan. | |
| **P08** | ¿Hay un **máximo de personas por inscripción**, más allá del cupo? (Para las entradas es 10.) | INS-10. | Sin máximo propio: lo limita el cupo. | |
| **P10** | ¿Hay **edad mínima o máxima** por actividad (por ejemplo para Tirolesa o Palestra)? Para **menores de edad**: ¿necesitan un **adulto responsable** inscripto? ¿Quién acepta los T&C por ellos? | ACT-12, VIS-09. | Edad válida de 0 a 120; **sin** restricción por actividad ni adulto responsable. | |
| **P11** | **DNI:** ¿solo argentino (7 u 8 dígitos) o también **extranjeros** (pasaporte, otros documentos)? ¿Se carga con puntos? | VIS-05, VIS-06. | Solo DNI argentino, **7 u 8 dígitos**, sin puntos. | |
| **P14** | ¿Qué **información debe llevar el email**? (actividad, fecha, hora, cantidad de personas, nombre de cada persona, código de reserva en texto, T&C, recomendaciones, ubicación de la actividad). | EML-02..05. | Actividad, fecha, horario, cantidad y nombres de las personas, código de reserva en texto y el QR. | |
| **P15** | **Términos y condiciones:** ¿**quién redacta** el texto de cada actividad? ¿Se aceptan **una vez por inscripción** (el titular acepta por todos) o **cada visitante**? ¿Hace falta **guardar evidencia** de la aceptación (versión + fecha y hora)? | ACT-11, INS-13..15, INS-18. | Textos de ejemplo propios; **una aceptación por inscripción**; se guarda **versión y momento**. | |
| **P16** | **Duplicados:** ¿puede la **misma persona (DNI)** estar dos veces en la misma inscripción? ¿Y en **el mismo horario de la misma actividad** en dos inscripciones distintas? ¿Y en **dos actividades distintas al mismo horario** (se superponen)? ¿Hay un **límite de actividades por persona por día**? | INS-12, REP-07, SRV-13. | Se rechaza el DNI repetido en la misma inscripción y en la misma actividad y horario. Sin otros límites. | |
| **P19** | **Parcialmente resuelta:** el grupo confirmó que **primero se elige la actividad y después el horario**. Queda por confirmar con el PO: las actividades sin ningún horario con cupo y los horarios **sin cupo**, ¿se **ocultan** o se muestran **deshabilitados** ("Agotado")? | CAT-04, CAT-07, API-04..05. | **Deshabilitados** ("Agotado"): la actividad figura con `disponible=False` y el horario agotado se muestra marcado. | |

## Prioridad baja

| ID | Pregunta | Por qué importa / pruebas afectadas | Si no responde, asumimos | Respuesta del PO |
|---|---|---|---|---|
| **P17** | ¿Las actividades tienen **costo adicional** o están **incluidas en la entrada**? | Si hay costo, aparece una integración de pago. Hoy no está en el alcance. | Sin costo. | |
| **P18** | El criterio dice "horario en que el parque está cerrado **o la actividad no está disponible**". ¿Cuándo una actividad "no está disponible"? (mantenimiento, clima, sin horarios cargados). ¿**Cómo** lo marcan los administradores? Si ya había inscriptos, ¿hay que **avisarles**? | INS-04, ACE-04. | "No disponible" = **no tiene horario cargado**; avisar a inscriptos queda **fuera de alcance**. | |
| **P20** | ¿Hay que poder **cancelar o modificar** una inscripción? ¿Y **reenviar** el email? | Agrandaría el alcance. | **Fuera de alcance** de esta US. | |
| **P21** | Al finalizar, el criterio solo habla del email. ¿Debe mostrarse además una **pantalla de confirmación** (qué datos)? | SRV-01, API-01. | Sí: resumen (actividad, fecha, horario, cantidad) y código de reserva. | |

---

## Cómo registrar las respuestas

1. Anotar la respuesta en la última columna, con la fecha y quién la dio.
2. Si difiere del supuesto, actualizar el **dato del *fixture*** (plan de pruebas, §3) y las pruebas marcadas con ese `P`.
3. Si la respuesta **agrega una regla nueva** que ninguna prueba cubre, escribir la prueba en el plan antes de tocar código (Test List de Beck).
4. Cuando todas las de prioridad alta estén respondidas, se puede empezar el ciclo Red-Green-Refactor.
