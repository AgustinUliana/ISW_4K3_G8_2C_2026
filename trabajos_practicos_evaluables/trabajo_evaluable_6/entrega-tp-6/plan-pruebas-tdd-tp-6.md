# TP6 – TDD: Plan de pruebas (Test List)

**User Story:** Inscribirme a actividad (EcoHarmony Park) · **Grupo 8** · ISW 4K3 · 2026
**Estado:** v0.4 – dominio, servicio, base PostgreSQL y adaptadores implementados con TDD · 2026-10-15 (ver §11)
**Documento hermano:** [preguntas-product-owner-tp-6.md](preguntas-product-owner-tp-6.md)
**Consigna:** [consigna-tp-6.pdf](../consigna-tp-6.pdf)

**Cambios de la v0.3 (respuestas del PO, ver [preguntas-product-owner-tp-6.md](preguntas-product-owner-tp-6.md)):** fixtures reales (horarios, cupos, edades, talles); ventana de inscripción de 24 h a 15 min; **un QR por visitante** en un mismo email; conflicto de horario por DNI en cualquier actividad; máximo 10 personas; sólo DNI (7–8 dígitos).

**Cambios de la v0.2:** base de datos **PostgreSQL** (en lugar de SQLite) para poder abrirla con DBeaver;
flujo de selección confirmado (**primero la actividad, después el horario**); política de dobles de prueba
y orden de los primeros ciclos ajustados a la bibliografía de la cátedra (Beck y Ble, ver §1);
sección nueva sobre dónde va el código (§9).

> COMO visitante QUIERO inscribirme a una actividad PARA reservar mi lugar en la misma.

---

## 1. Qué es este documento

Es la **Test List** de Kent Beck (*Test-Driven Development by Example*): la lista de todo lo que creemos
que hay que probar, ordenada de lo más simple a lo más complejo. Extiende y reemplaza a
`tests2-unitarios-tp6-inscribirme-actividad.md` (el borrador previo del grupo), incorporando lo que
faltaba para llegar a un sistema funcional de punta a punta: **persistencia (base de datos)**, la
construcción del **mensaje de email**, el **contenido del QR**, la **hora actual** y las dudas que hoy
tenemos con el PO.

Reglas de uso (Beck):

- La lista **no es un contrato cerrado**: al implementar van a aparecer pruebas nuevas, se anotan en la
  lista *antes* de escribir código (ver §8).
- Se toma **una prueba a la vez**, la más simple que quede (*Starter Test* / *One Step Test*), nunca la más completa.
- Ciclo: **Red** (falla por la razón correcta) → **Green** (código mínimo: *Fake It*, *Triangulation* u
  *Obvious Implementation*) → **Refactor** (sin agregar comportamiento, con todo en verde).
- Cada prueba se escribe empezando por el `assert` (*Assert First*) y con **datos evidentes**
  (*Evident Data*): cupo 10, piden 3 → quedan 7, el vínculo entre entrada y salida se ve a simple vista.

Bibliografía usada (carpeta `material_de_catedra/bibliografia/tdd/`): **Beck, *Test-Driven Development by
Example*** (patrones de los caps. 29–31: *One Step Test*, *Starter Test*, *Child Test*, *Mock Object*,
*Crash Test Dummy*, *Log String*, *Clean Check-in*, *Fake It*, *Triangulate*, *Obvious Implementation*) y
**Ble, *Diseño Ágil con TDD*** (cap. 3 ATDD, cap. 6 dobles de prueba, caps. 8–9 proyecto de ejemplo).

## 2. Convenciones

### 2.1 Identificadores y categorías

Cada prueba tiene un ID `GRUPO-NN`. La columna **Cat.** indica qué tipo de prueba es:

| Cat. | Tipo | Qué puede usar | Cuándo corre |
|---|---|---|---|
| **U** | Unitaria | Solo objetos del dominio y *test doubles*. Sin red, sin disco, sin reloj real. | Siempre (`pytest`) |
| **C** | Contrato / integración local | Cosas locales y gratuitas: librería `qrcode` y **PostgreSQL local** (base de pruebas `ecoharmony_test`, ver §9.1). Sin internet. | Con la base levantada (marcadores `@pytest.mark.local` y `@pytest.mark.db`); si no hay base, se saltean con un mensaje claro |
| **X** | Externa | Servicio real (email real a una casilla de prueba). | Manual, antes de la entrega (`@pytest.mark.externa`); **no** forma parte de esta lista |

La columna **PO** indica de qué pregunta depende el resultado esperado (ver el documento de preguntas).
Una prueba con PO marcado usa un **valor provisorio** (§3): si el PO responde otra cosa, cambia el dato
del *fixture*, no la prueba.

### 2.2 Principio de diseño que permite esto

Todo lo que el PO puede cambiar (horario de apertura, cupo, tallas, edades, máximo de personas…) se
**inyecta como configuración** (constructor / fixture), nunca se escribe fijo en la lógica. Así las
respuestas del PO se absorben cambiando datos, no reescribiendo tests.

### 2.2.1 Política de dobles de prueba

Siguiendo a Ble (cap. 6, regla de Freeman: *stubs para consultas, mocks para acciones*) y a Beck (*Mock Object*):

| Colaborador | Es una… | Doble en unitarias |
|---|---|---|
| `Reloj`, `Parque`, lecturas de repositorio, `GeneradorQR` | consulta (no cambia el mundo exterior) | **stub / fake**: se verifica el **estado** resultante, no cuántas veces se lo llamó |
| `ServicioEmail` | acción (cambia el mundo exterior) | **mock**: se verifica que se envió, una vez, con el mensaje correcto |
| Repositorios | almacenamiento | **fake en memoria**, validado con las mismas pruebas de contrato que el real (Grupo 8) |
| Fallas (email caído, QR roto, BD caída) | error improbable | ***Crash Test Dummy***: un doble que lanza la excepción |

Verificar llamadas a una consulta vuelve la prueba frágil: se rompería ante un refactor que no cambia el comportamiento.

### 2.3 Nombres

Funciones `test_<comportamiento_en_snake_case>` en español, sin tildes ni eñes, nombrando el
comportamiento y no el método (se lee como una frase). Archivos: `tests/test_actividad.py`,
`test_catalogo.py`, `test_parque.py`, `test_visitante.py`, `test_inscripcion.py`, `test_qr.py`,
`test_mensaje_email.py`, `test_repositorio.py`, `test_inscripcion_service.py`, `test_api.py`,
`test_aceptacion.py` (un archivo por grupo, en el orden de este documento).

