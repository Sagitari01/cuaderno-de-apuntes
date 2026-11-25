# Mapeo de datos en Make: píldoras, colecciones e Iterator

Imagina que te llega una orden de compra con tres productos. Tienes que guardar la orden en una hoja y, además, cada producto en su propia fila. ¿Cómo logras que Make copie cada dato en la columna correcta, sin que tú copies y pegues nada?

La respuesta es el **mapeo de datos**: decirle a Make qué dato va en qué lugar. En este apunte lo aprendes desde cero, con un ejemplo que puedes repetir en tu propia cuenta.

**Qué vas a aprender:**

- Qué es un bundle y qué es una píldora.
- Cómo mezclar datos que cambian con textos que siempre son iguales.
- Qué es una colección y qué es un arreglo, y en qué se diferencian.
- Para qué sirve el Iterator y cómo se usa.
- Por qué una ejecución en verde no siempre significa que todo salió bien.

**Qué necesitas:** una cuenta de Make y una cuenta de Google con Google Sheets. No necesitas saber programar. Todos los datos de este apunte son inventados.

> **Sobre las capturas:** son capturas reales de una cuenta de práctica. Make está en inglés y Google Sheets en español. Tu pantalla puede verse un poco distinta si Make cambia su diseño, pero los nombres de los botones y de los módulos son los mismos. Los recuadros violetas marcan lo que debes mirar.

---

## 1. Cómo viaja un dato dentro de Make

Antes de tocar nada, conviene tener claras cuatro palabras. Las vas a ver todo el tiempo.

- **Módulo:** una pieza del escenario que hace una tarea. Por ejemplo, guardar una fila en una hoja.
- **Bundle:** el paquete de datos que un módulo entrega al siguiente. Piensa en una caja con etiquetas.
- **Píldora:** la etiqueta de un dato que está dentro de la caja. Es una pastilla de color que puedes hacer clic para usar ese dato en otro módulo.
- **Mapear:** poner una píldora (o un texto) en el campo donde quieres usarlo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Tres módulos conectados; cada uno entrega una caja con etiquetas al siguiente" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m05-d1-viaje-del-dato" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Cómo viaja un dato entre módulos</text><circle cx="150" cy="170" r="56" fill="#cdbff5" stroke="#2d3250" stroke-width="2.8"/><text x="150" y="262" font-size="28" text-anchor="middle" fill="#2d3250" font-weight="400">Set variable</text><circle cx="450" cy="170" r="56" fill="#cdbff5" stroke="#2d3250" stroke-width="2.8"/><text x="450" y="262" font-size="28" text-anchor="middle" fill="#2d3250" font-weight="400">Parse JSON</text><circle cx="750" cy="170" r="56" fill="#a8e2c0" stroke="#2d3250" stroke-width="2.8"/><text x="750" y="262" font-size="28" text-anchor="middle" fill="#2d3250" font-weight="400">Add a Row</text><path d="M212 170 L388 170" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m05-d1-viaje-del-dato)"/><path d="M512 170 L688 170" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m05-d1-viaje-del-dato)"/><rect x="232" y="96" width="136" height="44" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="300" y="126" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">una caja</text><rect x="530" y="96" width="138" height="44" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="599" y="126" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">otra caja</text><rect x="214" y="296" width="158" height="30" rx="15" fill="#b9a6f2" stroke="#7b5fd6" stroke-width="2"/><text x="293.0" y="318" font-size="21" text-anchor="middle" fill="#2d2160" font-weight="400">datos_orden</text><rect x="420" y="296" width="86" height="30" rx="15" fill="#b9a6f2" stroke="#7b5fd6" stroke-width="2"/><text x="463.0" y="318" font-size="21" text-anchor="middle" fill="#2d2160" font-weight="400">Orden</text><rect x="512" y="296" width="134" height="30" rx="15" fill="#b9a6f2" stroke="#7b5fd6" stroke-width="2"/><text x="579.0" y="318" font-size="21" text-anchor="middle" fill="#2d2160" font-weight="400">Proveedor</text><rect x="656" y="296" width="86" height="30" rx="15" fill="#b9a6f2" stroke="#7b5fd6" stroke-width="2"/><text x="699.0" y="318" font-size="21" text-anchor="middle" fill="#2d2160" font-weight="400">Monto</text><text x="270" y="352" font-size="20" text-anchor="middle" fill="#2d3250" font-weight="400">Set variable entrega 1 etiqueta</text><text x="640" y="352" font-size="20" text-anchor="middle" fill="#2d3250" font-weight="400">Parse JSON entrega 3 etiquetas</text><text x="450" y="396" font-size="24" text-anchor="middle" fill="#5a4aa6" font-weight="400">Las etiquetas de colores son las píldoras.</text></svg><a href="contenido/make/imagenes/diagramas/m05-d1-viaje-del-dato.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Dibujo de tres módulos conectados. Cada uno entrega una caja con etiquetas al siguiente." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada módulo recibe la caja del anterior, la abre y entrega una caja nueva. Las etiquetas son las píldoras.</figcaption></figure>

Una idea importante: **un módulo solo puede usar los datos que los módulos anteriores ya produjeron.** Si un dato no está en el panel de píldoras, es porque ningún módulo anterior lo entrega.

---

## 2. El caso de práctica

**NovaDistribución** es una empresa inventada. Necesita registrar sus órdenes de compra en una hoja de cálculo. Cada orden trae tres datos: el número de orden, el nombre del proveedor y el monto.

En la vida real, esa orden llegaría desde un correo, un formulario o un sistema de la empresa. Para practicar, vamos a **simular** que la orden llega, escribiéndola nosotros mismos dentro de Make. Así podemos repetir la prueba las veces que queramos.

La orden se escribe en un formato llamado **JSON**. No te asustes: es solo una forma ordenada de escribir datos. Cada dato tiene un nombre y un valor, separados por dos puntos.

```json
{
  "orden": "OC-001",
  "proveedor": "Tecnologia Sur",
  "monto": 180000
}
```

Léelo en voz alta: la orden es OC-001, el proveedor es Tecnologia Sur y el monto es 180000. Eso es todo. El texto va entre comillas y el número va sin comillas. Esa diferencia importa, como verás más adelante.

### Prepara la hoja de destino

Crea una hoja de cálculo de Google llamada **Practica Make - NovaDistribucion**. Dentro crea tres pestañas con estos nombres exactos: `Ordenes`, `DetalleProductos` y `PruebaFalloSilencioso`.

En la fila 1 de cada pestaña escribe los encabezados. Estos son los nombres de las columnas. Make los va a leer para mostrarte un campo por cada columna.

| Pestaña | Encabezados (fila 1) |
| --- | --- |
| Ordenes | Orden, Proveedor, Monto, Estado, Fecha de registro |
| DetalleProductos | Orden, ID proveedor, Nombre proveedor, Producto, Cantidad, Precio unitario, Subtotal |
| PruebaFalloSilencioso | Orden, Proveedor, Monto, Estado, Fecha de registro |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-01-hoja-ordenes-encabezados.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Hoja de cálculo con la pestaña Ordenes y sus cinco encabezados en la fila 1, resaltados."><a href="contenido/make/imagenes/m05/make-m05-01-hoja-ordenes-encabezados.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Hoja de cálculo con la pestaña Ordenes y sus cinco encabezados en la fila 1, resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La pestaña Ordenes. Cada encabezado ocupa su propia celda. Escribe uno por celda, no todos juntos en la primera.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-02-hoja-detalle-encabezados.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña DetalleProductos con sus siete encabezados resaltados."><a href="contenido/make/imagenes/m05/make-m05-02-hoja-detalle-encabezados.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña DetalleProductos con sus siete encabezados resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La pestaña DetalleProductos, con siete columnas.</figcaption></figure>

