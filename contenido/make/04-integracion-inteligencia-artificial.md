# Integración con inteligencia artificial

Hasta ahora, todas las decisiones de nuestro escenario las tomaban reglas que escribimos nosotros: «si la prioridad es Alta, va a Urgentes». Pero ¿qué pasa cuando la solicitud llega como una frase escrita por una persona, sin ninguna prioridad marcada? «No puedo entrar al sistema y mañana debo entregar un informe». Una regla simple no entiende eso.

Aquí entra la **inteligencia artificial**. Vamos a pedirle a un modelo de lenguaje que lea la frase y **proponga** una categoría y una prioridad. Después, las reglas del Router (lo que aprendiste en el módulo 03) decidirán a dónde va cada solicitud. Y cuando la IA no esté segura, una **persona** revisará.

La idea central de este apunte es esta: **la IA propone, las reglas deciden y una persona revisa lo dudoso.**

**Qué vas a aprender:**

- Qué hace el módulo de Groq y cómo se estructura una conversación con un modelo.
- Escribir un prompt claro, dividido en cinco partes.
- Convertir la respuesta de la IA en datos que Make pueda usar (Parse JSON).
- Qué significa la insignia naranja que aparece en un módulo.
- Armar tres rutas, incluida una de **revisión humana**.
- Comprobar con casos reales, incluidos los difíciles.

**Qué necesitas:** haber hecho los módulos 02 y 03, una cuenta de Make, una de Google y **una conexión de Groq con tu propia clave**. Todos los datos son inventados.

> **Sobre las capturas:** son reales, de una cuenta de práctica. Make está en inglés y Google Sheets en español. El nombre de la conexión de Groq está desenfocado.

> **Importante sobre privacidad:** todo lo que mandas a un modelo de IA sale de tu cuenta hacia un servicio externo. En la práctica real, **no envíes datos personales o confidenciales** a una IA sin saber qué se hace con ellos. Aquí usamos solo datos inventados.

---

## 1. Primero, las ideas

### Un modelo de lenguaje recibe mensajes

Cuando le hablas a un modelo, le envías una lista de **mensajes**. Cada mensaje tiene un **rol**:

| Rol | Para qué sirve |
| --- | --- |
| **System** | Las instrucciones generales: quién es la IA y cómo debe comportarse |
| **User** | Lo que quiere la persona: aquí va la solicitud concreta |
| **Assistant** | Lo que responde el modelo (a veces se usa para dar ejemplos) |

Nosotros usaremos dos mensajes: uno **System** con las instrucciones y uno **User** con la solicitud recibida.

### Un prompt tiene cinco partes

Un buen prompt no es una frase suelta. Se ordena en cinco partes, y cada una responde una pregunta distinta:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Un prompt se divide en rol, contexto, tarea, restricciones y formato" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m04-d2-cinco-partes-del-prompt" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">Las cinco partes de un buen prompt</text><rect x="84" y="76" width="220" height="50" rx="10" fill="#ffeee6" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="194" y="109" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="700">ROL</text><path d="M306 101 L340 101" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d2-cinco-partes-del-prompt)"/><text x="350" y="109" font-size="23" text-anchor="start" fill="#2d3250" font-weight="400">quién es la IA</text><rect x="84" y="138" width="220" height="50" rx="10" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="194" y="171" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="700">CONTEXTO</text><path d="M306 163 L340 163" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d2-cinco-partes-del-prompt)"/><text x="350" y="171" font-size="23" text-anchor="start" fill="#2d3250" font-weight="400">qué datos recibe y qué opciones existen</text><rect x="84" y="200" width="220" height="50" rx="10" fill="#efe8ff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="194" y="233" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="700">TAREA</text><path d="M306 225 L340 225" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d2-cinco-partes-del-prompt)"/><text x="350" y="233" font-size="23" text-anchor="start" fill="#2d3250" font-weight="400">qué debe hacer, en una frase</text><rect x="84" y="262" width="220" height="50" rx="10" fill="#fff6d6" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="194" y="295" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="700">RESTRICCIONES</text><path d="M306 287 L340 287" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d2-cinco-partes-del-prompt)"/><text x="350" y="295" font-size="23" text-anchor="start" fill="#2d3250" font-weight="400">qué no debe hacer y cuándo dudar</text><rect x="84" y="324" width="220" height="50" rx="10" fill="#e6f1ff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="194" y="357" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="700">FORMATO</text><path d="M306 349 L340 349" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d2-cinco-partes-del-prompt)"/><text x="350" y="357" font-size="23" text-anchor="start" fill="#2d3250" font-weight="400">cómo debe responder</text><text x="450" y="400" font-size="21" text-anchor="middle" fill="#5a4aa6" font-weight="400">Cada parte responde una pregunta distinta. Si falta una, la IA improvisa.</text></svg><a href="contenido/make/imagenes/diagramas/m04-d2-cinco-partes-del-prompt.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Cinco recuadros: rol, contexto, tarea, restricciones y formato, cada uno con la pregunta que responde." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un prompt claro se divide en cinco partes. Si falta una, la IA tiende a improvisar.</figcaption></figure>

