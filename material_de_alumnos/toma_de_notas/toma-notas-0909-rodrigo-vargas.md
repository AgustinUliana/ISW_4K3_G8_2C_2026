# TP2 No Evaluable: US y Estimación

listado user stories EcoHarmony Park:
- Registrar usuario visitante
- Consultar horarios de alimentación
- Visualizar el mapa interactivo
- Consultar información de show especial
- Comprar entradas
- Inscibirse a actividades
- Validar entradas en el ingreso
- Visualizar información de las exhibiciones

MVP:
- Hipótesis: Existen usrs que quieren saber el itinerario de alimentación de los animales, autogestionar sus entradas e inscribirse a las actividades en sus visitas al parque

- Alcance: 
    - Visualizar el mapa interactivo
    - Consultar horarios de alimentación
    - Comprar entradas 
    - Inscibirse a actividades
    - Consultar actividades
    - Registrar usuario visitante 

- Fuera del alcance: 


Describir user story "Comprar entradas"

1. Relato: Como visitante de EcoHarmony Park, quiero comprar entradas desde la aplicación, para poder gestionar mi ingreso al parque de manera anticipada y evitar demoras en la boletería
2. CA:
- El visitante debe estar registrado y autenticado para comprar entradas
- Debe poder acceder a la sección "Comprar entrada"
- Debe poder seleccionar la fecha de visita
- Debe indicar la cantidad de entradas
- La cantidad máxima de entradas por compra debe ser 10
- Debe indicar la edad correspondiente a cada visitante
- El sistema debe calcular y mostrar el monto total
- El visitante debe poder seleccionar el medio de pago:
    - Pago en efectivo en boleteria
    - Pago a traves de Mercado Pago
- Una vez completado correctamente el proceso, debe recibir una confirmación por email
- Las entradas adquiridas deben poder ser verificadas al momento del ingreso al parque
3. Pruebas de usuario:
- Compra válida: 
    - Dado: que el visitante está registrado
    - Cuando: selecciona una fecha, ingresa una cantidad válida de entradas y las edades correspondientes.
    - Entonces: el sistema calcula y muestra correctamente el importe total
- Probar comprar cantidad inválida de entradas:
    - Dado: que el visitante está realizando una compra
    - Cuando: intenta comprar 11 entradas
    - Entonces: el sistema rechaza la cantidad e informa que el máximo permitido es 10
- Pago en efectivo:
    - Dado: que el visitante completó los datos de las entradas
    - Cuando: selecciona efectivo
    - Entonces: el sistema registra la compra indicando que el pago será realizado en boleteria
- Pago electrónico:
    - Dado: que el visitante completo los datos de las entradas
    - Cuando: selecciona el pago a traves de Mercado Pago
    - Entonces: El sistema lo redirige a Mercado Pago para completar el pago
- Confirmación:
    - Dado: que el pago fue realizado correctamente
    - Cuando: Mercado Pago confirma la operación
    - Entonces: la aplicación registra la compra y envia la confirmación al email del visitante
4. Estimación: 8 Story Points
Es una de las historias más complejas porque involucra usuarios registrados, cálculo de precios, múltiples entradas, edades, dos modalidades de pago, integración con Mercado Pago y confirmación por email

# Notas

MVP → Lata de US del MVP 
- Hipótesis
- Alcance
- Fuera de alcance


