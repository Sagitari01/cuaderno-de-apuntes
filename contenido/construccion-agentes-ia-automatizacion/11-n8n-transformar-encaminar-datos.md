# Cómo transformar y encaminar datos en n8n

Una tienda recibe seis pedidos y necesita decidir qué hacer con cada uno: calcular el IVA, descartar los que traen un monto inválido, aplicar un descuento según el tipo de cliente y clasificar cada total. En este apunte armas ese flujo en n8n y sigues los datos nodo por nodo. Para cada paso verás qué recibe el nodo, qué cambia y qué entrega.

Si todavía no abres el editor, parte por el [primer apunte de n8n](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-docker-primer-workflow). Aquí damos por hecho que puedes crear un workflow y agregar nodos.

## 1. El problema y los datos de entrada

Estos son los seis pedidos del día. Cada fila será un **ítem** en n8n.

| Cliente | Monto | ¿Cliente VIP? |
| --- | --- | --- |
| Ana | 25000 | Sí |
| Bruno | 80000 | No |
| Carla | 0 | Sí |
| Diego | 120000 | Sí |
| Elena | 15000 | No |
| Fabián | -5000 | No |

Carla y Fabián traen montos inválidos a propósito, para que el flujo tenga algo que descartar. Las reglas del negocio son estas.

| Regla | Detalle |
| --- | --- |
| IVA | Se suma un 19 % al monto. |
| Pedido válido | El monto debe ser mayor que 0. |
| Descuento | 20 % para clientes VIP y 5 % para el resto. Se aplica sobre el monto con IVA. |
| Tramo | **Bajo** si el total es menor que 50000. **Medio** si va de 50000 a 100000, ambos incluidos. **Alto** si supera 100000. |

El flujo tiene dos tramos. Este es el primero, hasta que las dos ramas del IF vuelven a unirse en el Merge. El segundo tramo, con el Switch, aparece en el paso 10. El número sobre cada conexión indica cuántos ítems pasaron por ella.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/00a-flujo-inicio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="508" alt="Primer tramo del flujo en n8n: un disparador, un Code, un Edit Fields, un Filter, un IF con dos ramas y un Merge."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/00a-flujo-inicio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Primer tramo del flujo en n8n: un disparador, un Code, un Ed" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Primer tramo, ya ejecutado. Del disparador sale 1 ítem, el Code entrega 6, el Filter deja pasar 4 y el IF los reparte de a 2 entre las dos ramas.</figcaption></figure>

Esta tabla resume lo que hace cada nodo con los datos del caso.

| Nodo | Tipo | Recibe | Entrega |
| --- | --- | --- | --- |
| Pedidos de ejemplo | Code | El inicio manual | 6 ítems con `cliente`, `monto` y `vip`. |
| Calcular IVA | Edit Fields | 6 ítems | Los mismos 6, con el campo nuevo `monto_con_iva`. |
| Filter: solo montos válidos | Filter | 6 ítems | 4 ítems. Carla y Fabián quedan fuera. |
| IF: ¿cliente VIP? | IF | 4 ítems | 2 por la salida `true` y 2 por la salida `false`. |
| Descuento VIP 20% y Descuento normal 5% | Edit Fields | 2 ítems cada uno | Los mismos ítems, con `descuento` y `tipo`. |
| Merge: juntar ramas | Merge | 2 + 2 ítems | 4 ítems en una sola lista. |
| Armar resumen | Edit Fields | 4 ítems | Los mismos 4, con `total_a_pagar` y `mensaje`. |
| Switch: tramo del total | Switch | 4 ítems | 2 por `Bajo`, 1 por `Medio` y 1 por `Alto`. |
| Tramo bajo, Tramo medio y Tramo alto | Edit Fields | 2, 1 y 1 ítems | Los mismos ítems, con el campo `tramo`. |

## 2. Cómo leer el editor: INPUT, OUTPUT y los ítems

Al hacer doble clic sobre un nodo se abre su panel. Tiene tres zonas:

- **INPUT**, a la izquierda: los datos que llegan al nodo, agrupados por el nodo de origen.
- **Parámetros**, al centro: lo que configuras.
- **OUTPUT**, a la derecha: lo que el nodo entrega después de ejecutarse.