### La IA no decide: propone

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Una solicitud pasa por Groq, Parse JSON y un Router que la envía a Urgentes, Normales o Revisión humana" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m04-d1-la-ia-propone-las-reglas-deciden" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">La IA propone y las reglas deciden</text><rect x="72" y="150" width="130" height="70" rx="10" fill="#fff6d6" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="137" y="178" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Solicitud</text><text x="137" y="204" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">escrita</text><path d="M204 185 L262 185" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d1-la-ia-propone-las-reglas-deciden)"/><circle cx="318" cy="185" r="52" fill="#ffd9c9" stroke="#2d3250" stroke-width="2.8"/><text x="318" y="180" font-size="26" text-anchor="middle" fill="#2d3250" font-weight="700">Groq</text><text x="318" y="205" font-size="20" text-anchor="middle" fill="#2d3250" font-weight="400">(la IA)</text><path d="M372 185 L430 185" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d1-la-ia-propone-las-reglas-deciden)"/><rect x="434" y="150" width="120" height="70" rx="10" fill="#efe8ff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="494" y="178" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">Parse</text><text x="494" y="204" font-size="24" text-anchor="middle" fill="#2d3250" font-weight="400">JSON</text><path d="M556 185 L606 185" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d1-la-ia-propone-las-reglas-deciden)"/><circle cx="652" cy="185" r="46" fill="#a8e2c0" stroke="#2d3250" stroke-width="2.8"/><text x="652" y="191" font-size="21" text-anchor="middle" fill="#2d3250" font-weight="700">Router</text><path d="M700 175 L748 112" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d1-la-ia-propone-las-reglas-deciden)"/><rect x="752" y="90" width="140" height="46" rx="10" fill="#ffeee6" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="822" y="120" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">Urgentes</text><path d="M700 185 L748 192" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d1-la-ia-propone-las-reglas-deciden)"/><rect x="752" y="170" width="140" height="46" rx="10" fill="#e8f8ef" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="822" y="200" font-size="22" text-anchor="middle" fill="#2d3250" font-weight="700">Normales</text><path d="M700 205 L748 272" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d1-la-ia-propone-las-reglas-deciden)"/><rect x="752" y="250" width="140" height="46" rx="10" fill="#f4efff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="822" y="280" font-size="15" text-anchor="middle" fill="#2d3250" font-weight="700">Revisión humana</text><text x="318" y="262" font-size="21" text-anchor="middle" fill="#c0562d" font-weight="400">propone</text><text x="494" y="262" font-size="21" text-anchor="middle" fill="#5a4aa6" font-weight="400">ordena</text><text x="656" y="262" font-size="21" text-anchor="middle" fill="#1f8f5f" font-weight="400">decide</text><text x="450" y="345" font-size="22" text-anchor="middle" fill="#5a4aa6" font-weight="400">La IA solo sugiere una clasificación. Las reglas del Router</text><text x="450" y="375" font-size="22" text-anchor="middle" fill="#5a4aa6" font-weight="400">deciden a dónde va cada solicitud, y una persona revisa lo dudoso.</text></svg><a href="contenido/make/imagenes/diagramas/m04-d1-la-ia-propone-las-reglas-deciden.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: Una solicitud escrita pasa por Groq, que propone; por Parse JSON, que ordena; y por un Router, que decide entre Urgentes, Normales y Revisión humana." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La IA solo sugiere una clasificación. El Router decide y una persona revisa lo dudoso.</figcaption></figure>

---

## 2. El caso y la hoja

Seguimos con la empresa ficticia de solicitudes, pero ahora **nadie escribe la prioridad**: solo hay una descripción libre. Crea una hoja llamada **Practica Make - IA** con cuatro pestañas:

| Pestaña | Encabezados (fila 1) |
| --- | --- |
| Solicitudes | ID, Nombre, Descripción |
| Urgentes, Normales y Revision | ID, Nombre, Descripción, Categoria, Prioridad, Resumen, Requiere revision |

En `Solicitudes` escribe cuatro casos. Cada uno prueba algo distinto:

| ID | Nombre | Descripción | Qué probamos |
| --- | --- | --- | --- |
| SOL-201 | Ana | No puedo entrar al sistema desde ayer y hoy tengo que entregar un informe a primera hora | Un caso claramente urgente |
| SOL-202 | Carlos | Quisiera saber el horario de atencion de los sabados | Un caso claramente normal |
| SOL-203 | Laura | Necesito ayuda con lo de siempre | Un caso **ambiguo** |
| SOL-204 | Diego | hola | Un caso con **información insuficiente** |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-01-hoja-solicitudes-ia.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Solicitudes con cuatro casos de prueba resaltados."><a href="contenido/make/imagenes/m04/make-m04-01-hoja-solicitudes-ia.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Solicitudes con cuatro casos de prueba resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cuatro casos pensados: uno urgente, uno normal, uno ambiguo y uno casi vacío.</figcaption></figure>

---

## 3. El disparador y el módulo de Groq

