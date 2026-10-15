# TP6 – Partición de equivalencias corregida: "Inscribirse a actividad"

**Grupo 8** · ISW 4K3 · 2026 · versión corregida con las respuestas del PO del 2026-10-15
Versión original: la del grupo (antes de las respuestas). Acá se listan primero **qué se corrigió** y después el cuadro completo.

## 1. Qué había que corregir

| # | Observación sobre la versión original | Corrección |
|---|---|---|
| 1 | **Horario**: se pedía "fecha mayor o igual a la actual". Ahora hay una **ventana**: solo desde 24 h antes hasta 15 min antes del turno `[PO #23, #30]`. | Se reemplaza por clases de ventana (válida / demasiado pronto / demasiado tarde o pasada). |
| 2 | Faltaba que el horario debe ser **un turno**: en punto, entre 9:00 y 17:00. A las 18:00 no hay turno `[PO #12]`. | Nueva clase inválida: hora que no es turno. |
| 3 | "Fecha en el que el parque está cerrado": ahora se sabe cuándo: **lunes, 25/12 y 1/1** `[PO #1]`. | Se detallan las clases. |
| 4 | "Fecha en la que la actividad no está disponible" no tiene definición del PO (P18). | Se mantiene como clase, marcada *pendiente*. |
| 5 | **Cantidad de personas**: además de 1–10, el **cupo restante** del turno limita (8, 10 o 12 según actividad) `[PO #13]`. Y la cantidad debe coincidir con los visitantes cargados. | Nuevas clases: supera el cupo; no coincide con los datos cargados. |
| 6 | **Edad**: la mínima depende de la actividad: Palestra 12, Tirolesa 8, resto todas `[PO #15]`. Además "todas las edades" incluye 0 años, y el límite superior de 100 es una suposición del grupo, no del PO. | Se agrega la clase "menor a la edad mínima de la actividad"; el rango pasa a 0–100. |
| 7 | **Talla**: solo se pide en **Palestra y Tirolesa** `[PO #9]`; los valores son XS–XXL `[PO #14]`. Faltaba la clase "la actividad no la pide". | Se separan los casos según la actividad. |
| 8 | **DNI**: la clase "numero con formato invalido" estaba **repetida**. Y falta el conflicto de horario `[PO #29]`. | Se elimina la repetición; nueva clase "DNI ya inscripto en ese horario". |
| 9 | **Nombre**: el máximo de 30 caracteres y "alfanumérico" son suposiciones del grupo (el PO no los definió; `[PO #22]` es ambiguo, ver P22). Un nombre real lleva letras, espacios, tildes y apóstrofes, no números. | Se marca *provisorio*; el valor límite 30 se conserva hasta que el PO responda. |
| 10 | **Usuario logueado**: el PO nunca dijo que se requiera login (P02 abierta). | Se marca *pendiente (P02)*; se mantiene como clase para no perderla. |
| 11 | **T&C**: falta la clase "aceptó los T&C de **otra** actividad" `[PO #16]`. | Nueva clase inválida. |
| 12 | **Salida**: el email lleva **un QR por visitante**, todos en el mismo mensaje `[PO #28]`. | Se detalla la clase de salida y se agrega la clase inválida "email con menos QR que visitantes". |

## 2. Cuadro corregido

### Condiciones de entrada

| Condición externa | Clases válidas | Clases inválidas |
|---|---|---|
| **Usuario** *(pendiente P02)* | Visitante (logueado, si se exige login) | Usuario no logueado · usuario logueado con perfil distinto al de visitante |
| **Fecha y hora del turno** | Turno (fecha y hora en punto entre 9:00 y 17:00) de un día en que el parque abre, **a entre 24 h y 15 min de distancia** del momento actual | Valor vacío · formato inválido · hora que no es turno (p. ej. 10:30, 8:00, 18:00) · lunes · 25/12 · 1/1 · turno a **menos de 15 min** o ya pasado · turno a **más de 24 h** · actividad no disponible en ese horario *(pendiente P18)* |
| **Actividad** | Una de Tirolesa, Safari, Palestra o Jardinería, **con cupo para el turno** | No selecciona · selección múltiple · actividad fuera de la lista · actividad sin cupo en el turno |
| **Cantidad de personas** | Entero de 1 a 10 y **no mayor al cupo restante** del turno, igual a la cantidad de visitantes cargados | Vacío · formato inválido · entero ≤ 0 · entero > 10 · mayor al cupo restante · distinta de la cantidad de visitantes cargados |
| **Nombre del visitante** *(provisorio)* | Cadena de 1 a 30 caracteres, solo letras (con tildes), espacios y apóstrofe | Vacío · solo espacios · caracteres inválidos (dígitos, símbolos) · más de 30 caracteres |
| **DNI del visitante** | Entero de 7 u 8 dígitos, **no inscripto en otro turno del mismo horario** y no repetido en la inscripción | Vacío · formato inválido (letras, puntos) · 6 o menos dígitos · 9 o más dígitos · DNI ya inscripto en ese horario (en cualquier actividad) · DNI repetido en la misma inscripción |
| **Edad del visitante** | Entero de 0 a 100 **y mayor o igual a la edad mínima de la actividad** (Tirolesa 8, Palestra 12, resto sin mínimo) | Vacío · formato inválido · entero < 0 · entero > 100 · menor a la edad mínima de la actividad |
| **Talla de vestimenta** | *Actividad que la requiere (Tirolesa, Palestra):* XS, S, M, L, XL o XXL · *Actividad que no la requiere:* sin talla | *Requerida:* no selecciona · valor fuera de la lista · selección múltiple · *No requerida:* (cualquier talla se ignora, no es inválida) |
| **Términos y condiciones** | Acepta los T&C **de la actividad elegida** | No acepta · acepta los de **otra** actividad · cualquier otro valor |
| **Email de contacto** *(pendiente P01)* | Dirección con formato válido | Vacío · formato inválido |

### Condiciones de salida

| Condición | Clases válidas | Clases inválidas |
|---|---|---|
| **Email de confirmación** | Un email con el resumen de la inscripción y **un QR por visitante** | Email con menos QR que visitantes · email sin resumen · email no enviado (comportamiento pendiente, P13b) |
| **Cupo del turno** | Se descuenta exactamente la cantidad de personas inscriptas | Se descuenta de más o de menos · se descuenta en una inscripción rechazada |

## 3. Valores límite (para los casos de prueba)

| Variable | Valores |
|---|---|
| Anticipación del turno | 24 h 1 min (✗) · **24 h (✓)** · 15 min (✓) · 14 min (✗) |
| Hora del turno | 8:00 (✗) · **9:00 (✓)** · 17:00 (✓) · 18:00 (✗) |
| Cantidad de personas | 0 (✗) · **1 (✓)** · 10 (✓) · 11 (✗) · y contra el cupo: cupo (✓) · cupo + 1 (✗) |
| Cupo restante | 0 (✗) · 1 (✓ con 1 persona) |
| DNI (dígitos) | 6 (✗) · **7 (✓)** · 8 (✓) · 9 (✗) |
| Edad | −1 (✗) · **0 (✓ en Safari/Jardinería)** · 100 (✓) · 101 (✗) |
| Edad mínima Tirolesa | 7 (✗) · 8 (✓) |
| Edad mínima Palestra | 11 (✗) · 12 (✓) |
| Nombre (caracteres) | 0 (✗) · 1 (✓) · 30 (✓) · 31 (✗) |

Estos valores se ejecutan en el plan de pruebas: [plan-pruebas-tdd-tp-6.md](plan-pruebas-tdd-tp-6.md).