Tanto INPUT como OUTPUT se pueden ver como **Schema** (los campos y un ejemplo de su valor), **Table** (una fila por ítem) o **JSON**. Para probar un nodo sin ejecutar todo el flujo, usa **Execute step**. Si necesita datos de nodos anteriores, n8n los ejecuta primero.

### Los datos de prueba

Crea un disparador manual y conéctalo a un nodo **Code**. Elige **Code in JavaScript**, deja el modo **Run Once for All Items** y reemplaza el código por este. Cada objeto con la clave `json` se convierte en un ítem.

```javascript
// Datos de ejemplo: 6 pedidos de una tienda. Cada objeto = 1 item en n8n.
return [
  { json: { cliente: 'Ana',    monto: 25000,  vip: true  } },
  { json: { cliente: 'Bruno',  monto: 80000,  vip: false } },
  { json: { cliente: 'Carla',  monto: 0,      vip: true  } },
  { json: { cliente: 'Diego',  monto: 120000, vip: true  } },
  { json: { cliente: 'Elena',  monto: 15000,  vip: false } },
  { json: { cliente: 'Fabián', monto: -5000,  vip: false } }
];
```

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/01-entrada-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1700" height="950" alt="Panel del nodo Pedidos de ejemplo con el código a la izquierda y una tabla de seis filas a la derecha."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/01-entrada-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel del nodo Pedidos de ejemplo con el código a la izquier" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Pedidos de ejemplo</strong> después de pulsar <strong>Execute step</strong>. <strong>①</strong> INPUT: el disparador manual no envía campos, por eso aparece vacío. <strong>②</strong> El código que crea los datos. <strong>③</strong> OUTPUT: 6 ítems con <code>cliente</code>, <code>monto</code> y <code>vip</code>.</figcaption></figure>

Cada fila de OUTPUT es un ítem. Los nodos que siguen se ejecutan una vez por ítem, y por eso un solo nodo puede dar resultados distintos para Ana y para Bruno.

### Valor fijo o expresión

Cada campo de un nodo puede llevar un **valor fijo** o una **expresión**.

| | Valor fijo | Expresión |
| --- | --- | --- |
| Qué es | Un texto o un número escrito tal cual. | Una fórmula entre dobles llaves que n8n calcula. |
| Ejemplo | `VIP` o `0.2` | <code>&#123;&#123; $json.monto * 1.19 &#125;&#125;</code> |
| Cuándo usarlo | El valor es el mismo para todos los ítems. | El valor depende del ítem que se está procesando. |

Dentro de una expresión, <code>$json</code> es **el ítem actual**: el que el nodo está procesando en ese momento. <code>$json.monto</code> lee el campo `monto` de ese ítem. Como el nodo procesa seis ítems, la expresión se evalúa seis veces, una con los datos de Ana, otra con los de Bruno y así hasta Fabián. Debajo del campo, n8n muestra una vista previa del resultado con el primer ítem.

### Leer un dato de otro nodo

`$json` solo ve el ítem que llega al nodo. Si necesitas un dato de un nodo anterior, nómbralo entre paréntesis. Esta expresión devuelve el cliente del ítem original, aunque el ítem haya pasado por varios nodos.

<pre><code class="language-text">&#123;&#123; $('Pedidos de ejemplo').item.json.cliente &#125;&#125;</code></pre>

`.item` devuelve el ítem de ese nodo que dio origen al ítem actual, así que cada fila obtiene su propio valor. Para probarlo, agrega al final de **Armar resumen** un nodo **Edit Fields** con un campo `origen` de tipo **String** y esa expresión. En OUTPUT, `origen` debe repetir el valor de `cliente` en cada ítem. Puedes borrar ese nodo después.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/15-variables.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="950" alt="Nodo Edit Fields con el campo origen y una expresión que lee el cliente del nodo Pedidos de ejemplo. A la derecha, la vista Schema del resultado."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/15-variables.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Edit Fields con el campo origen y una expresión que lee" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El nodo de prueba. <strong>①</strong> La expresión que lee el campo de otro nodo. <strong>②</strong> El campo <code>origen</code> aparece en OUTPUT con el mismo valor que <code>cliente</code> (Ana en el primer ítem).</figcaption></figure>

## 3. Si los pedidos llegan agrupados: Split Out

