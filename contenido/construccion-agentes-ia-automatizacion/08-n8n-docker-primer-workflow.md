# Primer vistazo a n8n y Docker

Imagina que a un equipo le llegan presupuestos todo el día. Alguien tiene que mirar cada monto y decidir si se aprueba, se deja pendiente o se revisa porque falta información. **n8n** permite automatizar ese recorrido conectando pasos en una pantalla.

## 1. Qué es n8n

Un **workflow** es el recorrido completo de la automatización. Cada paso es un **nodo**. El primer nodo suele ser un **disparador** (*trigger*). Le dice a n8n cuándo empezar. Por ejemplo, un disparador manual inicia el flujo cuando alguien pulsa el botón de ejecutar.

| Si ya conoces Make | En n8n lo verás como |
| --- | --- |
| Escenario | Workflow o flujo |
| Módulo | Nodo |
| Bundle o paquete de datos | Ítem o registro, aproximadamente |
| Filtro que decide por dónde sigue un dato | Nodo If con una salida para cada respuesta |

## 2. Cómo pasan los datos de un nodo a otro

Cada presupuesto es un **ítem**. Puede tener campos como el nombre del documento y el monto. Una sola **ejecución** puede procesar varios ítems. Si entran cuatro presupuestos, el mismo flujo puede revisar los cuatro y darles resultados distintos.

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/01-workflow-items.svg" target="_blank" rel="noopener noreferrer"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/01-workflow-items.svg" style="display:block;width:100%;height:auto" loading="lazy" alt="Manual Trigger inicia el flujo; Documentos de prueba genera ítems que evalúa el primer If."></a><figcaption>El disparador inicia una ejecución. El nodo de decisión revisa el monto de cada documento.</figcaption></figure>

Al abrir un nodo, **Input** muestra lo que recibió y **Output** lo que devolvió. Por ejemplo, si el nodo recibe un presupuesto por $320.000 y agrega el estado «Aprobado», el monto sigue ahí y el estado aparece como un campo nuevo.

## 3. Cómo se toma una decisión

Un nodo **If** hace una pregunta sobre los datos y tiene dos salidas: **true** si la condición se cumple y **false** si no se cumple. En el ejemplo de Calbuco se usan dos preguntas en orden. Primero, ¿tenemos el monto? Si lo tenemos, ¿supera los $500.000?

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/03-rutas-calbuco.svg" target="_blank" rel="noopener noreferrer"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/03-rutas-calbuco.svg" style="display:block;width:100%;height:auto" loading="lazy" alt="El primer If manda los datos sin monto a contingencia; el segundo separa valores superiores a 500.000 de los demás."></a><figcaption>El primer If comprueba si hay monto. El segundo aplica la regla de aprobación.</figcaption></figure>

| Lo que llega | Qué pasa |
| --- | --- |
| Presupuesto por $320.000 | **Aprobado**. El monto queda por debajo del límite. |
| Presupuesto por $500.000 | **Aprobado**. La condición pregunta si el monto es estrictamente mayor. |
| Presupuesto por $1.250.000 | **Pendiente**. El monto supera el límite. |
| Presupuesto sin monto | **Contingencia**. Hace falta revisar el documento. |

Un presupuesto sin monto puede recorrer una ruta prevista. Si un nodo falla al leer o guardar datos, miramos el historial de la ejecución para ubicar el error técnico.

## 4. Para qué sirve Docker

Puedes usar n8n como servicio en la nube o ejecutarlo en tu propio equipo. **Docker** permite hacer lo segundo usando una configuración repetible.

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/02-docker-local.svg" target="_blank" rel="noopener noreferrer"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/02-docker-local.svg" style="display:block;width:100%;height:auto" loading="lazy" alt="El navegador accede a n8n por el puerto local 5690 y el contenedor usa un volumen para los datos."></a><figcaption>El navegador abre n8n en tu equipo. Docker ejecuta la aplicación y el volumen conserva sus datos.</figcaption></figure>

| Palabra | Explicación |
| --- | --- |
| **Imagen** | Paquete de software que contiene n8n y lo que necesita para arrancar. |
| **Contenedor** | Una instancia de ese paquete que Docker pone en marcha. |
| **Puerto** | Número que usa el navegador para conectarse con la aplicación. |
| **Volumen** | Espacio donde Docker guarda datos para que sigan disponibles al recrear el contenedor. |
| **Compose** | Herramienta que lee un archivo con la configuración y pone en marcha los servicios. |

Cuando n8n corre en tu equipo, necesita que el equipo y el servicio sigan encendidos para ejecutar automatizaciones. También puedes exportar un workflow como archivo **JSON**, que guarda la estructura de los nodos y sus conexiones.

## Autoevaluación

```quiz
? Entran cuatro presupuestos en una sola ejecución. ¿Qué representa cada ítem?
- Un workflow completo.
+ Un documento con sus datos.
- Un contenedor de Docker.
> La misma ejecución puede llevar cuatro registros, uno por documento.
? Con la regla «mayor que $500.000», ¿qué pasa con un presupuesto de exactamente $500.000?
- Queda pendiente.
- Va a contingencia.
+ Queda aprobado.
> La condición solo se cumple si el monto supera los $500.000.
? ¿Qué elemento de Docker permite conservar los datos cuando se recrea el contenedor?
+ El volumen.
- El puerto.
- La pestaña del navegador.
> El volumen mantiene los datos fuera del contenedor.
```