**Comprueba:** haz clic en la celda B1 de cada pestaña. Si B1 está vacía y el texto se ve "desbordado" desde A1, escribiste todo en una sola celda. Corrígelo antes de seguir.

---

## 3. Demostración 1: mapeo simple

**El problema:** tenemos la orden escrita como un texto largo. Queremos que cada dato (orden, proveedor, monto) llegue a su propia columna, y que además se agregue un estado fijo y la fecha del registro.

**El plan:** usaremos tres módulos.

1. **Tools > Set variable:** guarda la orden de prueba.
2. **JSON > Parse JSON:** abre ese texto y separa sus datos.
3. **Google Sheets > Add a Row:** agrega una fila en la hoja con esos datos.

Crea un escenario nuevo con el botón **Create scenario** y ponle un nombre, por ejemplo `Practica Make - Mapeo simple`. Si es tu primera vez en el editor, mira antes el módulo 01 de este apartado.

### Paso 1. Guarda la orden con Set variable

Haz clic en el **+** central, elige la aplicación **Tools** y luego el módulo **Set variable**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-04-tools-elegir-set-variable.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de acciones de la aplicación Tools con Set variable resaltado."><a href="contenido/make/imagenes/m05/make-m05-04-tools-elegir-set-variable.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de acciones de la aplicación Tools con Set variable resaltado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tools es una aplicación interna de Make. No se conecta a ningún servicio externo: sirve para manejar datos dentro del escenario.</figcaption></figure>

**Set variable** guarda un valor con un nombre. Aquí lo usamos como una "orden de prueba". Completa dos campos:

- **Variable name:** `datos_orden`
- **Variable value:** pega el JSON de la orden, en una sola línea.

```json
{"orden": "OC-001", "proveedor": "Tecnologia Sur", "monto": 180000}
```

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-06-set-variable-nombre-y-valor.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana de Set variable con el nombre datos_orden y el JSON de la orden en el valor."><a href="contenido/make/imagenes/m05/make-m05-06-set-variable-nombre-y-valor.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana de Set variable con el nombre datos_orden y el JSON de la orden en el valor." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Set variable con su nombre y su valor. Al hacer clic en el valor se abre un panel lateral: por ahora puedes ignorarlo.</figcaption></figure>

Pulsa **Save**. Este módulo no habla con nadie: solo deja la orden lista para el siguiente módulo.

### Paso 2. Abre el texto con Parse JSON

**El problema:** para Make, la orden que acabamos de guardar es **un solo texto largo**. No sabe que adentro hay tres datos distintos. Si no los separamos, no podremos mandar cada uno a su columna.

**La solución:** el módulo **Parse JSON** "abre" el texto y entrega cada dato por separado, como píldoras.

Haz clic en el **+** que está a la derecha del primer módulo, busca **JSON** y elige **Parse JSON**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-07-parse-json-estructura-y-texto.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana de Parse JSON con los campos Data structure y JSON string resaltados."><a href="contenido/make/imagenes/m05/make-m05-07-parse-json-estructura-y-texto.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana de Parse JSON con los campos Data structure y JSON string resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Parse JSON tiene dos campos: la estructura de datos (cómo es la orden) y el texto que debe abrir.</figcaption></figure>

#### Crea la estructura de datos

La **estructura de datos** (Data structure) es una descripción de cómo es la orden: qué datos tiene y de qué tipo es cada uno. Te ahorra escribirla a mano: Make la genera a partir de un ejemplo.

1. Pulsa **Add** (a la derecha de Data structure).
2. Ponle un nombre, por ejemplo `Orden de compra simple`.
3. Pulsa **Generate**.
4. En **Sample data** pega el mismo JSON de la orden y pulsa **Generate**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-09-generar-estructura-desde-muestra.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana Generate con el JSON de ejemplo pegado en el campo Sample data."><a href="contenido/make/imagenes/m05/make-m05-09-generar-estructura-desde-muestra.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana Generate con el JSON de ejemplo pegado en el campo Sample data." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>En Sample data pegas un ejemplo y Make deduce la estructura.</figcaption></figure>

Make creó tres campos. Fíjate en el **tipo** de cada uno.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-10-estructura-generada-tipos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Estructura de datos generada con los campos Orden y Proveedor de tipo text y Monto de tipo number."><a href="contenido/make/imagenes/m05/make-m05-10-estructura-generada-tipos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Estructura de datos generada con los campos Orden y Proveedor de tipo text y Monto de tipo number." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Orden y Proveedor son texto (text). Monto es un número (number). Make lo dedujo porque 180000 está sin comillas.</figcaption></figure>

Esto es importante: si el monto es un **número**, Google Sheets lo puede sumar, ordenar y usar en cálculos. Si fuera un texto, se vería igual pero se comportaría distinto.

Una cosa curiosa: Make muestra los nombres con la primera letra en mayúscula (Orden, Proveedor). Pero el nombre real del campo sigue siendo el que escribiste en minúscula. Puedes comprobarlo abriendo un campo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-11-estructura-nombre-real-del-campo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Detalle de un campo de la estructura con el nombre real orden en minúscula."><a href="contenido/make/imagenes/m05/make-m05-11-estructura-nombre-real-del-campo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Detalle de un campo de la estructura con el nombre real orden en minúscula." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El nombre real del campo es orden. La mayúscula es solo la etiqueta que muestra Make.</figcaption></figure>

Pulsa **Save** para guardar la estructura. De vuelta en Parse JSON, ya aparece elegida.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-12-parse-json-estructura-elegida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Parse JSON con la estructura Orden de compra simple elegida en Data structure."><a href="contenido/make/imagenes/m05/make-m05-12-parse-json-estructura-elegida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Parse JSON con la estructura Orden de compra simple elegida en Data structure." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La estructura quedó elegida. Falta decirle qué texto debe abrir.</figcaption></figure>

#### Usa tu primera píldora

Haz clic dentro del campo **JSON string**. Se abre el **panel de píldoras**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-13-panel-de-pildoras.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de píldoras abierto junto al campo JSON string. Muestra el módulo Tools Set variable y la píldora datos_orden."><a href="contenido/make/imagenes/m05/make-m05-13-panel-de-pildoras.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de píldoras abierto junto al campo JSON string. Muestra el módulo Tools Set variable y la píldora datos_orden." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El panel de píldoras muestra todo lo que producen los módulos anteriores. Ahora solo hay uno: Tools, con la píldora datos_orden.</figcaption></figure>

Haz clic en la píldora **datos_orden**. Queda dentro del campo como una pastilla morada.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-14-pildora-datos-orden.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="El campo JSON string con la píldora datos_orden insertada."><a href="contenido/make/imagenes/m05/make-m05-14-pildora-datos-orden.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: El campo JSON string con la píldora datos_orden insertada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La píldora ya está en el campo. Si pasas el cursor por encima, un recuadro te dice su tipo: any, es decir, cualquier tipo.</figcaption></figure>

