# Routers, filtros y condiciones

Hasta ahora, nuestra automatización siempre hace lo mismo con todo lo que recibe. Pero imaginemos que algunas solicitudes necesitan atención inmediata y otras pueden esperar. ¿Cómo conseguimos que nuestro escenario tome caminos diferentes dependiendo de la información que recibe?

Para eso usaremos un **Router**: una pieza que reparte los datos por distintas rutas, y los **filtros**, que son las reglas que deciden por cuál ruta puede pasar cada dato. Todo con reglas claras que tú defines, sin inteligencia artificial.

**Qué vas a aprender:**

- Qué es una condición y qué es un filtro.
- Qué hace un Router y cómo se crean sus rutas.
- Comparar texto con operadores, y combinar reglas con **AND** y **OR**.
- Qué es la ruta de reserva (**fallback**).
- Por qué un Router **no** es un «si / si no»: varias rutas pueden ejecutarse a la vez.
- Comprobar los resultados con casos de prueba.

**Qué necesitas:** haber hecho el módulo 02 (o tener claro cómo funciona un disparador y un Add a Row), una cuenta de Make y una de Google. Todos los datos son inventados.

> **Sobre las capturas:** son reales, de una cuenta de práctica. Make está en inglés y Google Sheets en español. Los recuadros violetas marcan lo que debes mirar.

---

## 1. Primero, las ideas

### Una condición es una pregunta que se responde con sí o no

«¿La prioridad es Alta?» es una condición. Para cada solicitud, la respuesta es sí o no.

### Un filtro deja pasar o detiene

Un **filtro** usa una condición para decidir si los datos pueden seguir su camino. Si la respuesta es sí, pasan. Si es no, se detienen ahí.

### Un Router reparte por rutas

