# Cómo manejar errores y leer ejecuciones en n8n

Una biblioteca recibe solicitudes para consultar su catálogo. Si el servicio responde, la biblioteca muestra cuántos ejemplares están disponibles. Si el servicio falla, la respuesta depende de la consulta. Una ficha opcional puede quedar pendiente. Para confirmar disponibilidad hace falta un dato válido del catálogo.

Aquí construirás, paso a paso, un workflow que sabe volver a intentar una consulta, continuar por una ruta de contingencia y registrar una falla que detiene la ejecución. Es la continuación de la [biblioteca de loops y subworkflows](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-loops-subworkflows), con los mismos libros, pero es un ejercicio independiente: no necesitas haber importado nada de ese apunte.

## 1. El problema de la biblioteca

La biblioteca ofrece un servicio de consulta de disponibilidad. Alguien pregunta por un libro y n8n pregunta a una API ficticia del catálogo. Ese catálogo puede:

1. responder bien;
2. fallar un momento y recuperarse;
3. quedar fuera de servicio;
4. responder bien que no quedan ejemplares.

Cada caso exige una decisión distinta: confirmar el dato, continuar con una contingencia o dejar registrada una falla. Estos son los libros del catálogo ficticio:

| Libro | Total | Préstamos | Disponibles |
| --- | ---: | ---: | ---: |
| El faro de papel | 5 | 2 | 3 |
| Jardines de tinta | 4 | 4 | 0 |
| Atlas de las nubes verdes | 7 | 1 | 6 |
| La casa de los mapas | 3 | 0 | 3 |
| Viaje al bosque azul | 6 | 4 | 2 |
| Historias del reloj | 8 | 3 | 5 |

Todos los títulos y registros son ficticios.

## 2. Qué vas a lograr y qué necesitas saber

Al terminar sabrás:

- configurar reintentos en un nodo y enviar sus fallas por una salida de error;
- construir un workflow de errores con **Error Trigger** y vincularlo con otro workflow;
- detener una ejecución a propósito con **Stop And Error**;
- leer **Executions** para distinguir una ejecución correcta, una degradada y una fallida;
- usar **Retry execution** y entender qué vuelve a ejecutar.

Necesitas Docker con Docker Compose para levantar n8n y el simulador del catálogo, y haber usado antes un **Webhook**, **Edit Fields** e **IF**. No necesitas programar. Las capturas corresponden a **n8n 2.44.6**: si tu versión muestra otros nombres, los explicamos donde cambian.

## 3. Una respuesta válida no siempre es una respuesta buena

Antes de construir, separa tres ideas que parecen parecidas.

| Respuesta del catálogo | Qué significa | Cómo debe tratarla el flujo |
| --- | --- | --- |
| HTTP `200` con `disponibles: 3` | El catálogo respondió y hay ejemplares. | Confirmar la disponibilidad. |
| HTTP `200` con `disponibles: 0` | El catálogo respondió y no quedan ejemplares. | Confirmar que hay cero. No es un error. |
| HTTP `503` | El servicio no está disponible por ahora. | Reintentar, y si sigue fallando, decidir según el tipo de consulta. |

El valor `0` es un dato conocido. Cuando el servicio no responde, la biblioteca no sabe cuántos ejemplares hay, y eso se expresa con `null`. Confundir ambos produciría información falsa: decir «no hay ejemplares» cuando en realidad no se pudo consultar.

También conviene distinguir dos niveles de falla:

- **Error de un nodo:** un nodo no puede completar su trabajo, por ejemplo **HTTP Request** recibe un `503`. Puedes manejarlo dentro del mismo workflow.
- **Falla completa del workflow:** la ejecución termina en estado de error. Puedes avisar a otro workflow para que registre el incidente.

## 4. Arquitectura general

El ejemplo usa dos workflows y un simulador del catálogo:

- **Workflow principal.** Recibe la consulta por un webhook, pregunta al catálogo con un **HTTP Request** y, según lo que responda, sigue por la ruta correcta, por una contingencia (consulta opcional) o por una falla crítica (consulta obligatoria).
- **Workflow de errores.** Empieza en **Error Trigger** y registra el incidente cuando el principal falla.
- **Simulador del catálogo.** Un servicio HTTP que puede responder bien o fallar a propósito.

Las dos capturas siguientes muestran los dos workflows terminados.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/01-flujo-principal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow principal con el webhook, la consulta al catálogo, la ruta correcta, la contingencia y la falla crítica."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/01-flujo-principal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow principal con el webhook, la consulta al catálogo, la ruta correcta, la contingencia y la falla crítica." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El workflow principal. De la salida <b>Error</b> de <b>Consultar catálogo</b> parten dos caminos: contingencia para consultas opcionales y falla crítica para las obligatorias.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/04-flujo-de-error.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow de incidentes con Error Trigger, Preparar registro del incidente y Registro final para inspección."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/04-flujo-de-error.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow de incidentes con Error Trigger, Preparar registro del incidente y Registro final para inspección." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El workflow de errores es independiente. Empieza en <b>Error Trigger</b> y termina en un nodo donde puedes inspeccionar el registro desde <b>Executions</b>.</figcaption></figure>

## 5. Prepara el simulador del catálogo

**¿Qué estamos haciendo?** Levantamos un servicio HTTP pequeño que representa al catálogo y que puede fallar a propósito.

**¿Para qué sirve?** Para provocar errores reales y repetibles. El nodo **HTTP Request** recibirá un `503` de verdad, no un error fingido con un **IF**.

**¿Cómo lo configuramos?** El simulador va incluido en el paquete que descargas al final del apunte. Descomprímelo, abre una terminal en esa carpeta y ejecuta:

<pre><code class="language-text">docker compose up -d</code></pre>

Esto inicia dos contenedores en la misma red: **n8n** (en `http://localhost:5678`) y el **catálogo** simulado. No tienes que crear ni construir nada. Si tu puerto 5678 está ocupado, usa `N8N_PUERTO=5679 docker compose up -d`.

El simulador responde según el campo `escenario` de cada consulta:

| Escenario | Respuestas del simulador | Qué practicas |
| --- | --- | --- |
| `exito` | 200 | Consulta confirmada. |
| `temporal` | 503 y luego 200 | Recuperación con reintentos. |
| `caida` | 503, 503, 503 | Contingencia o falla crítica, según el tipo de consulta. |
| `sin_stock` | 200 con 0 ejemplares | Un cero que no es un error. |

Además lleva un contador por solicitud. Puedes leerlo en `http://localhost:8081/intentos?solicitud_id=LIB-201` para saber cuántas peticiones recibió.

**¿Qué resultado debemos observar?** Al abrir `http://localhost:8081/salud` verás `"estado": "activo"`.

**Importante:** dentro de un contenedor, `localhost` apunta al propio contenedor, no a tu computador. Por eso el workflow llamará al catálogo con el nombre de su servicio, `http://catalogo:8080`. Si ya tienes un n8n instalado, el README del paquete explica cómo conectarlo.