Pulsa **Save**. Acabas de hacer tu primer **mapeo**: le dijiste a Parse JSON que abra el texto que guardó el módulo anterior.

### Paso 3. Agrega la fila con Google Sheets

Haz clic en el **+** a la derecha de Parse JSON, busca **Google Sheets** y elige **Add a Row**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-15-sheets-elegir-add-a-row.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de módulos de Google Sheets con Add a Row resaltado."><a href="contenido/make/imagenes/m05/make-m05-15-sheets-elegir-add-a-row.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de módulos de Google Sheets con Add a Row resaltado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Add a Row agrega una fila nueva al final de la tabla.</figcaption></figure>

Ahora configura el módulo. Fíjate bien en el primer campo.

> **Cuidado con la conexión.** Si tu cuenta de Make tiene varias conexiones de Google, Make puede dejar seleccionada una que no es la que quieres. Revisa siempre el campo **Connection** y elige la cuenta de Google donde creaste la hoja. Si eliges otra, el módulo buscará la hoja en el lugar equivocado.

Después completa estos campos:

1. **Search Method:** Search by path.
2. **Drive:** My Drive.
3. **Spreadsheet Name:** haz clic en "Click here to choose file" y elige tu hoja `Practica Make - NovaDistribucion`.
4. **Sheet Name:** elige la pestaña `Ordenes`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-18-sheets-archivo-elegido.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Campo Spreadsheet Name con la hoja Practica Make - NovaDistribucion elegida."><a href="contenido/make/imagenes/m05/make-m05-18-sheets-archivo-elegido.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo Spreadsheet Name con la hoja Practica Make - NovaDistribucion elegida." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La hoja ya está elegida. El campo Sheet Name se llena a continuación.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-19-sheets-lista-de-pestanas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de pestañas de la hoja: Ordenes, DetalleProductos y PruebaFalloSilencioso."><a href="contenido/make/imagenes/m05/make-m05-19-sheets-lista-de-pestanas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de pestañas de la hoja: Ordenes, DetalleProductos y PruebaFalloSilencioso." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Make lee las pestañas de tu hoja. Elige Ordenes.</figcaption></figure>

En cuanto eliges la pestaña, Make lee los encabezados y crea **un campo por cada columna**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-20-sheets-columnas-detectadas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Sección Values in columns con un campo por columna: Orden, Proveedor, Monto y Estado."><a href="contenido/make/imagenes/m05/make-m05-20-sheets-columnas-detectadas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Sección Values in columns con un campo por columna: Orden, Proveedor, Monto y Estado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un campo por columna. Por eso los encabezados deben estar bien escritos.</figcaption></figure>

### Paso 4. Mapea cada columna

Hay tres formas de llenar un campo. Las vas a usar todas en este ejemplo.

| Forma | Qué es | Ejemplo aquí |
| --- | --- | --- |
| **Dato dinámico** | Una píldora. Cambia en cada ejecución. | Orden, Proveedor, Monto |
| **Dato estático** | Un texto escrito por ti. Es igual siempre. | Estado = Registrado |
| **Variable de Make** | Un valor que Make calcula solo. | Fecha de registro = now |

**Datos dinámicos.** Haz clic en el campo **Orden (A)**. En el panel de píldoras, bajo el módulo **JSON - Parse JSON**, haz clic en la píldora **Orden**. Haz lo mismo con **Proveedor (B)** y **Monto (C)**, cada uno con su píldora.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-21-sheets-panel-pildoras-orden.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de píldoras con la píldora Orden del módulo Parse JSON resaltada."><a href="contenido/make/imagenes/m05/make-m05-21-sheets-panel-pildoras-orden.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de píldoras con la píldora Orden del módulo Parse JSON resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Elige la píldora que tiene el mismo nombre que la columna. Aquí Orden va en Orden.</figcaption></figure>

**Dato estático.** En **Estado (D)** escribe directamente el texto `Registrado`. No uses ninguna píldora: queremos que siempre diga lo mismo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-22-sheets-estado-texto-fijo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Campo Estado con el texto fijo Registrado."><a href="contenido/make/imagenes/m05/make-m05-22-sheets-estado-texto-fijo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo Estado con el texto fijo Registrado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un texto que escribes tú. Aparece sin color de píldora.</figcaption></figure>

**Variable de Make.** En **Fecha de registro (E)** queremos la fecha y hora del momento exacto en que se agrega la fila. Eso no viene de la orden: lo calcula Make. Haz clic en el campo y abre la pestaña del **calendario** en el panel de píldoras.

Primero ve a la pestaña de variables generales, que tiene forma de engranaje. Ahí **no** está la fecha.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-23-panel-variables-generales.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña de funciones generales del panel, con la variable executionId resaltada."><a href="contenido/make/imagenes/m05/make-m05-23-panel-variables-generales.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña de funciones generales del panel, con la variable executionId resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>En la pestaña general solo hay executionId. La fecha no está aquí.</figcaption></figure>

Cambia a la pestaña del calendario (Date and time). Ahí están **timestamp** y **now**. Haz clic en **now**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-24-panel-fecha-y-hora-now.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Date and time del panel con la variable now resaltada."><a href="contenido/make/imagenes/m05/make-m05-24-panel-fecha-y-hora-now.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Date and time del panel con la variable now resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>now es la fecha y hora de este instante. Cada ejecución guarda una distinta.</figcaption></figure>

> **Cierra los paneles con su botón de cierre (la X), no con la tecla Escape.** Si pulsas Escape con la ventana del módulo abierta, Make la cierra sin guardar y pierdes lo que configuraste.

Así debe verse el mapeo completo:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-25-sheets-mapeo-completo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Mapeo completo del módulo Add a Row: tres píldoras moradas, un texto fijo y la variable now."><a href="contenido/make/imagenes/m05/make-m05-25-sheets-mapeo-completo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Mapeo completo del módulo Add a Row: tres píldoras moradas, un texto fijo y la variable now." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tres píldoras de Parse JSON, un texto fijo y la variable now.</figcaption></figure>

Pulsa **Save** en la ventana del módulo y luego el botón **Save** del escenario, abajo.

### Paso 5. Ejecuta y revisa

Pulsa **Run once**. Este botón ejecuta el escenario una sola vez, ahora, sin programarlo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-27-primera-ejecucion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="El escenario con tres módulos terminados. Cada uno muestra una marca verde y la burbuja de una operación."><a href="contenido/make/imagenes/m05/make-m05-27-primera-ejecucion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: El escenario con tres módulos terminados. Cada uno muestra una marca verde y la burbuja de una operación." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los tres módulos terminaron bien: marca verde y una operación cada uno.</figcaption></figure>

Haz clic en la burbuja que está sobre **Parse JSON**. Verás qué entró y qué salió.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-28-bundle-parse-json.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de entradas y salidas de Parse JSON. A la izquierda el texto de entrada, a la derecha tres datos de salida con sus tipos."><a href="contenido/make/imagenes/m05/make-m05-28-bundle-parse-json.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de entradas y salidas de Parse JSON. A la izquierda el texto de entrada, a la derecha tres datos de salida con sus tipos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>A la izquierda, el texto largo que entró. A la derecha, tres datos separados: dos de texto y uno numérico. También indica 1 operación y 1 crédito.</figcaption></figure>

