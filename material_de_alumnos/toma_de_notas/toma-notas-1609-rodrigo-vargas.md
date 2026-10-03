# Recircula tus prendas

Hipotesis: Existe gente que quiere vender sus ropas como prendas de segunda mano

Alcance:
- US1: Registrar vendedor |→ Vendedor
- US2: Registrar formulario de selección de prendas |→ Vendedor
- US3: Registrar ficha básica de prenda |→ Analista de selección
- US4: Completar ficha de producto |→ Analista de publicación
- US5: Confirmar propuesta de venta |→ Vendedor

| - Consultar productos        |
| - Consultar un producto      | 
| - Comprar carrito de compras |  No entran en el MVP
| - Registrar comprador        |
| - liquidar ventas            |

NO incluye:
- Liquidacion
- Validación de telefono
- Donaciones
- Logistica
- Compra de prendas
- Notificación por email de seguimiento
- Sign in/Log in con Google

US Canónica: Registrar categoria de prenda
Complejidad baja(ABMC simple), Incertidumbre baja(Categorias varias iniciales y se agregan en caso de haber sido contempladas en un principio) 


US3: Registrar ficha básica de prenda 

1. Relato: Como analista de selección quiero registrar la ficha básica de la prenda para establecer si cumple con las politicas definidas para ser seleccionada para publicación.

2. Criterios de aceptación:
- El AS debe indicar categoria de la prenda, marca y si está seleccionada o no
- En el caso de que la prenda este 
- 

3. Pruebas de usuario:
- Probar cargar la ficha indicando categoría, marca y el estado(seleccionada o no) → Pasa
- Probar cargar la ficha con algun campo faltante → No pasa

4. Estimación:  5 story points
Es una de las historias simples donde existe una cierta incertidumbre en la generación del qr, es un formulario de varios campos que son cargados por el analista de selección, un acceso a la base de datos para el registro de la ficha y la generacion de un qr unico asociado al codigo de producto