Crea un escenario nuevo con **Google Sheets > Watch New Rows**, apuntando a la pestaña `Solicitudes` de esta hoja. Recuerda dos cosas del módulo 02: elige **All** como punto de inicio y sube el **Limit** a `10` para procesar los cuatro casos de una vez.

Haz clic en el **+** del disparador y busca la aplicación **Groq**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-02-buscar-groq.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Buscador de aplicaciones con la palabra Groq escrita y la aplicación Groq resaltada."><a href="contenido/make/imagenes/m04/make-m04-02-buscar-groq.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Buscador de aplicaciones con la palabra Groq escrita y la aplicación Groq resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Groq aparece como una aplicación más de Make.</figcaption></figure>

Verás varios módulos. Los que nos interesan son dos:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-03-modulos-de-groq.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Lista de módulos de Groq con Create a Chat Completion y Create a JSON Chat Completion resaltados."><a href="contenido/make/imagenes/m04/make-m04-03-modulos-de-groq.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de módulos de Groq con Create a Chat Completion y Create a JSON Chat Completion resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Dos formas de conversar con el modelo: una devuelve texto y la otra devuelve directamente un JSON.</figcaption></figure>

Elegimos **Create a Chat Completion**, que devuelve **texto**. Así aprenderás a convertir ese texto en datos, un paso que verás en muchos escenarios reales.

### La conexión y el modelo

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-04-groq-conexion-modelo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Ventana de Groq con la conexión desenfocada, el campo Model vacío y la sección Messages resaltados."><a href="contenido/make/imagenes/m04/make-m04-04-groq-conexion-modelo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana de Groq con la conexión desenfocada, el campo Model vacío y la sección Messages resaltados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La conexión guarda tu clave de Groq, igual que la de Google guardaba una autorización. Después hay que elegir un modelo y escribir los mensajes.</figcaption></figure>

Si todavía no tienes una conexión, el botón **Add** te guía para crearla con tu propia clave. **No pegues tu clave en ningún texto compartido.**

Haz clic en **Model** para ver los modelos disponibles.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-05-lista-de-modelos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Lista desplegable de modelos disponibles en la cuenta."><a href="contenido/make/imagenes/m04/make-m04-05-lista-de-modelos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista desplegable de modelos disponibles en la cuenta." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada cuenta ve una lista distinta, según lo que tenga habilitado.</figcaption></figure>

En nuestra cuenta de práctica la lista incluía modelos de moderación, de voz y de texto. Elegimos **openai/gpt-oss-20b**, un modelo de texto. La tuya puede mostrar otros: elige uno de texto general.

---

## 4. Los mensajes

En **Messages** pulsa **Add item**. Se crea el mensaje 1. Elige su rol:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-06-roles-del-mensaje.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Lista de roles con Empty, System, User y Assistant."><a href="contenido/make/imagenes/m04/make-m04-06-roles-del-mensaje.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de roles con Empty, System, User y Assistant." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los cuatro roles posibles de un mensaje.</figcaption></figure>

Elige **System**. En **Content** escribimos las instrucciones. Este es el texto que usamos, dividido en las cinco partes:

> **ROL:** Eres un asistente que ayuda a clasificar solicitudes de atención de una empresa ficticia.
>
> **CONTEXTO:** Recibirás la descripción que escribió una persona. Las categorías posibles son: Soporte tecnico, Consulta general, Facturacion y Otro. Las prioridades posibles son: Alta y Normal.
>
> **TAREA:** Analiza la descripción y propón una categoría, una prioridad y un resumen de una sola frase.
>
> **RESTRICCIONES:** No inventes datos que no estén en la descripción. Usa la prioridad Alta solo si hay un problema que impide trabajar o una urgencia clara. Si la descripción es ambigua o no tiene información suficiente para clasificar con seguridad, marca requiere_revision como true.
>
> **FORMATO:** Responde únicamente con un objeto JSON, sin texto adicional y sin comillas invertidas, con estas claves: categoria, prioridad, resumen y requiere_revision (true o false).

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-07-system-prompt.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Campo Content del mensaje System con el prompt completo escrito."><a href="contenido/make/imagenes/m04/make-m04-07-system-prompt.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo Content del mensaje System con el prompt completo escrito." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El mensaje System, con las cinco partes.</figcaption></figure>

Fíjate en dos detalles del prompt:

- Las **restricciones** le dicen a la IA qué hacer cuando **duda**. Sin esa instrucción, tiende a inventar una respuesta.
- El **formato** pide un JSON y nada más. Si la IA agrega texto extra, el paso siguiente falla.

### El mensaje User

Pulsa **Add item** otra vez. Elige el rol **User**. En **Content** escribe el texto fijo `Solicitud recibida: ` (con un espacio al final).

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-08-mensaje-user-texto.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Mensaje 2 con rol User y el texto Solicitud recibida en el campo Content."><a href="contenido/make/imagenes/m04/make-m04-08-mensaje-user-texto.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Mensaje 2 con rol User y el texto Solicitud recibida en el campo Content." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La parte fija del mensaje del usuario.</figcaption></figure>