Esa lista de la derecha es el **bundle de salida**. Cada dato de ese bundle es una de las píldoras que usaste en el módulo siguiente.

Ahora la burbuja de **Google Sheets**:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-29-bundle-google-sheets.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de entradas y salidas de Add a Row. A la derecha, el rango actualizado y el número de fila."><a href="contenido/make/imagenes/m05/make-m05-29-bundle-google-sheets.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de entradas y salidas de Add a Row. A la derecha, el rango actualizado y el número de fila." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Add a Row informa en qué pestaña escribió y en qué fila (Row Number: 2).</figcaption></figure>

Por último, lo más importante: **mira la hoja**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-30-hoja-primera-fila.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Ordenes con una fila nueva: OC-001, Tecnologia Sur, 180000, Registrado y la fecha."><a href="contenido/make/imagenes/m05/make-m05-30-hoja-primera-fila.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Ordenes con una fila nueva: OC-001, Tecnologia Sur, 180000, Registrado y la fecha." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La fila quedó en su lugar. El monto aparece alineado a la derecha: es un número. La fecha termina en Z, que significa hora universal (UTC).</figcaption></figure>

### Paso 6. ¿Qué cambia y qué no?

Para entenderlo de verdad, vuelve a ejecutar con otra orden. Abre el módulo **Set variable**, cambia el valor por esta orden y pulsa **Save**. Después pulsa **Run once**.

```json
{"orden": "OC-002", "proveedor": "Distribuidora Norte", "monto": 95000}
```

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-31-set-variable-segunda-orden.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Set variable con el valor cambiado a la orden OC-002."><a href="contenido/make/imagenes/m05/make-m05-31-set-variable-segunda-orden.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Set variable con el valor cambiado a la orden OC-002." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cambiamos solo el dato de entrada.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-33-hoja-dos-ordenes.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Ordenes con dos filas: OC-001 y OC-002."><a href="contenido/make/imagenes/m05/make-m05-33-hoja-dos-ordenes.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Ordenes con dos filas: OC-001 y OC-002." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Se agregó una fila nueva. Las dos órdenes conviven en la hoja.</figcaption></figure>

| Columna | ¿Cambió? | Por qué |
| --- | --- | --- |
| Orden | Sí | Viene de una píldora |
| Proveedor | Sí | Viene de una píldora |
| Monto | Sí | Viene de una píldora |
| Estado | No | Es un texto fijo |
| Fecha de registro | Sí | now cambia en cada ejecución |

### Paso 7. Un mensaje con texto fijo y datos

Muchas automatizaciones terminan avisando algo: "La orden tal fue registrada". Ese aviso mezcla texto fijo con datos que cambian. Se arma igual que el mapeo: escribes el texto y haces clic en las píldoras.

Agrega un cuarto módulo **Tools > Set variable** después de Google Sheets. Ponle de nombre `mensaje_orden`. En el valor escribe `La orden `, haz clic en la píldora **Orden**, escribe ` de `, haz clic en **Proveedor**, escribe ` por $ `, haz clic en **Monto** y escribe ` fue registrada en la hoja Ordenes.`

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-34-mensaje-texto-y-pildoras.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Campo de valor con texto fijo y tres píldoras mezcladas formando una frase."><a href="contenido/make/imagenes/m05/make-m05-34-mensaje-texto-y-pildoras.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo de valor con texto fijo y tres píldoras mezcladas formando una frase." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Texto escrito por ti y píldoras. Al pasar el cursor por Monto, Make indica que es un número.</figcaption></figure>

Para probar solo este módulo, sin agregar otra fila a la hoja, haz clic derecho sobre él y elige **Run this module only**. Make te pide valores de prueba para las píldoras, porque no ejecuta los módulos anteriores.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-35-ejecutar-solo-este-modulo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana Run this module only con tres campos de prueba: Orden, Proveedor y Monto."><a href="contenido/make/imagenes/m05/make-m05-35-ejecutar-solo-este-modulo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana Run this module only con tres campos de prueba: Orden, Proveedor y Monto." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Escribe tú los valores de prueba: OC-002, Distribuidora Norte y 95000.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-36-bundle-mensaje.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Salida del módulo con el mensaje armado: La orden OC-002 de Distribuidora Norte por $ 95000 fue registrada en la hoja Ordenes."><a href="contenido/make/imagenes/m05/make-m05-36-bundle-mensaje.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida del módulo con el mensaje armado: La orden OC-002 de Distribuidora Norte por $ 95000 fue registrada en la hoja Ordenes." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El mensaje quedó armado.</figcaption></figure>

**¿Y si quiero mandarlo por correo?** El mensaje es una píldora más: `mensaje_orden`. Si agregaras un módulo **Gmail > Send an email**, la pondrías en el campo del cuerpo del mensaje, igual que cualquier otra. En la captura de abajo solo mostramos la configuración: **no se envió ningún correo** y el módulo se eliminó después.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-37-mensaje-en-un-correo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="763" height="265" alt="Campo Content de un módulo Gmail con el texto Hola, la píldora mensaje_orden y una frase final."><a href="contenido/make/imagenes/m05/make-m05-37-mensaje-en-un-correo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo Content de un módulo Gmail con el texto Hola, la píldora mensaje_orden y una frase final." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La píldora mensaje_orden dentro del cuerpo de un correo. Es solo una ilustración: en la práctica no envíes correos de prueba a personas reales.</figcaption></figure>

### Errores frecuentes en la demostración 1

| Qué ves | Qué pasó | Cómo lo revisas |
| --- | --- | --- |
| La hoja no se encuentra o escribe en otro lado | Elegiste una conexión de Google equivocada | Revisa el campo Connection |
| El módulo pierde lo que configuraste | Cerraste la ventana con Escape | Cierra con la X y guarda con Save |
| Make no muestra campos por columna | Los encabezados no están en la fila 1 o están en una sola celda | Revisa la fila 1 de la pestaña |
| Aparece un texto raro en vez de un dato | Pegaste el JSON con un error de comillas o llaves | Compáralo con el ejemplo |
| Cada ejecución agrega una fila más | Es lo esperado: Add a Row siempre agrega, no revisa duplicados | Cambia el dato de prueba o borra la fila de prueba |

### Para pensar

1. ¿Por qué necesitamos Parse JSON si Set variable ya tiene los datos?
2. ¿Qué pasaría con la columna Estado si cambiaras el texto `Registrado` por una píldora?
3. ¿Por qué la fecha termina en Z? ¿Qué significa?

---

## 4. Demostración 2: colecciones, arreglos e Iterator

**El problema:** hasta ahora cada orden tenía un solo proveedor y un solo monto. Pero una orden real trae varios productos. Imagina que llega esta:

- Teclado, 2 unidades, a 15000 cada una.
- Mouse, 3 unidades, a 10000 cada una.
- Monitor, 1 unidad, a 120000.

Queremos guardar **cada producto en su propia fila** de la pestaña `DetalleProductos`, junto con el número de orden y los datos del proveedor.

### Tres tipos de datos que debes distinguir

