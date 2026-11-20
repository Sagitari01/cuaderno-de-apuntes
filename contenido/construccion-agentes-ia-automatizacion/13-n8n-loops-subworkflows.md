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

## Un ejemplo completo: disponibilidad de una biblioteca

Una biblioteca ficticia mantiene seis títulos. Para cada uno conoce `ejemplares_totales` y `prestamos_activos`. El cálculo es **disponibles = ejemplares totales menos préstamos activos**. Todos los títulos y cantidades siguientes son datos inventados para este ejemplo.

| Título | Ejemplares totales | Préstamos activos | Disponibles |
| --- | ---: | ---: | ---: |
| El faro de papel | 5 | 2 | 3 |
| Jardines de tinta | 4 | 4 | 0 |
| Atlas de las nubes verdes | 7 | 1 | 6 |
| La casa de los mapas | 3 | 0 | 3 |
| Viaje al bosque azul | 6 | 4 | 2 |
| Historias del reloj | 8 | 3 | 5 |

Los datos son números enteros no negativos y los préstamos no superan el total. El ejemplo se concentra en lotes y reutilización; no incorpora validación de inventario ni actualiza una base de datos.

### Del catálogo a los lotes

**Seis libros** es un nodo Edit Fields con una lista llamada `libros`. **Separar libros** usa Split Out sobre ese campo y produce seis ítems, uno por título. **Lotes de dos** es Loop Over Items con **Batch Size = 2** y sin activar Reset.

La salida **loop** se conecta a **Consultar disponibilidad**, que llama al subworkflow. Su salida regresa a la entrada de **Lotes de dos**: ese cable permite avanzar al siguiente lote. La salida **done** se conecta a **Catálogo disponible**, un nodo No Operation que permite inspeccionar el conjunto final sin modificarlo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/01-catalogo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Catálogo ejecutado con seis libros, loop, conexión de regreso y salida done."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/01-catalogo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Catálogo ejecutado con seis libros, loop, conexión de regreso y salida done." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El cable inferior regresa desde Consultar disponibilidad a Lotes de dos. La rama superior continúa por done.</figcaption></figure>

Para esta resta no hace falta un loop: Edit Fields puede procesar varios ítems. Aquí los lotes sirven para observar cómo se distribuye una lista y cómo se coordina una llamada reutilizable por cada grupo.

### El contrato de entrada y el cálculo

El subworkflow **Biblioteca | Calcular disponibilidad** tiene dos nodos. **Recibir libro** es Execute Sub-workflow Trigger y **Calcular disponibles** es Edit Fields. Las notas adhesivas resumen la responsabilidad de cada flujo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/03-subworkflow.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Subworkflow con Recibir libro, Calcular disponibles y una nota adhesiva."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/03-subworkflow.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Subworkflow con Recibir libro, Calcular disponibles y una nota adhesiva." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El cálculo queda en un flujo separado que pueden llamar distintos workflows.</figcaption></figure>

El disparador usa **Define using fields below** y declara tres entradas: `titulo` de tipo **String**, `ejemplares_totales` de tipo **Number** y `prestamos_activos` de tipo **Number**. Cada ítem recibido representa un libro; el subworkflow puede recibir dos en una misma ejecución.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/04-entradas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Entradas del subworkflow: titulo String, ejemplares_totales Number y prestamos_activos Number."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/04-entradas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Entradas del subworkflow: titulo String, ejemplares_totales Number y prestamos_activos Number." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los nombres y tipos del disparador definen qué datos recibe cada libro.</figcaption></figure>

En **Calcular disponibles**, el campo nuevo `disponibles` es de tipo **Number** y usa esta expresión:

<pre><code>&#123;&#123; $json.ejemplares_totales - $json.prestamos_activos &#125;&#125;</code></pre>

**Include Other Input Fields** está activado para conservar el título, el total y los préstamos junto al resultado. El último nodo devuelve esos cuatro campos al flujo que lo llamó.

### Asignar los datos al subworkflow

En **Consultar disponibilidad**, el origen es **Database** y se elige **Biblioteca | Calcular disponibilidad** desde la lista de workflows. El mapeo envía el valor del ítem actual a cada entrada:

| Entrada | Expresión |
| --- | --- |
| `titulo` | <code>&#123;&#123; $json.titulo &#125;&#125;</code> |
| `ejemplares_totales` | <code>&#123;&#123; $json.ejemplares_totales &#125;&#125;</code> |
| `prestamos_activos` | <code>&#123;&#123; $json.prestamos_activos &#125;&#125;</code> |

El modo **Run once with all items** envía juntos los dos libros de cada lote. **Wait For Sub-Workflow Completion** está activado para recibir los resultados antes de regresar al loop. En n8n 2.44.6, esta opción se agrega desde **Options > Add option** si aún no aparece. Si las entradas no se muestran después de elegir el subworkflow, cierra y vuelve a abrir el nodo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/05-mapeo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Execute Sub-workflow con tres expresiones mapeadas, modo por lote y espera activada."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/05-mapeo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Execute Sub-workflow con tres expresiones mapeadas, modo por lote y espera activada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La tercera llamada recibe dos libros y devuelve sus disponibilidades. Los tres campos se asignan desde el ítem actual.</figcaption></figure>

