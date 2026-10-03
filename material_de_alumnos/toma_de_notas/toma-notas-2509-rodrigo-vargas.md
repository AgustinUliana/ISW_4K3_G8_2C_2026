PUD Workflow

              |- Requerimientos
              |- Análisis
              |- Diseño
P Unitarias   |- Implementación - TDD
P Integración |- Prueba
P Sistema     |
P Aceptación  |- Implementación


# Testing de Software 

## Contexto
El testing es una pequeña parte del QA

## Definición
El objetivo del testing es encontrar defectos.

Se define como un proceso destructivo para encontrar defectos cuya existencia se asume

## Consideraciones

Error != Defecto

radica en el momento en el que se introduce y se trata.

> [!IMPORTANT]
> la falla es un mal funcionamiento del sistema

### Categorizacion de Defectos

Severidad(Urgencia de negocio):
1. Bloqueante: alude a la falta total de poder realizar acciones
2. Crítico: impide la continuidad de una acción
3. Mayor: permite caminos alternativos para realizar un objetivo
4. Menor: permite realizar acciones con normalidad pero notifica al usuario
5. Cosmético: afecta a la perspectiva del usuario final

Prioridad(Efecto en el software):
1. Urgencia
2. Alta
3. Media
4. Baja

## Niveles de Prueba

1. Pruebas unitarias(primer nivel de testing) → Componentes | TDD
2. Pruebas de integración(segundo nivel de testing)/ Prueba de interfaces → Comunicación de componentes →Build | FDD
3. Pruebas de sistema | 
4. Pruebas de aceptacion | UAT

## Ambientes para Construcción de SW

- Desarrollo
- Prueba
- Pre-Producción
- Producción

## Caso de Prueba

Permite reproducir paso a paso el defecto encontrado

Buscar abarcar la mayor cantidad de situaciones posibles con la menor cantidad  de casos de prueba

## Ciclo de Prueba

Abarca la ejecucion de la totalidad de casos de prueba establecidos para una versión del sistema a probar
