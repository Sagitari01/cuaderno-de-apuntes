# Escenarios, módulos y ejecuciones

Hasta ahora sabes qué es Make y por dónde moverte. Ahora viene lo importante: **cómo se arma una automatización y cómo sabes qué hizo**. Imagina que alguien te pide: "cada vez que pase tal cosa, haz tal otra". ¿Cómo se lo explicas a Make? ¿Y cómo compruebas que de verdad lo hizo?

En este apunte vamos a construir un escenario muy pequeño, de dos módulos, y lo vamos a mirar por dentro: qué datos entran, qué datos salen, cuántas veces trabaja cada pieza, dónde queda el registro y cómo se programa. No necesitas ninguna cuenta externa: solo Make.

**Qué vas a aprender:**

- Qué es un escenario y qué es un módulo.
- Qué diferencia hay entre un disparador, una búsqueda y una acción.
- Qué es un bundle y cómo viaja un dato de un módulo a otro.
- Cómo se ejecuta un escenario y cómo se leen sus resultados.
- Cómo se consulta el historial y cómo se programa.
- Cómo activar y desactivar un escenario sin sorpresas.

> **Sobre las capturas:** son capturas reales de una cuenta de práctica. Make está en inglés. Los recuadros violetas marcan lo que debes mirar. Si algo se ve distinto en tu pantalla, busca el mismo nombre de botón o de módulo.

---

## 1. La idea general

Piensa en una receta de cocina. Tiene **ingredientes** (los datos) y **pasos** (lo que se hace con ellos). Cada paso recibe lo que dejó el paso anterior y entrega algo para el siguiente.

En Make pasa lo mismo:

- Un **módulo** es un paso: una pieza que hace una sola tarea.
- Un **escenario** es la receta completa: varios módulos conectados en orden.

Cada módulo pertenece a una **aplicación**, como Google Sheets, Gmail o las herramientas internas de Make. Y cada aplicación ofrece varios módulos distintos.

### Tres clases de módulos

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Tarjetas que explican disparador, búsqueda y acción" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m01-d1-disparador-busqueda-accion" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Tres clases de módulos</text><rect x="70" y="90" width="240" height="250" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><circle cx="190" cy="156" r="38" fill="#ffffff" stroke="#2d3250" stroke-width="2.8"/><text x="190" y="168" font-size="38" text-anchor="middle" fill="#2d3250" font-weight="700">!</text><text x="190" y="226" font-size="30" text-anchor="middle" fill="#2d3250" font-weight="700">Disparador</text><text x="190" y="262" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Avisa que hay</text><text x="190" y="290" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">algo nuevo</text><text x="190" y="322" font-size="20" text-anchor="middle" fill="#5a4aa6" font-weight="400">Ej: llegó una fila</text><rect x="330" y="90" width="240" height="250" rx="12" fill="#f4efff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><circle cx="450" cy="156" r="38" fill="#ffffff" stroke="#2d3250" stroke-width="2.8"/><text x="450" y="168" font-size="38" text-anchor="middle" fill="#2d3250" font-weight="700">?</text><text x="450" y="226" font-size="30" text-anchor="middle" fill="#2d3250" font-weight="700">Búsqueda</text><text x="450" y="262" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Va a buscar</text><text x="450" y="290" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">datos y los trae</text><text x="450" y="322" font-size="20" text-anchor="middle" fill="#5a4aa6" font-weight="400">Ej: buscar una fila</text><rect x="590" y="90" width="240" height="250" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><circle cx="710" cy="156" r="38" fill="#ffffff" stroke="#2d3250" stroke-width="2.8"/><text x="710" y="168" font-size="38" text-anchor="middle" fill="#2d3250" font-weight="700">ok</text><text x="710" y="226" font-size="30" text-anchor="middle" fill="#2d3250" font-weight="700">Acción</text><text x="710" y="262" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Hace un cambio:</text><text x="710" y="290" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">guarda o envía</text><text x="710" y="322" font-size="20" text-anchor="middle" fill="#5a4aa6" font-weight="400">Ej: agregar una fila</text><text x="450" y="384" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Un escenario suele empezar con uno que avisa y seguir con los que actúan.</text></svg><a href="contenido/make/imagenes/diagramas/m01-d1-disparador-busqueda-accion.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Tres tarjetas: disparador (avisa que hay algo nuevo), búsqueda (va a buscar datos) y acción (hace un cambio)." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los módulos se agrupan en tres clases según lo que hacen.</figcaption></figure>