Con **Run once for each item**, los mismos seis libros producirían seis llamadas al subworkflow. El tamaño del lote y el modo de llamada son ajustes distintos.

### Qué muestran las ejecuciones y la salida done

En la ejecución del catálogo, el nodo de llamada se ejecuta **tres veces**, con dos ítems cada vez. El nodo Loop Over Items se ejecuta **cuatro veces**: tres para entregar lotes y una última para reunir los resultados por **done**.

| Ejecución de Loop Over Items | Ítems por loop | Ítems por done |
| --- | ---: | ---: |
| Run 1 | 2 | 0 |
| Run 2 | 2 | 0 |
| Run 3 | 2 | 0 |
| Run 4 | 0 | 6 |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/02-lote.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Loop Over Items con Batch Size igual a 2 y Run 1 of 4 con dos ítems en Loop Branch."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/02-lote.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Loop Over Items con Batch Size igual a 2 y Run 1 of 4 con dos ítems en Loop Branch." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Batch Size vale 2. Run 1 of 4, Loop Branch, entrega El faro de papel y Jardines de tinta: dos ítems del primer lote.</figcaption></figure>

El **6 items total** del cable es un acumulado de las tres pasadas, no el tamaño de un lote. El selector **Run** permite revisar cada pasada. En el nodo de llamada, **Run 3 of 3** muestra los dos últimos libros y una subejecución para ese lote.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/06-done.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Catálogo disponible con seis filas y los campos de cada libro."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/06-done.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Catálogo disponible con seis filas y los campos de cada libro." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La salida final conserva los seis libros e incorpora disponibles: 3, 0, 6, 3, 2 y 5.</figcaption></figure>

Los seis resultados conservan sus títulos y sus cantidades originales. El campo `disponibles` contiene, en el orden del catálogo, **3, 0, 6, 3, 2 y 5**. El libro sin ejemplares disponibles también sigue en la salida: este flujo no filtra libros.

### Otro workflow, el mismo cálculo

**Biblioteca | Consulta individual** usa Manual Trigger, Edit Fields (**Un libro**) y Execute Sub-workflow (**Consultar disponibilidad**). Envía **El faro de papel**, con 5 ejemplares totales y 2 préstamos activos, al mismo subworkflow del catálogo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/07-segundo-flujo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Segundo workflow ejecutado con Un libro y una llamada al mismo subworkflow."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/07-segundo-flujo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Segundo workflow ejecutado con Un libro y una llamada al mismo subworkflow." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La consulta individual reutiliza el cálculo sin un loop ni una copia de la resta.</figcaption></figure>

El nodo de llamada devuelve **un ítem con 3 disponibles**. La resta sigue definida únicamente en **Calcular disponibles**, dentro del subworkflow compartido. El segundo flujo solo prepara la entrada y utiliza el resultado.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/08-segundo-resultado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Segundo flujo con un libro, cinco ejemplares, dos préstamos y tres disponibles."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-biblioteca/08-segundo-resultado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Segundo flujo con un libro, cinco ejemplares, dos préstamos y tres disponibles." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una llamada, un resultado: El faro de papel tiene 3 ejemplares disponibles.</figcaption></figure>

## Workflows para importar

Los tres archivos incluyen los datos ficticios y las notas adhesivas que aparecen en las capturas. No requieren credenciales ni servicios externos. Las capturas y la importación corresponden a **n8n 2.44.6**.

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-biblioteca/subworkflow-disponibilidad.json" download="subworkflow-disponibilidad.json">Descargar el subworkflow de disponibilidad</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-biblioteca/biblioteca-lotes.json" download="biblioteca-lotes.json">Descargar el catálogo por lotes</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-biblioteca/biblioteca-consulta.json" download="biblioteca-consulta.json">Descargar la consulta individual</a></p>

Importa cada JSON en un workflow nuevo mediante **Import > From file**, comenzando por el subworkflow. En los otros dos workflows, abre **Consultar disponibilidad** y selecciona el subworkflow que acabas de importar desde **From list**. El marcador `ELEGIR_SUBWORKFLOW` no es un identificador válido: debes reemplazarlo con esa selección, porque cada instancia asigna sus propios identificadores. Si aparecen dos entradas con el mismo nombre, elige la del workflow guardado, no el marcador importado.

Al seleccionar el subworkflow desde **Workflow > From list** en n8n 2.44.6, estos archivos conservan los tres campos y sus expresiones: no necesitas volver a mapearlos. Comprueba que coincidan con la tabla anterior, que el modo sea **Run once with all items** y que la espera esté activada. Si los campos no aparecen, cierra y vuelve a abrir el nodo. Ejecuta el catálogo para obtener los seis resultados y la consulta individual para obtener uno. Ambos usan Manual Trigger, por lo que estas pruebas se lanzan desde **Execute workflow**.

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