Un **Router** divide el escenario en varias **rutas**. Cada ruta tiene sus propios módulos y su propio filtro. Cuando llega un dato, Make revisa **cada ruta**: si el filtro de esa ruta se cumple, el dato la recorre.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Una solicitud llega a un Router que la envía por la ruta cuyo filtro coincide; la ruta de reserva recibe lo que no coincide" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m03-d1-router-y-rutas" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Un Router reparte los datos por rutas</text><rect x="70" y="170" width="170" height="70" rx="10" fill="#fff6d6" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="155" y="200" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Llega una</text><text x="155" y="228" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">solicitud</text><path d="M240 205 L330 205" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none"  marker-end="url(#p-m03-d1-router-y-rutas)"/><circle cx="385" cy="205" r="56" fill="#a8e2c0" stroke="#2d3250" stroke-width="2.8"/><text x="385" y="211" font-size="26" text-anchor="middle" fill="#2d3250" font-weight="700">Router</text><path d="M435 190 L520 118" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none"  marker-end="url(#p-m03-d1-router-y-rutas)"/><rect x="524" y="90" width="190" height="56" rx="10" fill="#ffeee6" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="619" y="114" font-size="19" text-anchor="middle" fill="#c0562d" font-weight="400">filtro:</text><text x="619" y="136" font-size="21" text-anchor="middle" fill="#2d3250" font-weight="400">Prioridad = Alta</text><path d="M716 118 L770 118" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none"  marker-end="url(#p-m03-d1-router-y-rutas)"/><rect x="774" y="96" width="110" height="44" rx="10" fill="#ffffff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="829" y="126" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">Urgentes</text><path d="M435 205 L520 218" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none"  marker-end="url(#p-m03-d1-router-y-rutas)"/><rect x="524" y="190" width="190" height="56" rx="10" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="619" y="214" font-size="19" text-anchor="middle" fill="#1f8f5f" font-weight="400">filtro:</text><text x="619" y="236" font-size="21" text-anchor="middle" fill="#2d3250" font-weight="400">Prioridad = Normal</text><path d="M716 218 L770 218" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none"  marker-end="url(#p-m03-d1-router-y-rutas)"/><rect x="774" y="196" width="110" height="44" rx="10" fill="#ffffff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="829" y="226" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">Normales</text><path d="M435 225 L520 318" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none"  marker-end="url(#p-m03-d1-router-y-rutas)"/><rect x="524" y="290" width="190" height="56" rx="10" fill="#f4efff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="619" y="314" font-size="19" text-anchor="middle" fill="#7b5fd6" font-weight="400">filtro:</text><text x="619" y="336" font-size="21" text-anchor="middle" fill="#2d3250" font-weight="400">ninguna coincide</text><path d="M716 318 L770 318" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none"  marker-end="url(#p-m03-d1-router-y-rutas)"/><rect x="774" y="296" width="110" height="44" rx="10" fill="#ffffff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="829" y="326" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">Pendientes</text><text x="619" y="362" font-size="21" text-anchor="middle" fill="#7b5fd6" font-weight="400">La última es la ruta de reserva (fallback):</text><text x="619" y="390" font-size="21" text-anchor="middle" fill="#7b5fd6" font-weight="400">solo actúa si ninguna otra coincidió.</text></svg><a href="contenido/make/imagenes/diagramas/m03-d1-router-y-rutas.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Una solicitud llega a un Router. Tres rutas con filtros: Prioridad igual a Alta va a Urgentes, Prioridad igual a Normal va a Normales y la ruta de reserva recibe lo que no coincide con ninguna." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Router reparte cada solicitud según el filtro de cada ruta. La ruta de reserva (fallback) solo actúa cuando ninguna otra coincidió.</figcaption></figure>

### Un Router no es un «si / si no»

Es importante entender esto desde el principio. En muchos lenguajes, un «si / si no» elige **una sola** opción. El Router de Make **revisa todas las rutas** y ejecuta **todas las que cumplan su filtro**. Si dos filtros coinciden, se ejecutan las dos. Lo comprobaremos con una prueba más adelante.

(Make también ofrece un módulo llamado **If-else**, que sirve para dividir el flujo con condiciones y luego volver a unirlo. En este apunte nos concentramos en el Router, que es el más usado.)

---

## 2. El caso: clasificar solicitudes

Seguimos con la empresa ficticia que recibe solicitudes de atención. Ahora queremos clasificarlas en tres grupos:

- **Urgentes:** prioridad Alta.
- **Normales:** prioridad Normal.
- **Pendientes de clasificar:** todo lo demás (sin prioridad, o con una prioridad que no reconocemos).

Esta vez construimos un **escenario independiente**, con su propio libro de cálculo, para no tocar el del módulo 02.

### Prepara el libro

Crea una hoja de cálculo llamada **Practica Make - Clasificacion** con cuatro pestañas: `Solicitudes`, `Urgentes`, `Normales` y `Pendientes`.

| Pestaña | Encabezados (fila 1) |
| --- | --- |
| Solicitudes | ID, Nombre, Descripción, Prioridad |
| Urgentes, Normales y Pendientes | ID, Nombre, Descripción, Prioridad, Ruta |

La columna **Ruta** dirá por qué ruta pasó cada solicitud. Nos servirá para comprobar los resultados.

En `Solicitudes` escribe cuatro casos de prueba. Fíjate que cada uno está pensado para probar algo distinto:

| ID | Nombre | Descripción | Prioridad | Qué probamos |
| --- | --- | --- | --- | --- |
| SOL-101 | Ana | No puedo entrar al sistema | Alta | Una solicitud urgente |
| SOL-102 | Carlos | Consulta de horario | Normal | Una solicitud normal |
| SOL-103 | Laura | Cambio de direccion | *(vacía)* | Una solicitud **sin prioridad** |
| SOL-104 | Diego | Error en una factura | Critica | Una prioridad **desconocida** |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-01-hoja-solicitudes-cuatro-casos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Solicitudes con cuatro casos de prueba resaltados. La celda de prioridad de SOL-103 está vacía."><a href="contenido/make/imagenes/m03/make-m03-01-hoja-solicitudes-cuatro-casos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Solicitudes con cuatro casos de prueba resaltados. La celda de prioridad de SOL-103 está vacía." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los cuatro casos de prueba. Uno no tiene prioridad y otro tiene una prioridad que no existe en nuestras reglas.</figcaption></figure>

---

## 3. El disparador

Crea un escenario llamado `Practica Make - Router y filtros`. Agrega **Google Sheets > Watch New Rows** como en el módulo 02: tu conexión, el archivo `Practica Make - Clasificacion` y la pestaña `Solicitudes`.

Esta vez cambiamos un valor: pon **Limit** en `10`. Recuerda que es el máximo de filas por ejecución, y queremos procesar nuestras cuatro de una vez.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-02-disparador-limite.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Watch New Rows con la pestaña Solicitudes elegida y el campo Limit con el valor 10, resaltados."><a href="contenido/make/imagenes/m03/make-m03-02-disparador-limite.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Watch New Rows con la pestaña Solicitudes elegida y el campo Limit con el valor 10, resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El disparador. Cambiamos el límite de 2 a 10.</figcaption></figure>

Guarda el módulo y elige el punto de inicio: clic derecho sobre el módulo > **Choose where to start** > **All**. Si no recuerdas por qué, repasa el módulo 02.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-03-disparador-listo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="808" height="374" alt="Escenario con el módulo Watch New Rows ya configurado y su botón para agregar el siguiente módulo."><a href="contenido/make/imagenes/m03/make-m03-03-disparador-listo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario con el módulo Watch New Rows ya configurado y su botón para agregar el siguiente módulo." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El disparador listo, sin avisos.</figcaption></figure>

---

## 4. Agrega el Router

Haz clic en el **+** a la derecha del disparador. Busca la aplicación **Flow Control** y elige el módulo **Router**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-04-router-dos-rutas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario con el disparador, el Router y dos rutas numeradas 1st y 2nd."><a href="contenido/make/imagenes/m03/make-m03-04-router-dos-rutas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario con el disparador, el Router y dos rutas numeradas 1st y 2nd." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Router nace con dos rutas, marcadas como 1st y 2nd. Cada ruta termina en un módulo vacío que agregaremos.</figcaption></figure>

Necesitamos tres rutas. Haz clic derecho sobre el Router y elige **Add route**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-05-menu-agregar-ruta.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Menú del Router con la opción Add route resaltada."><a href="contenido/make/imagenes/m03/make-m03-05-menu-agregar-ruta.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Menú del Router con la opción Add route resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El menú del Router. También tiene Order routes, para cambiar el orden de las rutas.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-06-router-tres-rutas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Router con tres rutas numeradas 1st, 2nd y 3rd resaltadas."><a href="contenido/make/imagenes/m03/make-m03-06-router-tres-rutas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Router con tres rutas numeradas 1st, 2nd y 3rd resaltadas." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tres rutas. Si el escenario se ve muy grande, puedes alejar el lienzo con la rueda del mouse.</figcaption></figure>

---

## 5. Los módulos de cada ruta

Cada ruta necesita su propio módulo **Google Sheets > Add a Row**.

1. En la **ruta 1**, agrega Add a Row. Elige el archivo `Practica Make - Clasificacion` y la pestaña **Urgentes**.
2. En la **ruta 2**, lo mismo, con la pestaña **Normales**.
3. En la **ruta 3**, con la pestaña **Pendientes**.

> **Cuidado con la conexión.** Make recuerda la última que usaste, pero revísala siempre en el campo Connection.

Mapea los campos con píldoras, igual que en el módulo 02. Haz clic en un campo y elige la píldora del disparador que tiene el mismo nombre.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-07-ruta-1-panel-de-pildoras.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Módulo Add a Row de la ruta 1 con el campo ID enfocado y el panel de píldoras abierto con la píldora ID resaltada."><a href="contenido/make/imagenes/m03/make-m03-07-ruta-1-panel-de-pildoras.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Módulo Add a Row de la ruta 1 con el campo ID enfocado y el panel de píldoras abierto con la píldora ID resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El panel de píldoras muestra lo que entrega el disparador. Aquí no hay nada nuevo: lo mismo que en el módulo anterior.</figcaption></figure>

En el campo **Ruta** escribe un texto fijo: `Urgente` en la ruta 1, `Normal` en la ruta 2 y `Pendiente de clasificar` en la ruta 3.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-08-ruta-1-mapeo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Cuatro campos con píldoras y el campo Ruta con el texto Urgente."><a href="contenido/make/imagenes/m03/make-m03-08-ruta-1-mapeo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Cuatro campos con píldoras y el campo Ruta con el texto Urgente." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Mapeo de la ruta 1: cuatro píldoras y un texto fijo.</figcaption></figure>

Guarda cada módulo.

---

## 6. Los filtros: lo central

Ahora definimos **cuándo** pasa una solicitud por cada ruta. El filtro se configura en el pequeño círculo que está sobre la línea que une el Router con el módulo de cada ruta. Haz clic en el de la ruta 1.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-09-filtro-vacio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana Set up a filter con tres zonas resaltadas: etiqueta, opción de fallback y condición."><a href="contenido/make/imagenes/m03/make-m03-09-filtro-vacio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana Set up a filter con tres zonas resaltadas: etiqueta, opción de fallback y condición." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ventana del filtro tiene tres zonas: una etiqueta, la opción de ruta de reserva y la condición.</figcaption></figure>

- **Label:** un nombre para la ruta. Ayuda a leer el escenario.
- **Fallback:** si la ruta es la de reserva. Lo veremos en un momento.
- **Condition:** la regla. Tiene tres partes: *qué dato comparo*, *cómo lo comparo* y *con qué lo comparo*.

### Primera ruta: Urgentes

En **Label** escribe `Urgentes`. Después haz clic en el primer campo de la condición. Se abre el panel de píldoras: elige la píldora **Prioridad (D)**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-10-filtro-condicion-con-pildoras.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel de píldoras junto al campo de la condición, con la píldora Prioridad resaltada."><a href="contenido/make/imagenes/m03/make-m03-10-filtro-condicion-con-pildoras.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel de píldoras junto al campo de la condición, con la píldora Prioridad resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Elegimos qué dato comparar: la prioridad de cada solicitud.</figcaption></figure>

El **operador** viene por defecto como **Equal to** (igual a), de la familia de operadores de texto. En el último campo escribe `Alta`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-11-filtro-prioridad-igual-alta.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Condición completa: la píldora Prioridad, el operador igual a y el valor Alta."><a href="contenido/make/imagenes/m03/make-m03-11-filtro-prioridad-igual-alta.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Condición completa: la píldora Prioridad, el operador igual a y el valor Alta." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La regla se lee así: «la prioridad es igual a Alta».</figcaption></figure>

### Combinar reglas: OR y AND

Una sola regla a veces no alcanza. Imagina que tu equipo a veces escribe `Urgente` en vez de `Alta`. Querríamos que cualquiera de las dos pase por la ruta de urgentes. Eso se resuelve con una regla **OR** («o»).

Haz clic en **Add OR rule**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-12-filtro-regla-or.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Segunda regla agregada debajo de la primera, separadas por la palabra or."><a href="contenido/make/imagenes/m03/make-m03-12-filtro-regla-or.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Segunda regla agregada debajo de la primera, separadas por la palabra or." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Aparece un segundo bloque, unido al primero por la palabra «or».</figcaption></figure>

Completa la segunda regla: píldora **Prioridad (D)**, operador «igual a» y el valor `Urgente`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-13-filtro-or-completo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Dos reglas unidas por or: Prioridad igual a Alta, o Prioridad igual a Urgente."><a href="contenido/make/imagenes/m03/make-m03-13-filtro-or-completo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Dos reglas unidas por or: Prioridad igual a Alta, o Prioridad igual a Urgente." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ruta de urgentes deja pasar las solicitudes cuya prioridad sea Alta **o** Urgente.</figcaption></figure>

Hay otra forma de combinar reglas: **AND** («y»). Con AND, deben cumplirse **todas** las reglas a la vez.

| | Significa | Ejemplo |
| --- | --- | --- |
| **OR** | Basta con que se cumpla **una** | Prioridad es Alta **o** Prioridad es Urgente |
| **AND** | Deben cumplirse **todas** | Prioridad es Alta **y** la descripción contiene «factura» |

Pulsa **Save**.

### Segunda ruta: Normales

Haz lo mismo en la ruta 2: etiqueta `Normales`, píldora Prioridad, igual a `Normal`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-14-filtro-normales.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Filtro de la ruta 2: Prioridad igual a Normal."><a href="contenido/make/imagenes/m03/make-m03-14-filtro-normales.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Filtro de la ruta 2: Prioridad igual a Normal." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una sola regla.</figcaption></figure>

### Tercera ruta: la ruta de reserva (fallback)

Pensemos en la solicitud sin prioridad (SOL-103) y en la que tiene una prioridad desconocida (SOL-104). No cumplen ni el filtro de Urgentes ni el de Normales. Si no hacemos nada, **se perderían sin avisar**.

La solución es una **ruta de reserva** o **fallback**: una ruta que solo se ejecuta cuando **ninguna otra** coincidió. Haz clic en el filtro de la ruta 3, escribe la etiqueta `Pendientes de clasificar` y en la pregunta de fallback elige **Yes**. Esta ruta no necesita ninguna condición.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-15-ruta-fallback.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Ventana de filtro de la ruta 3 con la etiqueta Pendientes de clasificar y la opción Yes de fallback resaltada."><a href="contenido/make/imagenes/m03/make-m03-15-ruta-fallback.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana de filtro de la ruta 3 con la etiqueta Pendientes de clasificar y la opción Yes de fallback resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Marcamos la ruta como fallback. Un Router solo puede tener una ruta de reserva.</figcaption></figure>

Guarda el filtro y el escenario. Ahora las rutas muestran su etiqueta:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-16-router-con-etiquetas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Router con las tres rutas etiquetadas: Urgentes, Normales y fallback Pendientes."><a href="contenido/make/imagenes/m03/make-m03-16-router-con-etiquetas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Router con las tres rutas etiquetadas: Urgentes, Normales y fallback Pendientes." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El escenario completo. Un vistazo basta para entender qué hace cada ruta.</figcaption></figure>

---

## 7. Pruebas

### Prueba 1: los cuatro casos

Pulsa **Run once**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-17-ejecucion-cuatro-casos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario ejecutado. Las etiquetas muestran Urgentes con 1, Normales con 1 y el módulo de la ruta 3 con 2 operaciones."><a href="contenido/make/imagenes/m03/make-m03-17-ejecucion-cuatro-casos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado. Las etiquetas muestran Urgentes con 1, Normales con 1 y el módulo de la ruta 3 con 2 operaciones." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El disparador entregó cuatro solicitudes. La ruta Urgentes procesó 1, Normales procesó 1 y Pendientes procesó 2.</figcaption></figure>

Los números cuadran con lo esperado. Ahora **mira cada hoja**. Recuerda: una marca verde no demuestra que el resultado sea correcto.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-18-urgentes-resultado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="942" height="436" alt="Pestaña Urgentes con la fila SOL-101 y la ruta Urgente."><a href="contenido/make/imagenes/m03/make-m03-18-urgentes-resultado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Urgentes con la fila SOL-101 y la ruta Urgente." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-101, prioridad Alta: va a Urgentes.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-19-normales-resultado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="942" height="436" alt="Pestaña Normales con la fila SOL-102 y la ruta Normal."><a href="contenido/make/imagenes/m03/make-m03-19-normales-resultado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Normales con la fila SOL-102 y la ruta Normal." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-102, prioridad Normal: va a Normales.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-20-pendientes-resultado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Pendientes con las filas SOL-103 y SOL-104, con la ruta Pendiente de clasificar."><a href="contenido/make/imagenes/m03/make-m03-20-pendientes-resultado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Pendientes con las filas SOL-103 y SOL-104, con la ruta Pendiente de clasificar." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-103 (sin prioridad) y SOL-104 (prioridad desconocida) caen en la ruta de reserva.</figcaption></figure>

| Solicitud | Prioridad | Ruta esperada | Ruta real |
| --- | --- | --- | --- |
| SOL-101 | Alta | Urgentes | Urgentes |
| SOL-102 | Normal | Normales | Normales |
| SOL-103 | *(vacía)* | Pendientes | Pendientes |
| SOL-104 | Critica | Pendientes | Pendientes |

Gracias al fallback, ninguna solicitud se perdió.

### Prueba 2 (aislada): una solicitud que coincide con varias rutas

Ahora comprobemos lo que dijimos: que un Router no es un «si / si no». Para esta prueba hacemos un cambio **temporal**, que después deshacemos.

Agrega una solicitud más en la hoja:

| ID | Nombre | Descripción | Prioridad |
| --- | --- | --- | --- |
| SOL-105 | Marta | Cobro duplicado en la factura | Alta |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-21-hoja-con-sol-105.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="942" height="436" alt="Pestaña Solicitudes con SOL-105 resaltada."><a href="contenido/make/imagenes/m03/make-m03-21-hoja-con-sol-105.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Solicitudes con SOL-105 resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una solicitud con prioridad Alta cuya descripción menciona la palabra factura.</figcaption></figure>

Abre el filtro de la ruta 2 (Normales) y agrega una regla OR: que **también** deje pasar las solicitudes cuya descripción contenga la palabra «factura». Para eso hay que cambiar el operador. Haz clic en la lista de operadores.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-22-lista-de-operadores.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de operadores con las opciones Exists, Does not exist y los operadores de texto."><a href="contenido/make/imagenes/m03/make-m03-22-lista-de-operadores.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de operadores con las opciones Exists, Does not exist y los operadores de texto." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Make ofrece muchos operadores. Hay un buscador para encontrar el que necesitas.</figcaption></figure>

Escribe `contain` en el buscador y elige **Contains (case insensitive)**: «contiene», sin distinguir mayúsculas.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-23-buscar-operador-contiene.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Buscador de operadores con la palabra contain y la opción Contains (case insensitive) resaltada."><a href="contenido/make/imagenes/m03/make-m03-23-buscar-operador-contiene.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Buscador de operadores con la palabra contain y la opción Contains (case insensitive) resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Compara texto sin importar si está en mayúsculas o minúsculas.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-24-filtro-temporal-contiene.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Filtro de Normales con dos reglas: Prioridad igual a Normal, o Descripción contiene factura."><a href="contenido/make/imagenes/m03/make-m03-24-filtro-temporal-contiene.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Filtro de Normales con dos reglas: Prioridad igual a Normal, o Descripción contiene factura." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El filtro temporal de Normales.</figcaption></figure>

Guarda y pulsa **Run once**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-25-ejecucion-coincidencia-multiple.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Escenario ejecutado. Urgentes y Normales muestran una operación cada una y el módulo de la ruta 3 no se ejecutó."><a href="contenido/make/imagenes/m03/make-m03-25-ejecucion-coincidencia-multiple.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado. Urgentes y Normales muestran una operación cada una y el módulo de la ruta 3 no se ejecutó." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Dos rutas se ejecutaron y el fallback no.</figcaption></figure>

Revisa las hojas:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-26-urgentes-con-105.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="942" height="436" alt="Pestaña Urgentes con SOL-101 y SOL-105."><a href="contenido/make/imagenes/m03/make-m03-26-urgentes-con-105.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Urgentes con SOL-101 y SOL-105." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-105 llegó a Urgentes, porque su prioridad es Alta.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-27-normales-con-105.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="942" height="436" alt="Pestaña Normales con SOL-102 y SOL-105."><a href="contenido/make/imagenes/m03/make-m03-27-normales-con-105.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Normales con SOL-102 y SOL-105." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Y también a Normales, porque su descripción contiene «factura».</figcaption></figure>

**SOL-105 se escribió dos veces**, una en cada ruta. Es exactamente lo que significa que un Router no sea excluyente. Y el fallback no se ejecutó, porque sí hubo rutas que coincidieron.

Ahora **deshacemos el cambio**: vuelve al filtro de Normales, borra la regla temporal con la X y deja solo «Prioridad igual a Normal». Guarda. Así el escenario vuelve a su configuración correcta.

### Mostrar una regla AND

Para ver cómo se configura una regla AND sin cambiar nada, abre un filtro y pulsa **Add AND rule**. Aparece un segundo bloque unido por la palabra «and». **Cancela sin guardar** si no quieres conservarlo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m03/make-m03-28-filtro-regla-and.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Filtro con dos reglas unidas por la palabra and: Prioridad igual a Normal, y una segunda regla vacía."><a href="contenido/make/imagenes/m03/make-m03-28-filtro-regla-and.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Filtro con dos reglas unidas por la palabra and: Prioridad igual a Normal, y una segunda regla vacía." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Con AND deben cumplirse las dos reglas. Aquí solo mostramos cómo se arma; no lo ejecutamos.</figcaption></figure>

---

## 8. Errores frecuentes y cómo revisarlos

| Qué ves | Qué puede estar pasando | Cómo lo revisas |
| --- | --- | --- |
| Una solicitud no aparece en ninguna hoja | Ningún filtro coincidió y no hay ruta de reserva | Agrega una ruta fallback |
| Una solicitud aparece en dos hojas | Dos filtros coinciden: el Router no es excluyente | Revisa las condiciones de cada ruta |
| Una solicitud que debería pasar se detiene | El texto no es idéntico: una mayúscula distinta o un espacio de más | Abre la burbuja del disparador y mira el valor exacto que llegó; revisa si tu operador distingue mayúsculas (los de texto vienen en pares, con y sin «case insensitive») |
| Los filtros no se ven | El círculo está sobre la línea, a veces pequeño | Aleja o acerca el lienzo |
| Hay filas repetidas | Cambiaste el punto de inicio del disparador | Repasa el módulo 02 |

---

## 9. Resumen

- Una **condición** es una pregunta de sí o no; un **filtro** deja pasar o detiene según esa condición.
- Un **Router** divide el escenario en rutas. Cada ruta tiene su filtro.
- Una condición tiene tres partes: el dato (una píldora), el **operador** y el valor con el que se compara.
- **OR**: basta con que se cumpla una regla. **AND**: deben cumplirse todas.
- La ruta de reserva (**fallback**) recibe lo que ninguna otra ruta aceptó. Evita que se pierdan datos.
- Un Router **no es excluyente**: si varios filtros coinciden, se ejecutan varias rutas.
- Revisa siempre las hojas de destino, no solo las marcas verdes.

## 10. Ponlo en práctica

### Desafío: una cuarta categoría

La empresa decide que las solicitudes con prioridad **Baja** también deben registrarse, en una pestaña propia llamada `Bajas`.

**Resultado esperado:** al agregar una solicitud con prioridad `Baja` y ejecutar el escenario, aparece **solo** en la pestaña `Bajas`, y no en Pendientes.

### Pistas (ábrelas de a una)

<details>
<summary>Pista 1: ¿qué necesito crear?</summary>

Una pestaña nueva con los mismos encabezados que las demás, y una ruta nueva en el Router con su propio módulo Add a Row.

</details>

<details>
<summary>Pista 2: la solicitud sigue apareciendo en Pendientes</summary>

El fallback solo actúa si **ninguna** otra ruta coincidió. Si tu nueva ruta aún no tiene filtro, deja pasar todo. Revisa su condición.

</details>

<details>
<summary>Pista 3: ¿qué operador uso?</summary>

Igual que en Urgentes y Normales: la píldora Prioridad, el operador «igual a» y el valor Baja.

</details>

<details>
<summary>Pista 4: ¿cómo compruebo que no se pierde nada?</summary>

Prueba también una solicitud con una prioridad rara, como «Media». Debe llegar a Pendientes.

</details>

### Cómo diagnosticar si algo no funciona

1. Mira las etiquetas de las rutas después de **Run once**: ¿cuántas operaciones tuvo cada una?
2. Abre el filtro de la ruta que no se comportó como esperabas y relee la condición en voz alta.
3. Abre la burbuja del disparador y mira el valor exacto de la prioridad que llegó.
4. Compara con la hoja de destino.

## 11. Comprueba lo aprendido

```quiz
? ¿Qué hace un filtro en una ruta del Router?
- Cambia el nombre de la hoja de destino.
+ Deja pasar los datos solo si cumplen su condición.
- Borra los datos que no cumplen.
> Si no se cumple la condición, los datos simplemente no recorren esa ruta.
? Una solicitud cumple los filtros de dos rutas distintas. ¿Qué ocurre?
- Make elige solo la primera ruta.
+ Se ejecutan las dos rutas.
- Make muestra un error.
> El Router revisa todas las rutas y ejecuta todas las que coinciden. No es excluyente.
? ¿Para qué sirve la ruta de reserva (fallback)?
- Para ejecutar siempre, sin importar los filtros.
+ Para recibir lo que ninguna otra ruta aceptó, así nada se pierde.
- Para repetir las filas que ya se procesaron.
> Solo se ejecuta cuando ninguna otra ruta coincidió.
? Quieres que una ruta acepte las prioridades «Alta» o «Urgente». ¿Qué usas?
- Una regla AND.
+ Una regla OR.
- Dos Routers seguidos.
> OR significa que basta con que se cumpla una de las reglas.
? ¿Qué significa «case insensitive» junto a un operador de texto, como en Contains (case insensitive)?
- Que el operador solo funciona con números.
+ Que compara el texto sin distinguir mayúsculas de minúsculas.
- Que el operador está desactivado.
> Los operadores de texto vienen en versiones con y sin distinción de mayúsculas. Elige la que corresponda a tu caso.
```
