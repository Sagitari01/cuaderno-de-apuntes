# Nuestra primera automatización

Imagina una pequeña empresa que recibe solicitudes de atención. Cada vez que alguien escribe una, la anotan en una hoja de cálculo. Después, alguien tiene que revisar esa hoja y pasar cada solicitud a otro lugar para darle seguimiento. Es un trabajo repetitivo y, si se acumula, algunas solicitudes se olvidan.

En este apunte vamos a construir, paso a paso, **nuestra primera automatización de verdad**: un escenario que vigila una hoja de cálculo y, cada vez que aparece una solicitud nueva, la copia a un registro y le pone el estado «Recibida». No usa inteligencia artificial: solo reglas simples y datos que tú controlas.

**Qué vas a aprender:**

- Preparar una hoja de cálculo para que Make la entienda.
- Conectar Make con Google Sheets de forma segura.
- Configurar un disparador que vigila filas nuevas (**Watch New Rows**).
- Configurar una acción que agrega filas (**Add a Row**) mapeando con píldoras.
- Entender cómo decide Make qué filas procesar y cómo evitar duplicados.
- Probar el escenario con una solicitud, con varias y con ninguna.

**Qué necesitas:** una cuenta de Make y una cuenta de Google. Todos los datos son inventados.

> **Sobre las capturas:** son capturas reales de una cuenta de práctica. Make está en inglés y Google Sheets en español. Los recuadros violetas marcan lo que debes mirar. Los nombres de las cuentas de Google se muestran desenfocados.

---

## 1. El plan

Antes de tocar nada, pensemos qué queremos que ocurra:

1. Llega una solicitud nueva a la hoja **Solicitudes**.
2. Make se da cuenta de que hay una fila nueva.
3. Make copia esa solicitud a la hoja **Registro** y agrega una columna **Estado** con el valor «Recibida».

Eso se traduce en dos módulos:

- **Google Sheets > Watch New Rows:** el **disparador**. Vigila la hoja y avisa cuando hay filas nuevas.
- **Google Sheets > Add a Row:** la **acción**. Agrega una fila a la otra hoja.

Los dos son de la misma aplicación, pero hacen cosas distintas. Mira cómo Make los muestra juntos:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-03-modulos-de-google-sheets.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de módulos de Google Sheets con Add a Row, Search Rows y Watch New Rows resaltados."><a href="contenido/make/imagenes/m02/make-m02-03-modulos-de-google-sheets.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de módulos de Google Sheets con Add a Row, Search Rows y Watch New Rows resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una sola aplicación ofrece módulos de acción (Add a Row), de búsqueda (Search Rows) y de disparador (Watch New Rows).</figcaption></figure>

---

## 2. Prepara la hoja de cálculo

Crea una hoja de cálculo de Google llamada **Practica Make - Solicitudes**. Dentro necesitas dos pestañas: `Solicitudes` y `Registro`.

En la fila 1 de cada pestaña escribe los encabezados. Son los nombres de las columnas, y **Make los usa para mostrarte un campo por cada una**. Por eso deben estar bien escritos y en la fila 1.

| Pestaña | Encabezados (fila 1) |
| --- | --- |
| Solicitudes | ID, Nombre, Descripción, Prioridad |
| Registro | ID, Nombre, Descripción, Prioridad, **Estado** |

La pestaña Registro tiene una columna más: **Estado**. Será un dato que nuestra automatización agregará por su cuenta.

En la pestaña Solicitudes escribe la primera solicitud (solo una por ahora):

| ID | Nombre | Descripción | Prioridad |
| --- | --- | --- | --- |
| SOL-001 | Ana | Problema de acceso | Alta |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-01-hoja-solicitudes-primera-fila.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Solicitudes con los encabezados y la fila SOL-001 resaltada."><a href="contenido/make/imagenes/m02/make-m02-01-hoja-solicitudes-primera-fila.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Solicitudes con los encabezados y la fila SOL-001 resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La hoja de entrada, con una solicitud.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-02-hoja-registro-encabezados.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Registro con los cinco encabezados, incluido Estado, resaltados."><a href="contenido/make/imagenes/m02/make-m02-02-hoja-registro-encabezados.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Registro con los cinco encabezados, incluido Estado, resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La hoja de salida, todavía vacía. Fíjate en la columna extra: Estado.</figcaption></figure>

