# Conociendo Make

¿Te ha pasado que cada día copias información de un lugar a otro? Un dato llega por correo, lo copias a una hoja, avisas a alguien y vuelves a empezar mañana. Son tareas simples, pero se repiten, consumen tiempo y es fácil equivocarse.

**Make** es una herramienta pensada para que esas tareas las haga una máquina por ti, y sin escribir código. En este primer apunte vamos a conocer qué es, qué problemas resuelve y cómo se ve por dentro. Todavía no vamos a construir nada: primero queremos que te sientas cómodo en el lugar donde vas a trabajar.

**Qué vas a aprender:**

- Qué significa automatizar y cuándo conviene hacerlo.
- Qué es Make y cómo se organiza (organizaciones, equipos, escenarios y conexiones).
- Qué diferencia hay entre una automatización tradicional y una que usa inteligencia artificial.
- Cómo se cuentan los créditos y por qué importan.
- Qué cuidados de seguridad conviene tener desde el primer día.

> **Sobre la información de planes:** los datos de créditos y límites que verás aquí se revisaron en las páginas oficiales de Make el 25 de noviembre de 2026. Los planes cambian con el tiempo y no todas las cuentas tienen las mismas funciones. Si algo no coincide con lo que ves en tu pantalla, confía en tu pantalla y en la información oficial.

---

## 1. ¿Qué es Make?

Make es una plataforma **visual** para conectar aplicaciones entre sí. En vez de programar, armas un recorrido dibujando piezas en una pantalla: una pieza recibe un dato, otra lo transforma y otra lo guarda o lo envía.

Piensa en una línea de montaje. Cada estación hace una sola tarea pequeña, y el producto pasa de una a otra. En Make, cada estación es un **módulo**, y el recorrido completo se llama **escenario**.

Con Make puedes, por ejemplo:

- Guardar en una hoja de cálculo cada solicitud que llega.
- Avisar por correo cuando algo importante cambia.
- Ordenar información que llega desordenada.
- Pedirle a un modelo de inteligencia artificial que clasifique textos.

No necesitas saber programar. Sí necesitas pensar con orden: qué dato llega, qué quieres hacer con él y dónde debe terminar. Esa forma de pensar es justamente lo que vamos a practicar en este Cuaderno.

---

## 2. ¿Qué significa automatizar?

**Automatizar es dejar que una máquina siga por ti un procedimiento que ya conoces.** No es adivinar ni decidir cosas nuevas: es repetir, sin cansarse, los pasos que tú le explicaste.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Cuatro pasos manuales frente a un escenario de Make que los hace solo" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m00-d1-a-mano-o-con-make" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Una tarea repetida, de dos maneras</text><text x="230" y="92" font-size="30" text-anchor="middle" fill="#c0562d" font-weight="700">A mano</text><rect x="110" y="108" width="240" height="48" rx="12" fill="#ffeee6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="230" y="140" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="400">Abres el correo</text><path d="M230 156 L230 170" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d1-a-mano-o-con-make)"/><rect x="110" y="170" width="240" height="48" rx="12" fill="#ffeee6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="230" y="202" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="400">Copias los datos</text><path d="M230 218 L230 232" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d1-a-mano-o-con-make)"/><rect x="110" y="232" width="240" height="48" rx="12" fill="#ffeee6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="230" y="264" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="400">Los pegas en la hoja</text><path d="M230 280 L230 294" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d1-a-mano-o-con-make)"/><rect x="110" y="294" width="240" height="48" rx="12" fill="#ffeee6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="230" y="326" font-size="23" text-anchor="middle" fill="#2d3250" font-weight="400">Avisas a alguien</text><text x="230" y="372" font-size="24" text-anchor="middle" fill="#c0562d" font-weight="400">Lo haces tú, cada vez</text><text x="670" y="92" font-size="30" text-anchor="middle" fill="#1f8f5f" font-weight="700">Con Make</text><rect x="520" y="112" width="300" height="58" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="670" y="148" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Llega una solicitud</text><path d="M670 170 L670 204" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d1-a-mano-o-con-make)"/><circle cx="670" cy="248" r="42" fill="#cdbff5" stroke="#2d3250" stroke-width="2.8"/><text x="670" y="256" font-size="26" text-anchor="middle" fill="#2d3250" font-weight="700">Make</text><path d="M670 292 L670 326" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d1-a-mano-o-con-make)"/><rect x="520" y="328" width="300" height="52" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="670" y="362" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Hoja y aviso listos</text><text x="670" y="404" font-size="24" text-anchor="middle" fill="#1f8f5f" font-weight="400">Tú solo revisas el resultado</text></svg><a href="contenido/make/imagenes/diagramas/m00-d1-a-mano-o-con-make.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Dos columnas: a la izquierda cuatro pasos manuales uno bajo otro; a la derecha una solicitud que entra a Make y produce una hoja y un aviso listos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La misma tarea de dos maneras. A mano, la haces tú cada vez. Con Make, tú solo revisas el resultado.</figcaption></figure>