## 6. Crea el workflow principal

**¿Qué estamos haciendo?** Armamos la entrada del workflow: un webhook que recibe la consulta y un nodo que ordena los datos.

**¿Para qué sirve?** Todo lo que sigue necesita saber cuatro cosas: qué solicitud es, qué libro se consulta, si la consulta es opcional u obligatoria y cómo debe comportarse el simulador.

**¿Cómo lo configuramos?**

1. Abre n8n en `http://localhost:5678`. Crea tu cuenta local la primera vez. Crea un workflow nuevo desde **Create workflow**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/15-nuevo-workflow-vacio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lienzo vacío de n8n con el botón Add first step."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/15-nuevo-workflow-vacio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lienzo vacío de n8n con el botón Add first step." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un workflow nuevo empieza vacío. El recuadro <b>Add first step</b> abre el selector de nodos.</figcaption></figure>

2. Pulsa **Add first step**, escribe `Webhook` y elige **Webhook**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/16-selector-webhook.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Selector de nodos con la búsqueda Webhook y las opciones Webhook y Respond to Webhook."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/16-selector-webhook.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Selector de nodos con la búsqueda Webhook y las opciones Webhook y Respond to Webhook." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El selector muestra los disparadores. Elige <b>Webhook</b>: es el que inicia el workflow cuando alguien llama a su dirección.</figcaption></figure>

3. Cambia el nombre del nodo a **Recibir consulta** y configura:

| Campo | Valor |
| --- | --- |
| **HTTP Method** | `POST` |
| **Path** | `consulta-disponibilidad` |
| **Respond** | `Using 'Respond to Webhook' Node` |

La opción **Respond** le indica a n8n que la respuesta la enviará un nodo **Respond to Webhook** más adelante. Así puedes responder distinto en cada ruta.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/21-webhook-parametros.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Parámetros del nodo Webhook con método POST, ruta consulta-disponibilidad y respuesta mediante un nodo Respond to Webhook."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/21-webhook-parametros.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Parámetros del nodo Webhook con método POST, ruta consulta-disponibilidad y respuesta mediante un nodo Respond to Webhook." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Configuración del nodo <b>Recibir consulta</b>.</figcaption></figure>

El nodo muestra dos direcciones. La **Test URL** solo funciona mientras el editor está escuchando un evento de prueba. La **Production URL** funciona cuando el workflow está publicado y es la que usaremos en todas las pruebas.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/27-webhook-url-produccion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo Webhook con la pestaña Production URL seleccionada y su dirección."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/27-webhook-url-produccion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Webhook con la pestaña Production URL seleccionada y su dirección." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La pestaña <b>Production URL</b>. El puerto depende de tu instalación: en tu equipo puede ser 5678.</figcaption></figure>

4. Agrega **Edit Fields** y llámalo **Preparar solicitud**. Estos campos copian los datos que llegan en el cuerpo de la consulta (`body`):

| Campo | Tipo | Expresión |
| --- | --- | --- |
| `solicitud_id` | String | <code>&#123;&#123; $json.body.solicitud_id &#125;&#125;</code> |
| `titulo` | String | <code>&#123;&#123; $json.body.titulo &#125;&#125;</code> |
| `tipo_consulta` | String | <code>&#123;&#123; $json.body.tipo_consulta &#125;&#125;</code> |
| `escenario` | String | <code>&#123;&#123; $json.body.escenario &#125;&#125;</code> |

Una expresión se escribe entre dobles llaves. `$json` representa el ítem que llega al nodo, y `body` es el JSON que envió quien hizo la consulta. Por ejemplo, <code>&#123;&#123; $json.body.titulo &#125;&#125;</code> entrega `El faro de papel` cuando la consulta trae ese título.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/22-preparar-solicitud.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo Edit Fields con los campos solicitud_id, titulo, tipo_consulta y escenario tomados del cuerpo de la consulta."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/22-preparar-solicitud.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Edit Fields con los campos solicitud_id, titulo, tipo_consulta y escenario tomados del cuerpo de la consulta." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El nodo <b>Preparar solicitud</b> deja los cuatro datos al mismo nivel, listos para usarlos.</figcaption></figure>

La consulta que enviarás tiene esta forma. Los valores admitidos de `tipo_consulta` son `opcional` y `obligatoria`, y los de `escenario` son `exito`, `temporal`, `caida` y `sin_stock`:

<pre><code class="language-text">{
  "solicitud_id": "LIB-201",
  "titulo": "El faro de papel",
  "tipo_consulta": "obligatoria",
  "escenario": "exito"
}</code></pre>

**¿Qué resultado debemos observar?** Dos nodos conectados: **Recibir consulta** y **Preparar solicitud**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/17-etapa-1-webhook-y-preparar.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lienzo con los nodos Recibir consulta y Preparar solicitud conectados."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/17-etapa-1-webhook-y-preparar.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lienzo con los nodos Recibir consulta y Preparar solicitud conectados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Primera etapa del workflow: la entrada.</figcaption></figure>

## 7. Configura HTTP Request

**¿Qué estamos haciendo?** Agregamos el nodo que consulta al catálogo.

**¿Para qué sirve?** Es el único punto del flujo que depende de un servicio externo y por eso es donde pueden ocurrir las fallas.

**¿Cómo lo configuramos?** Agrega **HTTP Request**, llámalo **Consultar catálogo** y completa:

| Campo | Valor |
| --- | --- |
| **Method** | `GET` |
| **URL** | `http://catalogo:8080/disponibilidad` |
| **Send Query Parameters** | Activado |

En **Query Parameters** agrega tres pares. Cada valor es una expresión que lee un campo de **Preparar solicitud**:

| Name | Value |
| --- | --- |
| `solicitud_id` | <code>&#123;&#123; $json.solicitud_id &#125;&#125;</code> |
| `titulo` | <code>&#123;&#123; $json.titulo &#125;&#125;</code> |
| `escenario` | <code>&#123;&#123; $json.escenario &#125;&#125;</code> |

Usamos `GET` porque solo leemos información. Repetir una lectura no cambia nada en el catálogo, así que reintentarla es seguro.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/02-http-parametros.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo HTTP Request con método GET y la URL del catálogo resaltada."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/02-http-parametros.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo HTTP Request con método GET y la URL del catálogo resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La dirección <code>catalogo</code> es el nombre del servicio del simulador dentro de la red de Docker.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/33-http-parametros-consulta.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Parámetros de consulta solicitud_id, titulo y escenario con sus expresiones."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/33-http-parametros-consulta.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Parámetros de consulta solicitud_id, titulo y escenario con sus expresiones." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los tres parámetros viajan en la dirección como <code>?solicitud_id=...&titulo=...&escenario=...</code>.</figcaption></figure>