**Comprueba:** cada encabezado debe estar en su propia celda. Si ves todos los nombres amontonados en la celda A1, se escribieron en una sola celda y Make no podrá encontrar las columnas.

---

## 3. Construye el disparador

Crea un escenario nuevo y ponle un nombre, por ejemplo `Practica Make - Primera automatizacion`. Haz clic en el **+** central, busca **Google Sheets** y elige **Watch New Rows**.

Se abre la ventana de configuración. Lo primero es la **conexión**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-04-watch-new-rows-inicial.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana de Watch New Rows con la conexión, el método de búsqueda, el archivo y los encabezados resaltados."><a href="contenido/make/imagenes/m02/make-m02-04-watch-new-rows-inicial.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana de Watch New Rows con la conexión, el método de búsqueda, el archivo y los encabezados resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ventana del disparador. Arriba, la conexión. Después, qué archivo y qué pestaña vigilar.</figcaption></figure>

### La conexión: una autorización, no tu contraseña

Para que Make lea tu hoja, necesita permiso. Ese permiso se guarda en una **conexión**. La primera vez, Make te pide iniciar sesión con Google y aceptar los permisos. Esa autorización la das **tú**, en una ventana de Google: nunca le entregas tu contraseña a Make ni a nadie más.

> **Cuidado:** si tu cuenta de Make tiene varias conexiones de Google, Make puede dejar seleccionada una que no es la que quieres. Revisa siempre este campo. Elige la cuenta de Google donde creaste la hoja.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-05-lista-de-conexiones.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista desplegable con tres conexiones de Google. Una de ellas está resaltada."><a href="contenido/make/imagenes/m02/make-m02-05-lista-de-conexiones.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista desplegable con tres conexiones de Google. Una de ellas está resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Si tienes varias conexiones, elige con cuidado cuál usar. Los nombres de las cuentas están desenfocados.</figcaption></figure>

### El archivo y la pestaña

Haz clic en **Click here to choose file** y elige tu hoja.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-06-selector-de-archivo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Selector de archivos del Drive con la hoja Practica Make - Solicitudes resaltada."><a href="contenido/make/imagenes/m02/make-m02-06-selector-de-archivo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Selector de archivos del Drive con la hoja Practica Make - Solicitudes resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Make lista los archivos de tu Drive. Elige la hoja que creaste.</figcaption></figure>

Después elige la pestaña que se va a vigilar: **Solicitudes**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-07-lista-de-pestanas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de pestañas de la hoja con Solicitudes y Registro."><a href="contenido/make/imagenes/m02/make-m02-07-lista-de-pestanas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de pestañas de la hoja con Solicitudes y Registro." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Make lee las pestañas de tu hoja. Para el disparador, elige Solicitudes.</figcaption></figure>

Deja los demás campos como están. Hay dos que conviene conocer:

- **Table contains headers: Yes.** Le dice a Make que la fila 1 tiene nombres de columnas.
- **Limit: 2.** Es el máximo de filas que procesa en cada ejecución. Lo vamos a notar enseguida.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-08-watch-new-rows-configurado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Watch New Rows configurado con la pestaña Solicitudes, los encabezados y el límite resaltados."><a href="contenido/make/imagenes/m02/make-m02-08-watch-new-rows-configurado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Watch New Rows configurado con la pestaña Solicitudes, los encabezados y el límite resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El disparador configurado.</figcaption></figure>

Pulsa **Save**. Verás que el módulo tiene una insignia roja con el número 1.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-09-disparador-guardado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Módulo Watch New Rows con una insignia roja con un 1 encima."><a href="contenido/make/imagenes/m02/make-m02-09-disparador-guardado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Módulo Watch New Rows con una insignia roja con un 1 encima." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La insignia roja avisa que algo falta. Lo descubriremos más adelante.</figcaption></figure>

