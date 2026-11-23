# APIs y webhooks en n8n

En el [primer apunte de n8n](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-docker-primer-workflow) vimos cómo abrir el editor. Ahora un cliente enviará una solicitud a n8n. El workflow consultará una API, seleccionará dos campos de su respuesta y se los devolverá al cliente.

## 1. Cuándo usar Make o n8n

Antes de elegir, revisa dónde viven los datos, qué conexiones están disponibles y quién mantendrá la automatización.

| Si necesitas… | Qué conviene revisar |
| --- | --- |
| Conectar aplicaciones que el equipo ya usa | Comprueba qué operaciones cubre el conector de cada plataforma. Si falta una operación, revisa si el servicio la ofrece por API. |
| Automatizar aplicaciones SaaS sin administrar un servidor propio | Make es una opción directa si sus módulos cubren el flujo. n8n Cloud también ofrece una instalación gestionada. |
| Ejecutar el flujo en una red interna | n8n autohospedado permite elegir dónde corre. El equipo a cargo debe gestionar actualizaciones, accesos y respaldos. |
| Estimar costos | Dibuja el flujo, calcula el volumen de entradas y de llamadas, y compara los planes. En una instalación propia, incluye infraestructura y tiempo de operación. |

Por ejemplo, si un equipo ya administra sus flujos de Gmail y Google Sheets en Make, puede reutilizar esas conexiones. Si la automatización debe consultar una API que solo está disponible en una red interna, evalúa ejecutar n8n en una instancia con acceso a esa red.

## 2. Qué entra y qué sale

Una **API HTTP** define qué solicitudes acepta un servicio y cómo responde. Un **webhook** es una URL que recibe una solicitud cuando otro sistema quiere avisar de un evento o iniciar una acción. Puedes simular ese sistema enviando la solicitud desde Postman.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks/02-viaje-solicitud.webp" style="display:block;width:100%;height:auto" loading="lazy" width="1536" height="1024" alt="En una hoja de cuaderno, unos sobres ilustran el intercambio de mensajes entre Postman, n8n y PokéAPI."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks/02-viaje-solicitud.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar El viaje de una solicitud" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Postman envía un <code>POST</code> al Webhook de n8n. n8n consulta PokéAPI con un <code>GET</code> y devuelve a Postman un JSON con los campos seleccionados.</figcaption></figure>

| Tramo | Quién hace la solicitud | Qué ocurre en n8n |
| --- | --- | --- |
| Entrada · `POST` | Postman envía `{"pokemon":"ditto"}` | **Webhook** inicia el workflow y deja el JSON en `body`. |
| Consulta · `GET` | n8n solicita la ficha a PokéAPI | **HTTP Request** recibe la ficha de Ditto. |
| Respuesta | n8n devuelve el resultado a Postman | **Edit Fields** selecciona los datos y **Respond to Webhook** envía el JSON al cliente. |

El cliente puede enviar credenciales para acceder al webhook. El workflow también puede necesitar otras credenciales para consultar su API de destino. Cada servicio comprueba las credenciales de la solicitud que recibe.

## 3. Dos URLs para el mismo webhook

| URL | Cuándo utilizarla |
| --- | --- |
| **Test URL** · `/webhook-test/…` | Abre el nodo y pulsa **Listen for test event** antes de enviar el `POST`. El editor muestra el evento recibido. |
| **Production URL** · `/webhook/…` | Publica el workflow para que n8n registre esa URL. Puedes revisar lo que ocurrió en **Executions**. |

En una instalación local, ambas URLs pueden comenzar con `http://localhost:5690`. El prefijo `/webhook/` indica el modo de ejecución de n8n. La dirección `localhost` sigue apuntando al equipo donde se abre.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks/01-webhook-header-auth.png" style="display:block;width:100%;height:auto" loading="lazy" alt="Nodo Webhook de n8n con método POST, un campo Path, autenticación Header Auth y botón Listen for test event."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks/01-webhook-header-auth.png" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura del nodo Webhook" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>En esta captura de ejemplo, el nodo tiene una ruta propia y usa <strong>Header Auth</strong>. El botón naranja prepara la URL de prueba.</figcaption></figure>

## 4. Ejemplo guiado con PokéAPI

Con n8n abierto en el puerto `5690`, crea un workflow con los nodos de la tabla. Para iniciar en local, deja el Webhook con **Authentication** en **None**. Usa una rama de entrada válida y otra para contestar cuando falte el campo.

| Nodo | Configuración |
| --- | --- |
| **Webhook** | Método `POST`, **Path** `ficha-pokemon` y **Respond** en **Using 'Respond to Webhook' Node**. |
| **If** | Añade una condición **Boolean → is true** y pega la expresión de validación del bloque de abajo. Conecta **true** con **HTTP Request** y **false** con su propio **Respond to Webhook**. |
| **HTTP Request** | Usa `GET`, **Authentication** en **None** y pega la expresión de URL del segundo bloque. |
| **Edit Fields** | Usa **Manual Mapping**. Crea `pokemon` como **String** con <code>&#123;&#123; $json.name &#125;&#125;</code> e `id` como **Number** con <code>&#123;&#123; $json.id &#125;&#125;</code>. Deja **Include Other Input Fields** desactivado para devolver solo esos dos campos. |
| **Respond to Webhook** · rama válida | En **Respond With**, elige **First Incoming Item**. Devuelve los dos campos del nodo anterior con el código `200` predeterminado. |
| **Respond to Webhook** · rama inválida | En **Respond With**, elige **JSON** y usa `{"error":"Envía un nombre de Pokémon en el campo pokemon"}`. En **Options → Response Code**, indica `400`. |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks/03-dos-caminos-solicitud.webp" style="display:block;width:100%;height:auto" loading="lazy" width="1536" height="1024" alt="Una solicitud llega al nodo If. La rama superior va hacia un archivo y la rama inferior devuelve un sobre marcado con una cruz."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks/03-dos-caminos-solicitud.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Dos caminos para una solicitud" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La rama <strong>true</strong>, arriba, consulta PokéAPI y devuelve <code>200</code> si la consulta tiene éxito. La rama <strong>false</strong>, abajo, devuelve <code>400</code> cuando el dato de entrada falta o tiene un formato inválido.</figcaption></figure>