### Ejemplos de la vida diaria

- Guardar en una carpeta los archivos adjuntos que te llegan por correo.
- Anotar automáticamente en una hoja cada gasto que registras.
- Recibir un mensaje cada mañana con las tareas del día.

### Ejemplos del trabajo

- Registrar en una hoja las solicitudes de atención que llegan.
- Separar las solicitudes urgentes de las normales.
- Avisar al equipo cuando entra una orden de compra.

### ¿Manual o automatizado?

| | Proceso manual | Proceso automatizado |
| --- | --- | --- |
| Quién lo hace | Una persona, cada vez | Make, cada vez que se cumple una condición |
| Constancia | Depende del día y del cansancio | Siempre sigue los mismos pasos |
| Errores | Son frecuentes al copiar y pegar | Son raros, pero se repiten si el diseño está mal |
| Si el trabajo crece | Hace falta más tiempo de personas | Casi no cambia el esfuerzo |
| Quién supervisa | La misma persona que lo hace | Una persona que revisa resultados |

Fíjate en la fila de los errores. Una automatización mal diseñada repite el mismo error muchas veces, y muy rápido. Por eso en este Cuaderno siempre vamos a **comprobar el resultado** y no solo confiar en que "salió en verde".

### ¿Cuándo conviene automatizar?

Una tarea es buena candidata si cumple casi todo esto:

1. Se repite con frecuencia.
2. Siempre sigue los mismos pasos.
3. Trabaja con información digital.
4. Tiene un resultado claro que puedes comprobar.

Si una tarea ocurre una sola vez, o cada caso exige mucho criterio personal, probablemente es mejor hacerla a mano.

---

## 3. Automatización tradicional y automatización con IA

Hay dos formas de decidir qué hacer con un dato.

**Automatización tradicional.** Tú escribes reglas fijas: "si la prioridad es Alta, envíala a la hoja Urgentes". Siempre que llegue el mismo dato, el resultado será el mismo. Es predecible y fácil de comprobar.