## 3. Datos base (*fixtures*)

Valores confirmados por el PO el 2026-10-15 salvo los marcados *provisorio*.

| Dato | Valor | Origen |
|---|---|---|
| Reloj (`Reloj` inyectado, congelado) | miércoles **2026-11-04 08:00** | – |
| Parque | abre **08:30**, cierra **19:00**; cerrado **lunes**, **25/12** y **1/1** | PO #1, #11 |
| Turnos de actividad | uno por hora en punto, de **09:00 a 17:00** (a las 18:00 no hay turno) | PO #12 |
| Horario base `H1` | 2026-11-04 **10:00–11:00** | – |
| Ventana de inscripción | desde **24 h** antes hasta **15 min** antes del turno (ambos límites inclusivos, *supuesto*) | PO #23, #30 |
| Cupo por turno | Tirolesa **10** · Safari **8** · Palestra **12** · Jardinería **12** | PO #13 |
| Máximo por inscripción | **10** personas | PO #31 |
| Requieren talla | **Tirolesa y Palestra** | PO #9 |
| Talles válidos | `XS, S, M, L, XL, XXL` | PO #14 |
| Edad mínima | Tirolesa **8** · Palestra **12** · Safari y Jardinería sin mínimo | PO #15 |
| DNI | **7 u 8 dígitos** numéricos | PO #32 |
| Edad máxima válida | **100** años (*provisorio*, de la partición de equivalencias del grupo) | – |
| Visitante base | Ana Pérez · DNI `30123456` · 30 años · talla `M` | – |
| Email de contacto base | `ana.perez@example.com` | P01 abierta |

## 4. Cambios al modelo propuesto en el borrador previo

El borrador definía `Actividad`, `Horario`, `Visitante`, `TerminosYCondiciones`, `Inscripcion`,
`GeneradorQR`, `ServicioEmail`, `InscripcionService`. Para llegar a un sistema real hacen falta:

| Agregado | Por qué |
|---|---|
| `Reloj` (interfaz, inyectada) | "Horario ya pasado" y "horario ya comenzó" no se pueden probar con el reloj del sistema. |
| `Parque` (días y horas de funcionamiento) | Responde "¿está abierto en este horario?". Antes estaba mezclado en `Actividad`. |
| `Catalogo` / consultas de disponibilidad | La US exige elegir de una lista las actividades con cupo y horarios disponibles. |
| `InscripcionRepositorio` y `ActividadRepositorio` (interfaces) | Sin persistencia los cupos no existen. Implementaciones: `EnMemoria` (fake, para unitarias) y `Postgres` (real, gratuita, visible desde DBeaver). |
| `ConstructorMensajeEmail` (función pura) | Separar **armar** el mensaje (se prueba sin mocks) de **enviarlo** (`ServicioEmail`, se mockea). |
| `MotivoRechazo` (enumeración) | Las pruebas verifican **por qué** se rechazó, no solo que se rechazó. Un test que solo mira `False` no distingue un rechazo correcto de uno accidental. |
| Dato `email_de_contacto` en la inscripción | La US pide nombre/DNI/edad/talla del visitante, pero **no dice a qué email se envía** (P01). |

`GeneradorQR` y `ServicioEmail` siguen siendo interfaces inyectadas por constructor.

## 5. Test List

Orden de implementación sugerido = orden de los grupos. Formato de cada fila: **Dado → Entonces**.

### Grupo 1 – `Actividad`: cupos y reglas propias (ACT)

El grupo más simple: sin colaboradores. Se empieza acá.

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| ACT-01 | `test_hay_cupo_si_se_piden_menos_personas_que_el_cupo_restante` | Tirolesa 10:00 con cupo 10; piden 3 → `True` | U | – |
| ACT-02 | `test_hay_cupo_si_se_piden_exactamente_las_personas_del_cupo_restante` | cupo 10; piden 10 → `True` (borde) | U | – |
| ACT-03 | `test_no_hay_cupo_si_se_piden_mas_personas_que_el_cupo_restante` | cupo 10; piden 11 → `False` (borde) | U | – |
| ACT-04 | `test_no_hay_cupo_si_el_cupo_esta_agotado` | restante 0; piden 1 → `False` | U | – |
| ACT-05 | `test_no_hay_cupo_en_un_horario_que_no_es_turno_de_la_actividad` | turnos de 9:00 a 17:00 en punto; consultas 8:00, 10:30 y 18:00 (cota superior, no hay turno) → `False` | U | P04 |
| ACT-06 | `test_reservar_descuenta_del_cupo_restante` | cupo 10; reservar 3 → restante 7 | U | – |
| ACT-07 | `test_reservas_sucesivas_se_acumulan` | cupo 10; reservar 3 y luego 4 → restante 3 (*triangulación* de ACT-06) | U | – |
| ACT-08 | `test_reservar_mas_que_el_restante_falla_sin_modificar_el_cupo` | restante 2; reservar 3 → `CupoInsuficiente` y restante sigue en 2 | U | – |
| ACT-09 | `test_el_cupo_de_un_horario_no_afecta_a_otro_horario` | reservar 3 en 10:00 → 11:00 sigue en 10 | U | – |
| ACT-10 | `test_cada_actividad_declara_si_requiere_talla` | Tirolesa sí · Palestra sí · Safari no · Jardinería no (tabla parametrizada) | U | – |
| ACT-11 | `test_cada_actividad_tiene_sus_propios_terminos_y_condiciones` | los T&C de Tirolesa y de Jardinería son distintos y ninguno está vacío | U | P15 |
| ACT-12 | `test_actividad_rechaza_visitantes_menores_a_su_edad_minima` | Tirolesa mín. 8: 7 no / 8 sí · Palestra mín. 12: 11 no / 12 sí · Safari y Jardinería: 0 sí (borde) | U | – |

### Grupo 2 – Catálogo y disponibilidad (CAT)