| Tipo | Qué es | Ejemplo |
| --- | --- | --- |
| **Dato simple** | Un solo valor | orden: OC-001 |
| **Colección** | Una caja con varios datos de **una sola cosa** | el proveedor, con su ID y su nombre |
| **Arreglo** | Una **lista** de cosas parecidas | los productos: una lista de tres elementos |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Una caja con id y nombre (colección) junto a una lista de tres cajas de productos (arreglo)" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m05-d2-coleccion-vs-arreglo" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Colección y arreglo</text><text x="230" y="96" font-size="30" text-anchor="middle" fill="#7b5fd6" font-weight="700">Colección</text><rect x="100" y="112" width="260" height="190" rx="12" fill="#f4efff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="230" y="146" font-size="26" text-anchor="middle" fill="#2d3250" font-weight="700">proveedor</text><rect x="124" y="164" width="212" height="52" rx="12" fill="#ffffff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="230" y="198" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">PROV-001</text><rect x="124" y="232" width="212" height="52" rx="12" fill="#ffffff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="230" y="266" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Tecnologia Sur</text><text x="230" y="336" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Una caja con varios datos</text><text x="230" y="364" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">de una sola cosa</text><text x="650" y="96" font-size="30" text-anchor="middle" fill="#1f8f5f" font-weight="700">Arreglo</text><path d="M436 118 L420 118 L420 292 L436 292" fill="none" stroke="#1f8f5f" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><path d="M874 118 L890 118 L890 292 L874 292" fill="none" stroke="#1f8f5f" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><rect x="438" y="130" width="136" height="150" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="506" y="168" font-size="26" text-anchor="middle" fill="#2d3250" font-weight="700">Teclado</text><text x="506" y="208" font-size="19" text-anchor="middle" fill="#2d3250" font-weight="400">cantidad 2</text><text x="506" y="240" font-size="19" text-anchor="middle" fill="#2d3250" font-weight="400">15000 c/u</text><rect x="586" y="130" width="136" height="150" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="654" y="168" font-size="26" text-anchor="middle" fill="#2d3250" font-weight="700">Mouse</text><text x="654" y="208" font-size="19" text-anchor="middle" fill="#2d3250" font-weight="400">cantidad 3</text><text x="654" y="240" font-size="19" text-anchor="middle" fill="#2d3250" font-weight="400">10000 c/u</text><rect x="734" y="130" width="136" height="150" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="802" y="168" font-size="26" text-anchor="middle" fill="#2d3250" font-weight="700">Monitor</text><text x="802" y="208" font-size="19" text-anchor="middle" fill="#2d3250" font-weight="400">cantidad 1</text><text x="802" y="240" font-size="19" text-anchor="middle" fill="#2d3250" font-weight="400">120000 c/u</text><text x="660" y="336" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">productos: una lista de</text><text x="660" y="364" font-size="24" text-anchor="middle" fill="#1f8f5f" font-weight="400">cosas parecidas, entre [ ]</text></svg><a href="contenido/make/imagenes/diagramas/m05-d2-coleccion-vs-arreglo.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Dibujo con una caja llamada proveedor que contiene id y nombre, y una lista de tres cajas llamada productos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una colección es una caja con varias etiquetas. Un arreglo es una fila de cajas parecidas. En Make los arreglos se reconocen por los corchetes [].</figcaption></figure>

Así se ve la orden completa. Mira cómo el proveedor es una colección (tiene llaves adentro) y los productos son un arreglo (lista entre corchetes).

```json
{
  "orden": "OC-001",
  "proveedor": {
    "id": "PROV-001",
    "nombre": "Tecnologia Sur"
  },
  "productos": [
    { "nombre": "Teclado", "cantidad": 2, "precio_unitario": 15000 },
    { "nombre": "Mouse", "cantidad": 3, "precio_unitario": 10000 },
    { "nombre": "Monitor", "cantidad": 1, "precio_unitario": 120000 }
  ]
}
```

### El escenario

Crea un escenario nuevo llamado `Practica Make - Colecciones e Iterator` con cuatro módulos:

1. **Tools > Set variable** (`datos_orden`, con el JSON de arriba en una sola línea).
2. **JSON > Parse JSON**.
3. **Flow Control > Iterator**.
4. **Google Sheets > Add a Row** (pestaña `DetalleProductos`).

Los pasos 1 y 2 son iguales a la demostración anterior. Esta vez, al generar la estructura con **Generate**, usa el JSON completo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-38-colecciones-set-variable.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Set variable con el JSON completo de la orden, con proveedor y productos."><a href="contenido/make/imagenes/m05/make-m05-38-colecciones-set-variable.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Set variable con el JSON completo de la orden, con proveedor y productos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El mismo módulo de siempre, con una orden más completa.</figcaption></figure>

Make reconoce los tipos solo. Fíjate en la columna de tipos.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-39-colecciones-tipos-de-datos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Estructura generada: Orden de tipo text, Proveedor de tipo collection y Productos de tipo array."><a href="contenido/make/imagenes/m05/make-m05-39-colecciones-tipos-de-datos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Estructura generada: Orden de tipo text, Proveedor de tipo collection y Productos de tipo array." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Proveedor es una colección (collection). Productos es un arreglo (array).</figcaption></figure>

Si abres Productos, verás que cada elemento del arreglo es una colección con tres datos.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-40-arreglo-de-colecciones.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Detalle de Productos: cada elemento es una colección con nombre de tipo text, cantidad y precio_unitario de tipo number."><a href="contenido/make/imagenes/m05/make-m05-40-arreglo-de-colecciones.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Detalle de Productos: cada elemento es una colección con nombre de tipo text, cantidad y precio_unitario de tipo number." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada elemento del arreglo tiene nombre (texto), cantidad (número) y precio unitario (número).</figcaption></figure>

### ¿Por qué necesitamos Iterator?

**El problema:** el arreglo `productos` es **un solo dato** con tres productos adentro. Si lo conectamos directo a Google Sheets, Make intenta guardar la lista completa en una sola fila. Nosotros queremos tres filas.