---

## 4. Construye la acción

Haz clic en el **+** a la derecha del disparador, busca **Google Sheets** y elige **Add a Row**. Elige la misma conexión y el mismo archivo, pero ahora la pestaña **Registro**.

En cuanto eliges la pestaña, Make lee sus encabezados y crea **un campo por cada columna**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-10-add-a-row-columnas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana de Add a Row con un campo por cada columna de la pestaña Registro: ID, Nombre, Descripción y Prioridad."><a href="contenido/make/imagenes/m02/make-m02-10-add-a-row-columnas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana de Add a Row con un campo por cada columna de la pestaña Registro: ID, Nombre, Descripción y Prioridad." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un campo por columna. Por eso los encabezados deben estar bien escritos.</figcaption></figure>

### Mapea con píldoras

Haz clic dentro del campo **ID (A)**. Se abre el **panel de píldoras**, con lo que entrega el disparador: una píldora por cada columna de la hoja Solicitudes.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-11-panel-de-pildoras-del-disparador.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de píldoras con las columnas del disparador: ID, Nombre, Descripción y Prioridad, además del número de fila."><a href="contenido/make/imagenes/m02/make-m02-11-panel-de-pildoras-del-disparador.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de píldoras con las columnas del disparador: ID, Nombre, Descripción y Prioridad, además del número de fila." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Lo que produce el disparador. Cada columna de Solicitudes es una píldora.</figcaption></figure>

Haz clic en la píldora que corresponde a cada campo: **ID (A)** en el campo ID, **Nombre (B)** en el campo Nombre, y así con las demás.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-12-mapeo-con-pildoras.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Los cuatro campos del módulo Add a Row con su píldora correspondiente cada uno."><a href="contenido/make/imagenes/m02/make-m02-12-mapeo-con-pildoras.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Los cuatro campos del módulo Add a Row con su píldora correspondiente cada uno." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada campo lleva la píldora de su misma columna.</figcaption></figure>

### El dato fijo: Estado

La columna **Estado** no viene de la hoja de Solicitudes: la agregamos nosotros. Haz clic en el campo **Estado (E)** y escribe directamente `Recibida`. No uses ninguna píldora, porque queremos que siempre diga lo mismo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-13-estado-texto-fijo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Campo Estado con el texto fijo Recibida, junto al panel de píldoras."><a href="contenido/make/imagenes/m02/make-m02-13-estado-texto-fijo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo Estado con el texto fijo Recibida, junto al panel de píldoras." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un texto que escribes tú: aparece sin color de píldora.</figcaption></figure>

Pulsa **Save** en el módulo y luego en el escenario.

---

## 5. El aviso que faltaba: el punto de inicio

Al guardar el escenario, Make muestra una ventana con un aviso.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-14-mensaje-punto-de-inicio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana de mensajes de Make que dice que primero hay que elegir desde qué punto empezar a procesar."><a href="contenido/make/imagenes/m02/make-m02-14-mensaje-punto-de-inicio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana de mensajes de Make que dice que primero hay que elegir desde qué punto empezar a procesar." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Make no sabe desde qué fila empezar. Necesita que se lo digas.</figcaption></figure>

Make dice: **debes elegir desde qué punto quieres empezar a procesar**. Es la insignia roja de antes. Cancelamos y lo configuramos.

### Por qué importa