**¿Qué resultado debemos observar?** Cuando el catálogo responde `200`, el nodo entrega el libro con `ejemplares_totales`, `prestamos_activos` y `disponibles`. Si recibe un `503`, el nodo falla. Para que un `503` cuente como error no actives **Never Error**, que está en las opciones de respuesta del nodo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/18-etapa-2-consulta-http.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lienzo con el nodo Consultar catálogo conectado a Preparar solicitud y una nota sobre los reintentos."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/18-etapa-2-consulta-http.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lienzo con el nodo Consultar catálogo conectado a Preparar solicitud y una nota sobre los reintentos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Segunda etapa: la consulta al catálogo.</figcaption></figure>

## 8. Agrega los reintentos

**¿Qué estamos haciendo?** Le decimos al nodo que vuelva a intentar la consulta si falla.

**¿Para qué sirve?** Muchas interrupciones duran un instante. Un segundo intento puede recuperar la consulta sin que nadie tenga que intervenir.

**¿Cómo lo configuramos?** Abre **Consultar catálogo** y ve a la pestaña **Settings**:

| Opción | Valor | Qué significa |
| --- | --- | --- |
| **Retry On Fail** | Activado | Repite el nodo cuando la llamada se considera un error. |
| **Max. Tries** | `3` | Intentos en total: una llamada inicial y hasta dos repeticiones. |
| **Wait Between Tries (ms)** | `1000` | Espera de un segundo entre intentos. |
| **On Error** | `Continue (using error output)` | Si se agotan los intentos, el ítem sale por una salida llamada **Error**. |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/03-http-settings.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Pestaña Settings de HTTP Request con Retry On Fail activado, Max. Tries 3, Wait Between Tries 1000 y On Error con la salida de error."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/03-http-settings.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pestaña Settings de HTTP Request con Retry On Fail activado, Max. Tries 3, Wait Between Tries 1000 y On Error con la salida de error." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los cuatro ajustes que gobiernan el comportamiento ante fallas.</figcaption></figure>

**On Error** ofrece tres opciones:

| Opción | Efecto |
| --- | --- |
| **Stop Workflow** | Detiene el flujo y la ejecución queda como fallida. |
| **Continue** | Permite avanzar por la salida normal tras el error. El resultado que recibe el nodo siguiente depende del nodo que falló. |
| **Continue (using error output)** | Envía la información del error por una salida separada para que el flujo pueda decidir qué hacer. |

**Continue On Fail** puede aparecer en materiales de versiones anteriores. En la interfaz actual esa idea está dentro de **On Error**.

**Cuándo reintentar y cuándo no.** Reintenta cuando la operación se puede repetir sin consecuencias, como una consulta `GET`. Ten cuidado con las operaciones que modifican datos, como crear un pedido o enviar un correo: si la primera llamada sí llegó pero la respuesta se perdió, un reintento duplicaría el efecto. En esos casos conviene una operación que reconozca repeticiones, por ejemplo con un identificador único por solicitud.

**¿Qué resultado debemos observar?** El nodo **Consultar catálogo** muestra ahora dos salidas, **Success** y **Error**, y un pequeño icono de reintento.

## 9. Encauza las rutas de éxito y de error

### La ruta correcta

Conecta la salida **Success** a un **Edit Fields** llamado **Confirmar disponibilidad**:

| Campo | Tipo | Expresión |
| --- | --- | --- |
| `solicitud_id` | String | <code>&#123;&#123; $('Preparar solicitud').item.json.solicitud_id &#125;&#125;</code> |
| `estado` | String | `confirmado` |
| `titulo` | String | <code>&#123;&#123; $json.titulo &#125;&#125;</code> |
| `disponibles` | Number | <code>&#123;&#123; $json.disponibles &#125;&#125;</code> |

<code>&#123;&#123; $('Preparar solicitud').item.json.solicitud_id &#125;&#125;</code> pide al nodo **Preparar solicitud** el identificador del ítem que corresponde. Lo necesitamos porque la respuesta del catálogo no trae todos los datos de la solicitud. El campo `disponibles` es numérico, de modo que un `0` se conserva como `0` y no se transforma en vacío.

Después agrega **Respond to Webhook**, llámalo **Responder consulta** y deja **Respond With** en `First Incoming Item`: responderá con el resultado que acaba de armarse.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/19-etapa-3-ruta-correcta.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lienzo con la ruta correcta: Consultar catálogo, Confirmar disponibilidad y Responder consulta."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/19-etapa-3-ruta-correcta.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lienzo con la ruta correcta: Consultar catálogo, Confirmar disponibilidad y Responder consulta." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tercera etapa: la ruta correcta ya responde al cliente.</figcaption></figure>

### La ruta de error

Conecta la salida **Error** a un **IF** llamado **¿Consulta opcional?**. Su condición compara el tipo de consulta con el texto `opcional`:

<pre><code class="language-text">Valor 1: &#123;&#123; $('Preparar solicitud').item.json.tipo_consulta &#125;&#125;
Operador: String, is equal to
Valor 2: opcional</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/23-if-condicion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo IF que compara tipo_consulta con la palabra opcional."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/23-if-condicion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo IF que compara tipo_consulta con la palabra opcional." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Si la condición es verdadera, la consulta puede continuar con una contingencia. Si es falsa, es obligatoria.</figcaption></figure>

**Salida verdadera: contingencia.** Agrega **Edit Fields** con el nombre **Registrar contingencia**, modo **JSON**, y este contenido. Observa que `disponibles` vale `null`: la biblioteca desconoce el dato.

<pre><code class="language-text">{
  "solicitud_id": "&#123;&#123; $('Preparar solicitud').item.json.solicitud_id &#125;&#125;",
  "estado": "degradado",
  "disponibles": null,
  "motivo": "catalogo_no_disponible"
}</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/24-registrar-contingencia.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo Edit Fields en modo JSON con el resultado degradado y disponibles en null."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/24-registrar-contingencia.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Edit Fields en modo JSON con el resultado degradado y disponibles en null." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El resultado degradado indica que la falla se gestionó pero la disponibilidad no pudo confirmarse.</figcaption></figure>

Conecta este nodo también a **Responder consulta**: un nodo puede recibir datos desde más de una ruta.

**Salida falsa: falla crítica.** Una consulta obligatoria no puede continuar sin el dato. Agrega, en este orden:

1. **Edit Fields** en modo **JSON**, llamado **Preparar error crítico**, con `solicitud_id`, `estado: "error"`, `motivo: "catalogo_no_disponible"` y un mensaje corto.
2. **Respond to Webhook** llamado **Responder con error**. En **Options** agrega **Response Code** con el valor `503`.
3. **Stop And Error** llamado **Detener ejecución**, con **Error Type** `Error Message`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/25-responder-con-error.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo Respond to Webhook con First Incoming Item y código de respuesta 503."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/25-responder-con-error.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Respond to Webhook con First Incoming Item y código de respuesta 503." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El cliente recibe un <code>503</code> con un mensaje claro.</figcaption></figure>

El mensaje de **Stop And Error** incluye el identificador de la solicitud, porque más adelante el manejador lo leerá desde el texto del error:

<pre><code class="language-text">Consulta obligatoria sin respuesta del catálogo. solicitud_id=&#123;&#123; $('Preparar solicitud').item.json.solicitud_id &#125;&#125;</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/26-stop-and-error.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo Stop And Error con un mensaje que incluye el identificador de la solicitud."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/26-stop-and-error.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Stop And Error con un mensaje que incluye el identificador de la solicitud." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><b>Stop And Error</b> hace fallar la ejecución a propósito y deja un mensaje que se puede buscar.</figcaption></figure>

**¿Por qué responder antes de detener?** Primero el flujo envía el `503` al cliente y después ejecuta **Stop And Error**. En las pruebas comprobamos que el cliente recibe su respuesta y que la ejecución queda igualmente como fallida.

**¿Qué resultado debemos observar?** Un workflow con tres caminos desde **Consultar catálogo**: correcto, contingencia y falla crítica.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/20-etapa-4-ruta-opcional.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lienzo con la ruta de contingencia agregada a continuación del nodo IF."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/20-etapa-4-ruta-opcional.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lienzo con la ruta de contingencia agregada a continuación del nodo IF." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cuarta etapa: la ruta opcional. Falta agregar la falla crítica para obtener el workflow completo de la primera captura.</figcaption></figure>

## 10. Construye el workflow de errores

**¿Qué estamos haciendo?** Creamos un segundo workflow cuyo único trabajo es registrar incidentes.

**¿Para qué sirve?** Cuando el flujo principal falla, n8n puede avisar a otro workflow. Ahí concentras el registro de incidentes: dónde falló, cuándo y por qué.

**¿Cómo lo configuramos?** Crea un workflow nuevo con el nombre **Biblioteca | Registro de incidentes** y agrega **Error Trigger** como primer nodo. Este nodo no tiene parámetros: solo se activa cuando otro workflow que lo tiene vinculado falla en una ejecución automática.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/28-error-trigger-config.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo Error Trigger con el aviso de que se ejecuta cuando hay un error en otro workflow."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/28-error-trigger-config.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Error Trigger con el aviso de que se ejecuta cuando hay un error en otro workflow." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><b>Error Trigger</b> no tiene parámetros. Recibe los datos del error desde n8n.</figcaption></figure>

Conecta un **Edit Fields** llamado **Preparar registro del incidente**. Error Trigger entrega, entre otros datos, el nombre del workflow, el identificador de la ejecución fallida, el último nodo que se ejecutó y el mensaje del error. Solo guardamos lo que entrega:

| Campo | Expresión | Qué obtiene |
| --- | --- | --- |
| `solicitud_id` | <code>&#123;&#123; ($json.execution.error.message.match(/solicitud_id=([A-Z0-9-]+)/) \|\| [])[1] \|\| 'sin_dato' &#125;&#125;</code> | El identificador que escribimos en el mensaje de Stop And Error. |
| `workflow` | <code>&#123;&#123; $json.workflow.name &#125;&#125;</code> | Nombre del workflow que falló. |
| `execution_id` | <code>&#123;&#123; $json.execution.id &#125;&#125;</code> | ID de la ejecución fallida. |
| `nodo` | <code>&#123;&#123; $json.execution.lastNodeExecuted &#125;&#125;</code> | Último nodo ejecutado. |
| `mensaje` | <code>&#123;&#123; $json.execution.error.message &#125;&#125;</code> | Texto del error. |
| `modo` | <code>&#123;&#123; $json.execution.mode &#125;&#125;</code> | Cómo se inició la ejecución. |
| `fecha` | <code>&#123;&#123; $now.toISO() &#125;&#125;</code> | Fecha y hora del registro. |

Error Trigger no incluye por sí solo el identificador de la solicitud. Por eso el mensaje de **Stop And Error** lo lleva escrito, y la primera expresión lo recupera: `match` busca el texto `solicitud_id=` seguido de letras, números o guiones, y `[1]` toma lo que quedó entre paréntesis. Si no lo encuentra, escribe `sin_dato` en vez de fallar.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/29-preparar-registro-config.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo Edit Fields con los primeros campos del registro del incidente."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/29-preparar-registro-config.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Edit Fields con los primeros campos del registro del incidente." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Primeros campos del registro: la solicitud, el workflow y la ejecución.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/34-preparar-registro-campos-finales.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Últimos campos del registro: nodo, mensaje, modo y fecha."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/34-preparar-registro-campos-finales.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Últimos campos del registro: nodo, mensaje, modo y fecha." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Últimos campos: el nodo donde se detuvo, el mensaje, el modo y la fecha.</figcaption></figure>

Termina con un nodo **No Operation, do nothing** llamado **Registro final para inspección**. No hace nada, pero deja guardados los datos para que los leas desde **Executions**.

**¿Qué resultado debemos observar?** Tres nodos conectados en secuencia, como en la captura de la sección 4.

## 11. Publica y vincula los workflows

**¿Qué estamos haciendo?** Dejamos listos los dos workflows y conectamos el principal con su manejador.

**¿Para qué sirve?** Sin el vínculo, el workflow de errores nunca se entera de las fallas.

**¿Cómo lo configuramos?**

1. **Publica primero el workflow de errores.** En n8n 2.44.6 un Error Workflow solo aparece como opción si está publicado. Pulsa **Publish**, escribe un nombre de versión (por ejemplo, `Versión 1`) y confirma. En versiones anteriores el equivalente era activar el workflow.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/30-publicar-manejador.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Cuadro Publish workflow con el nombre de versión del workflow de incidentes."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/30-publicar-manejador.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Cuadro Publish workflow con el nombre de versión del workflow de incidentes." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Publicar pide un nombre de versión.</figcaption></figure>

2. En el workflow principal abre el menú `...`, elige **Settings** y en **Error Workflow (to notify when this one errors)** selecciona **Biblioteca | Registro de incidentes**. Pulsa **Save**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/05-vinculo-error-workflow.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Diálogo Workflow settings con el Error Workflow resaltado y el manejador seleccionado."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/05-vinculo-error-workflow.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Diálogo Workflow settings con el Error Workflow resaltado y el manejador seleccionado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El vínculo vive en la configuración del workflow que puede fallar, no en el manejador.</figcaption></figure>

3. Publica el workflow principal.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/31-publicar-principal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Cuadro Publish workflow del workflow principal."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/31-publicar-principal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Cuadro Publish workflow del workflow principal." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Publicar el workflow principal registra su webhook de producción.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/32-principal-publicado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Mensaje de n8n indicando que el workflow quedó publicado y puede recibir llamadas a su URL de producción."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/32-principal-publicado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Mensaje de n8n indicando que el workflow quedó publicado y puede recibir llamadas a su URL de producción." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras publicar, n8n avisa que las llamadas a la URL de producción no se dibujan en el lienzo: se leen en <b>Executions</b>.</figcaption></figure>

**¿Qué resultado debemos observar?** El workflow principal muestra el estado **Published**. Si la lista de **Error Workflow** muestra el manejador en gris, todavía no está publicado.