Las consultas que alimentan las pantallas de selección. Flujo confirmado: **primero se elige la actividad
y después el horario** entre los que tienen cupo.

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| CAT-01 | `test_el_catalogo_contiene_exactamente_las_cuatro_actividades_con_sus_cupos` | → Tirolesa 10, Safari 8, Palestra 12, Jardinería 12 (ni más ni menos) | U | – |
| CAT-02 | `test_buscar_actividad_por_id_devuelve_la_actividad` | id de Safari → Safari | U | – |
| CAT-03 | `test_buscar_una_actividad_inexistente_falla` | id "rafting" → `ActividadNoEncontrada` | U | – |
| CAT-04 | `test_los_horarios_disponibles_de_una_actividad_solo_incluyen_los_que_tienen_cupo` | 10:00 con cupo, 11:00 agotado → solo 10:00 | U | P19 |
| CAT-05 | `test_los_horarios_disponibles_excluyen_los_que_el_parque_tiene_cerrado` | franja 08:00 y 18:00 cargadas → no aparecen | U | P04 |
| CAT-06 | `test_los_horarios_disponibles_solo_incluyen_los_que_estan_en_ventana_de_inscripcion` | reloj miércoles 08:00 → 10:00 de hoy sí; 8:15 no (a menos de 15 min); turno de dentro de 25 h no | U | – |
| CAT-07 | `test_una_actividad_sin_ningun_horario_con_cupo_figura_como_no_disponible` | Safari con todos sus horarios agotados → en el listado figura `disponible=False`; las demás `True` (cumple "siempre y cuando tengan cupos disponibles") | U | P19 |
| CAT-08 | `test_los_horarios_disponibles_muestran_el_cupo_restante` | Tirolesa 10:00 con 3 reservadas → muestra `7`; turno agotado → muestra `0` | U | P19b |

### Grupo 3 – `Parque` y `Horario` (PAR / HOR)

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| PAR-01 | `test_el_parque_esta_abierto_un_dia_comun_dentro_de_su_horario` | miércoles 10:00–11:00 (parque 8:30–19:00) → abierto | U | – |
| PAR-02 | `test_el_parque_esta_cerrado_si_el_horario_empieza_antes_de_la_apertura` | 08:00–09:00 → cerrado | U | – |
| PAR-03 | `test_el_parque_esta_cerrado_si_el_horario_termina_despues_del_cierre` | 18:30–19:30 → cerrado | U | – |
| PAR-04 | `test_el_parque_esta_abierto_en_el_borde_de_la_apertura` | 08:30–09:30 → abierto | U | – |
| PAR-05 | `test_el_parque_esta_abierto_en_el_borde_del_cierre` | 18:00–19:00 → abierto | U | – |
| PAR-06 | `test_el_parque_esta_cerrado_los_lunes` | lunes 2026-11-02 10:00 → cerrado | U | – |
| PAR-07 | `test_el_parque_esta_cerrado_el_25_de_diciembre_y_el_1_de_enero` | 2026-12-25 y 2027-01-01 a las 10:00 → cerrado (feriados fijos) | U | – |
| HOR-01 | `test_un_horario_dura_una_hora` | inicio 10:00 → fin 11:00 | U | – |
| HOR-02 | `test_dos_horarios_con_la_misma_fecha_e_inicio_son_iguales` | igualdad por valor | U | – |
| HOR-03 | `test_un_horario_es_turno_si_empieza_en_punto_entre_las_9_y_las_17` | 9:00 sí · 17:00 sí · 18:00 no (cota superior) · 8:00 no · 10:30 no (valores límite) | U | – |
| HOR-04 | `test_se_puede_inscribir_hasta_15_minutos_antes_del_turno` | turno 10:00: reloj 09:45 → sí (borde); 09:46 → no | U | – |
| HOR-05 | `test_no_se_puede_inscribir_con_mas_de_24_horas_de_anticipacion` | turno jueves 10:00: reloj miércoles 10:00 → sí (borde, 24 h); 09:59 → no | U | – |

### Grupo 4 – `Visitante`: validación individual (VIS)

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| VIS-01 | `test_visitante_con_nombre_dni_y_edad_es_valido_si_la_actividad_no_requiere_talla` | Ana Pérez, 30123456, 30; sin talla; Safari → válido | U | – |
| VIS-02 | `test_visitante_sin_nombre_es_invalido` | nombre `""` → `NOMBRE_REQUERIDO` | U | – |
| VIS-03 | `test_visitante_con_nombre_de_solo_espacios_es_invalido` | `"   "` → `NOMBRE_REQUERIDO` | U | – |
| VIS-04 | `test_visitante_sin_dni_es_invalido` | → `DNI_REQUERIDO` | U | – |
| VIS-05 | `test_visitante_con_dni_no_numerico_es_invalido` | `"12A45678"` → `DNI_INVALIDO` | U | P11 |
| VIS-06 | `test_el_dni_valido_tiene_7_u_8_digitos` | 6 díg. inválido · 7 válido · 8 válido · 9 inválido (valores límite) | U | P11 |
| VIS-07 | `test_visitante_sin_edad_es_invalido` | → `EDAD_REQUERIDA` | U | – |
| VIS-08 | `test_visitante_con_edad_no_entera_es_invalido` | `"abc"`, `12.5` → `EDAD_INVALIDA` | U | – |
| VIS-09 | `test_la_edad_valida_esta_entre_0_y_120` | −1 inválida · 0 válida · 120 válida · 121 inválida (valores límite) | U | P10 |
| VIS-10 | `test_visitante_sin_talla_es_invalido_si_la_actividad_la_requiere` | Tirolesa, sin talla → `TALLA_REQUERIDA` | U | P09 |
| VIS-11 | `test_visitante_con_talla_es_valido_si_la_actividad_la_requiere` | Tirolesa, talla `M` → válido | U | P09 |
| VIS-12 | `test_visitante_con_talla_fuera_de_los_valores_permitidos_es_invalido` | Tirolesa, talla `XXXXL` → `TALLA_INVALIDA` | U | P09 |
| VIS-13 | `test_visitante_con_talla_es_valido_aunque_la_actividad_no_la_requiera` | Safari, talla `M` → válido (la talla se ignora) | U | P09 |

### Grupo 5 – `Inscripcion`: reglas de negocio combinadas (INS)