En el nodo **If**, cambia el valor a **Expression**. Esta expresión acepta nombres de hasta 40 caracteres que contengan letras sin acentos, números o guiones. Tolera espacios al comienzo o al final.

<pre><code class="language-text">&#123;&#123; typeof $json.body?.pokemon === 'string' &amp;&amp; /^[a-z0-9-]{1,40}$/.test($json.body.pokemon.trim().toLowerCase()) &#125;&#125;</code></pre>

En el nodo **HTTP Request**, cambia la URL a **Expression**. El nodo recibe el mismo ítem que salió por la rama **true** del If.

<pre><code class="language-text">&#123;&#123; 'https://pokeapi.co/api/v2/pokemon/' + $json.body.pokemon.trim().toLowerCase() + '/' &#125;&#125;</code></pre>

### Probar desde Postman

1. Vuelve al Webhook, pulsa **Listen for test event** y copia la **Test URL**. Tiene una forma como `http://localhost:5690/webhook-test/ficha-pokemon`.
2. En Postman selecciona `POST`, pega la URL y elige **Body → raw → JSON**. Envía este cuerpo.

```json
{
  "pokemon": "ditto"
}
```

3. Comprueba que la respuesta sea `200 OK` y que el cuerpo contenga `{"pokemon":"ditto","id":132}`. En n8n, abre **HTTP Request** y compara su salida con la de **Edit Fields**. La salida de la API contiene la ficha completa.
4. Reactiva la escucha antes de cada prueba con la **Test URL** y envía los casos de la tabla.

| Cuerpo de prueba | Resultado esperado |
| --- | --- |
| `{"pokemon":"  PIKACHU "}` | `200` con `pokemon` igual a `pikachu` e `id` igual a `25`. |
| `{}` | `400` con el mensaje de validación. La rama falsa responde directamente. |
| `{"pokemon":"nombre-inexistente-demo"}` | El formato pasa la validación, pero la API devuelve `404` al **HTTP Request**. Con la configuración predeterminada, el nodo falla y n8n responde `500` a Postman porque el workflow se detiene antes de **Respond to Webhook**. |

Si Postman devuelve `404` en la URL de prueba y el editor sigue sin recibir un evento, revisa que el método, la URL y el modo de escucha coincidan. Si la ejecución sí aparece y el error empieza en **HTTP Request**, revisa la respuesta de la API en ese nodo.

### Probar el acceso con una cabecera

Cuando el flujo funcione, cambia la autenticación del Webhook a **Header Auth**. Crea una credencial con **Name** `X-Lab-Token` y un valor de prueba propio. En Postman, añade esa cabecera en **Headers**. Vuelve a enviar el cuerpo de Ditto con el valor correcto y luego quita la cabecera para comprobar que n8n rechaza la segunda solicitud. Reactiva la escucha según corresponda. Usa los campos de credenciales de n8n para guardar secretos.

## Autoevaluación

```quiz
? Postman envía un evento y n8n consulta otra API. ¿Qué nodo recibe el evento?
- HTTP Request.
+ Webhook.
- Edit Fields.
> Webhook inicia el flujo con la solicitud entrante. HTTP Request hace la llamada saliente.
? ¿Qué paso habilita la Test URL desde el editor?
+ Pulsar Listen for test event.
- Exportar el workflow como JSON.
- Cambiar el método de POST a GET.
> La escucha registra temporalmente la URL de prueba para recibir una solicitud.
? ¿Qué debe coincidir cuando el Webhook usa Header Auth?
- El nombre del workflow con el método HTTP.
- El identificador del Pokémon con el puerto de n8n.
+ El nombre y el valor de la cabecera con los de la credencial de entrada.
> La autenticación verifica la cabecera de la solicitud que recibe el webhook.
? El cliente recibe 400 al enviar un JSON sin el campo pokemon. ¿Qué parte del ejemplo respondió?
+ Respond to Webhook en la rama falsa del If.
- HTTP Request después de consultar PokéAPI.
- Edit Fields al convertir el identificador en texto.
> La rama falsa responde al cliente antes de consultar la API.
```

## Documentación de referencia

- [Nodo Webhook de n8n](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [Configuración de HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [Configuración de Respond to Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/)
- [Credenciales de Webhook en n8n](https://docs.n8n.io/integrations/builtin/credentials/webhook/)
- [Alojamiento de n8n](https://docs.n8n.io/hosting/)
- [Webhooks en Make](https://help.make.com/webhooks)
- [Referencia de PokéAPI](https://pokeapi.co/docs/v2#pokemon)