## 12. Ejecuta las pruebas

**¿Qué estamos haciendo?** Enviamos los cinco casos y comparamos lo que ocurre con lo que esperamos.

**¿Cómo lo hacemos?** Envía cada consulta a la **Production URL** con `curl`, Postman o el script `probar_escenarios.py` del paquete. Una ejecución manual desde el editor no basta: el Error Workflow solo se dispara con ejecuciones automáticas, como las del webhook de producción. Ejemplo con el primer caso:

<pre><code class="language-text">curl -X POST http://localhost:5678/webhook/consulta-disponibilidad \
  -H "Content-Type: application/json" \
  -d '{"solicitud_id":"LIB-201","titulo":"El faro de papel","tipo_consulta":"obligatoria","escenario":"exito"}'</code></pre>

Estos son los resultados que debes obtener:

| Solicitud | Escenario | Tipo | Respuesta que recibes | Peticiones del simulador |
| --- | --- | --- | --- | --- |
| LIB-201 | `exito` | obligatoria | 200, `confirmado`, `disponibles: 3` | 200 |
| LIB-202 | `temporal` | obligatoria | 200, `confirmado`, `disponibles: 6` | 503 y 200 |
| LIB-203 | `caida` | opcional | 200, `degradado`, `disponibles: null` | 503, 503 y 503 |
| LIB-204 | `caida` | obligatoria | 503, `error`. La ejecución falla | 503, 503 y 503 |
| LIB-205 | `sin_stock` | obligatoria | 200, `confirmado`, `disponibles: 0` | 200 |

### Caso 1: consulta correcta
El catálogo responde `200` en el primer intento. La ejecución sigue por **Success**, confirma la disponibilidad y responde.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/06-exito-normal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución de la consulta correcta con la ruta verde por Success, Confirmar disponibilidad y Responder consulta."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/06-exito-normal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la consulta correcta con la ruta verde por Success, Confirmar disponibilidad y Responder consulta." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Ejecución de LIB-201. Los nodos resaltados en verde muestran la ruta que recorrió el flujo.</figcaption></figure>

### Caso 2: falla temporal y recuperación
El primer intento recibe `503`. n8n espera un segundo y repite la llamada, y esta vez el catálogo responde `200`. Desde afuera solo ves una respuesta correcta un poco más lenta (alrededor de 1,5 segundos en las pruebas). El simulador registra las dos peticiones, y es la evidencia de que el mismo nodo hizo los reintentos.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/07-reintento-recuperado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución de la consulta con falla temporal, recuperada por el reintento."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/07-reintento-recuperado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la consulta con falla temporal, recuperada por el reintento." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Ejecución de LIB-202. En el nodo <b>Consultar catálogo</b> el icono de reintento indica que el nodo repitió la llamada.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/35-simulador-intentos-temporal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Respuesta del simulador para LIB-202 con dos peticiones: 503 y 200."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/35-simulador-intentos-temporal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Respuesta del simulador para LIB-202 con dos peticiones: 503 y 200." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El simulador recibió dos peticiones para LIB-202: la primera respondió 503 y la segunda 200.</figcaption></figure>

### Caso 3: caída en una consulta opcional
Los tres intentos reciben `503`. El ítem sale por **Error**, el IF detecta que la consulta es opcional y la ejecución continúa con la contingencia. La respuesta es `200` con `estado: degradado` y `disponibles: null`. La ejecución aparece como correcta aunque el catálogo falló: lo que la distingue es el campo `estado`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/08-contingencia.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución con la salida Error de Consultar catálogo, el IF y Registrar contingencia."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/08-contingencia.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución con la salida Error de Consultar catálogo, el IF y Registrar contingencia." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Ejecución de LIB-203: la ruta pasó por la salida de error y terminó en la contingencia.</figcaption></figure>

### Caso 4: caída en una consulta obligatoria
Los tres intentos fallan y el IF envía la ejecución a la falla crítica. El cliente recibe `503`, **Stop And Error** hace fallar la ejecución y n8n activa el workflow de errores. Esta ejecución queda en rojo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/09-ejecucion-fallida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución fallida con el nodo Detener ejecución en rojo y el mensaje del error."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/09-ejecucion-fallida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución fallida con el nodo Detener ejecución en rojo y el mensaje del error." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Ejecución de LIB-204: el nodo <b>Detener ejecución</b> quedó en rojo y n8n muestra el mensaje con el identificador de la solicitud.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/36-simulador-intentos-caida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Respuesta del simulador para LIB-204 con tres peticiones 503."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/36-simulador-intentos-caida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Respuesta del simulador para LIB-204 con tres peticiones 503." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Para LIB-204 el simulador recibió tres peticiones y respondió 503 las tres veces: los tres intentos configurados.</figcaption></figure>

### Caso 5: sin ejemplares
El catálogo responde correctamente que quedan cero ejemplares. No es una falla: el resultado es `confirmado` con `disponibles: 0`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/13-disponibilidad-cero.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución de la consulta sin ejemplares por la ruta correcta."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/13-disponibilidad-cero.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la consulta sin ejemplares por la ruta correcta." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Ejecución de LIB-205. Por tratarse de una respuesta válida, el flujo sigue por <b>Success</b>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/42-disponibilidad-cero-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Confirmar disponibilidad con disponibles igual a 0."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/42-disponibilidad-cero-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Confirmar disponibilidad con disponibles igual a 0." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El campo numérico <code>disponibles</code> conserva el <code>0</code>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/11-simulador-http.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Registro del simulador con los contadores por solicitud y las primeras peticiones recibidas."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/11-simulador-http.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registro del simulador con los contadores por solicitud y las primeras peticiones recibidas." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El registro completo del simulador, con las peticiones de todas las solicitudes.</figcaption></figure>

## 13. Depura: lee las ejecuciones

**¿Qué estamos haciendo?** Aprendemos a leer lo que n8n guardó de cada ejecución.

**¿Para qué sirve?** En producción nadie mira el lienzo mientras corre el flujo. Cuando algo falla, la evidencia está en **Executions**.

### Encuentra la ejecución

Abre el workflow principal y pulsa la pestaña **Executions**. Cada fila es una ejecución, con su fecha, su estado y su duración. Las correctas dicen **Succeeded** y la fallida dice **Error**. Las dos que terminaron bien y las que usaron la contingencia se ven iguales en la lista: abre la ejecución para distinguirlas.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/37-executions-lista.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lista de ejecuciones del workflow principal con cuatro correctas y una fallida."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/37-executions-lista.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de ejecuciones del workflow principal con cuatro correctas y una fallida." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La lista de <b>Executions</b>. Se ve la ejecución fallida entre las correctas.</figcaption></figure>

### Revisa el nodo que falló