Usa `Actividad`, `Parque`, `Visitante` reales, `Reloj` fijo. Todavía sin QR, email ni base de datos.
Cada rechazo se verifica por su `MotivoRechazo`.

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| INS-01 | `test_se_confirma_con_todos_los_datos_validos` | Tirolesa, `H1`, 1 visitante válido con talla, T&C de Tirolesa aceptados, email válido → confirmada | U | – |
| INS-02 | `test_se_rechaza_sin_actividad` | actividad `None` → `ACTIVIDAD_REQUERIDA` | U | – |
| INS-03 | `test_se_rechaza_sin_horario` | horario `None` → `HORARIO_REQUERIDO` | U | – |
| INS-04 | `test_se_rechaza_si_el_horario_no_pertenece_a_la_actividad` | horario no cargado para esa actividad → `HORARIO_NO_DISPONIBLE` | U | P18 |
| INS-05 | `test_se_rechaza_si_el_parque_esta_cerrado_en_el_horario` | 08:00 o lunes → `PARQUE_CERRADO` | U | P04 |
| INS-06 | `test_se_rechaza_si_el_turno_es_dentro_de_menos_de_15_minutos_o_ya_paso` | turno 10:00; reloj 09:46 o 10:30 → `INSCRIPCION_CERRADA` | U | – |
| INS-06b | `test_se_rechaza_si_el_turno_esta_a_mas_de_24_horas` | turno viernes 10:00, reloj martes → `FUERA_DE_VENTANA` | U | – |
| INS-07 | `test_se_rechaza_si_no_hay_cupo` | restante 0 → `SIN_CUPO` | U | – |
| INS-08 | `test_se_rechaza_si_el_cupo_alcanza_solo_para_parte_del_grupo` | restante 3, 4 visitantes → `SIN_CUPO`, no se inscribe a 3 | U | P07 |
| INS-09 | `test_se_rechaza_sin_visitantes` | lista vacía → `CANTIDAD_INVALIDA` | U | – |
| INS-10 | `test_se_rechaza_si_supera_el_maximo_de_10_personas_por_inscripcion` | 10 visitantes → ok · 11 visitantes → `CANTIDAD_INVALIDA` (valores límite) | U | – |
| INS-11 | `test_se_rechaza_si_algun_visitante_es_invalido` | 3 visitantes, el 2.º sin DNI → `VISITANTE_INVALIDO` con la posición (2) | U | – |
| INS-12 | `test_se_rechaza_si_hay_un_dni_repetido_dentro_de_la_misma_inscripcion` | dos visitantes con DNI `30123456` → `DNI_DUPLICADO` | U | – |
| INS-13 | `test_se_rechaza_sin_aceptar_los_terminos_y_condiciones` | sin aceptación → `TERMINOS_NO_ACEPTADOS` | U | P15 |
| INS-14 | `test_se_rechaza_si_se_aceptan_los_terminos_de_otra_actividad` | Tirolesa con T&C de Jardinería → `TERMINOS_DE_OTRA_ACTIVIDAD` | U | P15 |
| INS-15 | `test_se_confirma_cuando_se_aceptan_los_terminos_especificos_de_la_actividad` | Jardinería con T&C de Jardinería → confirmada | U | P15 |
| INS-16 | `test_se_rechaza_sin_email_de_contacto_valido` | `""` o `"ana@"` → `EMAIL_INVALIDO` | U | P01 |
| INS-17 | `test_la_inscripcion_confirmada_tiene_id_unico_y_estado_confirmada` | dos confirmaciones → ids distintos, estado `CONFIRMADA` | U | – |
| INS-18 | `test_la_inscripcion_confirmada_registra_version_de_terminos_y_momento_de_aceptacion` | → versión de T&C y `reloj.ahora()` guardados | U | P15 |
| INS-19 | `test_se_acumulan_todos_los_motivos_de_rechazo` | sin horario **y** sin T&C → ambos motivos en el resultado (el front puede mostrar todos los errores juntos) | U | decisión del equipo |
| INS-20 | `test_se_rechaza_si_el_titular_no_esta_registrado` | solo si P02 = "sí requiere registro" → `USUARIO_NO_REGISTRADO` | U | P02 |

### Grupo 6 – Código QR (QR)

Se separa **qué dice** el QR (función pura, `U`) de **cómo se dibuja** (librería `qrcode`, `C`).
Probar un *fake* de `GeneradorQR` no aporta nada: el fake solo se usa como doble en el Grupo 9.

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| QR-01 | `test_el_contenido_del_qr_incluye_el_codigo_de_la_inscripcion` | inscripción `INS-0001` → el contenido contiene `INS-0001` | U | P12b |
| QR-02 | `test_el_contenido_del_qr_es_distinto_para_cada_visitante` | mismo `INS-0001`, visitantes 1 y 2 → contenidos distintos (un QR por visitante) | U | – |
| QR-03 | `test_el_contenido_del_qr_es_el_mismo_para_el_mismo_visitante` | dos llamadas → igual (determinista) | U | – |
| QR-04 | `test_el_contenido_del_qr_no_expone_datos_personales` | no aparecen DNI, nombre ni email en el contenido | U | P12 |
| QR-05 | `test_el_contenido_firmado_detecta_adulteraciones` *(opcional)* | cambiar un carácter del código → la verificación de firma falla | U | P12 |
| QR-06 | `test_no_se_arma_el_qr_de_una_inscripcion_no_confirmada` | inscripción rechazada → `InscripcionNoConfirmada` | U | – |
| QR-07 | `test_el_generador_local_devuelve_una_imagen_png_valida` | contenido cualquiera → bytes no vacíos que empiezan con la firma PNG | C | – |
| QR-08 | `test_el_generador_local_devuelve_imagenes_distintas_para_contenidos_distintos` | A ≠ B → bytes distintos | C | – |
| QR-09 | `test_la_imagen_generada_se_decodifica_al_contenido_original` *(opcional)* | decodificar el PNG → contenido original (requiere librería de lectura de QR) | C | – |

El PO confirmó **un QR por visitante**, todos en el mismo email: el contenido se arma con el código de la inscripción y el número de visitante.

### Grupo 7 – Mensaje de email (EML)