- **Disparador (trigger):** es el que **empieza** el escenario. Avisa que ocurrió algo, por ejemplo "llegó una fila nueva a la hoja". Normalmente es el primer módulo.
- **Búsqueda (search):** va a **buscar** información y la trae al escenario.
- **Acción (action):** **hace** algo: guarda un dato, envía un mensaje, crea un archivo.

En el módulo 02 vas a usar un disparador real de Google Sheets. Hoy usaremos módulos internos de Make, que no necesitan conectar ninguna cuenta, para entender la mecánica sin distracciones.

---

## 2. Cómo viajan los datos

Cuando un módulo termina su trabajo, entrega un **bundle**: un paquete con los datos que produjo. Piensa en una caja con etiquetas. El siguiente módulo recibe esa caja y puede usar cada etiqueta, que en Make se llama **píldora**.

- La **salida** de un módulo es lo que entrega.
- La **entrada** de un módulo es lo que recibe y usa.

Un mismo módulo puede entregar **varios bundles** en una sola ejecución. Cuando eso pasa, el módulo siguiente trabaja una vez por cada bundle. Lo vamos a ver con nuestros propios ojos en un momento.

---

## 3. Construyamos un escenario

**El objetivo:** observar cómo un dato que genera un módulo lo usa otro módulo.

**El plan:** usaremos dos módulos.

1. **Flow Control > Repeater:** repite una acción un número de veces y entrega un número que va aumentando (1, 2, 3).
2. **Tools > Set variable:** guarda un texto. Armaremos una frase que incluye el número que entregó el Repeater.

Ninguno de los dos necesita una cuenta externa.

### Paso 1. Crea el escenario

Desde la sección **Scenarios**, pulsa **Create scenario**. Se abre el **editor**: el lugar donde dibujas tu automatización.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-01-editor-vacio-con-asistente.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Editor de un escenario nuevo con el panel del asistente de Make a la izquierda resaltado."><a href="contenido/make/imagenes/m01/make-m01-01-editor-vacio-con-asistente.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Editor de un escenario nuevo con el panel del asistente de Make a la izquierda resaltado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El editor se abre con un panel del asistente de Make. Su disponibilidad depende de tu plan: si te aparece, puedes cerrarlo con la X.</figcaption></figure>

Si cierras el panel, ves el editor limpio. Mira qué hay:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-02-editor-vacio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Editor vacío con el nombre del escenario, la programación, el botón central y la barra inferior resaltados."><a href="contenido/make/imagenes/m01/make-m01-02-editor-vacio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Editor vacío con el nombre del escenario, la programación, el botón central y la barra inferior resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El editor vacío. Arriba a la izquierda, el nombre. Arriba a la derecha, la programación y el interruptor de activación. Al centro, el botón para agregar el primer módulo. Abajo, la barra de herramientas.</figcaption></figure>

- **Nombre del escenario** (arriba a la izquierda): por ahora dice "New scenario".
- **Programación y activación** (arriba a la derecha): cuándo se ejecuta y si está encendido.
- **Botón + central:** aquí agregas el primer módulo.
- **Barra inferior:** tiene los botones **Run once** y **Save**, entre otros.

Haz clic en el nombre y escribe uno que te sirva para reconocerlo, por ejemplo `Practica Make - Mi primer escenario`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-03-nombre-del-escenario.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Nombre del escenario ya escrito en el campo superior."><a href="contenido/make/imagenes/m01/make-m01-03-nombre-del-escenario.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nombre del escenario ya escrito en el campo superior." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Ponle un nombre claro desde el principio. Cuando tengas muchos escenarios te lo agradecerás.</figcaption></figure>

### Paso 2. Agrega el primer módulo: Repeater

Haz clic en el **+** central. Se abre el buscador de aplicaciones. Escribe `Flow Control` y elígela.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-04-buscar-aplicacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Buscador de aplicaciones con Flow Control escrito y la aplicación resaltada."><a href="contenido/make/imagenes/m01/make-m01-04-buscar-aplicacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Buscador de aplicaciones con Flow Control escrito y la aplicación resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El buscador de aplicaciones. Flow Control es una aplicación interna de Make.</figcaption></figure>