Abre la ejecución fallida y haz doble clic en un nodo para ver lo que recibió y lo que entregó. En **Detener ejecución** aparece el mensaje del error. En **Consultar catálogo**, la pestaña **Error Branch** muestra el detalle de la última respuesta: el código `503` y el cuerpo que envió el simulador.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/40-stop-and-error-detalle.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo Detener ejecución con el mensaje de error y el ítem de entrada."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/40-stop-and-error-detalle.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Detener ejecución con el mensaje de error y el ítem de entrada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>A la izquierda está lo que recibió el nodo y a la derecha, el mensaje del error.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/41-http-error-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida Error del nodo Consultar catálogo con el detalle del 503."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/41-http-error-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida Error del nodo Consultar catálogo con el detalle del 503." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La rama <b>Error Branch</b> de <b>Consultar catálogo</b> conserva el detalle del problema, útil para saber qué respondió el servicio.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/38-http-reintento-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida Success de Consultar catálogo en la ejecución de la falla temporal."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/38-http-reintento-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida Success de Consultar catálogo en la ejecución de la falla temporal." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>En la falla temporal solo ves la salida final: el nodo entregó la respuesta correcta del segundo intento.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/39-contingencia-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida del nodo Registrar contingencia con estado degradado y disponibles null."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/39-contingencia-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida del nodo Registrar contingencia con estado degradado y disponibles null." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ejecución degradada terminó como correcta. El estado <code>degradado</code> y el <code>null</code> la distinguen de una confirmada.</figcaption></figure>

### Encuentra el registro del incidente

El incidente no está en el workflow principal sino en el de errores. Abre **Biblioteca | Registro de incidentes** y su pestaña **Executions**: encontrarás una ejecución con el modo `error`, iniciada por **Error Trigger**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/43-executions-manejador.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lista de ejecuciones del workflow de incidentes con una ejecución exitosa."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/43-executions-manejador.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de ejecuciones del workflow de incidentes con una ejecución exitosa." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El manejador tiene su propia lista de ejecuciones.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/44-ejecucion-manejador.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución del workflow de incidentes con sus tres nodos completados."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/44-ejecucion-manejador.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución del workflow de incidentes con sus tres nodos completados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Ejecución del manejador: Error Trigger entregó los datos y los otros dos nodos los registraron.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/45-error-trigger-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Error Trigger con los datos de la ejecución fallida y del workflow."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/45-error-trigger-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Error Trigger con los datos de la ejecución fallida y del workflow." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Esto es lo que entrega Error Trigger: la ejecución (identificador, dirección, error, último nodo y modo) y el workflow.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/10-registro-incidente.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Preparar registro del incidente con la solicitud, el workflow, el ID de la ejecución, el nodo y el mensaje."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/10-registro-incidente.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Preparar registro del incidente con la solicitud, el workflow, el ID de la ejecución, el nodo y el mensaje." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El registro final. <code>execution_id</code> coincide con el ID de la ejecución fallida del flujo principal.</figcaption></figure>

Para relacionar ambas ejecuciones compara el valor de `execution_id` con el **ID** que aparece en la cabecera de la ejecución fallida del flujo principal (`ID#4` en las capturas). También tienes el identificador de la solicitud, `LIB-204`, y el nodo donde se detuvo.

Si la falla ocurre en el disparador, o si n8n no guarda la ejecución original, parte de esos datos puede faltar. Por eso conviene que el mensaje de error lleve el identificador de la solicitud.

### Usa Retry execution

En una ejecución fallida, el botón de reintento ofrece dos opciones:

- **Retry with currently saved workflow (from node with error)**: vuelve a procesar la ejecución con el workflow tal como está guardado ahora.
- **Retry with original workflow (from node with error)**: usa el workflow tal como estaba cuando ocurrió la ejecución.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/12-reintentar-ejecucion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Menú de reintento de una ejecución fallida con las dos opciones."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/12-reintentar-ejecucion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Menú de reintento de una ejecución fallida con las dos opciones." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El menú de <b>Retry execution</b> de la ejecución fallida.</figcaption></figure>

Observa el texto **from node with error**: el reintento **vuelve a empezar desde el nodo que falló**, con los datos que ya tenía la ejecución. En este flujo el nodo que falló es **Detener ejecución**, no **Consultar catálogo**: el HTTP Request ya había entregado su ítem por la salida de error. Por eso el reintento no vuelve a llamar al catálogo y el simulador no recibe peticiones nuevas (sigue en tres). La ejecución reintentada falla otra vez, y n8n activa el manejador una segunda vez.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/47-reintento-lista.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lista de ejecuciones con una ejecución de reintento de la ejecución 4."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/47-reintento-lista.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de ejecuciones con una ejecución de reintento de la ejecución 4." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ejecución reintentada indica <b>Retry of execution #4</b>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/51-reintento-nodo-detener.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo Detener ejecución en la ejecución reintentada con el mismo mensaje de error."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/51-reintento-nodo-detener.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Detener ejecución en la ejecución reintentada con el mismo mensaje de error." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El reintento falló en el mismo nodo, con el mismo mensaje.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/48-reintento-resultado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución reintentada con el nodo Detener ejecución en rojo."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/48-reintento-resultado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución reintentada con el nodo Detener ejecución en rojo." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ejecución reintentada termina en error, como la original.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/49-manejador-tras-reintento.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución del manejador creada tras el reintento."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/49-manejador-tras-reintento.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución del manejador creada tras el reintento." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El reintento también activó el workflow de incidentes.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/50-simulador-tras-reintento.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Respuesta del simulador para LIB-204 que sigue mostrando tres peticiones."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/50-simulador-tras-reintento.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Respuesta del simulador para LIB-204 que sigue mostrando tres peticiones." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El simulador continúa con tres peticiones para LIB-204: el reintento no llamó otra vez al catálogo.</figcaption></figure>

**Qué enseña este resultado.** Retry execution sirve para reprocesar una ejecución cuando el problema ya se resolvió, por ejemplo después de corregir un dato o un ajuste del nodo que falló. Si el motivo del error sigue ahí, volverá a fallar. Y no reintenta lo que ya terminó bien: si necesitas volver a llamar al servicio, vuelve a enviar la consulta.

## Comprueba lo que entendiste