Después, con el cursor al final de ese texto, haz clic en la píldora **Descripción (C)** del panel del disparador.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-09-mensaje-user-pildora.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Campo Content con el texto fijo seguido de la píldora Descripción, a la vez que el panel de píldoras."><a href="contenido/make/imagenes/m04/make-m04-09-mensaje-user-pildora.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo Content con el texto fijo seguido de la píldora Descripción, a la vez que el panel de píldoras." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Texto fijo y píldora juntos: cada ejecución enviará la descripción de la solicitud que llegó.</figcaption></figure>

Guarda el módulo y el escenario.

---

## 5. Primera prueba: ¿qué responde la IA?

Antes de seguir armando, pulsa **Run once** y mira qué responde el modelo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-10-groq-ejecutado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Escenario con Watch New Rows y Groq ejecutados; Groq muestra el número 2 en la burbuja."><a href="contenido/make/imagenes/m04/make-m04-10-groq-ejecutado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario con Watch New Rows y Groq ejecutados; Groq muestra el número 2 en la burbuja." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Groq trabajó 2 veces porque el límite del disparador aún estaba en 2.</figcaption></figure>

Haz clic en la burbuja de Groq. Abre el panel de **salida** (Output).

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-11-respuesta-de-groq.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Salida de Groq con el campo Result, que contiene un texto con llaves y comillas."><a href="contenido/make/imagenes/m04/make-m04-11-respuesta-de-groq.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Groq con el campo Result, que contiene un texto con llaves y comillas." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La respuesta está en el campo Result: es un solo texto que **parece** un JSON.</figcaption></figure>

Esta es la clave del módulo. Lo que devolvió Groq es **un texto largo**. Se ve como datos ordenados (categoría, prioridad, resumen), pero para Make sigue siendo una única cadena de letras. No puedes usar solo la prioridad en un filtro.

La operación mostró un costo de **1 crédito** por ejecución de Groq. El costo de las funciones de IA puede variar según el módulo y el modelo, así que revisa siempre la página de consumo de tu cuenta.

---

## 6. Parse JSON: del texto a las píldoras

El módulo **Parse JSON** (en la aplicación **JSON**) lee un texto con forma de JSON y lo separa en piezas.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><svg style="display:block;width:100%;height:auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 420" role="img" aria-label="Parse JSON convierte el texto de la respuesta en píldoras separables" font-family="Caveat, 'Comic Sans MS', 'Segoe Print', cursive" font-size="26" fill="#2d3250"><defs><marker id="p-m04-d3-texto-a-pildoras" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#2d3250" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><rect width="900" height="420" rx="14" fill="#fffdf6"/><line x1="0" y1="56" x2="900" y2="56" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="88" x2="900" y2="88" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="120" x2="900" y2="120" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="152" x2="900" y2="152" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="184" x2="900" y2="184" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="216" x2="900" y2="216" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="248" x2="900" y2="248" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="280" x2="900" y2="280" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="312" x2="900" y2="312" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="344" x2="900" y2="344" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="376" x2="900" y2="376" stroke="#d8e4f2" stroke-width="1.5"/><line x1="0" y1="408" x2="900" y2="408" stroke="#d8e4f2" stroke-width="1.5"/><line x1="56" y1="0" x2="56" y2="420" stroke="#f1a9a9" stroke-width="2"/><text x="450" y="44" font-size="34" text-anchor="middle" fill="#2d3250" font-weight="700">De un texto con forma de JSON a píldoras</text><rect x="70" y="100" width="310" height="120" rx="10" fill="#fff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="225" y="130" font-size="21" text-anchor="middle" fill="#c0562d" font-weight="700">Lo que entrega Groq</text><text x="225" y="164" font-size="21" text-anchor="middle" fill="#2d3250" font-weight="400">un solo texto largo:</text><text x="225" y="194" font-size="19" text-anchor="middle" fill="#7b5fd6" font-weight="400">{"categoria":"Soporte", ...}</text><path d="M384 160 L506 160" stroke="#2d3250" stroke-width="2.8" stroke-linecap="round" fill="none" marker-end="url(#p-m04-d3-texto-a-pildoras)"/><text x="445" y="146" font-size="21" text-anchor="middle" fill="#2d3250" font-weight="700">Parse JSON</text><rect x="512" y="76" width="340" height="168" rx="10" fill="#efe8ff" stroke="#2d3250" stroke-width="2.4" stroke-linejoin="round"/><text x="672" y="106" font-size="21" text-anchor="middle" fill="#5a4aa6" font-weight="700">Lo que ves después</text><rect x="540" y="122" width="130" height="38" rx="10" fill="#d9c8ff" stroke="#7b5fd6" stroke-width="2.4" stroke-linejoin="round"/><text x="605" y="148" font-size="18" text-anchor="middle" fill="#2d3250" font-weight="400">Categoria</text><rect x="680" y="122" width="130" height="38" rx="10" fill="#d9c8ff" stroke="#7b5fd6" stroke-width="2.4" stroke-linejoin="round"/><text x="745" y="148" font-size="18" text-anchor="middle" fill="#2d3250" font-weight="400">Prioridad</text><rect x="540" y="174" width="130" height="38" rx="10" fill="#d9c8ff" stroke="#7b5fd6" stroke-width="2.4" stroke-linejoin="round"/><text x="605" y="200" font-size="18" text-anchor="middle" fill="#2d3250" font-weight="400">Resumen</text><rect x="680" y="174" width="170" height="38" rx="10" fill="#d9c8ff" stroke="#7b5fd6" stroke-width="2.4" stroke-linejoin="round"/><text x="765" y="200" font-size="18" text-anchor="middle" fill="#2d3250" font-weight="400">Requiere revision</text><text x="450" y="300" font-size="23" text-anchor="middle" fill="#5a4aa6" font-weight="400">Sin Parse JSON el texto no se puede separar en piezas.</text><text x="450" y="336" font-size="23" text-anchor="middle" fill="#5a4aa6" font-weight="400">Con Parse JSON cada dato es una píldora que puedes mapear o filtrar.</text><text x="450" y="376" font-size="21" text-anchor="middle" fill="#c0562d" font-weight="400">Requiere revision es booleano: solo puede valer verdadero o falso.</text></svg><a href="contenido/make/imagenes/diagramas/m04-d3-texto-a-pildoras.svg" target="_blank" rel="noopener noreferrer" aria-label="Ampliar diagrama: A la izquierda un texto largo con llaves entregado por Groq; a la derecha, después de Parse JSON, cuatro píldoras separadas: Categoria, Prioridad, Resumen y Requiere revision." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Parse JSON convierte un texto en píldoras que puedes mapear y filtrar.</figcaption></figure>