Verás una lista de módulos agrupados por tipo de tarea. Puedes escribir el nombre del módulo en el buscador de esa ventana.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-05-modulos-de-flow-control.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de módulos de Flow Control organizados por tipo: ramificación y acciones sobre bundles."><a href="contenido/make/imagenes/m01/make-m01-05-modulos-de-flow-control.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de módulos de Flow Control organizados por tipo: ramificación y acciones sobre bundles." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Flow Control reúne módulos para controlar el recorrido del escenario. El buscador te ahorra bajar por la lista.</figcaption></figure>

Busca `Repeater` y haz clic en él. Su descripción lo explica bien: *corre los módulos siguientes un número de veces y entrega un número que va aumentando*.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-06-repeater-en-la-lista.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Resultado de buscar Repeater con el módulo resaltado y su descripción."><a href="contenido/make/imagenes/m01/make-m01-06-repeater-en-la-lista.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Resultado de buscar Repeater con el módulo resaltado y su descripción." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El módulo Repeater.</figcaption></figure>

Se abre su ventana de configuración. Tiene dos campos y los dos vienen con un valor listo:

- **Initial value:** con qué número empieza. Déjalo en `1`.
- **Repeats:** cuántas veces se repite. Déjalo en `3`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-07-repeater-configuracion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana del Repeater con Initial value igual a 1 y Repeats igual a 3 resaltados."><a href="contenido/make/imagenes/m01/make-m01-07-repeater-configuracion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana del Repeater con Initial value igual a 1 y Repeats igual a 3 resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Empieza en 1 y se repite 3 veces. Make avisa que el máximo es 10.000.</figcaption></figure>

Pulsa **Save**. El módulo queda en el lienzo y aparece un pequeño **+** a su derecha: es el botón para agregar el siguiente módulo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-08-repeater-guardado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Módulo Repeater en el lienzo con el botón más de su derecha resaltado."><a href="contenido/make/imagenes/m01/make-m01-08-repeater-guardado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Módulo Repeater en el lienzo con el botón más de su derecha resaltado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Con ese + agregas el siguiente módulo, ya conectado al anterior.</figcaption></figure>

### Paso 3. Agrega el segundo módulo: Set variable

Haz clic en ese **+**, busca la aplicación **Tools** y elige el módulo **Set variable**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-09-buscar-tools.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Buscador con Tools escrito y la aplicación Tools resaltada."><a href="contenido/make/imagenes/m01/make-m01-09-buscar-tools.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Buscador con Tools escrito y la aplicación Tools resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La aplicación Tools. Aquí usaremos su módulo Set variable.</figcaption></figure>

**Set variable** guarda un valor con un nombre. Es una forma sencilla de "producir" un dato y ver cómo se usa. Tiene dos campos: el nombre y el valor.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-10-set-variable-vacio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana de Set variable con los campos Variable name y Variable value vacíos y resaltados."><a href="contenido/make/imagenes/m01/make-m01-10-set-variable-vacio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana de Set variable con los campos Variable name y Variable value vacíos y resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Dos campos: cómo se llama la variable y qué valor guarda.</figcaption></figure>

En **Variable name** escribe `mensaje`.

Ahora viene la parte importante. Queremos que el valor sea una frase que incluya el número que entregó el Repeater. Haz clic en **Variable value** y escribe `Este es el paquete numero `. Verás que se abre el **panel de píldoras**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-11-panel-con-pildora-i.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de píldoras abierto junto al campo Variable value. Muestra el módulo Repeater y su píldora i resaltada."><a href="contenido/make/imagenes/m01/make-m01-11-panel-con-pildora-i.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de píldoras abierto junto al campo Variable value. Muestra el módulo Repeater y su píldora i resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El panel de píldoras muestra lo que producen los módulos anteriores. El Repeater entrega una píldora llamada i, que es el número que va aumentando.</figcaption></figure>

Haz clic en la píldora **i**. Queda dentro del campo. Después escribe ` de 3.`

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-12-mensaje-con-pildora.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Campo Variable value con el texto Este es el paquete numero, la píldora i y el texto de 3."><a href="contenido/make/imagenes/m01/make-m01-12-mensaje-con-pildora.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo Variable value con el texto Este es el paquete numero, la píldora i y el texto de 3." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La frase mezcla texto que escribiste y una píldora. La píldora cambiará en cada vuelta.</figcaption></figure>

