# ISW_4K3_G8_2C_2026

Repositorio del Grupo 8 – Ingeniería de Software (ISW) – 4K3 – 2026.
Aquí se documentan todos los materiales de clase, trabajos prácticos, consignas y entregas del equipo.

## Integrantes

- ULIANA, Agustín – 97828
- LEDO FLORES, Francisco – 86489
- CASTELO, Matías – 88413
- DIAZ, Iván – 87473
- SORUCO, Jonatan – 79456
- GIAIMO, Gino – 78426
- PÁEZ DE LA TORRE, Matías – 83289
- RAMALLO, Mateo – 94441
- CORREA, Jeremías – 88714
- VARGAS FERNANDEZ, Rodrigo – 96417
- FORTI, Bruno – 80818
- TRONCOZO, Valentina – 86268
- LEYES MOLINA, Selene – 65743
- CARDOZO ROJAS, Fernando – 89064

## Estructura del repositorio

```
ISW_4K3_G8_2C_2026
│
├── README.md
│
├── material_de_alumnos
│   ├── ejercicios
│   ├── toma_de_notas
│   └── resumenes
│
├── material_de_catedra
│   ├── bibliografia
│   │   └── <<tema>>
│   ├── templates
│   ├── guias
│   └── u_<<numero_unidad>>_<<nombre_unidad>>
│       ├── filminas
│       └── grabaciones
│
├── planificacion_catedra
│
├── trabajos_investigacion
│   └── trabajo_investigacion_<<numero>>
│
└── trabajos_practicos_evaluables
    └── trabajo_evaluable_<<numero>>
```

## Reglas de nombrado generales

Las carpetas se nombran utilizando `snake_case` y los archivos utilizando `kebab-case`.

## Listado de ítems de configuración

| Ítem de Configuración | Regla de Nombrado | Ubicación |
|---|---|---|
| Ejercicios | `ejercicio-<<tema>>-<<autor>>.<<extension_apuntes>>` | `material_de_alumnos/ejercicios` |
| Toma de Notas | `toma-notas-<<ddmm>>-<<autor>>.<<extension_apuntes>>` | `material_de_alumnos/toma_de_notas` |
| Resumen | `resumen-<<numero_unidad>>-<<autor>>.<<extension_apuntes>>` | `material_de_alumnos/resumenes` |
| Bibliografía | `<<nombre-archivo>>.pdf` | `material_de_catedra/bibliografia/<<tema>>` |
| Templates | `template-<<tema>>-<<autor>>.pdf` | `material_de_catedra/templates` |
| Guía de Cátedra | `guia-<<tema>>.pdf` | `material_de_catedra/guias` |
| Diapositiva de Clase | `<<numero>>-<<nombre>>.pdf` | `material_de_catedra/u_<<numero_unidad>>_<<nombre_unidad>>/filminas` |
| Clase Grabada | `clase-grabada-<<numero>>-<<nombre>>.md` | `material_de_catedra/u_<<numero_unidad>>_<<nombre_unidad>>/grabaciones` |
| Consigna de TPIG | `consigna-tpig-<<numero>>.pdf` | `trabajos_investigacion/trabajo_investigacion_<<numero>>` |
| Presentación TPIG | `presentacion-tpig-<<numero>>.pdf` | `trabajos_investigacion/trabajo_investigacion_<<numero>>` |
| Consigna de TP Evaluable | `consigna-tp-<<numero>>.pdf` | `trabajos_practicos_evaluables/trabajo_evaluable_<<numero>>` |
| Entrega de TP Evaluable | `entrega-tp-<<numero>>.<<extension_tp>>` | `trabajos_practicos_evaluables/trabajo_evaluable_<<numero>>` |
| Presentación General de la Materia | `presentacion-general-isw.pdf` | `planificacion_catedra` |
| Cronograma | `cronograma-isw.xlsx` | `planificacion_catedra` |
| Programa | `programa-isw.pdf` | `planificacion_catedra` |

> **Nota sobre Clase Grabada:** dado que los archivos de video de las clases exceden el tamaño manejable para un repositorio Git público, este ítem no almacena el video en sí, sino un archivo `.md` con el enlace de acceso a la grabación (plataforma donde la cátedra la publica) y una breve referencia a su contenido.

## Glosario