Un disparador como **Watch New Rows** no puede mirar la hoja "para siempre desde cero". Necesita una **marca**: un punto que separa lo que ya procesó de lo que es nuevo. Cada vez que se ejecuta, entrega solo las filas que quedaron después de la marca y luego la mueve.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Una marca separa las filas ya procesadas de las nuevas; Watch New Rows solo entrega las nuevas" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m02-d1-marca-de-filas-procesadas" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Cómo decide Make qué filas procesar</text><text x="190" y="88" font-size="26" text-anchor="middle" fill="#7b5fd6" font-weight="700">Hoja Solicitudes</text><rect x="80" y="100" width="200" height="40" rx="10" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="180" y="128" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="400">SOL-001</text><text x="300" y="128" font-size="21" text-anchor="start" fill="#1f8f5f" font-weight="400">ya procesada</text><rect x="80" y="152" width="200" height="40" rx="10" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="180" y="180" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="400">SOL-002</text><text x="300" y="180" font-size="21" text-anchor="start" fill="#1f8f5f" font-weight="400">ya procesada</text><rect x="80" y="204" width="200" height="40" rx="10" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="180" y="232" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="400">SOL-003</text><text x="300" y="232" font-size="21" text-anchor="start" fill="#1f8f5f" font-weight="400">ya procesada</text><rect x="80" y="270" width="200" height="40" rx="10" fill="#fff6d6" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="180" y="298" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="400">SOL-004</text><text x="300" y="298" font-size="21" text-anchor="start" fill="#c0562d" font-weight="700">NUEVA</text><line x1="60" y1="262" x2="480" y2="262" stroke="#c0562d" stroke-width="4" stroke-dasharray="10 7"/><text x="470" y="254" font-size="22" text-anchor="end" fill="#c0562d" font-weight="400">marca</text><path d="M500 215 L590 215" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m02-d1-marca-de-filas-procesadas)"/><circle cx="650" cy="215" r="52" fill="#a8e2c0" stroke="#2d3250" stroke-width="2.8"/><text x="650" y="209" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">Watch</text><text x="650" y="235" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">New Rows</text><path d="M704 215 L770 215" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m02-d1-marca-de-filas-procesadas)"/><rect x="774" y="185" width="100" height="60" rx="10" fill="#fff6d6" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="824" y="213" font-size="20" text-anchor="middle" fill="#2d3250" font-weight="400">solo</text><text x="824" y="235" font-size="20" text-anchor="middle" fill="#2d3250" font-weight="400">SOL-004</text><text x="450" y="340" font-size="22" text-anchor="middle" fill="#5a4aa6" font-weight="400">Cada vez, Make mueve la marca y solo entrega lo que quedó después.</text><text x="450" y="374" font-size="22" text-anchor="middle" fill="#c0562d" font-weight="400">Si cambias la marca hacia atrás, vuelve a entregar filas ya procesadas.</text></svg><a href="contenido/make/imagenes/diagramas/m02-d1-marca-de-filas-procesadas.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Cuatro filas de una hoja. Las tres primeras están marcadas como ya procesadas y una línea punteada las separa de SOL-004, que es nueva. Watch New Rows solo entrega SOL-004." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una marca separa lo ya procesado de lo nuevo. Watch New Rows solo entrega lo que queda después de la marca.</figcaption></figure>

Haz clic derecho sobre el módulo y elige **Choose where to start**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-15-menu-del-modulo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Menú que aparece al hacer clic derecho sobre el módulo, con la opción Choose where to start resaltada."><a href="contenido/make/imagenes/m02/make-m02-15-menu-del-modulo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Menú que aparece al hacer clic derecho sobre el módulo, con la opción Choose where to start resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El menú del módulo. Aquí está la opción para elegir el punto de inicio.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-16-elegir-punto-de-inicio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana Choose where to start con tres opciones: Choose manually, All y Since specific ID."><a href="contenido/make/imagenes/m02/make-m02-16-elegir-punto-de-inicio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana Choose where to start con tres opciones: Choose manually, All y Since specific ID." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tres formas de decidir desde dónde empezar.</figcaption></figure>

| Opción | Qué hace |
| --- | --- |
| **Choose manually** | Te muestra las filas que ya existen y tú eliges desde cuál empezar |
| **All** | Procesa todas las filas que ya existen, desde la primera |
| **Since specific ID** | Empieza desde una fila concreta, indicada por su número |