Pulsa **Save**, y luego el botón **Save** de la barra inferior para guardar el escenario completo.

### Paso 4. Mira cómo quedan conectados

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-13-escenario-dos-modulos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario con dos módulos conectados por una línea de puntos con un ícono de filtro, y el aviso de que el escenario fue guardado."><a href="contenido/make/imagenes/m01/make-m01-13-escenario-dos-modulos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario con dos módulos conectados por una línea de puntos con un ícono de filtro, y el aviso de que el escenario fue guardado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los dos módulos conectados. La línea de puntos es la conexión. El pequeño embudo es el filtro: sirve para dejar pasar solo ciertos datos. Lo usaremos en el módulo 03.</figcaption></figure>

La **línea de puntos** indica que el bundle del primer módulo viaja al segundo. El **embudo** del medio es un filtro. Por ahora no lo usamos; en el módulo 03 aprenderás a configurarlo.

---

## 4. Ejecuta y observa

Ahora comprobemos qué pasa. Pulsa **Run once**. Este botón ejecuta el escenario **una sola vez, ahora mismo**, sin programarlo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-14-ejecucion-1-y-3.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="El escenario después de ejecutarse. Sobre Repeater hay una burbuja con el número 1 y sobre Set variable una burbuja con el número 3."><a href="contenido/make/imagenes/m01/make-m01-14-ejecucion-1-y-3.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: El escenario después de ejecutarse. Sobre Repeater hay una burbuja con el número 1 y sobre Set variable una burbuja con el número 3." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada módulo muestra una marca verde y una burbuja con un número. Ese número es la cantidad de **operaciones**: cuántas veces trabajó el módulo.</figcaption></figure>

Fíjate en los números:

- **Repeater: 1.** Trabajó una sola vez.
- **Set variable: 3.** Trabajó tres veces.

¿Por qué? Porque el Repeater entregó **tres bundles** y el módulo siguiente trabajó una vez con cada uno. Veámoslo.

### Qué entró y qué salió

Haz clic en la burbuja del **Repeater**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-15-repeater-entrada-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel del Repeater con la entrada a la izquierda (valor inicial 1, repeticiones 3) y la salida a la derecha (tres bundles)."><a href="contenido/make/imagenes/m01/make-m01-15-repeater-entrada-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel del Repeater con la entrada a la izquierda (valor inicial 1, repeticiones 3) y la salida a la derecha (tres bundles)." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>A la izquierda, lo que recibió: valor inicial 1, tres repeticiones. A la derecha, lo que entregó: tres bundles.</figcaption></figure>

El primer bundle tiene una sola píldora, `i`, con el valor 1. Si abres el bundle 2:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-16-bundle-2-abierto.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Bundle 2 desplegado con la píldora i igual a 2."><a href="contenido/make/imagenes/m01/make-m01-16-bundle-2-abierto.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Bundle 2 desplegado con la píldora i igual a 2." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El segundo bundle trae i igual a 2. El tercero traerá i igual a 3.</figcaption></figure>

Cada bundle es una caja distinta con su propio número. Ahora mira el segundo módulo. Haz clic en la burbuja de **Set variable**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-17-set-variable-operacion-1.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de Set variable con la operación 1 de 3. La entrada y la salida muestran la frase Este es el paquete numero 1 de 3."><a href="contenido/make/imagenes/m01/make-m01-17-set-variable-operacion-1.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de Set variable con la operación 1 de 3. La entrada y la salida muestran la frase Este es el paquete numero 1 de 3." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La operación 1 de 3. La píldora i se reemplazó por el número 1.</figcaption></figure>

Arriba del panel verás un selector: **Operation 1 of 3**. Usa las flechas para pasar a la siguiente.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-18-set-variable-operacion-2.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de Set variable con la operación 2 de 3. La frase dice Este es el paquete numero 2 de 3."><a href="contenido/make/imagenes/m01/make-m01-18-set-variable-operacion-2.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de Set variable con la operación 2 de 3. La frase dice Este es el paquete numero 2 de 3." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La operación 2 de 3. Ahora dice 2.</figcaption></figure>