**La solución:** el **Iterator** toma un arreglo y lo **separa**: entrega un bundle por cada elemento. Si el arreglo tiene tres productos, el módulo que viene después se ejecuta tres veces, una por producto.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Un arreglo de tres productos entra al Iterator y salen tres bundles, uno por producto" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m05-d3-iterator" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Qué hace el Iterator</text><text x="180" y="92" font-size="26" text-anchor="middle" fill="#1f8f5f" font-weight="700">Entra un arreglo</text><path d="M122 104 L106 104 L106 296 L122 296" fill="none" stroke="#1f8f5f" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><rect x="124" y="110" width="118" height="50" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="183" y="144" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Teclado</text><rect x="124" y="172" width="118" height="50" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="183" y="206" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Mouse</text><rect x="124" y="234" width="118" height="50" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="183" y="268" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Monitor</text><path d="M246 104 L262 104 L262 296 L246 296" fill="none" stroke="#1f8f5f" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><path d="M300 204 L396 204" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m05-d3-iterator)"/><path d="M400 140 L560 140 L520 270 L440 270 Z" fill="#cdeed9" stroke="#2d3250" stroke-width="2.8" stroke-linejoin="round"/><text x="480" y="214" font-size="30" text-anchor="middle" fill="#2d3250" font-weight="700">Iterator</text><text x="480" y="300" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">separa la lista</text><text x="740" y="92" font-size="26" text-anchor="middle" fill="#7b5fd6" font-weight="700">Salen 3 bundles</text><path d="M560 204 L640 140" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m05-d3-iterator)"/><rect x="646" y="112" width="130" height="58" rx="12" fill="#f4efff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="711" y="137" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="700">Teclado</text><text x="711" y="161" font-size="20" text-anchor="middle" fill="#2d3250" font-weight="400">cant: 2</text><path d="M780 140 L820 140" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m05-d3-iterator)"/><rect x="824" y="120" width="56" height="40" rx="8" fill="#a8e2c0" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="852" y="148" font-size="18" text-anchor="middle" fill="#2d3250" font-weight="400">fila 1</text><path d="M560 204 L640 210" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m05-d3-iterator)"/><rect x="646" y="182" width="130" height="58" rx="12" fill="#f4efff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="711" y="207" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="700">Mouse</text><text x="711" y="231" font-size="20" text-anchor="middle" fill="#2d3250" font-weight="400">cant: 3</text><path d="M780 210 L820 210" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m05-d3-iterator)"/><rect x="824" y="190" width="56" height="40" rx="8" fill="#a8e2c0" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="852" y="218" font-size="18" text-anchor="middle" fill="#2d3250" font-weight="400">fila 2</text><path d="M560 204 L640 280" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m05-d3-iterator)"/><rect x="646" y="252" width="130" height="58" rx="12" fill="#f4efff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="711" y="277" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="700">Monitor</text><text x="711" y="301" font-size="20" text-anchor="middle" fill="#2d3250" font-weight="400">cant: 1</text><path d="M780 280 L820 280" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m05-d3-iterator)"/><rect x="824" y="260" width="56" height="40" rx="8" fill="#a8e2c0" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="852" y="288" font-size="18" text-anchor="middle" fill="#2d3250" font-weight="400">fila 3</text><text x="450" y="352" font-size="24" text-anchor="middle" fill="#5a4aa6" font-weight="400">Los módulos de antes corren 1 vez.</text><text x="450" y="384" font-size="24" text-anchor="middle" fill="#5a4aa6" font-weight="400">El que viene después corre 3 veces: una por bundle.</text></svg><a href="contenido/make/imagenes/diagramas/m05-d3-iterator.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Dibujo de un arreglo de tres productos entrando al Iterator y saliendo tres bundles separados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Iterator recibe una lista y entrega un bundle por elemento. El módulo siguiente corre una vez por bundle.</figcaption></figure>

Haz clic en el **+** a la derecha de Parse JSON, busca **Iterator**. Está dentro de la aplicación **Flow Control**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-42-iterator-esta-en-flow-control.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Búsqueda de Iterator en Make. Aparece dentro de Flow Control con la descripción: divide un arreglo en bundles individuales."><a href="contenido/make/imagenes/m05/make-m05-42-iterator-esta-en-flow-control.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Búsqueda de Iterator en Make. Aparece dentro de Flow Control con la descripción: divide un arreglo en bundles individuales." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Iterator vive dentro de Flow Control.</figcaption></figure>

El Iterator tiene un solo campo: **Array**. Ahí va el arreglo que quieres separar.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-43-iterator-campo-array.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Configuración del Iterator con el campo Array resaltado."><a href="contenido/make/imagenes/m05/make-m05-43-iterator-campo-array.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Configuración del Iterator con el campo Array resaltado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un solo campo: el arreglo a separar.</figcaption></figure>

Haz clic en el campo. En el panel de píldoras, bajo **JSON - Parse JSON**, verás los dos tipos de dato complejos:

- **Proveedor** tiene una flecha que lo despliega y muestra lo de adentro (**ID** y **Nombre**). Es la colección.
- **Productos[]** lleva corchetes. Es el arreglo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-44-coleccion-proveedor-desplegada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de píldoras con la colección Proveedor desplegada mostrando ID y Nombre, y debajo Productos con corchetes."><a href="contenido/make/imagenes/m05/make-m05-44-coleccion-proveedor-desplegada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de píldoras con la colección Proveedor desplegada mostrando ID y Nombre, y debajo Productos con corchetes." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Despliega una colección con su flecha para llegar a cada dato de adentro.</figcaption></figure>

Despliega también **Productos[]**: adentro aparecen nombre, cantidad y precio_unitario.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-45-arreglo-productos-desplegado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de píldoras con Productos desplegado: nombre, cantidad y precio_unitario."><a href="contenido/make/imagenes/m05/make-m05-45-arreglo-productos-desplegado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de píldoras con Productos desplegado: nombre, cantidad y precio_unitario." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Dentro del arreglo están los datos de cada producto.</figcaption></figure>

Haz clic en la píldora **Productos[]** (la del nombre completo, no las de adentro). Pulsa **Save**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-46-iterator-con-productos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Iterator con la píldora Productos en el campo Array. El recuadro indica que su tipo es array."><a href="contenido/make/imagenes/m05/make-m05-46-iterator-con-productos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Iterator con la píldora Productos en el campo Array. El recuadro indica que su tipo es array." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Iterator ya sabe qué arreglo separar. El tipo es array.</figcaption></figure>

### Mapea la hoja DetalleProductos

Agrega el módulo **Google Sheets > Add a Row**. Recuerda revisar la **conexión**, y elige la pestaña `DetalleProductos`. Make crea un campo por cada columna.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-47-detalle-columnas-detectadas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Add a Row hacia DetalleProductos con campos para Orden, ID proveedor, Nombre proveedor y Producto."><a href="contenido/make/imagenes/m05/make-m05-47-detalle-columnas-detectadas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Add a Row hacia DetalleProductos con campos para Orden, ID proveedor, Nombre proveedor y Producto." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Siete columnas, siete campos.</figcaption></figure>

Ahora aparece algo nuevo: el panel muestra píldoras de **dos módulos** a la vez.

- Las **verdes** son del **Iterator**: nombre, cantidad, precio_unitario. Cambian en cada producto.
- Las **moradas** son de **Parse JSON**: Orden, Proveedor. Son las mismas para toda la orden.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-48-pildoras-del-iterator-y-del-json.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de píldoras con dos grupos: las del Iterator en verde y las de Parse JSON en morado."><a href="contenido/make/imagenes/m05/make-m05-48-pildoras-del-iterator-y-del-json.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de píldoras con dos grupos: las del Iterator en verde y las de Parse JSON en morado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Desde un módulo que viene después del Iterator puedes usar datos del Iterator y también de los módulos anteriores a él.</figcaption></figure>

Esto responde una duda frecuente: aunque pasaste por el Iterator, **los datos de los módulos anteriores siguen disponibles**. Por eso el número de orden y el proveedor pueden repetirse en las tres filas.

Mapea así:

| Columna | Qué pones | De dónde viene |
| --- | --- | --- |
| Orden | píldora **Orden** | Parse JSON |
| ID proveedor | píldora **ID** (dentro de Proveedor) | Parse JSON |
| Nombre proveedor | píldora **Nombre** (dentro de Proveedor) | Parse JSON |
| Producto | píldora **nombre** | Iterator |
| Cantidad | píldora **cantidad** | Iterator |
| Precio unitario | píldora **precio_unitario** | Iterator |
| Subtotal | cantidad × precio_unitario | Iterator, con un cálculo |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-49-detalle-mapeo-producto.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Campo Producto con la píldora nombre del Iterator, y la píldora nombre resaltada en el panel."><a href="contenido/make/imagenes/m05/make-m05-49-detalle-mapeo-producto.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo Producto con la píldora nombre del Iterator, y la píldora nombre resaltada en el panel." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El campo Producto lleva la píldora verde nombre, la del Iterator.</figcaption></figure>