Los pedidos de este caso ya llegan como seis ítems. Pero muchas APIs responden con **un solo ítem que contiene una lista**. El nodo **Split Out** convierte esa lista en un ítem por elemento.

Para probarlo, usa este código en un nodo **Code** llamado `Pedidos agrupados`. Devuelve un único ítem con la lista `pedidos`.

```javascript
// Los pedidos llegan dentro de UN solo item, en una lista llamada pedidos.
return [
  { json: { pedidos: [
    { cliente: 'Ana', monto: 25000, vip: true },
    { cliente: 'Bruno', monto: 80000, vip: false },
    { cliente: 'Carla', monto: 0, vip: true },
    { cliente: 'Diego', monto: 120000, vip: true },
    { cliente: 'Elena', monto: 15000, vip: false },
    { cliente: 'Fabián', monto: -5000, vip: false }
  ] } }
];
```

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/14-split-out-origen.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1190" height="950" alt="Nodo Code con una lista de pedidos dentro de un solo ítem y su salida de un ítem con el campo pedidos."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/14-split-out-origen.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Code con una lista de pedidos dentro de un solo ítem y " style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Pedidos agrupados</strong>. <strong>①</strong> El código devuelve un solo ítem. <strong>②</strong> OUTPUT muestra «1 item» y, dentro, la lista <code>pedidos</code> con seis elementos.</figcaption></figure>

Conecta un nodo **Split Out** después del Code. En **Fields To Split Out** escribe `pedidos`. Deja **Include** en **No Other Fields**, porque el ítem original no trae otros datos.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/13-split-out.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1700" height="950" alt="Nodo Split Out con el campo pedidos configurado. A la izquierda, un ítem con la lista pedidos. A la derecha, seis filas."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/13-split-out.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Split Out con el campo pedidos configurado" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Separar pedidos</strong>. <strong>①</strong> INPUT: un ítem con la lista <code>pedidos</code>. <strong>②</strong> El campo que contiene la lista. <strong>③</strong> OUTPUT: 6 ítems.</figcaption></figure>

La salida son los mismos seis ítems que entrega **Pedidos de ejemplo**: Ana, Bruno, Carla, Diego, Elena y Fabián, cada uno con `cliente`, `monto` y `vip`. En un flujo real, esta variante reemplazaría al nodo Code de datos de prueba y el resto del flujo seguiría igual. La operación inversa, juntar ítems en una lista, la hace el nodo **Aggregate**.

## 4. Edit Fields (Set): agregar un campo

**Edit Fields**, que en la documentación aparece como **Set**, crea campos nuevos o modifica los que ya existen. Aquí calcula el monto con IVA.

1. Agrega **Edit Fields** después del Code y llámalo `Calcular IVA`.
2. Deja **Mode** en **Manual Mapping** y pulsa **Add Field**.
3. Escribe el nombre `monto_con_iva` y elige el tipo **Number**.
4. En el valor usa esta expresión.

<pre><code class="language-text">&#123;&#123; $json.monto * 1.19 &#125;&#125;</code></pre>

5. Activa **Include Other Input Fields** para conservar `cliente`, `monto` y `vip`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/02-set-iva.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="950" alt="Nodo Edit Fields con el campo monto_con_iva, la expresión de IVA y una tabla de salida con una columna nueva."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/02-set-iva.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Edit Fields con el campo monto_con_iva, la expresión de" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Calcular IVA</strong>. <strong>①</strong> La expresión del campo. <strong>②</strong> Con esta opción activa, los campos originales pasan al resultado. <strong>③</strong> La columna <code>monto_con_iva</code> es nueva.</figcaption></figure>

En OUTPUT salen los mismos 6 ítems con una columna más. Ana pasa de 25000 a 29750 y Bruno de 80000 a 95200. Carla queda en 0 y Fabián en -5950: el IVA no corrige los montos inválidos, y por eso el siguiente nodo los descarta. Si desactivas **Include Other Input Fields**, el resultado solo contiene los campos que creaste.

## 5. Filter: descartar lo que no sirve

**Filter** deja pasar los ítems que cumplen una condición y descarta el resto.

1. Agrega **Filter** y llámalo `Filter: solo montos válidos`.
2. En el primer valor usa esta expresión.

<pre><code class="language-text">&#123;&#123; $json.monto &#125;&#125;</code></pre>