```quiz
? El catálogo responde 503 en la primera llamada y 200 en la segunda. ¿Cuántas llamadas realizó el nodo?
+ Dos. La segunda recuperó la consulta.
- Tres. Siempre se alcanza el máximo configurado.
- Una. El reintento se ejecuta en otro workflow.
> Max. Tries fija un límite. El nodo deja de reintentar cuando la llamada tiene éxito.
? Una consulta opcional sigue fallando después de los reintentos. ¿Qué debería mostrar la salida degradada?
- Un valor de cero y una disponibilidad confirmada.
+ Un estado degradado y la disponibilidad como null.
- Una cantidad estimada a partir del catálogo anterior.
> El estado degradado indica que se pudo manejar la falla. null conserva la diferencia entre falta de información y cero ejemplares.
? ¿Qué prueba permite comprobar que Error Trigger recibe un fallo real del flujo principal?
- Ejecutar solo el nodo Edit Fields del manejador.
- Disparar el flujo desde la Test URL en el editor.
+ Provocar una falla en una ejecución automática, con el Error workflow configurado.
> Error Trigger se activa ante fallas de ejecuciones automáticas. El manejador corre en una ejecución propia.
? El catálogo responde 200 y dice que quedan cero ejemplares. ¿Cómo debe tratarlo el flujo?
- Como un error, porque no hay libros.
- Como una contingencia, con disponibles en null.
+ Como una respuesta válida, con disponibles igual a 0.
> Cero es un dato conocido. Null se reserva para cuando no se pudo consultar.
? Reintentaste una ejecución fallida en la que el nodo que falló fue Stop And Error. ¿Qué ocurre con el catálogo?
- Recibe tres peticiones nuevas.
+ No recibe peticiones nuevas, porque el reintento parte desde el nodo con error.
- Responde 200 porque el reintento usa el workflow original.
> Retry execution comienza en el nodo que falló. El HTTP Request ya había terminado, así que no se vuelve a ejecutar.
? ¿Por qué conviene tener cuidado al reintentar una operación que crea o modifica datos?
- Porque n8n no permite reintentar esas operaciones.
+ Porque si la primera llamada sí llegó pero no se recibió la respuesta, el reintento podría duplicar el efecto.
- Porque los reintentos siempre cuestan dinero.
> Las lecturas se pueden repetir sin consecuencias. Las escrituras necesitan una forma de reconocer repeticiones.
```

## Documentación de n8n