### El subtotal: una multiplicación con píldoras

El subtotal de cada producto es la cantidad por el precio unitario. No necesitas escribir ninguna fórmula: se arma con clics.

1. Haz clic en el campo **Subtotal (G)**.
2. En el panel, haz clic en la píldora **cantidad**.
3. Abre la pestaña de **matemáticas** (el ícono de x con un número pequeño, Math functions).
4. En la fila **Operators**, haz clic en el signo **\***. Ese es el signo de multiplicar.
5. Vuelve a la primera pestaña (la estrella) y haz clic en la píldora **precio_unitario**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-62-panel-matematicas-operadores.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Math functions del panel, con la fila de operadores resaltada: multiplicar, dividir, mod, sumar y restar."><a href="contenido/make/imagenes/m05/make-m05-62-panel-matematicas-operadores.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Math functions del panel, con la fila de operadores resaltada: multiplicar, dividir, mod, sumar y restar." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los signos para calcular están en la pestaña de matemáticas, en la fila Operators.</figcaption></figure>

El campo debe quedar con tres piezas: la píldora cantidad, el signo por y la píldora precio_unitario.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-50-detalle-subtotal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Campo Subtotal con las piezas cantidad, signo de multiplicar y precio_unitario."><a href="contenido/make/imagenes/m05/make-m05-50-detalle-subtotal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo Subtotal con las piezas cantidad, signo de multiplicar y precio_unitario." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>cantidad por precio_unitario. Make hace la cuenta en cada vuelta.</figcaption></figure>

Pulsa **Save** en el módulo y en el escenario.

### Ejecuta y observa

Pulsa **Run once**. Mira los números sobre cada módulo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-52-colecciones-ejecucion-uno-uno-uno-tres.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="El escenario completo ejecutado. Tools, JSON e Iterator muestran 1 operación. Google Sheets muestra 3."><a href="contenido/make/imagenes/m05/make-m05-52-colecciones-ejecucion-uno-uno-uno-tres.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: El escenario completo ejecutado. Tools, JSON e Iterator muestran 1 operación. Google Sheets muestra 3." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tools, JSON e Iterator corrieron una vez. Google Sheets corrió <b>tres</b> veces: una por cada producto.</figcaption></figure>

Ese "1, 1, 1, 3" es la mejor explicación de lo que hace el Iterator. Haz clic en la burbuja del Iterator para ver los bundles.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-53-iterator-tres-bundles.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel del Iterator. A la izquierda entra un arreglo de 3 elementos. A la derecha salen tres bundles, con el primero abierto mostrando Teclado, cantidad 2 y precio 15000."><a href="contenido/make/imagenes/m05/make-m05-53-iterator-tres-bundles.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel del Iterator. A la izquierda entra un arreglo de 3 elementos. A la derecha salen tres bundles, con el primero abierto mostrando Teclado, cantidad 2 y precio 15000." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Entra un arreglo con 3 elementos. Salen 3 bundles. Cada uno trae su producto, su posición y el total de bundles.</figcaption></figure>

Y ahora la hoja:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-54-detalle-tres-filas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña DetalleProductos con tres filas: Teclado con subtotal 30000, Mouse con 30000 y Monitor con 120000."><a href="contenido/make/imagenes/m05/make-m05-54-detalle-tres-filas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña DetalleProductos con tres filas: Teclado con subtotal 30000, Mouse con 30000 y Monitor con 120000." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tres filas exactas. Los subtotales suman 180000, el monto total de la orden.</figcaption></figure>

**Verifica:** 2 × 15000 = 30000, 3 × 10000 = 30000 y 1 × 120000 = 120000. La suma es 180000, igual que el monto de la primera demostración. Esa es una buena costumbre: **comprueba que los números de la hoja cuadran con los de la orden**.

### Errores frecuentes en la demostración 2

| Qué ves | Qué pasó | Cómo lo revisas |
| --- | --- | --- |
| Una sola fila con todo revuelto | Pusiste el arreglo directo en Add a Row, sin Iterator | Revisa que el Iterator esté entre Parse JSON y Add a Row |
| El Iterator no deja elegir nada | Eligiste una píldora de un solo dato, no un arreglo | Usa la que tiene corchetes: Productos[] |
| El subtotal sale vacío o en cero | La multiplicación quedó mal armada | Revisa que haya píldora, signo y píldora, en ese orden |
| Se repiten filas al volver a ejecutar | Add a Row siempre agrega | Cada ejecución con estos datos genera tres filas nuevas |
| El proveedor no aparece | Elegiste la píldora Proveedor entera en vez de ID o Nombre | Despliega la colección y elige la que necesitas |

### Para pensar

1. ¿Por qué el número de orden se repite en las tres filas si el Iterator solo separó los productos?
2. Si la orden tuviera cinco productos, ¿cuántas veces correría Add a Row? ¿Tendrías que cambiar algo?
3. ¿Cuántas operaciones usaría esta ejecución en total? (Pista: mira los números sobre cada módulo.)

---

## 5. Demostración 3: cuando todo sale verde pero está mal

**El problema:** hasta ahora, cada ejecución terminó con marcas verdes y un resultado correcto. Es fácil pensar: "si Make dice que salió bien, salió bien". Vamos a comprobar si eso es verdad.

**El experimento:** usaremos la pestaña `PruebaFalloSilencioso`. Copiaremos el escenario de la demostración 1 y **cruzaremos a propósito** dos píldoras: el Monto irá en la columna Proveedor y el Proveedor irá en la columna Monto.

> Para copiar un escenario, entra a su página de detalle (la que muestra el diagrama) y usa el menú de los tres puntos > **Clone**. Cambia la pestaña de destino a `PruebaFalloSilencioso`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-55-fallo-pildoras-cruzadas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Add a Row con la píldora Monto en la columna Proveedor y la píldora Proveedor en la columna Monto, ambas resaltadas."><a href="contenido/make/imagenes/m05/make-m05-55-fallo-pildoras-cruzadas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Add a Row con la píldora Monto en la columna Proveedor y la píldora Proveedor en la columna Monto, ambas resaltadas." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las dos píldoras cruzadas a propósito.</figcaption></figure>

Pulsa **Run once**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-56-fallo-todo-en-verde.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario ejecutado con los cuatro módulos en verde."><a href="contenido/make/imagenes/m05/make-m05-56-fallo-todo-en-verde.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado con los cuatro módulos en verde." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Todo en verde. Make no vio ningún problema.</figcaption></figure>

Ahora mira la hoja.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-57-fallo-datos-en-columna-equivocada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña PruebaFalloSilencioso con 95000 en la columna Proveedor y Distribuidora Norte en la columna Monto."><a href="contenido/make/imagenes/m05/make-m05-57-fallo-datos-en-columna-equivocada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña PruebaFalloSilencioso con 95000 en la columna Proveedor y Distribuidora Norte en la columna Monto." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El resultado real: un número donde debería ir el nombre del proveedor y un nombre donde debería ir el monto.</figcaption></figure>