3. Abre el menú de operadores, elige **Number** y luego **is greater than**.
4. En el segundo valor escribe `0`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/16-filter-operadores.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="780" height="560" alt="Menú de operadores de un nodo Filter con el grupo Number desplegado y las opciones exists, is empty, is equal to, is greater than y otras."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/16-filter-operadores.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Menú de operadores de un nodo Filter con el grupo Number des" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los operadores se agrupan por tipo de dato: String, Number, Date &amp; Time, Boolean, Array y Object. Para comparar montos, elige <strong>Number</strong> y luego <strong>is greater than</strong>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/03-filter-kept.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="950" alt="Nodo Filter con la condición monto mayor que cero y una salida de cuatro ítems."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/03-filter-kept.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Filter con la condición monto mayor que cero y una sali" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Filter: solo montos válidos</strong>. <strong>①</strong> Valor 1, como expresión. <strong>②</strong> El operador. Debajo está el valor 2, que es <code>0</code>. <strong>③</strong> La pestaña <strong>Kept</strong> muestra los 4 ítems que pasan. <strong>④</strong> La pestaña <strong>Discarded</strong> muestra los que se quedaron fuera.</figcaption></figure>

El Filter tiene una sola salida: la de los ítems que pasan. La pestaña **Discarded** sirve para revisar qué quedó fuera, pero esos ítems no siguen por el flujo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/04-filter-discarded.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="950" alt="Pestaña Discarded del nodo Filter con dos filas: Carla con monto 0 y Fabián con monto -5000."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/04-filter-discarded.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Pestaña Discarded del nodo Filter con dos filas: Carla con m" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><strong>①</strong> La pestaña <strong>Discarded</strong>. <strong>②</strong> Los dos ítems descartados: Carla, con monto 0, y Fabián, con monto -5000.</figcaption></figure>

## 6. IF: elegir entre dos caminos

**IF** también evalúa una condición, pero no descarta nada: reparte los ítems entre dos salidas, **true** y **false**.

| | Filter | IF |
| --- | --- | --- |
| Salidas | Una: los ítems que cumplen. | Dos: `true` y `false`. |
| Qué pasa con los que no cumplen | Quedan fuera del flujo. | Siguen por la salida `false`. |
| Úsalo para | Limpiar los datos. | Darle un tratamiento distinto a cada grupo. |

Aquí el IF separa a los clientes VIP.

1. Agrega **IF** después del Filter y llámalo `IF: ¿cliente VIP?`.
2. En el primer valor usa esta expresión.

<pre><code class="language-text">&#123;&#123; $json.vip &#125;&#125;</code></pre>

3. Elige el operador **Boolean → is true**. Este operador no necesita un segundo valor.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/05-if-true.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="950" alt="Nodo IF con la condición vip es true y una tabla con Ana y Diego en la rama true."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/05-if-true.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo IF con la condición vip es true y una tabla con Ana y D" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>IF: ¿cliente VIP?</strong>. <strong>①</strong> Valor 1. <strong>②</strong> El operador booleano. <strong>③</strong> La pestaña <strong>True Branch</strong> muestra a Ana y a Diego. <strong>④</strong> La pestaña <strong>False Branch</strong> tiene el resto.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/06-if-false.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="950" alt="Pestaña False Branch del nodo IF con Bruno y Elena."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/06-if-false.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Pestaña False Branch del nodo IF con Bruno y Elena" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><strong>①</strong> La pestaña <strong>False Branch</strong>. <strong>②</strong> Bruno y Elena, los clientes que no son VIP, salen por esta rama.</figcaption></figure>

Para comprobar el reparto, suma los ítems de las dos pestañas. Deben dar 4, los mismos que salieron del Filter. Si necesitas más de una condición, **Add condition** permite combinarlas.

## 7. Un Edit Fields por rama

Cada salida del IF lleva su propio **Edit Fields**. Los dos hacen lo mismo con valores distintos. Activa **Include Other Input Fields** en ambos.

| Nodo | Conectado a | Campo | Tipo | Valor fijo |
| --- | --- | --- | --- | --- |
| Descuento VIP 20% | Salida `true` | `descuento` | Number | `0.2` |
| Descuento VIP 20% | Salida `true` | `tipo` | String | `VIP` |
| Descuento normal 5% | Salida `false` | `descuento` | Number | `0.05` |
| Descuento normal 5% | Salida `false` | `tipo` | String | `Normal` |