- [Manejo de errores](https://docs.n8n.io/flow-logic/error-handling/)
- [Configuración de nodos](https://docs.n8n.io/workflows/components/nodes/)
- [Error Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger/)
- [Stop And Error](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.stopanderror/)
- [Respond to Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/)
- [Historial y reintento de ejecuciones](https://docs.n8n.io/workflows/executions/all-executions/)
- [Biblioteca de loops y subworkflows](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-loops-subworkflows)

## Descarga e importación del ejemplo

Estos archivos incluyen los workflows, el simulador del catálogo y los datos de prueba. No contienen credenciales ni servicios externos. Las capturas y las pruebas corresponden a **n8n 2.44.6**.

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-manejo-errores/biblioteca-manejo-errores-completo.zip" download="biblioteca-manejo-errores-completo.zip">Descargar el paquete completo (ZIP)</a></p>

O descarga cada archivo por separado:

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-manejo-errores/biblioteca-manejo-errores-principal.json" download="biblioteca-manejo-errores-principal.json">Workflow principal</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-manejo-errores/biblioteca-error-workflow.json" download="biblioteca-error-workflow.json">Workflow del manejador de errores</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-manejo-errores/simulador_catalogo.py" download="simulador_catalogo.py">Simulador del catálogo</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-manejo-errores/compose.yaml" download="compose.yaml">Docker Compose (n8n y simulador)</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-manejo-errores/probar_escenarios.py" download="probar_escenarios.py">Script que prueba los cinco escenarios</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-manejo-errores/biblioteca-manejo-errores.postman_collection.json" download="biblioteca-manejo-errores.postman_collection.json">Colección de Postman</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-manejo-errores/README.md" download="README.md">README con instrucciones y solución de problemas</a></p>

### Importa y prueba desde cero

1. Descomprime el ZIP y ejecuta `docker compose up -d` en esa carpeta. El simulador arranca junto con n8n.
2. Abre n8n, crea un workflow vacío y, en el menú `...`, elige **Import > From file**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/52-importar-menu.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Menú de un workflow nuevo con Import y la opción From file resaltada."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/52-importar-menu.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Menú de un workflow nuevo con Import y la opción From file resaltada." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><b>Import > From file</b> carga un archivo JSON dentro del workflow abierto.</figcaption></figure>

3. Selecciona `biblioteca-manejo-errores-principal.json` y guarda con `Ctrl+S`. Repite en otro workflow vacío con `biblioteca-error-workflow.json`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/53-principal-importado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow principal después de importarlo, con todos sus nodos y conexiones."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/53-principal-importado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow principal después de importarlo, con todos sus nodos y conexiones." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El workflow principal tras la importación: se conservan los nodos, las conexiones, los reintentos y las notas.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/54-manejador-importado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow de incidentes después de importarlo."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/54-manejador-importado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow de incidentes después de importarlo." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El manejador tras la importación.</figcaption></figure>

4. Publica el manejador, vincúlalo desde **Settings** del workflow principal y publica el principal, como en la sección 11. El vínculo no viaja en el JSON porque depende del identificador que n8n asigna al importar: **debes crearlo tú**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/55-vincular-tras-importar.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Diálogo de configuración del workflow importado con el Error Workflow seleccionado."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/55-vincular-tras-importar.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Diálogo de configuración del workflow importado con el Error Workflow seleccionado." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El vínculo se hace después de importar, porque n8n asigna un identificador nuevo a cada workflow.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/14-workflows-importados.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lista de workflows con el principal y el manejador, ambos publicados."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/14-workflows-importados.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de workflows con el principal y el manejador, ambos publicados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los dos workflows importados y publicados.</figcaption></figure>

5. Prueba los cinco casos. Si usas el script: `python3 probar_escenarios.py http://localhost:5678/webhook/consulta-disponibilidad http://localhost:8081`. Si cambiaste los puertos, usa los tuyos. Si no tienes Python, o prefieres probar un caso a la vez, mira la sección final: «Prueba con Postman y conoce el simulador».

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/56-prueba-tras-importar.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida del script de pruebas con los cinco escenarios marcados como correctos."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/56-prueba-tras-importar.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida del script de pruebas con los cinco escenarios marcados como correctos." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El script compara cada respuesta con lo esperado y lee del simulador cuántas peticiones recibió.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/57-executions-tras-importar.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lista de ejecuciones del workflow importado con cuatro correctas y una fallida."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/57-executions-tras-importar.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de ejecuciones del workflow importado con cuatro correctas y una fallida." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las ejecuciones del workflow importado.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/58-manejador-tras-importar.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución del workflow de incidentes en la instancia con los workflows importados."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/58-manejador-tras-importar.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución del workflow de incidentes en la instancia con los workflows importados." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El incidente de la solicitud obligatoria también quedó registrado en la instancia con los workflows importados.</figcaption></figure>

### Si algo no funciona

- **Error 404 al llamar al webhook:** el workflow principal no está publicado o usaste la **Test URL**.
- **El manejador aparece en gris en Settings:** no está publicado.
- **No aparece ninguna ejecución del manejador:** revisa el vínculo y prueba por la **Production URL**, no desde el editor.
- **`ECONNREFUSED` en Consultar catálogo:** n8n no encuentra el simulador. Revisa la URL del nodo y que usas el compose del paquete.
- **El puerto está ocupado:** ejecuta `N8N_PUERTO=5679 CATALOGO_PUERTO=8082 docker compose up -d`.
- **`python` no se reconoce (Windows):** no tienes Python instalado. Ejecuta el script con `docker compose --profile pruebas run --rm pruebas` (última sección) o usa Postman.

El README del paquete tiene la lista completa, las instrucciones para conectar el simulador a un n8n que ya tengas y cómo limpiar todo con `docker compose down -v`.

## Prueba con Postman y conoce el simulador

Además del script, puedes probar cada caso por separado con **Postman** y ver el resultado de cada uno. El paquete incluye una colección lista para importar.

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-manejo-errores/biblioteca-manejo-errores.postman_collection.json" download="biblioteca-manejo-errores.postman_collection.json">Descargar la colección de Postman</a></p>

### Importa y ejecuta la colección

1. En Postman elige **Import**, arrastra el archivo `biblioteca-manejo-errores.postman_collection.json` y confirma.
2. Abre la colección y revisa sus variables: `n8n_url` (por defecto `http://localhost:5678`) y `simulador_url` (por defecto `http://localhost:8081`). Cambia los puertos si usaste otros. Postman corre en tu computador, por eso usa `localhost` y no los nombres `n8n` ni `catalogo`, que solo existen dentro de Docker.
3. Ejecuta en orden: **Reiniciar el simulador**, los cinco casos de **1. Casos de prueba** y las consultas de **2. Qué pasó en el simulador**.
4. En cada respuesta abre la pestaña **Test Results**. Una prueba en verde significa que el resultado coincide con lo esperado.

Para correr todo de una vez usa **Run collection**.

La colección tiene 12 requests, y solo cinco llaman a n8n:

| Carpeta | Request | Destino | Para qué sirve |
| --- | --- | --- | --- |
| 0. Preparar | Reiniciar el simulador | `GET` al simulador, ruta `/reiniciar` | Borra los contadores antes de repetir las pruebas. |
| 1. Casos de prueba | Los cinco casos, de LIB-201 a LIB-205 | `POST` al webhook de n8n, `/webhook/consulta-disponibilidad` | Envía una consulta. Lo que ves es la respuesta que armó n8n. |
| 2. Qué pasó en el simulador | Peticiones de cada solicitud y registro completo | `GET` al simulador, rutas `/intentos` y `/registro` | Muestra qué recibió el catálogo, sin pasar por n8n. |

Cada request tiene una prueba automática en la pestaña **Scripts** (sección **Post-response**). Comprueba el código HTTP, el `estado` y `disponibles`, y en la falla temporal que la respuesta tarde más de un segundo por la espera entre intentos. Esa prueba solo muestra verde o rojo: no cambia lo que se envía a n8n.

### Qué hace el simulador

El simulador es un servicio HTTP pequeño (`simulador_catalogo.py`) que hace de catálogo de la biblioteca. Responde sobre los seis libros ficticios, puede **fallar a propósito** según el escenario que pidas y **cuenta cuántas peticiones recibió** cada solicitud. El nodo **Consultar catálogo** de n8n lo llama con un `GET` a `/disponibilidad`. Las demás rutas son para que tú mires lo ocurrido.

Estos son los escenarios:

- **`exito`:** responde `200` con los datos del libro.
- **`temporal`:** responde `503` en las peticiones impares de cada solicitud (la 1.ª, la 3.ª...) y `200` en las pares. Con los reintentos, n8n recibe `503` y luego `200`.
- **`caida`:** responde `503` siempre.
- **`sin_stock`:** responde `200` con `disponibles: 0`.

El contador sigue sumando mientras no lo reinicies. Si repites el mismo `solicitud_id`, el escenario `temporal` puede empezar por una respuesta correcta. Para repetir una prueba desde cero, reinicia el simulador o usa otro identificador.

### Endpoints que puedes llamar

Todos son `GET` y puedes abrirlos en el navegador o crear un request nuevo en Postman. Con los puertos por defecto la dirección base es `http://localhost:8081`.

| Ruta | Qué hace | Ejemplo |
| --- | --- | --- |
| `/disponibilidad` | La que usa n8n. Recibe `solicitud_id`, `titulo` y `escenario`. Responde `200` con el libro, `503` en los escenarios de falla, `404` si el título no existe y `400` si faltan datos o el escenario no es válido. | `/disponibilidad?solicitud_id=PRUEBA-1&titulo=El faro de papel&escenario=exito` |
| `/intentos` | Cuántas peticiones recibió una solicitud y qué respondió el simulador en cada una. | `/intentos?solicitud_id=LIB-202` |
| `/registro` | Todas las peticiones recibidas, con su hora. | `/registro` |
| `/reiniciar` | Borra los contadores y el registro. | `/reiniciar` |
| `/salud` | Comprueba que el simulador está activo. | `/salud` |

Así responde `/disponibilidad` con el escenario `exito`:

<pre><code class="language-text">{
  "solicitud_id": "PRUEBA-1",
  "titulo": "El faro de papel",
  "ejemplares_totales": 5,
  "prestamos_activos": 2,
  "disponibles": 3
}</code></pre>

Y así con el escenario `caida`, que corresponde al error que recibe n8n:

<pre><code class="language-text">{
  "error": "servicio_no_disponible",
  "solicitud_id": "PRUEBA-1",
  "peticion": 1
}</code></pre>

Usa un `solicitud_id` distinto de LIB-201 a LIB-205, como `PRUEBA-1`, para no alterar los contadores de los cinco casos.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/35-simulador-intentos-temporal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Respuesta de la ruta /intentos con las dos peticiones de LIB-202: 503 y 200."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-manejo-errores/35-simulador-intentos-temporal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Respuesta de la ruta /intentos con las dos peticiones de LIB-202: 503 y 200." style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ruta <code>/intentos</code> muestra cada petición que recibió el simulador. Aquí se ve el reintento de la falla temporal.</figcaption></figure>

### Mira lo que ocurre en vivo

- **Simulador:** `docker compose logs -f catalogo` muestra una línea por cada petición, por ejemplo `LIB-202 #1 temporal -> 503` y después `LIB-202 #2 temporal -> 200`. Es la forma más clara de ver los reintentos.
- **n8n:** en **Executions** abre cada ejecución para ver por qué ruta pasó. El incidente de una consulta obligatoria queda en **Executions** del workflow **Biblioteca | Registro de incidentes**.
- **Registros de n8n:** `docker compose logs -f n8n` muestra el mensaje del error crítico, con el `solicitud_id`.

### Ejecuta el script sin instalar Python

Si el script falla con «Python was not found» (es habitual en Windows), el `compose.yaml` del paquete incluye un servicio `pruebas` que lo ejecuta dentro de Docker. Desde la carpeta del paquete, en PowerShell, `cmd` o cualquier terminal:

<pre><code class="language-text">docker compose --profile pruebas run --rm pruebas</code></pre>

Corre en la misma red que n8n y el simulador, así que no depende de los puertos que publicaste. Necesita los dos workflows importados, vinculados y publicados. Debe terminar con «Todos los escenarios coinciden».
