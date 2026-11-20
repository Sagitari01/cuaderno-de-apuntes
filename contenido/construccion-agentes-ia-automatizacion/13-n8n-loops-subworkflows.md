# Loops y subworkflows en n8n

En n8n, un **loop** permite procesar ítems por lotes. Un **subworkflow** permite que distintos flujos llamen a los mismos pasos. Puedes combinarlos cuando quieres aplicar una operación reutilizable a un lote a la vez.

## Procesar ítems por lotes

Muchos nodos de n8n procesan todos los ítems que reciben. Usa **Loop Over Items** cuando quieras controlar cuántos se procesan en cada pasada. La opción **Batch Size** fija el tamaño máximo del lote.

| Parte del nodo | Qué hace |
| --- | --- |
| **loop** | Entrega el siguiente lote a los nodos que lo procesan. |
| **Conexión de regreso** | Lleva la salida del último nodo de procesamiento a la entrada de **Loop Over Items**. Así el flujo pide el siguiente lote. |
| **done** | Entrega juntos los ítems procesados cuando termina el recorrido. Conecta aquí lo que debe ocurrir después de procesar todos los lotes. |

Por ejemplo, si entran cinco ítems y configuras **Batch Size** en 2, por **loop** salen tres lotes de 2, 2 y 1. Cuando vuelve el último lote, **done** entrega los cinco ítems procesados. Si en el lienzo ves un total acumulado, abre el nodo y usa el selector **Run** para revisar cuántos ítems salieron en cada pasada.

Si tus datos llegan como una lista dentro de un solo ítem, puedes usar **Split Out** antes del loop para convertir cada elemento de la lista en un ítem.

## Reutilizar pasos con un subworkflow

Un subworkflow tiene su propio lienzo. El flujo que lo llama le entrega datos y recibe el resultado del último nodo que se ejecuta en el subworkflow.

1. En el subworkflow, agrega el disparador **Execute Sub-workflow Trigger**. Puedes definir los campos que esperas recibir y sus tipos.
2. Agrega los nodos que realizan la tarea. Por ejemplo, un **Edit Fields** puede recibir un texto y devolverlo sin espacios al inicio ni al final.
3. En el flujo principal, agrega **Execute Sub-workflow** (también llamado **Execute Workflow** en algunas versiones), selecciona el subworkflow y asigna los valores que enviará a cada campo.
4. Si los siguientes nodos necesitan usar la salida del subworkflow, activa **Wait for Sub-Workflow Completion**.

Por ejemplo, un flujo que importa registros y otro que recibe un formulario pueden llamar al mismo subworkflow para limpiar nombres. Ambos le envían el campo `nombre` y reciben `nombre_limpio`. La regla de limpieza queda en un solo lugar.

## Combinar ambas ideas

Conecta la salida **loop** a **Execute Sub-workflow** y vuelve desde ese nodo a la entrada de **Loop Over Items**. En el nodo de llamada, elige **Run once with all items** para hacer una ejecución del subworkflow por cada lote. Si eliges **Run once for each item**, se hará una llamada por cada ítem del lote.

| Si ves esto | Revisa esto |
| --- | --- |
| Solo se procesa el primer lote. | Comprueba que el último nodo de esa rama regrese a la entrada de **Loop Over Items**. |
| El subworkflow recibe campos vacíos. | Revisa los valores asignados a los campos de entrada. Si no aparecen los campos, guarda el subworkflow y vuelve a abrir el nodo que lo llama. |
| Hay más llamadas de las esperadas. | Revisa el modo de ejecución del nodo de llamada y el número de ítems que entra en el loop. |

## Autoevaluación

```quiz
? Si entran siete ítems y Batch Size vale 3, ¿qué pasa por loop?
+ Tres lotes de 3, 3 y 1.
- Dos lotes de 3 y el último ítem sale solo por done.
- Un lote de siete ítems.
> Batch Size es el tamaño máximo. El último lote contiene los ítems que queden.
? ¿Dónde defines los campos de entrada de un subworkflow?
- En la salida done del loop.
+ En el disparador del subworkflow.
- En el último nodo del workflow principal.
> El nodo que llama al subworkflow asigna un valor a cada campo definido en el disparador.
```

## Documentación de referencia

- [Loop Over Items](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.splitinbatches/)
- [Execute Sub-workflow](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executeworkflow/)
- [Subworkflows en n8n](https://docs.n8n.io/flow-logic/subworkflows/)
- [Cómo transformar y encaminar datos en n8n](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-transformar-encaminar-datos)