Esto es lo central de este apunte: **un dato generado por un módulo (la píldora i) se usó en otro módulo (en la frase)**, y cada bundle produjo un resultado distinto.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="El Repeater entrega tres bundles y Set variable los procesa uno a uno" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m01-d2-bundles-y-operaciones" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Una ejecución de nuestro escenario</text><circle cx="130" cy="190" r="52" fill="#a8e2c0" stroke="#2d3250" stroke-width="2.8"/><text x="130" y="198" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">Repeater</text><text x="130" y="270" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">1 operación</text><path d="M186 190 L330 140" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m01-d2-bundles-y-operaciones)"/><rect x="334" y="110" width="150" height="60" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="409" y="148" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">bundle i = 1</text><path d="M486 140 L590 190" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m01-d2-bundles-y-operaciones)"/><path d="M186 190 L330 218" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m01-d2-bundles-y-operaciones)"/><rect x="334" y="188" width="150" height="60" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="409" y="226" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">bundle i = 2</text><path d="M486 218 L590 190" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m01-d2-bundles-y-operaciones)"/><path d="M186 190 L330 296" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m01-d2-bundles-y-operaciones)"/><rect x="334" y="266" width="150" height="60" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="409" y="304" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">bundle i = 3</text><path d="M486 296 L590 190" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m01-d2-bundles-y-operaciones)"/><circle cx="660" cy="190" r="52" fill="#cdbff5" stroke="#2d3250" stroke-width="2.8"/><text x="660" y="186" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">Set</text><text x="660" y="212" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">variable</text><text x="660" y="270" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">3 operaciones</text><path d="M714 190 L800 190" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m01-d2-bundles-y-operaciones)"/><rect x="804" y="160" width="76" height="60" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="842" y="196" font-size="20" text-anchor="middle" fill="#2d3250" font-weight="400">3 res.</text><text x="450" y="366" font-size="22" text-anchor="middle" fill="#5a4aa6" font-weight="400">El módulo siguiente trabaja una vez con cada bundle.</text><text x="450" y="398" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="700">Total: 4 operaciones, 4 créditos.</text></svg><a href="contenido/make/imagenes/diagramas/m01-d2-bundles-y-operaciones.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: El Repeater entrega tres bundles con i igual a 1, 2 y 3; el módulo Set variable trabaja una vez con cada uno." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una ejecución completa. El Repeater trabaja una vez y entrega 3 bundles. Set variable trabaja 3 veces. En total son 4 operaciones.</figcaption></figure>

### Las operaciones y los créditos

En el módulo 00 vimos que, en la mayoría de las aplicaciones, **una operación cuesta un crédito**. Aquí fueron 1 + 3 = **4 operaciones, 4 créditos**. Lo puedes confirmar en el historial, como veremos enseguida.

---

## 5. El historial: qué pasó y cuándo

Cada vez que algo ocurre en tu escenario, Make lo anota en el **historial**. Se abre desde la página del escenario, en la pestaña **History**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-23-historial.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Historial con cinco registros: edición, ejecución manual, activación, ejecución programada y desactivación. Las filas de ejecución manual y programada están resaltadas."><a href="contenido/make/imagenes/m01/make-m01-23-historial.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Historial con cinco registros: edición, ejecución manual, activación, ejecución programada y desactivación. Las filas de ejecución manual y programada están resaltadas." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El historial. Cada fila es un hecho: una edición, una ejecución, una activación. Los nombres de las personas están desenfocados.</figcaption></figure>

Para cada ejecución verás cuándo empezó, qué la disparó (**Trigger / Activity**), si salió bien (**Status**), cuánto duró y cuántos créditos y operaciones usó.

Haz clic en una ejecución para ver su detalle.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-24-detalle-de-ejecucion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Detalle de una ejecución con el diagrama del escenario a la izquierda y un resumen a la derecha: éxito, disparador manual, 4 operaciones, 4 créditos y 195 bytes."><a href="contenido/make/imagenes/m01/make-m01-24-detalle-de-ejecucion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Detalle de una ejecución con el diagrama del escenario a la izquierda y un resumen a la derecha: éxito, disparador manual, 4 operaciones, 4 créditos y 195 bytes." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El detalle de la ejecución manual: 4 operaciones y 4 créditos, tal como calculamos.</figcaption></figure>