Aquí no hace falta una expresión: el valor es el mismo para todos los ítems de la rama, y el IF ya decidió qué ítems llegan a cada una.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/07-set-vip.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="950" alt="Nodo Edit Fields de la rama VIP con descuento 0.2 y tipo VIP, y la tabla de salida con Ana y Diego."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/07-set-vip.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Edit Fields de la rama VIP con descuento 0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Descuento VIP 20%</strong>. <strong>①</strong> El valor fijo del descuento. <strong>②</strong> y <strong>③</strong> Las columnas <code>descuento</code> y <code>tipo</code> son nuevas. Solo llegan Ana y Diego.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/08-set-normal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="950" alt="Nodo Edit Fields de la rama normal con descuento 0.05 y tipo Normal, y la tabla de salida con Bruno y Elena."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/08-set-normal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Edit Fields de la rama normal con descuento 0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Descuento normal 5%</strong>. Es el mismo nodo con otros valores. <strong>①</strong> El descuento. <strong>②</strong> y <strong>③</strong> Las columnas <code>descuento</code> y <code>tipo</code>. Solo llegan Bruno y Elena.</figcaption></figure>

## 8. Merge: volver a un solo camino

Después de las dos ramas, el resto del flujo es igual para todos los ítems. **Merge** une las ramas en una sola lista. Sin él, el nodo siguiente se ejecutaría una vez por cada rama.

1. Agrega **Merge** a continuación de **Descuento VIP 20%**. Esa conexión queda en la entrada **Input 1**.
2. Arrastra la salida de **Descuento normal 5%** hasta la entrada **Input 2** del Merge.
3. Deja **Mode** en **Append** y llámalo `Merge: juntar ramas`.

<figure class="lamina-apunte" style="position:relative;max-width:760px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/17-merge-segunda-entrada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="860" height="500" alt="Lienzo de n8n con un IF cuyas dos ramas llegan al nodo Merge, una a Input 1 y la otra a Input 2."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/17-merge-segunda-entrada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Lienzo de n8n con un IF cuyas dos ramas llegan al nodo Merge" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Merge tiene dos entradas. La rama VIP, arriba, llega a <strong>Input 1</strong> y la rama normal, abajo, a <strong>Input 2</strong>. La segunda conexión se hace arrastrando desde la salida de <strong>Descuento normal 5%</strong>.</figcaption></figure>

En modo **Append**, el Merge coloca primero los ítems de la entrada 1 y después los de la entrada 2. El resultado son 4 ítems: Ana y Diego, y después Bruno y Elena. El orden cambia respecto de la entrada original, pero no se pierde ningún dato. n8n ofrece otros modos para combinar ítems, por ejemplo por un campo en común.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/09-merge.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1265" height="525" alt="Nodo Merge en modo Append. A la izquierda aparecen dos entradas, Input 1 e Input 2, y a la derecha una tabla de cuatro ítems."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/09-merge.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Merge en modo Append" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Merge: juntar ramas</strong>. <strong>①</strong> y <strong>②</strong> INPUT identifica de qué entrada viene cada grupo. <strong>③</strong> El modo <strong>Append</strong>. <strong>④</strong> OUTPUT: 4 ítems, primero los VIP y luego los normales.</figcaption></figure>

## 9. Armar el resumen

El último **Edit Fields** del tramo común calcula cuánto paga cada cliente y escribe un mensaje. Se llama `Armar resumen`, tiene **Include Other Input Fields** activo y define dos campos.

| Campo | Tipo | Expresión |
| --- | --- | --- |
| `total_a_pagar` | Number | <code>&#123;&#123; Math.round($json.monto_con_iva * (1 - $json.descuento)) &#125;&#125;</code> |
| `mensaje` | String | <code>&#123;&#123; $json.cliente &#125;&#125; (&#123;&#123; $json.tipo &#125;&#125;): paga $&#123;&#123; Math.round($json.monto_con_iva * (1 - $json.descuento)) &#125;&#125; con &#123;&#123; $json.descuento * 100 &#125;&#125;% de descuento</code> |