Haz clic en el **+** de Groq, elige la aplicación **JSON** y el módulo **Parse JSON**. Necesita una **estructura de datos**: una descripción de qué piezas esperamos. No hace falta escribirla a mano; Make la **genera** a partir de un ejemplo.

Junto a *Data structure* pulsa **Add**. Ponle un nombre, por ejemplo `Clasificacion de solicitud`, y pulsa **Generate**. En *Sample data* pega un ejemplo con la forma que esperas:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-12-parse-json-muestra.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Ventana Generate con el tipo de contenido JSON y el ejemplo escrito en Sample data."><a href="contenido/make/imagenes/m04/make-m04-12-parse-json-muestra.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana Generate con el tipo de contenido JSON y el ejemplo escrito en Sample data." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un ejemplo de lo que devolverá la IA. Make deduce de él las piezas.</figcaption></figure>

Pulsa **Generate**. Make crea la estructura sola:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-13-estructura-generada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Estructura con cuatro elementos: Categoria, Prioridad y Resumen de tipo texto, y Requiere revision de tipo booleano."><a href="contenido/make/imagenes/m04/make-m04-13-estructura-generada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Estructura con cuatro elementos: Categoria, Prioridad y Resumen de tipo texto, y Requiere revision de tipo booleano." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tres textos y un **booleano**. Un booleano solo puede valer verdadero o falso.</figcaption></figure>

Guarda la estructura. Ahora, en el campo **JSON string** hay que indicar **qué texto** debe leer. Haz clic en el campo: aparece el panel de píldoras de Groq.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-14-parse-json-panel.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Campo JSON string enfocado y el panel de píldoras de Groq, con la píldora Result resaltada."><a href="contenido/make/imagenes/m04/make-m04-14-parse-json-panel.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo JSON string enfocado y el panel de píldoras de Groq, con la píldora Result resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El panel muestra todo lo que entregó Groq. Elegimos Result.</figcaption></figure>

Elige **Result**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-15-parse-json-result.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Campo JSON string con la píldora Result dentro."><a href="contenido/make/imagenes/m04/make-m04-15-parse-json-result.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Campo JSON string con la píldora Result dentro." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Parse JSON leerá el texto que entregó Groq.</figcaption></figure>

Guarda el módulo y el escenario.

---

## 7. La insignia naranja

Al guardar, el módulo Parse JSON muestra una pequeña insignia **naranja** con un 1. Haz clic en ella.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-17-mensaje-insignia-naranja.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Ventana de mensajes que dice que no se están usando los datos generados por el módulo, con la insignia naranja resaltada."><a href="contenido/make/imagenes/m04/make-m04-17-mensaje-insignia-naranja.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana de mensajes que dice que no se están usando los datos generados por el módulo, con la insignia naranja resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El mensaje de la insignia naranja.</figcaption></figure>

El mensaje dice, en español: *no estás usando los datos generados por este módulo; considera quitarlo o agregar módulos después de él.*

Es un **aviso**, no un error. Make solo te avisa de que Parse JSON convierte datos, pero nadie los usa todavía. Más adelante, cuando conectemos el Router, **desaparece sola**. Ya lo vimos: la insignia **roja** del módulo 02 era distinta, porque pedía un dato obligatorio.

| Insignia | Qué significa |
| --- | --- |
| **Roja** | Falta algo obligatorio o hay un error. Hay que resolverlo |
| **Naranja** | Un aviso. El escenario puede funcionar igual, pero Make te recomienda revisar |