Es la mejor herramienta para diagnosticar problemas. Si algo no salió como esperabas, el historial te muestra qué hizo cada módulo.

---

## 6. La programación

Hasta ahora ejecutamos el escenario a mano con **Run once**. Pero Make también puede ejecutarlo solo, según una programación. Haz clic en el botón que dice **Every 15 minutes**, arriba a la derecha.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-19-programacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana Schedule settings con el modo At regular intervals y 15 minutos. Se resalta el aviso de que el valor debe ser mayor o igual que 15."><a href="contenido/make/imagenes/m01/make-m01-19-programacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana Schedule settings con el modo At regular intervals y 15 minutos. Se resalta el aviso de que el valor debe ser mayor o igual que 15." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La programación. El aviso indica el mínimo permitido en esta cuenta: 15 minutos.</figcaption></figure>

En **Run scenario** eliges cómo se ejecuta:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-20-opciones-de-programacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de opciones de Run scenario: a intervalos regulares, una vez, diaria, de lunes a viernes, semanal, mensual, en fechas específicas y bajo demanda."><a href="contenido/make/imagenes/m01/make-m01-20-opciones-de-programacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de opciones de Run scenario: a intervalos regulares, una vez, diaria, de lunes a viernes, semanal, mensual, en fechas específicas y bajo demanda." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las formas de programar un escenario.</figcaption></figure>

| Opción | Cuándo conviene |
| --- | --- |
| **At regular intervals** | Revisar cada cierto tiempo (cada 15 minutos, por ejemplo) |
| **Once** | Ejecutar una sola vez en una fecha y hora |
| **Daily, Weekdays, Weekly, Monthly** | Tareas que ocurren cada día, de lunes a viernes, cada semana o cada mes |
| **Specified dates** | En fechas concretas |
| **On demand** | Solo cuando alguien lo ordena (a mano o desde otra herramienta) |

El mínimo de 15 minutos corresponde al plan gratuito. Los planes de pago permiten intervalos más cortos; revisa la información oficial como vimos en el módulo 00.

---

## 7. Activar y desactivar

El interruptor de arriba a la derecha enciende o apaga el escenario.

- **Inactive (apagado):** el escenario solo se ejecuta cuando tú pulsas **Run once**.
- **Active (encendido):** Make lo ejecuta solo, según la programación.

Lo vamos a probar de forma **controlada**: lo encendemos unos segundos y lo apagamos enseguida, para ver qué ocurre.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-21-escenario-activo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Interruptor de activación en posición encendida con la etiqueta Active."><a href="contenido/make/imagenes/m01/make-m01-21-escenario-activo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Interruptor de activación en posición encendida con la etiqueta Active." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El escenario activado.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m01/make-m01-22-escenario-inactivo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Interruptor de activación en posición apagada con la etiqueta Inactive."><a href="contenido/make/imagenes/m01/make-m01-22-escenario-inactivo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Interruptor de activación en posición apagada con la etiqueta Inactive." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Lo apagamos de inmediato.</figcaption></figure>

¿Y qué pasó? Mira otra vez el historial de arriba. Hay una fila **Scenario activated** (activado) seguida, un segundo después, de una ejecución con el disparador **Schedule** (programación). Es decir: **al activar un escenario, Make lo ejecuta una vez de inmediato** y después sigue la programación. Esa ejecución también gastó 4 créditos. Después hay una fila **Scenario deactivated**.

Por eso la regla de oro es esta: **no actives un escenario si no quieres que se ejecute**, y **apaga lo que no uses**. Un escenario activo olvidado sigue consumiendo créditos, aunque no haya datos nuevos.

> En el plan gratuito puedes tener como máximo 2 escenarios activos al mismo tiempo (lo vimos en el panel principal).

---

## 8. Errores frecuentes y cómo revisarlos

| Qué ves | Qué puede estar pasando | Cómo lo revisas |
| --- | --- | --- |
| El botón Run once está gris | El escenario aún no tiene ningún módulo | Agrega un módulo y pulsa Save |
| Un módulo tiene un círculo rojo con un número | Le faltan datos obligatorios | Ábrelo y completa los campos marcados con asterisco |
| La píldora no aparece en el panel | El módulo anterior no la entrega, o aún no existe | Revisa el orden de los módulos y la salida del anterior |
| El resultado no es el esperado | El mapeo está mal o el dato de entrada es otro | Abre las burbujas y compara entrada y salida |
| Se gastaron créditos que no esperabas | Dejaste activo un escenario programado | Entra al historial y apágalo |