Función pura `armar_mensaje(inscripcion, qr_png) → MensajeEmail`. No manda nada: se prueba sin mocks.

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| EML-01 | `test_el_destinatario_es_el_email_de_contacto` | `ana.perez@example.com` → ese destinatario | U | P01 |
| EML-02 | `test_el_asunto_incluye_la_actividad` | Tirolesa → asunto contiene "Tirolesa" | U | P14 |
| EML-03 | `test_el_cuerpo_incluye_actividad_fecha_horario_y_cantidad_de_personas` | → "Tirolesa", "04/11/2026", "10:00", "3 personas" | U | P14 |
| EML-04 | `test_el_cuerpo_incluye_el_nombre_de_cada_visitante` | 3 visitantes → los 3 nombres | U | P14 |
| EML-05 | `test_el_cuerpo_incluye_el_codigo_de_reserva_en_texto` | → el código `INS-0001` (por si el cliente de correo bloquea imágenes) | U | P14 |
| EML-06 | `test_el_mensaje_adjunta_un_qr_png_por_visitante` | 3 visitantes → 3 adjuntos `image/png`, cada uno con los bytes de su QR, en el mismo mensaje | U | – |
| EML-07 | `test_no_se_arma_el_mensaje_de_una_inscripcion_no_confirmada` | → `InscripcionNoConfirmada` | U | – |

### Grupo 8 – Repositorios (REP)

Pruebas de **contrato**: el mismo conjunto corre contra `RepositorioEnMemoria` y contra
`RepositorioPostgres`, así se garantiza que el fake que usan las unitarias se comporta como el real
(riesgo que Beck señala en *Mock Object*: que el doble no se comporte como el objeto real).
El `RepositorioPostgres` usa la base `ecoharmony_test`; cada prueba arranca con las tablas vacías
(o dentro de una transacción que se revierte), así son independientes entre sí.

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| REP-01 | `test_se_guarda_y_se_recupera_una_inscripcion_por_id` | guardar → recuperar: mismos visitantes, horario, T&C, email | C | – |
| REP-02 | `test_recuperar_un_id_inexistente_devuelve_none` | → `None` | C | – |
| REP-03 | `test_el_cupo_reservado_se_conserva_al_recargar_la_actividad` | reservar 3 → recargar → restante 7 | C | – |
| REP-04 | `test_guardar_la_inscripcion_y_reservar_el_cupo_es_atomico` | si falla el guardado, el cupo no cambia | C | – |
| REP-05 | `test_dos_reservas_simultaneas_del_ultimo_cupo_solo_dejan_pasar_una` *(solo Postgres)* | 2 conexiones en paralelo, restante 1 → una confirma, otra `SIN_CUPO`; restante 0 (actualización atómica del cupo, no "leer y después escribir") | C | – |
| REP-06 | `test_la_carga_inicial_deja_las_cuatro_actividades_con_sus_horarios_y_cupos` | base vacía + `seed.sql` → 4 actividades configuradas | C | P06 |
| REP-07 | `test_se_puede_consultar_si_un_dni_ya_esta_inscripto_en_una_fecha_y_hora` | inscribir DNI X en Tirolesa 10:00 → consulta (10:00, cualquier actividad) `True`; 11:00 → `False` | C | – |
| REP-08 | `test_el_esquema_se_crea_desde_cero_en_una_base_vacia` *(solo Postgres)* | ejecutar `schema.sql` en una base vacía → existen las tablas y sus restricciones (cupo ≥ 0, DNI/horario únicos por actividad según P16) | C | P16 |

### Grupo 9 – `InscripcionService`: orquestación (SRV)

`Actividad`, `Parque`, `Visitante`, `Inscripcion` reales · `RepositorioEnMemoria` (fake) · `Reloj` fijo ·
`GeneradorQR` **stub** (devuelve siempre `b"QR-FALSO"`) · `ServicioEmail` **mock** (única acción hacia el exterior).
Orden de operaciones: **validar → reservar cupo y guardar (atómico) → generar QR → enviar email**.
Los rechazos comparten una aserción auxiliar `assert_sin_efectos()`: nada guardado, cupo intacto y
`ServicioEmail` sin ninguna llamada. No se cuentan llamadas al `GeneradorQR` (es una consulta): que no
se haya enviado ningún email ya prueba que ningún QR llegó a destino.

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| SRV-01 | `test_inscripcion_valida_se_confirma_y_devuelve_el_resumen` | caso feliz → resultado con id, actividad, horario y cantidad | U | P21 |
| SRV-02 | `test_inscripcion_valida_queda_persistida` | → el repositorio la devuelve por id | U | – |
| SRV-03 | `test_inscripcion_valida_descuenta_el_cupo` | cupo 10, 3 visitantes → restante 7 | U | – |
| SRV-04 | `test_cada_qr_adjunto_al_email_es_el_que_entrego_el_generador` | stub devuelve un QR distinto por visitante → el mensaje enviado lleva esos mismos QR, uno por visitante | U | – |
| SRV-05 | `test_inscripcion_valida_envia_un_unico_email_al_contacto` | `ServicioEmail` llamado exactamente 1 vez, con destinatario = email de contacto | U | P01 |
| SRV-06 | `test_sin_cupo_no_confirma_ni_envia_email` | restante 0 → `SIN_CUPO` + `assert_sin_efectos()` | U | – |
| SRV-07 | `test_parque_cerrado_no_confirma_ni_envia_email` | 08:00 → `PARQUE_CERRADO` + `assert_sin_efectos()` | U | P04 |
| SRV-08 | `test_turno_con_inscripcion_cerrada_no_confirma_ni_envia_email` | reloj a 14 min del turno → `INSCRIPCION_CERRADA` + `assert_sin_efectos()` | U | – |
| SRV-09 | `test_sin_aceptar_terminos_no_confirma_ni_envia_email` | → `TERMINOS_NO_ACEPTADOS` + `assert_sin_efectos()` | U | P15 |
| SRV-10 | `test_terminos_de_otra_actividad_no_confirman_ni_envian_email` | Tirolesa con T&C de Jardinería → `assert_sin_efectos()` | U | P15 |
| SRV-11 | `test_actividad_que_requiere_talla_sin_indicarla_no_confirma_ni_envia_email` | Tirolesa sin talla → `VISITANTE_INVALIDO` + `assert_sin_efectos()` | U | P09 |
| SRV-12 | `test_actividad_que_no_requiere_talla_sin_indicarla_confirma` | Safari sin talla → confirmada, email enviado | U | P09 |
| SRV-13 | `test_dni_ya_inscripto_en_el_mismo_horario_no_confirma_ni_envia_email` | DNI X ya inscripto en **Tirolesa** 10:00 → inscribirlo en **Safari** 10:00 → `DNI_YA_INSCRIPTO` + `assert_sin_efectos()` | U | – |
| SRV-14 | `test_el_ultimo_cupo_lo_obtiene_solo_la_primera_inscripcion` | restante 1; dos inscripciones seguidas → 1.ª confirma, 2.ª `SIN_CUPO` | U | – |
| SRV-15 | `test_si_falla_el_envio_del_email_la_inscripcion_sigue_confirmada` | *Crash Test Dummy*: `ServicioEmail` lanza error → confirmada, cupo descontado, resultado con `email_enviado=False` | U | P13 |
| SRV-16 | `test_si_falla_la_generacion_del_qr_no_se_confirma_ni_se_descuenta_cupo` | *Crash Test Dummy*: `GeneradorQR` lanza error → cupo intacto, nada guardado, no se envía email | U | P13 |
| SRV-17 | `test_si_falla_la_persistencia_no_se_envia_ningun_email` | *Crash Test Dummy*: el repositorio lanza error al guardar → el error se propaga y `ServicioEmail` sin llamadas | U | – |