Para esta primera prueba elegimos **All**: queremos que procese la solicitud que ya escribimos.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-17-punto-de-inicio-all.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Opción All seleccionada y el botón Save resaltado."><a href="contenido/make/imagenes/m02/make-m02-17-punto-de-inicio-all.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Opción All seleccionada y el botón Save resaltado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>All: procesar todo lo que ya existe.</figcaption></figure>

Pulsa **Save** y guarda el escenario. Ahora sí se guarda sin avisos.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-18-escenario-guardado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario con los dos módulos conectados y el mensaje de que se guardó."><a href="contenido/make/imagenes/m02/make-m02-18-escenario-guardado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario con los dos módulos conectados y el mensaje de que se guardó." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Escenario guardado, sin insignias rojas.</figcaption></figure>

---

## 6. Pruebas

Vamos a probar el escenario en cinco situaciones. En todas usamos **Run once** para ejecutarlo una sola vez, sin dejarlo activo.

### Prueba 1: una solicitud

Pulsa **Run once**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-19-prueba-1-ejecucion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario ejecutado: ambos módulos con marca verde y una operación cada uno."><a href="contenido/make/imagenes/m02/make-m02-19-prueba-1-ejecucion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado: ambos módulos con marca verde y una operación cada uno." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los dos módulos trabajaron una vez: una fila leída, una fila escrita.</figcaption></figure>

Abre la hoja **Registro**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-20-prueba-1-registro.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Registro con una fila: SOL-001, Ana, Problema de acceso, Alta y Recibida."><a href="contenido/make/imagenes/m02/make-m02-20-prueba-1-registro.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Registro con una fila: SOL-001, Ana, Problema de acceso, Alta y Recibida." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La solicitud quedó registrada con el estado Recibida. Funciona.</figcaption></figure>

Veamos qué entregó el disparador. Haz clic en la burbuja del primer módulo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-21-prueba-1-bundle-del-disparador.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Bundle de salida del disparador con ID, Nombre, Descripción y Prioridad, además del número de fila, el identificador de la hoja (desenfocado) y la pestaña."><a href="contenido/make/imagenes/m02/make-m02-21-prueba-1-bundle-del-disparador.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Bundle de salida del disparador con ID, Nombre, Descripción y Prioridad, además del número de fila, el identificador de la hoja (desenfocado) y la pestaña." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada fila nueva produce un bundle. Además de las columnas, trae el número de fila y la pestaña de origen.</figcaption></figure>

### Prueba 2: varias solicitudes

Agrega dos solicitudes más en la hoja **Solicitudes**.

| ID | Nombre | Descripción | Prioridad |
| --- | --- | --- | --- |
| SOL-002 | Carlos | Solicitud de información | Normal |
| SOL-003 | Laura | Actualización de datos | Normal |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-22-hoja-solicitudes-tres-filas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Solicitudes con tres solicitudes; las dos nuevas están resaltadas."><a href="contenido/make/imagenes/m02/make-m02-22-hoja-solicitudes-tres-filas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Solicitudes con tres solicitudes; las dos nuevas están resaltadas." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Dos solicitudes nuevas, debajo de la que ya procesamos.</figcaption></figure>

Pulsa **Run once** otra vez.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-23-prueba-2-ejecucion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario ejecutado: el disparador con una operación y Add a Row con dos."><a href="contenido/make/imagenes/m02/make-m02-23-prueba-2-ejecucion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado: el disparador con una operación y Add a Row con dos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Add a Row trabajó dos veces: una por cada solicitud nueva.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-24-prueba-2-registro.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Registro con tres solicitudes: SOL-001, SOL-002 y SOL-003."><a href="contenido/make/imagenes/m02/make-m02-24-prueba-2-registro.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Registro con tres solicitudes: SOL-001, SOL-002 y SOL-003." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Se agregaron solo las dos nuevas. SOL-001 no se repitió, porque Make ya la había procesado.</figcaption></figure>

Fíjate en lo importante: **Make recordó hasta dónde había llegado**. No volvió a procesar SOL-001.

### Prueba 3: sin solicitudes nuevas