---

## 8. El Router y los filtros

Haz clic en el **+** de Parse JSON. Busca **Flow Control** y elige **Router**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-18-router-agregado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Router agregado después de Parse JSON, con dos rutas vacías."><a href="contenido/make/imagenes/m04/make-m04-18-router-agregado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Router agregado después de Parse JSON, con dos rutas vacías." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Router nace con dos rutas.</figcaption></figure>

Necesitamos tres: Urgentes, Normales y Revisión humana. Haz clic derecho sobre el Router y elige **Add route**. En cada ruta agrega un **Google Sheets > Add a Row**: la primera hacia la pestaña `Urgentes`, la segunda hacia `Normales` y la tercera hacia `Revision`. Mapea con píldoras los siete campos.

Ahora, las píldoras vienen de **dos módulos distintos**:

- **ID, Nombre y Descripción** vienen del disparador.
- **Categoria, Prioridad, Resumen y Requiere revision** vienen de Parse JSON.

> **Un truco útil:** el panel de píldoras tiene un buscador arriba. Escribe el nombre de la píldora y aparece sola, sin tener que desplazarte por una lista larga.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-19-pildora-booleana.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Información de la píldora Requiere revision que indica que es de tipo booleano."><a href="contenido/make/imagenes/m04/make-m04-19-pildora-booleana.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Información de la píldora Requiere revision que indica que es de tipo booleano." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Al pasar el cursor sobre una píldora, Make muestra su tipo. Esta es booleana.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-20-rutas-sin-etiquetas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Router con tres módulos Add a Row, uno por ruta."><a href="contenido/make/imagenes/m04/make-m04-20-rutas-sin-etiquetas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Router con tres módulos Add a Row, uno por ruta." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las tres rutas, todavía sin filtros.</figcaption></figure>

### Filtro de Urgentes

Una solicitud va a Urgentes si la prioridad es **Alta** y además **no necesita revisión**. Son dos condiciones unidas por **AND**:

1. Píldora **Prioridad**, operador *Equal to*, valor `Alta`.
2. Píldora **Requiere revision**, operador *Is false*.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-21-filtro-urgentes-alta.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Filtro con la etiqueta Urgentes y la primera condición: Prioridad igual a Alta."><a href="contenido/make/imagenes/m04/make-m04-21-filtro-urgentes-alta.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Filtro con la etiqueta Urgentes y la primera condición: Prioridad igual a Alta." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La primera condición, de texto.</figcaption></figure>

Para la segunda condición hay que **cambiar el operador**. La lista tiene familias: de texto, numéricos, de fecha y **booleanos**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-22-lista-operadores.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Lista de operadores con las opciones básicas y de texto."><a href="contenido/make/imagenes/m04/make-m04-22-lista-operadores.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de operadores con las opciones básicas y de texto." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La lista de operadores. Tiene un buscador.</figcaption></figure>

Como `Requiere revision` es booleana, elegimos un operador de la familia *Boolean operators*: **Is false** (es falso).

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-23-filtro-urgentes-completo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Filtro con dos condiciones unidas por and: Prioridad igual a Alta y Requiere revision es falso."><a href="contenido/make/imagenes/m04/make-m04-23-filtro-urgentes-completo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Filtro con dos condiciones unidas por and: Prioridad igual a Alta y Requiere revision es falso." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El filtro completo de Urgentes.</figcaption></figure>

### Filtro de Normales

Igual, pero con `Normal`: Prioridad igual a `Normal` **AND** Requiere revision *Is false*.

### Ruta de revisión humana

La tercera ruta es el **fallback**: recibe lo que ninguna otra aceptó. Y aquí está lo importante: **todo lo que la IA marque con `requiere_revision` verdadero queda fuera de Urgentes y de Normales**, porque ambos filtros exigen que sea falso. Así llega **solo** a la ruta de revisión.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-24-ruta-revision-humana.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Filtro de la tercera ruta con la etiqueta Revision humana y la opción Yes de fallback resaltadas."><a href="contenido/make/imagenes/m04/make-m04-24-ruta-revision-humana.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Filtro de la tercera ruta con la etiqueta Revision humana y la opción Yes de fallback resaltadas." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ruta de revisión humana, marcada como fallback.</figcaption></figure>

Guarda todo.

---

## 9. Pruebas con casos reales

Vuelve a elegir **All** como punto de inicio (clic derecho en el disparador > Choose where to start) y pulsa **Run once**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-25-ejecucion-cuatro-casos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Escenario ejecutado. Urgentes 1, Normales 1, y la ruta de revisión con 2 operaciones."><a href="contenido/make/imagenes/m04/make-m04-25-ejecucion-cuatro-casos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado. Urgentes 1, Normales 1, y la ruta de revisión con 2 operaciones." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cuatro solicitudes: una a Urgentes, una a Normales y dos a Revisión humana.</figcaption></figure>