### Grupo 10 – API HTTP (API) – *se detalla al elegir framework*

Capa delgada entre el front React y el servicio (FastAPI o Flask, ver §9). El servicio se reemplaza por un doble.

| ID | Prueba | Dado → Entonces | Cat. | PO |
|---|---|---|---|---|
| API-01 | `test_post_inscripcion_valida_responde_201_con_el_resumen` | servicio confirma → `201` + id | U | P21 |
| API-02 | `test_post_inscripcion_sin_cupo_responde_409_con_el_motivo` | `SIN_CUPO` → `409` + motivo | U | – |
| API-03 | `test_post_inscripcion_con_datos_invalidos_responde_422_con_todos_los_motivos` | → `422` + lista de motivos | U | – |
| API-04 | `test_get_actividades_devuelve_las_cuatro_actividades_con_su_disponibilidad` | → 4 ítems, cada uno con `disponible` | U | P19 |
| API-05 | `test_get_horarios_de_una_actividad_devuelve_solo_los_que_tienen_cupo` | `GET /actividades/{id}/horarios?fecha=` → solo horarios con cupo (flujo: actividad primero, horario después) | U | P19 |
| API-06 | `test_get_terminos_de_una_actividad_devuelve_los_de_esa_actividad` | → texto + versión | U | P15 |
| API-07 | `test_un_error_inesperado_responde_500_sin_detalles_internos` | servicio lanza `Exception` → `500` genérico | U | – |

### Grupo 11 – Pruebas de aceptación (ACE)

Las 6 *pruebas de usuario* de la consigna + la regla de T&C específicos. Corren sobre
`InscripcionService` con **`RepositorioPostgres` real (base `ecoharmony_test`)**, `GeneradorQRLocal` real y
`ServicioEmail` *fake* que guarda lo "enviado". Es la red de seguridad de punta a punta.

Según Ble (ATDD, cap. 3), la prueba de aceptación es la **raíz del árbol**: se escribe **primero**
(ACE-01, contra los fakes en memoria) y queda en rojo mientras las pruebas unitarias van construyendo el
sistema. Al terminar se la apunta a Postgres y al QR real.

| ID | Prueba de usuario (consigna) | Resultado | PO |
|---|---|---|---|
| ACE-01 | Inscribirse a una actividad con cupo, horario, datos del visitante (con talla si se requiere), aceptando T&C → recibe email con QR | pasa | – |
| ACE-02 | Inscribirse a una actividad sin cupo para el horario elegido | falla | – |
| ACE-03 | Inscribirse sin ingresar talla porque la actividad no la requiere | pasa | P09 |
| ACE-04 | Inscribirse a un horario con el parque cerrado o la actividad no disponible | falla | P04, P18 |
| ACE-05 | Inscribirse sin aceptar los T&C de la actividad | falla | P15 |
| ACE-06 | Inscribirse sin ingresar la talla que la actividad requiere | falla | P09 |
| ACE-07 | Inscribirse aceptando T&C de **otra** actividad (criterio: "T&C específicos de la actividad") | falla | P15 |

## 6. Primeros ciclos sugeridos (método Beck)

Para arrancar sin pensar de más.

0. **Prueba de aceptación primero (ACE-01).** Se escribe contra fakes en memoria y se la marca
   `xfail(strict=True)` hasta que pase (Ble, ATDD: es la raíz del árbol; Beck, *Starter Test*: a veces
   la primera prueba está a nivel aplicación). No se la persigue todavía: se baja a lo unitario.