- **ISW** → Ingeniería y Calidad de Software.
- **U** → Abreviatura usada en el texto general de la cátedra para referirse a una Unidad temática (ej: "U3: Gestión del Software como producto"). En el nombrado de carpetas y archivos se utiliza el placeholder `NUMERO_UNIDAD` en su lugar (ver más abajo); no son literalmente lo mismo, sino que `NUMERO_UNIDAD` es el valor que reemplaza a U dentro de un nombre de archivo o carpeta.
- **NUMERO_UNIDAD** → Número de la unidad temática correspondiente (ej: 3), utilizado en el nombrado de carpetas y archivos (ej: `u_3_...`).
- **NOMBRE_UNIDAD** → Nombre descriptivo abreviado de la unidad temática, en `snake_case` (ej: `gestion_del_software_como_producto`).
- **TP** → Trabajo Práctico.
- **TPIG** → Trabajo Práctico de Investigación Grupal.
- **DDMM** → Formato de fecha Día/Mes.
- **TEMA** → Palabra o frase corta que identifica el tema específico del ítem (ej: `scm`, `requisitos`).
- **AUTOR** → Nombre del integrante del grupo que generó el ítem, en minúscula.
- **NOMBRE-ARCHIVO** → Nombre descriptivo del archivo de bibliografía, tal como fue provisto por la cátedra.
- **NUMERO** → Número identificador correlativo del ítem (de la diapositiva, la clase grabada, el TP o el TPIG, según corresponda).
- **NOMBRE** → Nombre descriptivo corto del ítem (de la diapositiva o la clase grabada).
- **K** → Referencia a la carrera de Ingeniería en Sistemas de Información, seguida del número de curso (ej: 4K3). Se usa únicamente en el nombre del repositorio y en la identificación general de la cátedra/curso; no es un placeholder dentro de las reglas de nombrado de los ítems de configuración.
- **PDF/XLSX** → extensiones de archivo.
- **EXTENSION_APUNTES** → Extensión correspondiente al formato del archivo utilizado para materiales elaborados por los alumnos, por ejemplo .pdf, .docx o .md.
- **EXTENSION_TP** → Extensión correspondiente al formato requerido para la entrega del Trabajo Práctico Evaluable, por ejemplo .pdf, .png o .jpg.

## Criterio de línea base

En nuestro proyecto, definimos una línea base luego de la devolución y corrección de cada Trabajo Práctico evaluable, momento en el cual se alcanza una versión final validada. Esta decisión permite que el repositorio mantenga versiones consolidadas, correctas y alineadas con los criterios establecidos por la cátedra. De esta manera, cada línea base funciona como un punto de referencia estable para el seguimiento y control de los cambios realizados durante el desarrollo del proyecto.

Cada línea base estará compuesta por los ítems de configuración asociados al Trabajo Práctico correspondiente: la consigna y la entrega final de ese Trabajo Práctico.

Para su identificación, adoptamos la convención de nombrado `LB-TP<<numero>>-vFinal`. Por ejemplo: `LB-TP1-vFinal`, `LB-TP2-vFinal`. Esta convención permite identificar de forma clara el Trabajo Práctico al que pertenece cada línea base y facilita la trazabilidad de las diferentes versiones.

Un ítem de configuración será considerado parte de la línea base cuando:

- Haya sido revisado y aprobado por al menos un integrante del grupo.
- Esté completo y en su versión definitiva, sin marcas de borrador o pendientes.
- Respete el formato, la regla de nombrado y la ubicación definidos en el listado de ítems de configuración.
- Corresponda al contenido validado del Trabajo Práctico luego de las correcciones realizadas.
- Se encuentre incorporado al repositorio en el momento de establecer la línea base.

Una vez establecida una línea base, los cambios posteriores sobre sus ítems deberán realizarse de manera controlada, manteniendo el registro de las modificaciones para garantizar la trazabilidad y evitar la pérdida de la versión validada.

**¿Qué sucede con el resto de los ítems?** El criterio de línea base aplica específicamente a los Trabajos Prácticos Evaluables, ya que son los únicos ítems que atraviesan una instancia formal de corrección y validación por parte de la cátedra, lo cual constituye el punto de referencia necesario para fijar una versión estable y definitiva. El resto de los ítems de configuración (ejercicios, tomas de notas, resúmenes, bibliografía, templates, guías, diapositivas, clases grabadas, TPIG, cronograma, programa y presentación general de la materia) constituye material de referencia de actualización continua a lo largo del cursado, que no atraviesa una instancia de corrección formal por parte de la cátedra. Por ese motivo no se definen líneas base individuales para ellos: su trazabilidad y control de versiones quedan garantizados por el propio historial de commits del repositorio, que permite identificar y recuperar cualquier estado anterior en caso de ser necesario.

## Link a este repositorio

https://github.com/AgustinUliana/ISW_4K3_G8_2C_2026