La primera aplica el descuento al monto con IVA y redondea. La segunda mezcla texto fijo con tres expresiones: cada fragmento entre dobles llaves se calcula por separado y el resto queda tal cual.

Para copiar sin errores, estas son las dos expresiones.

<pre><code class="language-text">&#123;&#123; Math.round($json.monto_con_iva * (1 - $json.descuento)) &#125;&#125;</code></pre>

<pre><code class="language-text">&#123;&#123; $json.cliente &#125;&#125; (&#123;&#123; $json.tipo &#125;&#125;): paga $&#123;&#123; Math.round($json.monto_con_iva * (1 - $json.descuento)) &#125;&#125; con &#123;&#123; $json.descuento * 100 &#125;&#125;% de descuento</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/10-set-resumen.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="950" alt="Nodo Edit Fields con los campos total_a_pagar y mensaje y una tabla de cuatro ítems con el resultado."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/10-set-resumen.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Edit Fields con los campos total_a_pagar y mensaje y un" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Armar resumen</strong>. <strong>①</strong> El total. <strong>②</strong> El mensaje. <strong>③</strong> La columna <code>total_a_pagar</code> en OUTPUT.</figcaption></figure>

Con los datos del caso, el resultado es este.

| Cliente | Tipo | Monto con IVA | Descuento | `total_a_pagar` |
| --- | --- | --- | --- | --- |
| Ana | VIP | 29750 | 0.2 | 23800 |
| Diego | VIP | 142800 | 0.2 | 114240 |
| Bruno | Normal | 95200 | 0.05 | 90440 |
| Elena | Normal | 17850 | 0.05 | 16958 |

## 10. Switch: más de dos salidas

El IF decide entre dos caminos. Para clasificar cada total en **tres** tramos, el **Switch** lo resuelve en un solo nodo con una salida por regla.

1. Agrega **Switch** después de **Armar resumen** y llámalo `Switch: tramo del total`. Deja **Mode** en **Rules**.
2. Crea tres reglas con **Add Routing Rule**. En cada una, el primer valor es esta expresión.

<pre><code class="language-text">&#123;&#123; $json.total_a_pagar &#125;&#125;</code></pre>

3. Elige el operador y el segundo valor de cada regla, y activa **Rename Output** para ponerle nombre a la salida.

| Regla | Operador | Segundo valor | Nombre de la salida |
| --- | --- | --- | --- |
| 1 | Number → is less than | `50000` | `Bajo` |
| 2 | Number → is less than or equal to | `100000` | `Medio` |
| 3 | Number → is greater than | `100000` | `Alto` |

Las reglas se evalúan **en orden** y el ítem sale por la primera que cumple. Por eso la regla `Medio` no necesita comprobar que el total sea de 50000 o más: si llegó a ella, la regla `Bajo` ya lo descartó.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/11-switch.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="1060" alt="Nodo Switch con tres reglas de enrutamiento y los nombres de salida Bajo, Medio y Alto. A la derecha, las pestañas de salida con sus ítems."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/11-switch.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Switch con tres reglas de enrutamiento y los nombres de" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo <strong>Switch: tramo del total</strong>. <strong>①</strong>, <strong>②</strong> y <strong>③</strong> Los operadores de las reglas Bajo, Medio y Alto. <strong>④</strong> En OUTPUT hay una pestaña por salida: Bajo (2 ítems), Medio (1) y Alto (1).</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/12-switch-medio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1170" height="1060" alt="Pestaña Medio de la salida del Switch con una fila: Bruno con un total de 90440."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/12-switch-medio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Pestaña Medio de la salida del Switch con una fila: Bruno co" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><strong>①</strong> La pestaña <strong>Medio</strong>. <strong>②</strong> Bruno, con un total de 90440, es el único ítem de ese tramo.</figcaption></figure>

Cada salida lleva un **Edit Fields** que escribe el campo `tramo` con un valor fijo de tipo **String**: `Bajo` en `Tramo bajo`, `Medio` en `Tramo medio` y `Alto` en `Tramo alto`. Con los datos del caso, Ana y Elena van a `Bajo`, Bruno a `Medio` y Diego a `Alto`.