Ahora ejecuta el escenario sin agregar nada.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-25-prueba-3-ejecucion-sin-datos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario ejecutado: el disparador tiene marca verde y burbuja 1, pero Add a Row no muestra marca ni burbuja."><a href="contenido/make/imagenes/m02/make-m02-25-prueba-3-ejecucion-sin-datos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado: el disparador tiene marca verde y burbuja 1, pero Add a Row no muestra marca ni burbuja." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El disparador revisó la hoja, pero Add a Row no se ejecutó.</figcaption></figure>

Haz clic en la burbuja del disparador.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-26-prueba-3-sin-datos-nuevos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel del disparador que dice que el módulo no devolvió datos nuevos, con 1 operación y 0 créditos."><a href="contenido/make/imagenes/m02/make-m02-26-prueba-3-sin-datos-nuevos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel del disparador que dice que el módulo no devolvió datos nuevos, con 1 operación y 0 créditos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Sin filas nuevas, el módulo no entrega bundles. Y como no hay bundles, el siguiente módulo no trabaja. No se gastó ningún crédito.</figcaption></figure>

Esto es lo que esperamos. El escenario terminó bien, solo que **no había nada que hacer**. Es importante entenderlo, porque cuando programes el escenario, la mayoría de las veces que se ejecute será así.

### Prueba 4: una solicitud después de la última ejecución

Agrega una cuarta solicitud:

| ID | Nombre | Descripción | Prioridad |
| --- | --- | --- | --- |
| SOL-004 | Diego | Error en una factura | Alta |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-27-hoja-solicitudes-cuatro-filas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Solicitudes con cuatro solicitudes; la última está resaltada."><a href="contenido/make/imagenes/m02/make-m02-27-hoja-solicitudes-cuatro-filas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Solicitudes con cuatro solicitudes; la última está resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una solicitud nueva, después de la última ejecución.</figcaption></figure>

Pulsa **Run once**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-28-prueba-4-ejecucion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario ejecutado: ambos módulos con una operación."><a href="contenido/make/imagenes/m02/make-m02-28-prueba-4-ejecucion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado: ambos módulos con una operación." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una fila nueva, una fila escrita.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-29-prueba-4-registro.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Registro con cuatro solicitudes; la última está resaltada."><a href="contenido/make/imagenes/m02/make-m02-29-prueba-4-registro.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Registro con cuatro solicitudes; la última está resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Solo se agregó SOL-004.</figcaption></figure>

### Prueba 5: cómo se generan duplicados

Ahora provocamos el problema a propósito, para que lo reconozcas si te pasa. Vamos a volver a elegir **All** como punto de inicio, lo que le dice a Make "olvida hasta dónde llegaste y empieza otra vez desde la primera fila".

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-30-duplicados-elegir-all.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana Choose where to start con la opción All seleccionada otra vez."><a href="contenido/make/imagenes/m02/make-m02-30-duplicados-elegir-all.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana Choose where to start con la opción All seleccionada otra vez." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Elegimos All de nuevo: Make olvida su marca.</figcaption></figure>

Pulsa **Save** y **Run once**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-31-duplicados-ejecucion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario ejecutado: el disparador con una operación y Add a Row con dos."><a href="contenido/make/imagenes/m02/make-m02-31-duplicados-ejecucion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado: el disparador con una operación y Add a Row con dos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Add a Row trabajó dos veces. ¿Por qué dos y no cuatro? Por el límite.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-32-duplicados-registro.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Registro con SOL-001 y SOL-002 repetidas en las filas 6 y 7."><a href="contenido/make/imagenes/m02/make-m02-32-duplicados-registro.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Registro con SOL-001 y SOL-002 repetidas en las filas 6 y 7." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Duplicados: SOL-001 y SOL-002 aparecen dos veces.</figcaption></figure>

Hay dos cosas que aprender aquí:

1. **Volver a elegir All reprocesa lo que ya estaba procesado.** Genera duplicados.
2. **Solo se repitieron dos filas, no cuatro, por el campo Limit.** El disparador procesa como máximo 2 filas por ejecución. Si en la hoja hay más, las demás esperan la siguiente ejecución.