**Automatización con inteligencia artificial.** Se usa cuando la información llega como texto libre y no hay una regla simple. Por ejemplo, alguien escribe "no puedo entrar al sistema desde ayer". Un modelo de lenguaje puede **proponer** una categoría y una prioridad.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Una regla fija decide siempre igual; un modelo de IA propone y se valida" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m00-d2-tradicional-vs-ia" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Automatización tradicional y con IA</text><text x="450" y="88" font-size="26" text-anchor="middle" fill="#7b5fd6" font-weight="700">Tradicional: una regla fija decide</text><rect x="90" y="104" width="190" height="62" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="185" y="142" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Prioridad: Alta</text><path d="M280 135 L350 135" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d2-tradicional-vs-ia)"/><rect x="350" y="104" width="200" height="62" rx="12" fill="#f4efff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="450" y="130" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Si es Alta,</text><text x="450" y="154" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">va a Urgentes</text><path d="M550 135 L620 135" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d2-tradicional-vs-ia)"/><rect x="620" y="104" width="190" height="62" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="715" y="142" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Hoja Urgentes</text><text x="450" y="204" font-size="22" text-anchor="middle" fill="#5a4aa6" font-weight="400">Mismo dato, mismo resultado, siempre.</text><text x="450" y="262" font-size="26" text-anchor="middle" fill="#1f8f5f" font-weight="700">Con IA: un modelo propone</text><rect x="90" y="276" width="190" height="62" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="185" y="302" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Texto libre:</text><text x="185" y="328" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">no puedo entrar</text><path d="M280 307 L330 307" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d2-tradicional-vs-ia)"/><rect x="330" y="276" width="240" height="62" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="450" y="302" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">El modelo propone</text><text x="450" y="328" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">categoría y prioridad</text><path d="M570 307 L620 307" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d2-tradicional-vs-ia)"/><rect x="620" y="276" width="190" height="62" rx="12" fill="#f4efff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="715" y="302" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Una regla o una</text><text x="715" y="328" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">persona valida</text><text x="450" y="384" font-size="22" text-anchor="middle" fill="#1f8f5f" font-weight="400">Puede equivocarse: por eso se revisa lo importante.</text></svg><a href="contenido/make/imagenes/diagramas/m00-d2-tradicional-vs-ia.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Dos recorridos: arriba un dato con una regla fija que lo envía a una hoja; abajo un texto libre que pasa por un modelo de IA y luego por una regla o una persona que valida." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una regla fija decide siempre igual. Un modelo de IA propone, y lo importante se valida.</figcaption></figure>

La palabra clave es **proponer**. Un modelo puede equivocarse o inventar. Por eso, cuando usemos IA, siempre habrá una regla o una persona que revise. Lo veremos con calma en el módulo 04.

---

## 4. Cómo acceder a Make

Para empezar necesitas una cuenta. Estos son los pasos generales:

1. Entra al sitio oficial de Make (make.com).
2. Elige la opción para crear una cuenta o para iniciar sesión.
3. Puedes registrarte con tu correo o con una cuenta de Google. Make te puede pedir confirmar tu correo y completar una verificación de seguridad.
4. Al entrar verás tu panel. La dirección del sitio incluye una zona (por ejemplo, `us2.make.com` o `eu1.make.com`). Es normal que la tuya sea distinta.

> **Importante:** nunca compartas tu contraseña con nadie, ni siquiera con quien te ayuda a aprender. Si alguien te acompaña, es mejor que tú escribas tus datos de acceso.

En este Cuaderno partimos con la sesión ya iniciada. Si tu pantalla se ve un poco distinta a las capturas, no te preocupes: Make mejora su diseño con frecuencia, pero las secciones y los nombres se mantienen.

---

## 5. Un recorrido por Make

No vamos a ver cada botón. Solo vamos a conocer los lugares que necesitamos para empezar.

### 5.1 El panel principal

Al entrar llegas al **panel de tu organización**. Es como la recepción: te muestra un resumen de lo que está pasando.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-01-panel-principal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Panel principal de Make con el menú de la izquierda, el botón Create scenario arriba y cuatro indicadores de uso resaltados."><a href="contenido/make/imagenes/m00/make-m00-01-panel-principal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Panel principal de Make con el menú de la izquierda, el botón Create scenario arriba y cuatro indicadores de uso resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El panel principal. A la izquierda, el menú. Arriba, el botón para crear un escenario. Abajo, cuatro indicadores de uso.</figcaption></figure>

Mira lo que está resaltado:

- **Menú de la izquierda:** de aquí te mueves a las secciones principales.
- **Create scenario:** el botón para crear tu primera automatización. Lo usaremos en el módulo 01.
- **Los cuatro indicadores:** el uso diario promedio, los créditos que te quedan, cuántos días faltan para que se reinicien y cuántos escenarios activos tienes frente al máximo que permite tu plan.

### 5.2 La navegación

El menú vertical de la izquierda tiene pocas opciones y vale la pena conocerlas:

| Opción | Para qué sirve |
| --- | --- |
| **Org** | El panel y la administración de tu organización: equipos, usuarios, plan y créditos |
| **Scenarios** | Tus automatizaciones. Aquí pasarás casi todo el tiempo |
| **AI Agents** | Agentes de inteligencia artificial. No los usaremos en este Cuaderno |
| **Credentials** | Tus conexiones: las cuentas que Make usa en tu nombre |
| **Webhooks** | Direcciones que permiten que otro sistema le avise algo a Make |
| **More** | Otras herramientas: plantillas, almacenes de datos, funciones y estructuras de datos |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-02-menu-more.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="170" height="315" alt="Menú More desplegado con Templates y Data structures resaltados."><a href="contenido/make/imagenes/m00/make-m00-02-menu-more.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Menú More desplegado con Templates y Data structures resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El menú More. Usaremos Templates para explorar ideas y Data structures cuando trabajemos con información ordenada en campos.</figcaption></figure>

### 5.3 Organizaciones y equipos

Make organiza el trabajo en capas. Una **organización** es el espacio general, por ejemplo tu empresa o tu cuenta personal. Dentro hay uno o más **equipos**, y cada equipo tiene sus propios escenarios y conexiones.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Una organización contiene equipos; cada equipo tiene escenarios, conexiones, plantillas y webhooks" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m00-d3-mapa-de-make" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Dónde vive cada cosa en Make</text><rect x="90" y="70" width="720" height="320" rx="18" fill="#fbf8ff" stroke="#7b5fd6" stroke-width="3" stroke-linejoin="round"/><text x="180" y="104" font-size="26" text-anchor="start" fill="#7b5fd6" font-weight="700">Organización</text><rect x="120" y="120" width="660" height="250" rx="16" fill="#ffffff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="210" y="152" font-size="24" text-anchor="start" fill="#2d3250" font-weight="700">Equipo</text><rect x="150" y="170" width="300" height="180" rx="12" fill="#f4efff" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="300" y="200" font-size="26" text-anchor="middle" fill="#2d3250" font-weight="700">Escenarios</text><circle cx="204" cy="262" r="32" fill="#cdbff5" stroke="#2d3250" stroke-width="2.4"/><text x="204" y="268" font-size="17" text-anchor="middle" fill="#2d3250" font-weight="400">módulo</text><path d="M236 262 L260 262" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d3-mapa-de-make)"/><circle cx="296" cy="262" r="32" fill="#cdbff5" stroke="#2d3250" stroke-width="2.4"/><text x="296" y="268" font-size="17" text-anchor="middle" fill="#2d3250" font-weight="400">módulo</text><path d="M328 262 L352 262" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m00-d3-mapa-de-make)"/><circle cx="388" cy="262" r="32" fill="#cdbff5" stroke="#2d3250" stroke-width="2.4"/><text x="388" y="268" font-size="17" text-anchor="middle" fill="#2d3250" font-weight="400">módulo</text><text x="300" y="330" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">tus automatizaciones</text><rect x="480" y="170" width="280" height="54" rx="12" fill="#fff6d6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="620" y="205" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Conexiones (tus cuentas)</text><rect x="480" y="238" width="280" height="50" rx="12" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="620" y="271" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Plantillas</text><rect x="480" y="302" width="280" height="48" rx="12" fill="#ffeee6" stroke="#2d3250" stroke-width="2.6" stroke-linejoin="round"/><text x="620" y="334" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="400">Webhooks</text></svg><a href="contenido/make/imagenes/diagramas/m00-d3-mapa-de-make.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Una organización contiene un equipo. El equipo contiene escenarios formados por módulos, y también conexiones, plantillas y webhooks." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Dónde vive cada cosa. Los escenarios, las conexiones, las plantillas y los webhooks pertenecen a un equipo.</figcaption></figure>