<figure class="lamina-apunte" style="position:relative;max-width:900px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/00c-flujo-switch.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1351" height="751" alt="Parte final del flujo: Merge, Armar resumen, el Switch con tres salidas y los nodos Tramo bajo, Tramo medio y Tramo alto."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-transformar-datos/00c-flujo-switch.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Parte final del flujo: Merge, Armar resumen, el Switch con t" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Switch tiene tres salidas con nombre. Los números sobre cada conexión confirman el reparto: 2 ítems por <code>Bajo</code>, 1 por <code>Medio</code> y 1 por <code>Alto</code>.</figcaption></figure>

### La misma decisión con IF

Un Switch con tres reglas equivale a dos IF encadenados. La comparación muestra por qué conviene el Switch cuando hay más de dos salidas.

| | Dos IF encadenados | Switch |
| --- | --- | --- |
| Nodos | Dos. El segundo recibe la salida `false` del primero. | Uno. |
| Cómo se lee | Primer IF: ¿total menor que 50000? Si no, segundo IF: ¿total menor o igual a 100000? | Una lista de reglas con una salida por tramo. |
| Salidas finales | Tres, repartidas entre dos nodos. | Tres, en el mismo nodo y con nombre. |
| Cuando agregas un cuarto tramo | Sumas otro IF. | Sumas otra regla. |

## 11. Práctica: comprueba que cada ítem llega a su rama

### Qué debes ver en cada nodo

Ejecuta el workflow completo con **Execute workflow** y abre cada nodo. Compara su OUTPUT con esta tabla.

| Nodo | Qué debe aparecer en OUTPUT |
| --- | --- |
| Pedidos de ejemplo | 6 ítems: Ana, Bruno, Carla, Diego, Elena y Fabián. |
| Calcular IVA | 6 ítems con `monto_con_iva`. Carla tiene 0 y Fabián -5950. |
| Filter: solo montos válidos | **Kept**: 4 ítems (Ana, Bruno, Diego, Elena). **Discarded**: Carla y Fabián. |
| IF: ¿cliente VIP? | **True**: Ana y Diego. **False**: Bruno y Elena. |
| Descuento VIP 20% / normal 5% | 2 ítems cada uno, con `descuento` y `tipo`. |
| Merge: juntar ramas | 4 ítems: Ana, Diego, Bruno y Elena, en ese orden. |
| Armar resumen | 4 ítems con `total_a_pagar` de 23800, 114240, 90440 y 16958. |
| Switch: tramo del total | **Bajo**: Ana y Elena. **Medio**: Bruno. **Alto**: Diego. |

Para seguir a un solo cliente, busca su nombre en la columna `cliente` de cada nodo. Si un ítem no aparece donde esperabas, revisa el nodo anterior: normalmente el ítem se quedó en la otra pestaña del Filter o del IF.

### Casos de borde

Reemplaza el código de **Pedidos de ejemplo** por este. Los datos ponen a prueba los límites de los tramos y los dos tipos de cliente.

```javascript
return [
  { json: { cliente: 'Prueba A', monto: 100000, vip: false } },
  { json: { cliente: 'Prueba B', monto: 40000, vip: true } },
  { json: { cliente: 'Prueba C', monto: 105042, vip: true } },
  { json: { cliente: 'Prueba D', monto: 52521, vip: true } },
  { json: { cliente: 'Prueba E', monto: 44230, vip: false } },
  { json: { cliente: 'Prueba F', monto: 1000, vip: false } }
];
```

Con estos datos, el Filter deja pasar los seis pedidos, porque todos los montos son positivos. El IF manda a `true` a Prueba B, Prueba C y Prueba D, y a `false` a Prueba A, Prueba E y Prueba F. Estos son los totales y el tramo esperado.

| Cliente | Monto | VIP | `total_a_pagar` | Tramo | Por qué |
| --- | --- | --- | --- | --- | --- |
| Prueba A | 100000 | No | 113050 | Alto | Supera 100000. |
| Prueba B | 40000 | Sí | 38080 | Bajo | Es menor que 50000. |
| Prueba C | 105042 | Sí | 100000 | Medio | El total es exactamente 100000, y la regla `Medio` es «menor o igual». |
| Prueba D | 52521 | Sí | 50000 | Medio | El total es exactamente 50000, y la regla `Bajo` pide «menor que». |
| Prueba E | 44230 | No | 50002 | Medio | Apenas supera el límite inferior. |
| Prueba F | 1000 | No | 1131 | Bajo | El cálculo da 1130,5 y `Math.round` lo redondea hacia arriba. |