### Un dato más: la fila que eliges se incluye

Hay otra forma de provocar el mismo problema. Si usas **Choose manually**, Make te muestra las filas que ya existen para que elijas una como punto de inicio.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-33-elegir-manualmente-lista.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Opción Choose manually con la lista de filas existentes, de la más nueva a la más antigua."><a href="contenido/make/imagenes/m02/make-m02-33-elegir-manualmente-lista.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Opción Choose manually con la lista de filas existentes, de la más nueva a la más antigua." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una lista de las filas que existen en este momento.</figcaption></figure>

Elegimos la última, SOL-004, pensando "empieza desde aquí".

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-34-elegir-manualmente-seleccion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="La fila SOL-004 seleccionada como punto de inicio."><a href="contenido/make/imagenes/m02/make-m02-34-elegir-manualmente-seleccion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: La fila SOL-004 seleccionada como punto de inicio." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Elegimos SOL-004.</figcaption></figure>

Después agregamos una solicitud nueva, SOL-005, y ejecutamos.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-35-manual-ejecucion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario ejecutado: el disparador con una operación y Add a Row con dos."><a href="contenido/make/imagenes/m02/make-m02-35-manual-ejecucion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado: el disparador con una operación y Add a Row con dos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Add a Row trabajó dos veces. Eran dos filas: la que elegimos y la nueva.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m02/make-m02-36-manual-registro.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Registro: la fila 8 repite SOL-004 y la fila 9 es SOL-005."><a href="contenido/make/imagenes/m02/make-m02-36-manual-registro.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Registro: la fila 8 repite SOL-004 y la fila 9 es SOL-005." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-004 se repitió. La fila que eliges como punto de inicio **también se procesa**.</figcaption></figure>

Es un detalle que sorprende. **La fila que eliges como inicio se incluye en el procesamiento.** Si no quieres que se repita, elige como inicio la primera fila que todavía **no** has procesado.

### ¿Cómo evitar duplicados?

- Elige **All** una sola vez, al empezar, y no lo vuelvas a tocar.
- Si necesitas cambiar el punto de inicio, piensa primero qué filas se volverán a procesar.
- Revisa siempre la hoja de destino después de una ejecución.
- Para evitar repetidos de verdad en un proceso importante, la hoja puede llevar una columna que marque las filas ya procesadas. Es un tema que veremos más adelante.

> **Recuerda:** **Add a Row no detecta duplicados.** Siempre agrega una fila, sea nueva o repetida. La protección está en cómo configuras el disparador.

---

## 7. Errores frecuentes y cómo revisarlos

| Qué ves | Qué puede estar pasando | Cómo lo revisas |
| --- | --- | --- |
| Insignia roja y mensaje sobre el punto de inicio | Falta elegir desde dónde empezar | Clic derecho en el disparador > Choose where to start |
| Make no muestra campos por columna | Los encabezados no están en la fila 1, o están en una sola celda | Revisa la fila 1 de la pestaña |
| Los datos no llegan o aparece otra hoja | Elegiste una conexión de Google equivocada | Revisa el campo Connection |
| Se procesan menos filas de las esperadas | El límite de filas por ejecución | Mira el campo Limit del disparador |
| Aparecen filas repetidas | Cambiaste el punto de inicio, o la fila elegida se incluyó | Revisa Choose where to start y el historial |
| El escenario "no hizo nada" | No había filas nuevas | Abre la burbuja del disparador: debe decir que no devolvió datos nuevos |

---

## 8. Resumen

- Para construir una automatización: **disparador** (Watch New Rows) y **acción** (Add a Row).
- Make usa los **encabezados** de la fila 1 para crear un campo por columna.
- Una **conexión** es una autorización que das tú, en Google, sin entregar tu contraseña.
- El disparador necesita un **punto de inicio**: una marca entre lo procesado y lo nuevo. Si no hay filas nuevas, no entrega nada y el siguiente módulo no trabaja.
- Los datos viajan en **bundles** y se mapean con **píldoras**. Un texto fijo, como el Estado, se escribe a mano.
- **Add a Row no detecta duplicados:** cambiar el punto de inicio puede reprocesar filas. La fila elegida como inicio se incluye.
- El campo **Limit** limita cuántas filas se procesan en cada ejecución.