Si trabajas solo, normalmente tendrás una organización con un equipo. Puedes verlo en la sección **Teams**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-03-equipos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Sección Teams con un equipo llamado My Team y los créditos que ha usado."><a href="contenido/make/imagenes/m00/make-m00-03-equipos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Sección Teams con un equipo llamado My Team y los créditos que ha usado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un equipo y los créditos que ha usado. Una cuenta nueva suele traer un equipo con un nombre genérico.</figcaption></figure>

### 5.4 Escenarios

Un **escenario** es una automatización completa. En la sección Scenarios ves la lista de los que has creado.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-07-lista-de-escenarios.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de escenarios con tres escenarios de práctica, el botón Create scenario y los interruptores de activación resaltados."><a href="contenido/make/imagenes/m00/make-m00-07-lista-de-escenarios.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de escenarios con tres escenarios de práctica, el botón Create scenario y los interruptores de activación resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La lista de escenarios. Cada fila muestra su nombre, su número de identificación, los créditos que usó y un interruptor para activarlo.</figcaption></figure>

Fíjate en el interruptor de cada fila: apagado significa que el escenario solo se ejecuta cuando tú lo ordenas. Activarlo significa que Make lo ejecutará solo, según una programación. Para practicar, **dejaremos los escenarios apagados**.

### 5.5 Conexiones

Para que Make pueda escribir en tu hoja de cálculo o leer tu correo, necesita permiso. Ese permiso se guarda en una **conexión**: una autorización que tú das a Make para actuar en una de tus cuentas.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-08-conexiones.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Sección Credentials con dos conexiones de Google en una lista. Una fila está resaltada."><a href="contenido/make/imagenes/m00/make-m00-08-conexiones.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Sección Credentials con dos conexiones de Google en una lista. Una fila está resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las conexiones guardadas. Cada una muestra su nombre, para qué cuenta fue creada y en cuántos escenarios se usa.</figcaption></figure>

Una conexión no es tu contraseña: es una autorización que puedes revisar y retirar cuando quieras. Aun así, da acceso a una cuenta tuya. Veremos cómo cuidarlo más adelante.

### 5.6 Webhooks

Un **webhook** es como un buzón con dirección propia. Otro sistema envía un mensaje a esa dirección y Make se activa. No lo vamos a usar, pero conviene reconocerlo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-09-webhooks.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Sección Webhooks con un webhook de ejemplo. Su dirección está desenfocada."><a href="contenido/make/imagenes/m00/make-m00-09-webhooks.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Sección Webhooks con un webhook de ejemplo. Su dirección está desenfocada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La lista de webhooks. La dirección web de un webhook es privada: quien la conozca puede enviarle mensajes a tu escenario. Aquí está desenfocada a propósito.</figcaption></figure>

### 5.7 Plantillas

Una **plantilla** es un escenario ya armado que puedes copiar y adaptar. Son útiles para tomar ideas.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-10-plantillas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Galería de plantillas públicas de Make con un buscador y varias plantillas."><a href="contenido/make/imagenes/m00/make-m00-10-plantillas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Galería de plantillas públicas de Make con un buscador y varias plantillas." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La galería de plantillas. Puedes buscarlas por aplicación o por nombre.</figcaption></figure>

Nuestro consejo: primero aprende a construir tus escenarios desde cero, como haremos aquí. Cuando entiendes cada pieza, las plantillas se vuelven mucho más fáciles de revisar y adaptar. Y antes de usar una, léela completa: debes saber qué datos toca y en qué cuentas.

---

## 6. Créditos y consumo

Make no cobra por cantidad de escenarios, sino por lo que tus escenarios **hacen**. La unidad se llama **crédito**.

Según la ayuda oficial, en la mayoría de las aplicaciones **una operación equivale a un crédito**. Una operación es una acción que realiza un módulo cada vez que se ejecuta. Algunas funciones de inteligencia artificial pueden usar más.

### Qué incluye el plan gratuito

Esto es lo que la página oficial de precios indicaba el 25 de noviembre de 2026 para el plan Free:

- **1.000 créditos al mes.**
- **2 escenarios activos** como máximo.
- **15 minutos** como intervalo mínimo entre ejecuciones programadas.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-05-suscripcion-plan-free.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="986" height="162" alt="Sección Subscription con el plan actual Free de 1.000 créditos al mes y el contador de créditos usados."><a href="contenido/make/imagenes/m00/make-m00-05-suscripcion-plan-free.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Sección Subscription con el plan actual Free de 1.000 créditos al mes y el contador de créditos usados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El plan de la cuenta de práctica: Free, 1.000 créditos al mes. El contador muestra cuántos se han usado y cuándo se reinicia el uso.</figcaption></figure>

Los planes pagados (por ejemplo Core, Pro o Teams) tienen más créditos y menos restricciones, pero el Cuaderno se puede seguir completo con el plan gratuito.

### Cómo se ve el consumo de verdad

En la sección **Credit usage** Make registra cada ejecución. Esto es lo que se ve en la cuenta de práctica al ejecutar tres escenarios de prueba:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-06-consumo-de-creditos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Registro de consumo con los escenarios de práctica y los créditos que usó cada ejecución resaltados."><a href="contenido/make/imagenes/m00/make-m00-06-consumo-de-creditos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registro de consumo con los escenarios de práctica y los créditos que usó cada ejecución resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada fila es una ejecución. Un escenario con tres módulos gastó 3 créditos; uno con cuatro módulos y un Iterator gastó 6. Un módulo ejecutado solo gastó 1.</figcaption></figure>

Mira cómo se relacionan los números: cada módulo que se ejecuta cuesta una operación. Más adelante verás que un Iterator hace que el módulo siguiente se ejecute varias veces, y eso se refleja en el consumo.

### Cómo cuidar tus créditos

- Prueba con el botón **Run once**, que ejecuta el escenario una sola vez, en vez de activar la programación.
- Usa pocos datos de prueba.
- Si activas un escenario, recuerda que se ejecutará cada cierto tiempo aunque no haya datos nuevos, y cada revisión puede gastar créditos.
- Apaga los escenarios que ya no necesites.

**Enlaces oficiales para revisar la información vigente:**

- <a href="https://www.make.com/en/pricing" target="_blank" rel="noopener noreferrer">Planes y precios de Make</a>
- <a href="https://help.make.com/credits" target="_blank" rel="noopener noreferrer">Cómo funcionan los créditos (ayuda oficial)</a>
- <a href="https://help.make.com/schedule-a-scenario" target="_blank" rel="noopener noreferrer">Programación de escenarios (ayuda oficial)</a>

---

## 7. Seguridad y permisos

Automatizar significa darle a una herramienta acceso a tus cuentas. Eso es cómodo, pero merece unos cuidados simples.

1. **Conecta solo cuentas que te correspondan.** Si usas una cuenta de trabajo, asegúrate de que tienes permiso para automatizar con ella.
2. **Revisa los permisos que pide una conexión** antes de aceptarlos.
3. **No compartas capturas con datos privados.** Direcciones de webhooks, claves, correos personales y nombres de clientes deben taparse.
4. **Practica con datos inventados.** En este Cuaderno todos los ejemplos son ficticios, y es lo mejor que puedes hacer cuando aprendes.
5. **Apaga lo que no uses.** Un escenario activo olvidado sigue funcionando.
6. **Revisa antes de compartir un escenario.** Al exportarlo se pueden incluir nombres de cuentas u otros datos.

### Roles y permisos

Cuando una organización tiene varias personas, Make asigna **roles** que definen qué puede hacer cada una.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m00/make-m00-04-roles-de-usuario.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Lista de roles de usuario con Owner, Admin y Member resaltados y una descripción de lo que permite cada uno."><a href="contenido/make/imagenes/m00/make-m00-04-roles-de-usuario.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de roles de usuario con Owner, Admin y Member resaltados y una descripción de lo que permite cada uno." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los roles por defecto. Owner tiene acceso total, Admin administra casi todo y Member ejecuta escenarios y gestiona sus propias conexiones.</figcaption></figure>

La idea es dar a cada persona **solo el acceso que necesita**. Si trabajas solo, tú eres el propietario y no tienes que hacer nada más.