En el Switch, las pestañas deben mostrar **Bajo (2 items)** con B y F, **Medio (3 items)** con C, D y E, y **Alto (1 item)** con A. Cuando termines, vuelve a los datos del caso.

## Autoevaluación

```quiz
? En un nodo Edit Fields, la expresión $json.monto aparece dentro de dobles llaves. ¿Qué lee?
- El monto del primer ítem de todo el flujo.
+ El campo monto del ítem que el nodo está procesando.
- La suma de los montos de todos los ítems.
> $json es el ítem actual. Con seis ítems, la expresión se evalúa seis veces.
? ¿Qué diferencia hay entre Filter e IF?
- El Filter evalúa expresiones y el IF solo valores fijos.
+ El Filter deja fuera los ítems que no cumplen y el IF los manda por su salida false.
- El IF descarta ítems y el Filter los reparte entre dos ramas.
> Con el IF no se pierde ningún ítem: se reparten entre true y false.
? Un pedido tiene un total_a_pagar de exactamente 100000. Con las reglas Bajo (menor que 50000), Medio (menor o igual a 100000) y Alto (mayor que 100000), ¿por qué salida sale?
- Alto, porque 100000 es el límite del tramo.
- Bajo, porque es la primera regla de la lista.
+ Medio, porque 100000 cumple «menor o igual a 100000».
> Las reglas se evalúan en orden y el ítem sale por la primera que cumple.
? ¿Qué entrega el Merge en modo Append con dos ramas de dos ítems cada una?
- Dos ítems, uno por rama.
+ Cuatro ítems: primero los de la entrada 1 y luego los de la entrada 2.
- Cuatro ítems mezclados según el campo cliente.
> Append pone los ítems de una entrada a continuación de los de la otra.
? El nodo anterior entrega un solo ítem con una lista llamada pedidos de seis elementos. ¿Qué hace Split Out con pedidos en Fields To Split Out?
- Entrega un ítem con seis campos.
- Suma los montos de los seis pedidos.
+ Entrega seis ítems, uno por pedido.
> Split Out crea un ítem por cada elemento de la lista.
```

## Documentación de referencia

- [Nodo Edit Fields (Set)](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.set/)
- [Nodo Filter](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.filter/)
- [Nodo If](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.if/)
- [Nodo Switch](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.switch/)
- [Nodo Merge](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.merge/)
- [Nodo Split Out](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.splitout/)
- [Nodo Aggregate](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.aggregate/)
- [Nodo Code](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.code/)
- [Expresiones en n8n](https://docs.n8n.io/code/expressions/)
- [Variables integradas](https://docs.n8n.io/code/builtin/overview/)

## Workflow para importar

Si quieres comprobar tu flujo, o probar el caso completo sin armarlo nodo por nodo, descarga el workflow de este apunte e impórtalo en n8n. Trae los trece nodos del flujo, con los seis pedidos ya cargados en **Pedidos de ejemplo**, y ocho notas adhesivas que explican cada paso en el lienzo. No usa credenciales ni llamadas externas, así que funciona sin configurar nada.

<a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-transformar-datos/transformar-encaminar-pedidos.json" download="transformar-encaminar-pedidos.json" rel="noopener" style="color:var(--color-text);text-decoration:none;margin:12px 0 4px">Descargar transformar-encaminar-pedidos.json <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11M7 11l5 5 5-5M5 20h14"></path></svg></a>

Para importarlo:

1. Crea un workflow nuevo.
2. Abre el menú de tres puntos junto al nombre, elige **Import** y luego **From file**, y selecciona el archivo descargado. También puedes abrirlo en un editor de texto, copiar todo su contenido y pegarlo con Ctrl+V sobre el lienzo vacío.
3. Pulsa **Execute workflow** y abre cada nodo para comparar su OUTPUT con la tabla de la sección 11.

Si todo salió bien, el Switch reparte los pedidos así: **Bajo** con Ana (23800) y Elena (16958), **Medio** con Bruno (90440) y **Alto** con Diego (114240). Descarga el archivo tal cual: si lo abres y lo guardas desde un procesador de texto, puede dejar de importar.