## 9. Ponlo en práctica

### Desafío: agrega una columna de seguimiento

Tu equipo quiere saber también **quién atendió** cada solicitud. Agrega al flujo una columna nueva llamada **Responsable** en la pestaña Registro, que siempre diga `Sin asignar`.

**Resultado esperado:** al agregar una solicitud nueva y ejecutar el escenario, la fila nueva del Registro tiene el estado «Recibida» y el responsable «Sin asignar». Las filas anteriores quedan sin responsable, porque ya estaban escritas.

### Pistas (ábrelas de a una)

<details>
<summary>Pista 1: ¿dónde empiezo?</summary>

Primero agrega el encabezado Responsable en la fila 1 de la pestaña Registro, en la columna F. Make solo conocerá la columna nueva cuando la vuelva a leer.

</details>

<details>
<summary>Pista 2: no aparece el campo Responsable en Add a Row</summary>

Cierra y vuelve a abrir el módulo Add a Row. Make lee los encabezados cada vez que abres la ventana, así que el campo nuevo aparece debajo de Estado.

</details>

<details>
<summary>Pista 3: ¿píldora o texto fijo?</summary>

Piensa: ¿el responsable viene de la hoja de Solicitudes o lo agregamos nosotros? Si lo agregamos nosotros y siempre es igual, es un texto fijo, igual que el Estado.

</details>

<details>
<summary>Pista 4: ¿cómo compruebo que funciona sin repetir filas?</summary>

Agrega una solicitud nueva (por ejemplo SOL-006) y ejecuta con Run once, sin cambiar el punto de inicio. Debe aparecer una sola fila nueva.

</details>

### Cómo diagnosticar si algo no funciona

1. Abre la burbuja del disparador: ¿entregó filas o dijo que no había datos nuevos?
2. Si entregó filas, abre la burbuja de Add a Row y mira en qué hoja escribió.
3. Revisa la hoja de destino y compárala con la de origen.
4. Si hay filas repetidas, recuerda qué hiciste con el punto de inicio.

## 10. Comprueba lo aprendido

```quiz
? ¿Qué hace el módulo Watch New Rows?
- Agrega una fila a una hoja.
+ Vigila una hoja y entrega las filas nuevas que aparecen.
- Borra las filas ya procesadas.
> Es un disparador: avisa que hay datos nuevos y empieza el escenario.
? Ejecutas el escenario y no hay filas nuevas. ¿Qué ocurre?
- Make da un error.
+ El disparador revisa la hoja, no entrega nada y Add a Row no se ejecuta.
- Add a Row agrega una fila vacía.
> No hay bundles, así que el módulo siguiente no trabaja. No se gastan créditos de más.
? ¿Para qué sirve el punto de inicio de un disparador?
- Para elegir el color del módulo.
+ Para separar lo que ya se procesó de lo que es nuevo.
- Para borrar los datos antiguos.
> Es una marca. Cada ejecución entrega lo que quedó después de ella.
? ¿Qué pasa si vuelves a elegir All como punto de inicio en un escenario que ya procesó filas?
- Nada, Make recuerda todo.
+ Se vuelven a procesar filas que ya estaban procesadas y se generan duplicados.
- Se borra la hoja de destino.
> All significa empezar desde la primera fila. Por eso aparecieron repetidas.
? ¿Por qué el campo Estado se escribe a mano en vez de usar una píldora?
- Porque las píldoras no funcionan con texto.
+ Porque el dato no viene de la hoja de entrada y siempre es el mismo.
- Porque Make no permite píldoras en la última columna.
> Un dato que no cambia entre ejecuciones se escribe como texto fijo.
```