---

## 8. Lo que necesitas para seguir

Antes de pasar al módulo 01, comprueba que tienes:

- Una cuenta de Make con la sesión iniciada.
- Una cuenta de Google en la que puedas crear hojas de cálculo (Google Sheets).
- Datos de prueba inventados, nunca información real de personas.

---

## 9. Resumen

- **Automatizar** es dejar que una máquina siga por ti un procedimiento que ya conoces.
- **Make** es una plataforma visual: armas escenarios con módulos conectados, sin programar.
- Una **organización** contiene **equipos**, y cada equipo tiene escenarios, conexiones, plantillas y webhooks.
- Una **conexión** es una autorización para que Make actúe en una de tus cuentas.
- Un **crédito** es la unidad de consumo: en la mayoría de las aplicaciones, una operación cuesta un crédito.
- En la **automatización con IA**, el modelo propone y una regla o una persona valida.
- Practica con datos ficticios y apaga lo que no uses.

## 10. Ponlo en práctica

### Desafío: tu mapa de automatizaciones

1. Escribe **tres tareas repetidas** de tu vida o de tu trabajo.
2. Para cada una, responde: ¿qué la dispara?, ¿qué datos usa?, ¿cuál es el resultado final?
3. Clasifícalas: ¿se resuelve con una regla fija o necesita criterio de una persona?
4. En tu cuenta de Make, encuentra: dónde ves los créditos que te quedan, dónde ves tus conexiones y cuántos escenarios activos permite tu plan.

**Resultado esperado:** una lista de tres tareas con su disparador, sus datos y su resultado, y tres lugares ubicados en Make.

### Pistas (ábrelas de a una)

<details>
<summary>Pista 1: no sé qué tarea elegir</summary>

Busca algo que hagas cada semana con los mismos pasos: copiar datos entre archivos, enviar el mismo aviso, ordenar mensajes. Si te aburre hacerlo, probablemente se puede automatizar.

</details>

<details>
<summary>Pista 2: no encuentro cuántos escenarios activos tengo</summary>

Entra a la sección Org. En el panel principal hay un indicador que se llama Active scenarios.

</details>

<details>
<summary>Pista 3: no sé si necesita criterio de una persona</summary>

Hazte esta pregunta: si le diera las instrucciones por escrito a alguien que no conoce el tema, ¿podría hacerlo sin preguntarme nada? Si la respuesta es sí, es una regla fija.

</details>

## 11. Comprueba lo aprendido

```quiz
? ¿Qué es un escenario en Make?
- Una cuenta de Google conectada.
+ Una automatización completa formada por módulos conectados.
- Un plan de pago.
> Un escenario es el recorrido completo: desde que llega un dato hasta que se guarda o envía el resultado.
? ¿Cuál de estas tareas es mejor candidata a automatizarse?
- Escribir una carta personal que solo se hará una vez.
+ Registrar en una hoja cada solicitud que llega, con los mismos pasos siempre.
- Decidir a quién contratar.
> Se automatiza lo que se repite, sigue los mismos pasos y tiene un resultado fácil de comprobar.
? ¿Qué diferencia hay entre una regla fija y un modelo de IA?
- La regla fija puede equivocarse más que la IA.
+ La regla fija decide siempre igual; el modelo de IA propone y conviene validarlo.
- No hay ninguna diferencia.
> Con IA el resultado puede variar y a veces es incorrecto, por eso se revisa.
? En la mayoría de las aplicaciones, ¿cuánto cuesta una operación de un módulo?
- Nada, es gratis siempre.
+ Un crédito.
- Cien créditos.
> Algunas funciones de IA pueden usar más, pero en la mayoría de las apps una operación equivale a un crédito.
? ¿Qué es una conexión?
- Una copia de tu contraseña.
+ Una autorización que le das a Make para actuar en una de tus cuentas.
- Un tipo de escenario.
> No es tu contraseña, pero da acceso a una cuenta tuya: conéctala con cuidado y retírala cuando no la uses.
```