**Esto es un fallo silencioso:** el escenario se ejecutó sin errores, pero los datos quedaron en el lugar equivocado.

### ¿Por qué Make no lo detectó?

Porque Make solo comprueba que **la operación se pudo hacer**. Escribir un nombre en una columna llamada Monto es posible: Google Sheets acepta cualquier texto o número en cualquier celda. Make no sabe qué significa para tu negocio cada columna. Eso lo sabes tú.

Dicho de otra forma: **verde significa "la máquina funcionó", no "el resultado es correcto".**

### Corrígelo

Vuelve a poner cada píldora en su columna: Proveedor en Proveedor y Monto en Monto. Guarda y ejecuta de nuevo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-59-fallo-mapeo-corregido.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Mapeo corregido: la píldora Proveedor en la columna Proveedor y la píldora Monto en la columna Monto."><a href="contenido/make/imagenes/m05/make-m05-59-fallo-mapeo-corregido.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Mapeo corregido: la píldora Proveedor en la columna Proveedor y la píldora Monto en la columna Monto." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada píldora vuelve a su columna.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m05/make-m05-61-fallo-incorrecta-y-corregida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña PruebaFalloSilencioso con dos filas: la primera con datos cruzados y la segunda con datos correctos."><a href="contenido/make/imagenes/m05/make-m05-61-fallo-incorrecta-y-corregida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña PruebaFalloSilencioso con dos filas: la primera con datos cruzados y la segunda con datos correctos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Compara las dos filas. La de arriba es el error. La de abajo es lo correcto.</figcaption></figure>

### Cómo protegerte de los fallos silenciosos

1. **Prueba con datos fáciles de reconocer.** Un monto como 95000 y un proveedor como "Distribuidora Norte" no se confunden. Si usaras "A" y "B" te costaría notar el cruce.
2. **Revisa siempre el resultado final**, no solo las marcas verdes. Abre la hoja y mira la fila.
3. **Pon nombres claros a tus píldoras y columnas.** Así es más difícil equivocarse.
4. **Haz una prueba de cuadre.** Por ejemplo, que la suma de los subtotales sea igual al monto total.
5. **Mira el tipo de dato.** Un monto que aparece alineado a la izquierda en la hoja suele ser un texto, no un número.

---

## 6. Resumen

- Un **bundle** es la caja de datos que pasa de un módulo a otro. Una **píldora** es la etiqueta de un dato de esa caja.
- **Mapear** es poner píldoras (o textos) en los campos de un módulo.
- Un campo puede llevar un **dato dinámico** (píldora), un **dato estático** (texto fijo) o una **variable de Make** (como `now`).
- Una **colección** es una caja con varios datos de una cosa. Un **arreglo** es una lista de cosas parecidas, y se reconoce por los corchetes.
- El **Iterator** separa un arreglo y entrega un bundle por elemento. El módulo que sigue corre una vez por bundle.
- Después del Iterator sigues pudiendo usar los datos de los módulos anteriores.
- Una ejecución en verde **no garantiza** que el resultado sea correcto. Revisa siempre el destino.

## 7. Practica por tu cuenta

### Actividad breve

Tu empresa inventada recibe esta factura de un proveedor:

```json
{
  "factura": "F-2026",
  "cliente": { "id": "CLI-9", "nombre": "Panaderia Central" },
  "items": [
    { "detalle": "Harina", "kilos": 20, "precio_kilo": 900 },
    { "detalle": "Azucar", "kilos": 10, "precio_kilo": 1100 }
  ]
}
```

Crea una hoja con una fila por cada item. Cada fila debe llevar la factura, el nombre del cliente, el detalle, los kilos, el precio por kilo y el total de la línea.

**Resultado esperado:** dos filas. Harina con total 18000 y Azucar con total 11000.

### Pistas (ábrelas de a una)

<details>
<summary>Pista 1: ¿qué módulos necesito?</summary>

Piensa en lo que hiciste en la demostración 2. Necesitas guardar el dato, abrirlo, separar la lista y escribir en la hoja. Son los mismos cuatro módulos.

</details>

<details>
<summary>Pista 2: ¿qué es la colección y qué es el arreglo?</summary>

El cliente tiene un id y un nombre dentro: es una colección. Los items son una lista: es un arreglo. Tendrás que separar uno de los dos con el Iterator.

</details>

<details>
<summary>Pista 3: ¿cómo calculo el total de la línea?</summary>

Es una multiplicación, igual que el subtotal. Usa las píldoras kilos y precio_kilo del Iterator y el signo de multiplicar del panel de matemáticas.

</details>

<details>
<summary>Pista 4: ¿cómo sé que quedó bien?</summary>

Abre la hoja y suma a mano: 20 por 900 es 18000 y 10 por 1100 es 11000. Si tus filas no dan eso, revisa qué píldora pusiste en cada columna.

</details>

### Cómo diagnosticar si algo no funciona

1. Haz clic en la burbuja de cada módulo después de **Run once**. Mira qué entró y qué salió.
2. Si un dato falta en el panel de píldoras, ningún módulo anterior lo entrega. Revisa la estructura de datos.
3. Si el resultado está en la hoja pero en la columna equivocada, revisa el mapeo píldora por píldora.
4. Si la hoja no cambia, revisa la conexión, el archivo y la pestaña elegidos.

## 8. Autoevaluación

```quiz
? En Make, ¿qué es una píldora?
- Un módulo que guarda datos en una hoja.
+ La etiqueta de un dato que produjo un módulo anterior y que puedes usar en un campo.
- Un tipo de conexión con Google.
> Las píldoras aparecen en el panel cuando haces clic en un campo. Representan los datos de los bundles de los módulos anteriores.
? Quieres que la columna Estado siempre diga Registrado. ¿Qué debes poner en ese campo?
- La píldora now.
- La píldora Proveedor.
+ El texto Registrado, escrito directamente, sin píldoras.
> Un dato estático es un texto que escribes tú y no cambia entre ejecuciones.
? ¿Qué diferencia hay entre una colección y un arreglo?
- Ninguna, son lo mismo.
+ La colección es una caja con varios datos de una cosa; el arreglo es una lista de cosas parecidas.
- El arreglo solo guarda números.
> Por ejemplo, el proveedor (con id y nombre) es una colección. Los productos (una lista) son un arreglo.
? Una orden trae cuatro productos en un arreglo. Pasa por un Iterator y luego por Add a Row. ¿Cuántas veces se ejecuta Add a Row?
- Una vez.
- Cuatro veces menos una.
+ Cuatro veces.
> El Iterator entrega un bundle por elemento y el módulo siguiente se ejecuta una vez por bundle.
? Tu escenario termina con todas las marcas verdes, pero la hoja tiene el monto en la columna del proveedor. ¿Qué explica esto?
- Make tuvo un error que no mostró.
+ Make solo comprueba que la operación se pudo hacer, no que cada dato esté en la columna correcta.
- Google Sheets cambió los datos por su cuenta.
> Es un fallo silencioso. Por eso conviene revisar siempre el resultado final.
? ¿Dónde está el signo para multiplicar dos píldoras?
- En la pestaña de fecha y hora.
+ En la pestaña de matemáticas (Math functions) del panel, en la fila Operators.
- Hay que escribir una fórmula larga con llaves.
> Se arma con clics: píldora, signo y píldora.
```
