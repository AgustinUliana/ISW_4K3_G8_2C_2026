# Testing

*Viernes, 25 de septiembre de 2026 - 20:56*

## PUD

Tiene un conjunto de workflows:

1. Requerimientos
2. Análisis
3. Diseño
4. Implementación
5. **Pruebas**
6. Despliegue

## Contexto

El testing no asegura calidad.

Se busca que el producto tenga calidad llevando a cabo intervenciones a lo largo del ciclo de vida.

## Definición

El objetivo del testing es encontrar defectos.

**Testing:** proceso destructivo que trata de encontrar defectos en el código.

## Error vs. Defecto

La diferencia es el momento en el que se detecta.

Lo ideal es que los errores se hayan introducido en la etapa de implementación. Sin embargo, pueden venir de la etapa de análisis o diseño. En el caso de errores de requerimiento, hay que tirar.

Son defectos también, ya que son de una etapa anterior.

> [!NOTE]
> Un error de arquitectura encontrado haciendo revisión de arquitectura es un error. En una etapa posterior es un defecto.

## Falla

Mal funcionamiento del sistema.

> [!IMPORTANT]
> Un defecto puede o no generar una falla en el sistema.

## Clasificación de Defectos

Cuando aparece un defecto necesitamos clasificarlo para ayudarnos a la gestión de la resolución.

### Severidad

Qué tanto afecta al funcionamiento ese defecto:

- Bloqueante
- Crítico
- Mayor
- Menor
- Cosmético

### Prioridad

Urgencia del negocio:

- Urgente
- Alta
- Media
- Baja

## Niveles de Prueba

- Unitarias (implementación)
- De integración (implementación o pruebas)
- De sistema (pruebas)
- De aceptación (despliegue)

## Ambiente o Entorno

Conjunto de herramientas que es necesario que estén disponibles para que un sistema se pueda construir, probar o desplegar.

## Caso de Prueba

Conjunto de instrucciones que describe un caso de prueba de una historia de usuario.

Una buena definición de caso de prueba nos ayuda a poder reproducir defectos.