En Groq y en Parse JSON hubo **4 operaciones**, una por solicitud. Ahora, **revisa cada hoja**:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-26-resultado-urgentes.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1077" height="498" alt="Pestaña Urgentes con SOL-201, categoría Soporte tecnico, prioridad Alta y Requiere revision falso."><a href="contenido/make/imagenes/m04/make-m04-26-resultado-urgentes.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Urgentes con SOL-201, categoría Soporte tecnico, prioridad Alta y Requiere revision falso." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-201 («no puedo entrar al sistema... entregar un informe a primera hora») quedó en Urgentes.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-27-resultado-normales.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1077" height="498" alt="Pestaña Normales con SOL-202, categoría Consulta general, prioridad Normal y Requiere revision falso."><a href="contenido/make/imagenes/m04/make-m04-27-resultado-normales.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Normales con SOL-202, categoría Consulta general, prioridad Normal y Requiere revision falso." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-202 (horario de los sábados) quedó en Normales.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-28-resultado-revision.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="623" alt="Pestaña Revision con SOL-203 y SOL-204, ambas con Requiere revision verdadero. SOL-204 tiene categoría y prioridad vacías."><a href="contenido/make/imagenes/m04/make-m04-28-resultado-revision.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Revision con SOL-203 y SOL-204, ambas con Requiere revision verdadero. SOL-204 tiene categoría y prioridad vacías." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-203 y SOL-204 llegaron a Revisión humana. SOL-204 tiene los campos vacíos.</figcaption></figure>

| Solicitud | Resultado | Por qué |
| --- | --- | --- |
| SOL-201 | Urgentes | La IA vio un problema que impide trabajar y una fecha límite |
| SOL-202 | Normales | Una consulta sin urgencia |
| SOL-203 | Revisión humana | «Lo de siempre» no dice qué es: ambigua |
| SOL-204 | Revisión humana | «hola» no tiene información |

### ¿Por qué SOL-204 tiene campos vacíos?

Abre la respuesta de Groq para esa solicitud (en la burbuja de Groq, cambia de operación con las flechas hasta la 4).

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-29-respuesta-ante-hola.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Salida de Groq ante la solicitud hola: categoria nula, prioridad nula, resumen vacío y requiere_revision verdadero."><a href="contenido/make/imagenes/m04/make-m04-29-respuesta-ante-hola.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Groq ante la solicitud hola: categoria nula, prioridad nula, resumen vacío y requiere_revision verdadero." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Ante «hola», la IA **no inventó**: devolvió valores nulos y marcó la revisión.</figcaption></figure>

La IA respondió `categoria` nula, `prioridad` nula y `requiere_revision` verdadero. Es justo lo que le pedimos en las restricciones: **no inventar y marcar revisión cuando no hay información**. Gracias a eso, una persona verá esa solicitud en vez de que una clasificación falsa se cuele en una hoja de urgentes.

> **Lección:** una buena automatización con IA no es la que acierta siempre, sino la que **sabe cuándo no está segura** y pide ayuda.

---

## 10. Errores frecuentes y cómo revisarlos

| Qué ves | Qué puede estar pasando | Cómo lo revisas |
| --- | --- | --- |
| El módulo siguiente falla al leer la respuesta | La IA agregó texto extra o comillas invertidas junto al JSON | Mira Result en la burbuja de Groq y refuerza la parte de **formato** del prompt |
| No aparecen píldoras de Parse JSON | Falta la estructura de datos o el JSON string está vacío | Revisa el módulo Parse JSON |
| Una solicitud va a una hoja incorrecta | La IA propuso otra prioridad | Lee la respuesta de Groq; ajusta las **restricciones** del prompt |
| Todas van a Revisión humana | La IA duda demasiado | Revisa si el contexto del prompt es claro |
| Solo se procesan 2 solicitudes | El límite del disparador | Cambia Limit a un valor mayor |
| La IA clasifica distinto en otra ejecución | Un modelo de lenguaje puede variar entre ejecuciones | Por eso el Router y la revisión humana importan |

---

## 11. Resumen

- Un modelo de lenguaje recibe **mensajes** con roles: System (instrucciones) y User (la solicitud).
- Un prompt claro tiene **cinco partes**: rol, contexto, tarea, restricciones y formato.
- La IA **propone**; el Router **decide**; una persona **revisa** lo dudoso.
- La respuesta de Groq es un **texto**; **Parse JSON** lo convierte en píldoras usando una estructura de datos.
- Un **booleano** solo vale verdadero o falso y se filtra con operadores booleanos.
- La insignia **naranja** es un aviso informativo; la **roja** pide algo obligatorio.
- Pide a la IA que **marque la duda** y úsalo para enviar esos casos a una persona.
- No envíes datos personales a un servicio externo sin saber qué se hace con ellos.

## 12. Ponlo en práctica

### Desafío: predice y comprueba

Agrega estas dos solicitudes a la pestaña `Solicitudes` y, **antes de ejecutar**, escribe en un papel a qué ruta crees que irá cada una y por qué:

| ID | Nombre | Descripción |
| --- | --- | --- |
| SOL-205 | Marta | Me cobraron dos veces la factura de este mes y no puedo pagar el arriendo |
| SOL-206 | Julia | Quisiera cambiar el correo asociado a mi cuenta cuando tengan tiempo |