---

## 9. Resumen

- Un **escenario** es la receta completa; un **módulo** es un paso.
- Hay módulos **disparadores** (avisan que algo ocurrió), de **búsqueda** (traen datos) y de **acción** (hacen un cambio).
- Un módulo entrega **bundles** con **píldoras**. El siguiente módulo trabaja una vez por cada bundle.
- **Run once** ejecuta el escenario una vez, ahora. Las burbujas muestran cuántas operaciones hizo cada módulo.
- El **historial** guarda cada hecho: ejecuciones, activaciones y ediciones.
- La **programación** define cuándo se ejecuta; en el plan gratuito, como mínimo cada 15 minutos.
- Al **activar** un escenario, se ejecuta de inmediato una vez. Apaga lo que no uses.

## 10. Ponlo en práctica

### Desafío: cambia el número de repeticiones

Antes de tocar nada, **predice**: si cambias **Repeats** de 3 a 5, ¿cuántas operaciones hará cada módulo y cuántos créditos gastará la ejecución?

Después comprueba tu predicción:

1. Abre el módulo Repeater y cambia **Repeats** a `5`. Guarda.
2. Pulsa **Run once**.
3. Mira las burbujas y el historial.

**Resultado esperado:** el Repeater trabaja 1 vez y Set variable 5 veces. Total: 6 operaciones y 6 créditos. La última frase dice "Este es el paquete numero 5 de 3", lo que te muestra que el texto fijo no se actualiza solo.

### Pistas (ábrelas de a una)

<details>
<summary>Pista 1: no estoy seguro de cuántas operaciones serán</summary>

Recuerda lo que vimos: el Repeater trabaja una sola vez y entrega varios bundles. El módulo siguiente trabaja una vez por cada bundle.

</details>

<details>
<summary>Pista 2: ¿dónde veo los créditos de la ejecución?</summary>

En el historial del escenario, en la columna Credits, o en el panel que se abre al hacer clic en la burbuja de un módulo.

</details>

<details>
<summary>Pista 3: la frase dice "de 3" aunque haya 5 paquetes</summary>

Ese "3" lo escribiste tú como texto fijo. Para que cambie, necesitarías una píldora. Piensa: ¿qué módulo entrega la cantidad de repeticiones? Puedes mirar su entrada.

</details>

### Cómo diagnosticar si algo no funciona

1. Abre la burbuja de cada módulo después de **Run once** y compara la entrada con la salida.
2. Si falta una píldora, revisa si el módulo anterior realmente la entrega.
3. Si no sabes qué pasó, ve al historial y abre el detalle de la ejecución.

## 11. Comprueba lo aprendido

```quiz
? ¿Qué es un bundle?
- Un tipo de aplicación de Make.
+ Un paquete de datos que un módulo entrega al siguiente.
- El botón para ejecutar un escenario.
> Un módulo entrega bundles con píldoras, y el módulo siguiente los recibe y los usa.
? El Repeater entrega 4 bundles y después hay un módulo Set variable. ¿Cuántas operaciones hará Set variable?
- 1
+ 4
- 5
> El módulo trabaja una vez por cada bundle que recibe.
? ¿Qué hace el botón Run once?
- Activa el escenario para siempre.
+ Ejecuta el escenario una sola vez, ahora, sin programarlo.
- Guarda el escenario.
> Es la forma ideal de probar sin gastar créditos de más ni dejar nada programado.
? Activas un escenario con programación cada 15 minutos. ¿Qué ocurre de inmediato?
- Nada hasta que pasen 15 minutos.
+ Make lo ejecuta una vez y después sigue la programación.
- Se borra el historial.
> Lo comprobamos en el historial: hubo una ejecución justo después de la activación.
? ¿Cuál de estos módulos es un disparador?
- El que guarda una fila en una hoja.
+ El que avisa que llegó una fila nueva y empieza el escenario.
- El que arma una frase con una píldora.
> El disparador es el que inicia el escenario cuando ocurre algo.
```