1. **ACT-01 – Red:** `Actividad` no existe, falla. **Green con *Fake It*:** `return True`. Pasa.
2. **ACT-03 – Red:** `return True` falla. **Green:** acá la generalización es evidente, así que *Obvious
   Implementation*: `return cantidad <= restante`. Si el borde sale al revés (error por uno), se baja de
   marcha a *Fake It*/*Triangulate*: ACT-02 y ACT-03 son justamente esa red de seguridad. Beck reserva
   *Triangulate* para cuando no se sabe cuál es la abstracción correcta.
3. **ACT-04** probablemente pase de entrada: está bien, se deja (*Another Test*; confirma, no obliga a codificar).
4. **ACT-06 – *Fake It*:** `restante = 7`. **ACT-07 – *Triangulate*:** acá sí hay duda real (¿se pisa o se acumula?) y el segundo ejemplo obliga a `restante -= cantidad`.
5. **ACT-08:** agrega el `raise CupoInsuficiente`.
6. **Refactor:** con ACT-01..08 en verde, evaluar extraer un objeto `Cupo` si hay duplicación de `restante`.

Para los grupos con listas (Visitantes en `Inscripcion`, INS-11) aplica *One to Many*: primero la
inscripción con **un** visitante, después con varios.

Si un paso no sale (la prueba es demasiado grande), se aplica *Child Test*: se escribe una prueba más chica
sobre la parte que falla, se la hace pasar y se vuelve a la grande. Al cortar una sesión en solitario se
puede dejar la última prueba en rojo como marcador (*Broken Test*).

**Commits y evidencia del ciclo.** Beck (*Clean Check-in*) pide integrar siempre con todas las pruebas en
verde. Para conciliarlo con la consigna (que pide demostrar Red-Green-Refactor):

- Se trabaja en una rama `tp6-tdd`. Ahí se puede commitear cada fase: `test(ACT-03): rojo`,
  `feat(ACT-03): verde`, `refactor: …`. Eso deja la evidencia trazable.
- A `main` entra solo con **todo en verde**.

Convención de mensajes en español, como el resto del historial del repositorio.

## 7. Trazabilidad con los criterios de aceptación de la US

| Criterio de aceptación | Pruebas que lo sostienen |
|---|---|
| Seleccionar actividad de la lista (Tirolesa, Safari, Palestra, Jardinería) con cupo disponible | CAT-01, CAT-03, CAT-07, ACT-01..05, INS-02, INS-07 |
| Seleccionar horario dentro de los disponibles | CAT-04..06, PAR-01..06, HOR-01..04, INS-03..06 |
| Indicar la cantidad de personas | ACT-01..03, INS-08..10 |
| Datos del visitante: nombre, DNI, edad y talla si la actividad lo demanda | VIS-01..13, ACT-10, ACT-12, INS-11..12 |
| Aceptar los T&C **específicos** de la actividad | ACT-11, INS-13..15, INS-18, API-06 |
| Al finalizar, enviar email con la información y un código QR | QR-01..09, EML-01..07, SRV-04..05, SRV-15..16 |
| *(Implícito)* El cupo se respeta y no se sobrevende | ACT-06..09, REP-03..05, SRV-03, SRV-14 |
| *(Implícito)* Los datos quedan guardados en una base consultable | REP-01..08, SRV-02, ACE-01 |

## 8. Pruebas que probablemente emerjan (candidatas)

No se implementan hasta que el código las pida. Se anotan para que no se pierdan:

- `Actividad.liberar_cupo()` (si el rollback del Grupo 9 lo necesita).
- Normalización de espacios/mayúsculas en nombre y email.
- Idempotencia: reenviar la misma inscripción (doble clic) no duplica ni descuenta dos veces.
- Reenvío del email de confirmación.
- Zonas horarias (se asume hora de Argentina, `America/Argentina/Cordoba`, un único huso).

**Fuera de alcance de esta US** (salvo que el PO indique lo contrario): cancelar o modificar una inscripción,
lista de espera, cobro de la actividad, panel de administración de cupos y horarios (el PO dijo que se
gestiona "por fuera de la aplicación"), notificaciones si se suspende una actividad, y la lógica de la
pantalla React (tendría su propia lista con Jest + React Testing Library).

## 9. Decisiones pendientes del equipo (no son del PO)

| Tema | Estado / propuesta |
|---|---|
| **Reglas de estilo de código** | **Decidido:** PEP 8 para Python (confirmado por el grupo, 2026-10-11). |
| Framework de la API | FastAPI (gratis, tipado, `TestClient`) o Flask. Decidir antes del Grupo 10. |
| Base de datos | **PostgreSQL** (decidido por el grupo para poder inspeccionarla con DBeaver). Detalle en §9.1. |
| Acceso a datos | **Decidido:** SQL plano con **psycopg 3**, sin ORM (`schema.sql` / `seed.sql` versionados). Mantiene la capa fina y deja explícita la actualización atómica del cupo (REP-05). |
| Email real y gratuito | Brevo (300/día, sin tarjeta) o Gmail SMTP con contraseña de aplicación. Según el borrador previo; **verificar que los límites sigan vigentes** al implementar. |
| QR | Librería `qrcode` (local, gratis, sin red). |
| **Dónde va el código** | **Decidido:** `entrega-tp-6/codigo/`, en este mismo repositorio (ver §9.2). |
| **Secretos** | El repositorio es **público**: credenciales SMTP / API keys / contraseña de la base van en `.env` (en `.gitignore`), nunca en un commit. Se versiona un `.env.example`. |

### 9.1 PostgreSQL y DBeaver

| Tema | Propuesta |
|---|---|
| Cómo se instala | **Docker** con un `docker-compose.yml` (imagen oficial `postgres`). Gratis, sin instalar Postgres en Windows, y cualquier integrante la levanta igual con `docker compose up -d`. Docker Desktop parece estar instalado en esta PC. Alternativas: instalador de Postgres para Windows, o una base gratuita en la nube (hay que revisar condiciones y límites vigentes antes de elegir). |
| Dos bases | `ecoharmony`: desarrollo y demo, **la que se abre con DBeaver**. `ecoharmony_test`: solo para las pruebas automáticas, que la vacían en cada corrida; no sirve para mirar datos. |
| Conexión en DBeaver | PostgreSQL → host `localhost`, puerto **`5433`** (el del host; evita chocar con otras bases locales), base `ecoharmony`, usuario y contraseña de `.env`. |
| Esquema | `schema.sql` en SQL plano, versionado: se lee en DBeaver y la prueba REP-08 lo ejecuta sobre una base vacía. Las actividades se cargan desde el catálogo en Python (`preparar_base`), así hay una sola fuente de verdad (no hay `seed.sql`). |
| Tablas tentativas | `actividad`, `horario_actividad` (cupo total y ocupado), `inscripcion`, `visitante_inscripto`, `aceptacion_terminos`. Se afinan cuando el PO responda P03–P06 y P15–P16. |
| Cómo corren las pruebas | Unitarias (U): sin base, siempre. Contrato y aceptación (C/ACE): requieren `docker compose up -d`; si la base no responde se saltean con un mensaje que lo explica, para que `pytest` no falle por infraestructura. |

### 9.2 ¿El código forma parte de la entrega? ¿Dónde se guarda?

**Sí.** La consigna pide como resultado: *implementación funcional de la User Story*, *conjunto de pruebas
automatizadas* y un *documento que justifique las decisiones de diseño*: **código + tests + un documento**.

**Decidido por el grupo (2026-10-11):** todo lo que compone la entrega vive en una carpeta
`entrega-tp-6/` dentro de `trabajo_evaluable_6/`, en este mismo repositorio. La consigna queda afuera, a
nivel del TP, como en los demás trabajos.

```
trabajos_practicos_evaluables/trabajo_evaluable_6
├── consigna-tp-6.pdf
└── entrega-tp-6
    ├── plan-pruebas-tdd-tp-6.md          ← este documento
    ├── preguntas-product-owner-tp-6.md
    ├── (documento de decisiones de diseño, al final del TP)
    └── codigo
        ├── README.md                     ← cómo levantar todo
        ├── docker-compose.yml
        ├── .env.example
        ├── backend
        │   ├── src/…                     ← dominio, servicios, repositorios, API
        │   ├── tests/…                   ← un archivo por grupo de este plan
        │   └── sql/ (schema.sql, seed.sql)
        └── frontend/…                    ← React
```

Implicancias a resolver más adelante (no bloquean esta etapa):

- El README del repositorio define la entrega como un archivo (`entrega-tp-<n>.<extensión>`); acá es una
  **carpeta**. Cuando se arme la línea base `LB-TP6-vFinal`, conviene aclararlo en el README (el grupo decide).
- La regla "archivos en `kebab-case`" aplica a los documentos; el código sigue PEP 8 (`snake_case.py`).
- Hace falta un `.gitignore` antes del primer commit de código: `.env`, `.venv`, `__pycache__`,
  `node_modules`, datos de Postgres.
- Conviene confirmar con la cátedra si evalúa el código desde el repositorio o solo el documento de entrega.

## 10. Del *mock* a lo real

Se mantiene la estrategia del borrador previo: durante el TDD, `GeneradorQR` y `ServicioEmail` son
interfaces con dobles. Antes de la entrega se agregan `GeneradorQRLocal` (`qrcode`), `ServicioEmailBrevo`
o `ServicioEmailGmail` y `RepositorioPostgres`. Las **únicas** pruebas que tocan internet son las de
categoría **X** (un email real a una casilla del grupo), fuera de esta lista y fuera de la corrida normal.
Los contratos de los Grupos 6, 7 y 8 garantizan que reemplazar un doble por la pieza real no toca
`Inscripcion` ni `InscripcionService`.

---

*Total: 12 + 8 + 12 + 13 + 21 + 9 + 7 + 8 + 17 + 7 + 7 = 121 pruebas (QR-05 y QR-09 son opcionales). Se espera que la lista cambie durante la implementación.*


## 11. Estado de la implementación (2026-10-15)

Rama `tp6-tdd`: cada prueba se hizo con su ciclo visible en `git log` (`test(ID): rojo` → `feat(ID): verde` →
`refactor`); las pruebas que pasaron de entrada figuran como `ya verde`. **195 pruebas verdes** (170 sin base de
datos + 25 contra PostgreSQL real), PEP 8 limpio con `ruff`.

| Grupo | Archivo de pruebas | Estado |
|---|---|---|
| Actividad (ACT) | `test_actividad.py` | Hecho (ACT-01..09, 12). ACT-10 y ACT-11 pasaron al catálogo (CAT-01/ACT-11). |
| Catálogo (CAT) | `test_catalogo.py`, `test_repositorio.py` | CAT-01, 02, 03 hechos. **CAT-04..08 (consultas de horarios disponibles) pendientes**: los necesita la API. |
| Parque / Horario | `test_parque.py`, `test_horario.py` | Hecho (PAR-01..07, HOR-01..05). |
| Visitante (VIS) | `test_visitante.py` | Hecho (VIS-01..16). Nuevos: VIS-14/15 (nombre, *provisorio*, P22) y VIS-16 (edad mínima). |
| Inscripción (INS) | `test_inscripcion.py` | Hecho (INS-01..19, 06b). INS-20 (usuario registrado) queda fuera mientras P02 siga abierta. |
| QR | `test_qr.py`, `test_generador_qr_local.py` | Hecho (QR-01..04, 06..08). QR-05 y QR-09 (opcionales) no se hicieron. |
| Email (EML) | `test_mensaje_email.py` | Hecho (EML-01..07). |
| Adaptador SMTP (SMTP, nuevo) | `test_servicio_email_smtp.py` | Hecho (SMTP-01..05) con un SMTP falso. El envío **real** a una casilla (categoría X) falta: requiere credenciales. |
| Repositorios (REP) | `test_repositorio.py`, `test_esquema_postgres.py`, `test_preparar_base.py` | Hecho (REP-01..09, PREP-01/02), con el mismo contrato para el fake y para PostgreSQL. |
| Servicio (SRV) | `test_inscripcion_service.py` | Hecho (SRV-01..20). Nuevos: SRV-18 actividad inexistente, SRV-19 y SRV-20 carreras por cupo y por DNI. |
| Aceptación (ACE) | `test_aceptacion.py` | Hecho (ACE-01..07), cada una con fakes y con PostgreSQL + QR real. |
| Reloj / entorno (nuevos) | `test_reloj.py`, `test_entorno.py` | Hecho. |
| API HTTP (API) | – | **Pendiente.** |
| Front React | – | **Pendiente** (Jest + React Testing Library, lista aparte). |

### Decisiones que cambiaron respecto de lo planeado

- **Orden de las operaciones del servicio:** validar → confirmar (código) → **generar los QR** → **guardar** (reserva
  atómica de cupo + inscripción) → **enviar el email**. El QR se genera *antes* de guardar para que un fallo del QR no
  deje la inscripción a medias (SRV-16); un fallo del email no deshace la inscripción (SRV-15, supuesto P13b).
- **Reserva de cupo atómica en SQL** (una sola sentencia `INSERT … ON CONFLICT DO UPDATE … WHERE`): dos pedidos por el
  último lugar no pueden ganar los dos (REP-05, probado con dos hilos contra PostgreSQL real).
- **Conflicto de horario por DNI:** además de la comprobación previa (SRV-13) hay una restricción `UNIQUE (dni, fecha,
  hora)` en la base (REP-09) y el servicio traduce esa carrera a `DNI_YA_INSCRIPTO` (SRV-20).
- **Una prueba de contrato encontró un defecto real:** en el fake en memoria, `guardar` reservaba el cupo sobre la copia
  de la actividad que traía la inscripción y no sobre la del repositorio (REP-03). Y una prueba (REP-04) dependía de que
  el fake devolviera la misma instancia; se corrigió para preparar el estado usando solo la API del repositorio.
- **Email por SMTP genérico:** un solo adaptador sirve para Gmail o Brevo (cambia solo la configuración del `.env`).

### Lo que falta

1. **Consultas de disponibilidad** (CAT-04..08) y la **API HTTP** (FastAPI) que la pantalla consume.
2. **Front React** (paleta y fuente Lato del PO, responsive).
3. **Prueba externa** de email real a una casilla del grupo (necesita credenciales de Gmail o Brevo).
4. **Textos reales de los T&C** de cada actividad (hoy son un texto provisorio en `catalogo.py`).
5. **Documento de decisiones de diseño** (`entrega-tp-6`), que pide la consigna.
6. Preguntas abiertas al PO (ver `preguntas-product-owner-tp-6.md` §3): P01, P02, P07, P10b, P13b, P17.