Después pulsa **Run once** (sin cambiar el punto de inicio) y compara.

**Resultado esperado:** SOL-205 llega a **Urgentes** (categoría de facturación, prioridad Alta) y SOL-206 llega a **Normales** (consulta general, prioridad Normal). Ninguna pasa por la revisión humana.

### Pistas (ábrelas de a una)

<details>
<summary>Pista 1: ¿en qué debo fijarme para predecir?</summary>

Mira las restricciones del prompt: la prioridad Alta se usa solo si hay un problema que impide trabajar o una urgencia clara. Pregúntate si cada frase tiene eso.

</details>

<details>
<summary>Pista 2: no aparece ninguna fila nueva</summary>

El disparador solo entrega filas posteriores a la última que procesó. Comprueba que agregaste las filas **debajo** de las anteriores y que no cambiaste el punto de inicio.

</details>

<details>
<summary>Pista 3: la IA clasificó distinto a mi predicción</summary>

No siempre es un error: un modelo puede interpretar de otra forma. Lee la respuesta de Groq, mira el resumen que escribió y decide si ajustarías las restricciones del prompt.

</details>

<details>
<summary>Pista 4: una solicitud fue a Revisión humana y no esperaba eso</summary>

Abre la burbuja de Groq y mira `requiere_revision`. Si es verdadero, la IA dudó. Puede ser porque la frase es ambigua o porque el prompt no le da suficiente contexto.

</details>

### Cómo diagnosticar si algo no funciona

1. Abre la burbuja de **Groq**: ¿qué texto devolvió en Result?
2. Abre la burbuja de **Parse JSON**: ¿separó bien las cuatro piezas?
3. Mira las etiquetas del **Router**: ¿cuántas operaciones tuvo cada ruta?
4. Revisa la hoja de destino y compárala con tu predicción.

### Resultado real del desafío

Así quedó en nuestra cuenta de práctica:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-30-hoja-solicitudes-seis.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1077" height="498" alt="Pestaña Solicitudes con SOL-205 y SOL-206 agregadas y resaltadas."><a href="contenido/make/imagenes/m04/make-m04-30-hoja-solicitudes-seis.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Solicitudes con SOL-205 y SOL-206 agregadas y resaltadas." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las dos solicitudes nuevas.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-31-ejecucion-desafio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1346" height="567" alt="Escenario ejecutado: Urgentes con 1 operación y Normales con 1 operación."><a href="contenido/make/imagenes/m04/make-m04-31-ejecucion-desafio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Escenario ejecutado: Urgentes con 1 operación y Normales con 1 operación." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una solicitud en cada ruta, ninguna en revisión humana.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-32-urgentes-con-205.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1077" height="498" alt="Pestaña Urgentes con SOL-205, categoría Facturacion, prioridad Alta."><a href="contenido/make/imagenes/m04/make-m04-32-urgentes-con-205.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Urgentes con SOL-205, categoría Facturacion, prioridad Alta." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-205 quedó en Urgentes.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/make/imagenes/m04/make-m04-33-normales-con-206.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1077" height="498" alt="Pestaña Normales con SOL-206, categoría Consulta general, prioridad Normal."><a href="contenido/make/imagenes/m04/make-m04-33-normales-con-206.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Normales con SOL-206, categoría Consulta general, prioridad Normal." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>SOL-206 quedó en Normales.</figcaption></figure>

La coincidencia con la predicción fue completa, pero **puede variar en tu cuenta**: es normal.

## 13. Comprueba lo aprendido

```quiz
? ¿Qué rol de mensaje usamos para las instrucciones generales de la IA?
- User.
+ System.
- Assistant.
> System define cómo debe comportarse la IA. User lleva la solicitud concreta.
? ¿Por qué hace falta Parse JSON después de Groq?
- Para que Groq responda más rápido.
+ Porque la respuesta es un texto y necesitamos separarlo en datos.
- Para borrar la respuesta original.
> El texto se ve ordenado, pero solo Parse JSON lo convierte en píldoras que puedes filtrar.
? ¿Para qué sirve la parte de restricciones de un prompt?
- Para decirle a la IA su nombre.
+ Para indicar qué no debe hacer y qué hacer cuando duda.
- Para elegir el modelo.
> Sin restricciones la IA tiende a inventar una respuesta cuando no tiene información.
? ¿Qué significa la insignia naranja en un módulo?
- Que el escenario se rompió.
+ Que es un aviso informativo, por ejemplo que nadie usa sus datos.
- Que falta una conexión.
> A diferencia de la roja, un aviso naranja no impide que el escenario funcione.
? ¿Por qué los filtros de Urgentes y Normales exigen que Requiere revision sea falso?
- Para que pasen más solicitudes.
+ Para que lo que la IA marque como dudoso quede fuera y llegue solo a revisión humana.
- Porque Make lo exige.
> Así la ruta de revisión recibe únicamente lo dudoso, sin duplicados en otras rutas.
```
