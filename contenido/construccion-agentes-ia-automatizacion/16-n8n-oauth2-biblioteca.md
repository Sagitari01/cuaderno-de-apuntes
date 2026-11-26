# OAuth 2.0 en n8n: consentimiento, permisos y tokens

Una biblioteca ficticia necesita permitir que n8n consulte el catálogo **sin compartir la contraseña de una persona**. En esta guía aprenderás a solicitar una autorización, aceptar o rechazar el consentimiento, consultar con permisos limitados, renovar un token y revocar el acceso.

**Continúa la [Guía 15: API Key, Basic Auth y JWT](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-credenciales-autenticacion)**, pero ofrece un **paquete avanzado completo** que puedes instalar de manera independiente. El escenario de biblioteca es el mismo; no necesitas construirlo desde cero si ya tienes la guía anterior funcionando.

**Objetivos de aprendizaje.** Al terminar podrás distinguir autenticación y autorización, explicar Authorization Code, configurar una credencial OAuth2 API, identificar la diferencia entre 401 y 403 y probar renovación y revocación.

**Requisitos previos.** Haber utilizado Webhook, HTTP Request, Docker Compose y credenciales de n8n. Necesitas Docker, n8n y Postman; no se exige programar en Python.

## 1. El problema: acceso delegado

En la biblioteca, consultar títulos públicos no exige permisos. Consultar préstamos y ejemplares disponibles sí. Antes, n8n utilizaba API Key, Basic Auth o JWT. Ahora una persona decide si autoriza a una aplicación para consultar datos, con permisos específicos (`catalogo.leer`), sin entregarle su contraseña.

**Lo que demostraremos:** rechazar y aceptar el consentimiento; consultar con `catalogo.leer` (200); intentar hacerlo con solo `perfil.leer` (403); renovar un access token vencido y revocar una autorización (401). Son dos credenciales distintas, no dos cuentas reales de Google.

El servidor OAuth de esta práctica es un **simulador local para enseñanza**, no Google Drive ni un proveedor real. Los valores de cliente y tokens son ficticios.

## 2. Preparar el entorno de biblioteca

### 2.1 Instalación desde cero

1. Descarga al final de esta guía el **ZIP avanzado** y descomprímelo.
2. Dentro de la carpeta del paquete abre una terminal y ejecuta `docker compose up -d`.
3. Comprueba `http://localhost:8091/salud` y abre **n8n en `http://localhost:5680`**, no en `127.0.0.1`.
4. Importa `biblioteca-acceso-seguro-workflow.json` en un workflow nuevo. El archivo trae los cuatro métodos de autenticación y 28 nodos con notas; **no trae los secretos** del gestor de credenciales.
5. Configura API Key, Basic Auth y JWT según el README o la [Guía 15](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-credenciales-autenticacion). Después crea las dos credenciales OAuth de la sección 3.5.
6. Antes de publicar, confirma que no hay otro workflow publicado con el mismo webhook `/webhook/acceso-seguro`. Despublica el antiguo si corresponde; guarda y publica este.

**No ejecutes simultáneamente los paquetes básico y avanzado con sus puertos predeterminados:** ambos son ediciones del mismo laboratorio. El ZIP avanzado ya incluye el catálogo y los tres métodos anteriores.

### 2.2 Si ya tienes instalada la versión básica

**Conserva tu instalación.** Respalda primero tu workflow, `compose.yaml`, `simulador_catalogo_seguro.py` y el volumen de n8n. Copia desde el paquete avanzado solo el nuevo `compose.yaml` y `simulador_catalogo_seguro.py` a tu carpeta actual y ejecuta:

```bash
docker compose config --quiet
docker compose up -d --no-deps catalogo
```

Si n8n estaba detenido, inicia ese servicio con `docker compose start n8n`. **No uses `docker compose down -v`**: la opción `-v` elimina los volúmenes y puede borrar tus credenciales y workflows.

Importa el JSON actualizado como **otro workflow** para conservar el anterior. Crea y vincula las credenciales OAuth, despublica el workflow básico y solo entonces publica el avanzado. Si el simulador se reinicia, se pierden sus autorizaciones guardadas en memoria y debes volver a pulsar **Connect**.

### 2.3 Vista del workflow ampliado

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/w17-workflow-completo-notas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Workflow avanzado con rutas API Key, Basic Auth, JWT y OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/w17-workflow-completo-notas.webp" target="_blank" rel="noopener noreferrer" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Paquete avanzado: las rutas anteriores se mantienen y se agregan autorización, acceso denegado y notas sobre OAuth 2.0.</figcaption></figure>

En una instalación desde cero, la importación conserva los nodos y las notas, pero es normal que primero aparezcan avisos de credenciales pendientes:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/x3-importado-con-notas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Workflow avanzado importado con credenciales por seleccionar"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/x3-importado-con-notas.webp" target="_blank" rel="noopener noreferrer" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Después de importar el JSON, asigna a cada nodo su credencial por nombre.</figcaption></figure>

---

## 3. OAuth 2.0: autorización con consentimiento

En la guía anterior aprendimos a utilizar API Key, Basic Auth y JWT. OAuth 2.0 resuelve otro problema: **una persona autoriza a una aplicación** a acceder a sus datos, con permisos limitados, sin darle su contraseña y pudiendo quitar el permiso cuando quiera.

Las capturas de esta sección se tomaron en una instalación de prueba paralela, con n8n en el puerto `5710` y el simulador en el `5711`. Con los valores por defecto del paquete verás `5680` y `8091`. Todo lo demás es igual.

### 3.1 La idea, sin jerga

Imagina que eres socia de la biblioteca y quieres que una amiga consulte por ti cuántos ejemplares hay disponibles.

- Si le das tu carnet y tu clave (**Basic Auth**), ella puede hacer todo lo que tú haces, y para quitarle el acceso tienes que cambiar tu clave.
- Con **OAuth 2.0**, la biblioteca te muestra una pantalla que dice «esta aplicación pide permiso para consultar el catálogo». Tú eliges **Autorizar** o **Rechazar**. La aplicación recibe un permiso limitado y temporal, nunca tu clave, y tú puedes anularlo cuando quieras sin cambiar nada más.

Así se explican los cuatro mecanismos, de menos a más:

1. **API Key**: la aplicación se identifica con una clave, como una llave de la sala. Quien la tenga, entra.
2. **Basic Auth**: la aplicación usa el usuario y la contraseña de una cuenta, y los envía en cada solicitud. Por eso necesita HTTPS.
3. **JWT**: la aplicación cambia su usuario y su clave por un token que vence. Debe controlar ese vencimiento.
4. **OAuth 2.0**: una persona autoriza a la aplicación, con permisos limitados. La aplicación recibe tokens y la persona puede revocarlos.

### 3.2 Los términos, uno por uno

| Término | Qué es | En este ejercicio |
| --- | --- | --- |
| **Autenticación** | Demostrar quién eres | El token identifica a la aplicación autorizada |
| **Autorización** | Decidir qué puedes hacer | El permiso (scope) que la persona concedió |
| **Client ID** | Identificador público de la aplicación registrada | `biblioteca-n8n` |
| **Client Secret** | Clave de la aplicación. Se guarda en la credencial y nunca pasa por el navegador | Valor de demostración en el `README.md` |
| **Consentimiento** | Pantalla donde la persona autoriza o rechaza | «Biblioteca (demostración): autorizar acceso» |
| **Scope** | El permiso concreto que se pide | `catalogo.leer` consulta el catálogo; `perfil.leer` solo muestra el nombre de la cuenta |
| **Authorization Code** | Código temporal y de un solo uso que se entrega tras autorizar. Solo sirve para canjearlo por tokens | Dura 60 segundos |
| **Access Token** | Token de vida corta que abre la API | Dura 5 minutos |
| **Refresh Token** | Token que solo sirve para pedir un access token nuevo | Dura 24 horas |
| **Renovación** | Pedir un access token nuevo con el refresh token, sin molestar a la persona | n8n la hace solo |
| **Revocación** | Quitar la autorización dada | Página de autorizaciones del simulador |
| **Error 401** | «No sé quién eres»: el token falta, no existe, venció o fue revocado | `falta_credencial`, `token_vencido`... |
| **Error 403** | «Sé quién eres, pero este permiso no alcanza» | `insufficient_scope` |

### 3.3 El recorrido, paso a paso

Participan tres: **la persona** (con su navegador), **n8n** y **el simulador** del catálogo, que hace de servidor de autorización y de API.

1. n8n abre en tu navegador la **Authorization URL** del simulador, con el Client ID, el permiso pedido, la dirección de vuelta (`redirect_uri`) y un valor aleatorio llamado `state`.
2. El simulador muestra la **pantalla de consentimiento**. La persona elige **Autorizar** o **Rechazar**.
3. Si autoriza, el simulador devuelve el navegador a n8n con un **código** (y el mismo `state`). Si rechaza, lo devuelve con `error=access_denied`.
4. n8n, desde su propio servidor y sin pasar por el navegador, **canjea el código por tokens** en la **Access Token URL**, mostrando su Client ID y su Client Secret.
5. Para consultar, n8n envía `Authorization: Bearer <access token>`.
6. Cuando el access token vence, n8n usa el **refresh token** y recibe uno nuevo.
7. Si la persona **revoca** la autorización, la renovación falla y hay que volver a autorizar.

Hay dos direcciones del mismo servidor, vistas desde dos lugares distintos. La **Authorization URL** (`http://localhost:8091/oauth/autorizar`) la abre **tu navegador**, que está en tu computador, por eso es `localhost`. La **Access Token URL** (`http://catalogo:8080/oauth/token`) la llama **n8n**, que corre dentro de Docker y conoce al simulador por su nombre.

### 3.4 Qué controles de seguridad tiene el simulador

El simulador es **educativo**, pero valida lo básico de un servidor de autorización:

- La `redirect_uri` debe ser **exactamente** la registrada. Si no lo es, no redirige a ningún lado y muestra el error en pantalla.
- El `state` es obligatorio y se devuelve intacto, para que n8n compruebe que la respuesta corresponde a su solicitud.
- El código vive 60 segundos y se usa **una sola vez**. Si alguien lo reutiliza, el simulador lo rechaza y revoca lo que ya había emitido con él.
- Para canjear el código hace falta el **Client Secret**.
- El permiso (scope) se valida en cada ruta: sin `catalogo.leer`, el catálogo responde `403`.
- **PKCE** (opcional): si la solicitud trae un `code_challenge` con método `S256`, el canje exige el verificador correcto.
- Ni el registro del simulador (`/registro`) ni sus mensajes en consola muestran códigos ni tokens.

**No es un servidor listo para producción:** guarda todo en memoria (al reiniciarlo se pierden las autorizaciones), no pide una contraseña real, no limita intentos y no usa HTTPS.

### 3.5 Crea las credenciales OAuth2 API en n8n

**¿Qué estamos haciendo?** Registramos en n8n la aplicación que pedirá permiso. Crearás **dos** credenciales: una con `catalogo.leer` (la que consulta el catálogo) y otra con solo `perfil.leer` (para ver el error 403).

**¿Cómo lo hacemos?** En **Credentials** pulsa **Create credential** y busca **OAuth2 API** (elige la que se llama exactamente así, no las de servicios como Google o GitHub). Completa:

| Campo | Valor |
| --- | --- |
| Nombre | `Biblioteca \| OAuth2 (demo)` |
| Grant Type | Authorization Code (viene por defecto) |
| Authorization URL | `http://localhost:8091/oauth/autorizar` |
| Access Token URL | `http://catalogo:8080/oauth/token` |
| Client ID | `biblioteca-n8n` |
| Client Secret | El valor de demostración del `README.md` (n8n lo enmascara) |
| Scope | `catalogo.leer` |
| Authentication | Header (viene por defecto) |

Comprueba que la **OAuth Redirect URL** diga `http://localhost:5680/rest/oauth2-credential/callback`. Si no, abriste n8n por otra dirección.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o01-credencial-oauth2-formulario.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="2400" height="1690" alt="Formulario de la credencial OAuth2 API con las direcciones resaltadas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o01-credencial-oauth2-formulario.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Formulario de la credencial OAuth2 API con las direcciones resaltadas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La credencial <b>OAuth2 API</b>. Resaltadas: la <b>Authorization URL</b> (la abre tu navegador) y la <b>Access Token URL</b> (la llama n8n) y el <b>Scope</b>. El Client Secret queda enmascarado.</figcaption></figure>

Pulsa **Save**. n8n avisa que falta conectar la cuenta:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o02-credencial-sin-conectar.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="2400" height="1690" alt="Credencial OAuth2 API guardada y sin conectar"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o02-credencial-sin-conectar.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial OAuth2 API guardada y sin conectar" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras <b>Save</b>, n8n avisa «Connect your account to use this credential». La <b>OAuth Redirect URL</b> es la dirección a la que el simulador devuelve el navegador.</figcaption></figure>

La segunda credencial se llama `Biblioteca | OAuth2 solo perfil (demo)` y es igual, pero con **Scope** `perfil.leer`.

### 3.6 Primero rechaza el consentimiento y después autoriza

**¿Qué estamos haciendo?** Vemos las dos decisiones posibles de la persona.

**¿Cómo lo hacemos?** En `Biblioteca | OAuth2 (demo)` pulsa **Connect**. Se abre una ventana con la pantalla de consentimiento:

<figure class="lamina-apunte" style="position:relative;max-width:760px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o03-pantalla-consentimiento.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1305" height="939" alt="Pantalla de consentimiento del simulador con los botones Autorizar y Rechazar"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o03-pantalla-consentimiento.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pantalla de consentimiento del simulador con los botones Autorizar y Rechazar" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La pantalla de consentimiento. Dice qué aplicación pide permiso, con qué cuenta (ficticia) y qué permiso (<code>catalogo.leer</code>). La persona elige <b>Autorizar</b> o <b>Rechazar</b>.</figcaption></figure>

Lee qué aplicación pide permiso y qué permiso. **Primero pulsa Rechazar.** El simulador devuelve el navegador a n8n con `error=access_denied`:

<figure class="lamina-apunte" style="position:relative;max-width:560px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o04-rechazo-mensaje-n8n.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="925" height="320" alt="Mensaje de n8n tras rechazar el consentimiento"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o04-rechazo-mensaje-n8n.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Mensaje de n8n tras rechazar el consentimiento" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Después de <b>Rechazar</b>, el simulador vuelve a n8n con <code>error=access_denied</code>. n8n muestra «Failed to connect» y no guarda ningún token.</figcaption></figure>

Cierra esa ventana. La credencial sigue sin conectar:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o05-credencial-tras-rechazo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="2400" height="1690" alt="Credencial sin conectar después de rechazar"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o05-credencial-tras-rechazo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial sin conectar después de rechazar" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La credencial sigue sin conectar: sin autorización no hay token.</figcaption></figure>

Ahora pulsa **Connect** otra vez y esta vez **Autorizar**. La ventana se cierra sola y la credencial queda conectada:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o06-credencial-conectada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="2400" height="1690" alt="Credencial conectada con el aviso Account connected"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o06-credencial-conectada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial conectada con el aviso Account connected" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras <b>Autorizar</b>, la credencial muestra <b>Account connected</b>. n8n canjeó el código por un access token y un refresh token, y los guardó cifrados.</figcaption></figure>

Nota lo que **no** ocurrió: no escribiste ningún token ni la contraseña de nadie. n8n obtuvo los tokens, los guardó cifrados y los usará por su cuenta.

Repite con la segunda credencial. La pantalla de consentimiento ahora muestra otro permiso:

<figure class="lamina-apunte" style="position:relative;max-width:760px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o07-consentimiento-solo-perfil.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1305" height="895" alt="Pantalla de consentimiento para el permiso perfil.leer"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o07-consentimiento-solo-perfil.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pantalla de consentimiento para el permiso perfil.leer" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Con la segunda credencial (Scope <code>perfil.leer</code>) la pantalla pide un permiso distinto: solo ver el nombre de la cuenta.</figcaption></figure>

Al terminar tienes cinco credenciales:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o08-lista-credenciales.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1500" alt="Lista con las cinco credenciales"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o08-lista-credenciales.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista con las cinco credenciales" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las cinco credenciales del ejercicio, con sus nombres. Las dos de tipo <b>OAuth2 API</b> son las nuevas.</figcaption></figure>

### 3.7 Agrega las rutas OAuth 2.0 al workflow

**¿Qué estamos haciendo?** Sumamos la cuarta ruta (y una quinta para ver el `403`) sin tocar las tres anteriores.

**¿Cómo lo hacemos?**

1. En el **Switch** **Tipo de autenticación** agrega dos reglas **antes** de la salida de respaldo: `oauth2` (salida «OAuth 2.0») y `oauth2_sin_permiso` (salida «OAuth 2.0 sin permiso»).
2. Agrega un **HTTP Request** llamado **Consultar con OAuth 2.0**: método `GET`, URL `http://catalogo:8080/catalogo/oauth`, **Authentication** **Generic Credential Type**, **Generic Auth Type** **OAuth2 API** y la credencial `Biblioteca | OAuth2 (demo)`. Envía el parámetro `titulo` como en las otras rutas y activa **Include Response Headers and Status** y **Never Error**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o10-nodo-consultar-oauth.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="3000" alt="Nodo Consultar con OAuth 2.0 con la credencial OAuth2 API"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o10-nodo-consultar-oauth.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Consultar con OAuth 2.0 con la credencial OAuth2 API" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El HTTP Request de la ruta OAuth: <b>Generic Credential Type</b>, <b>OAuth2 API</b> y la credencial elegida por su nombre. No hay ningún token escrito en el nodo.</figcaption></figure>

3. En **Settings** del mismo nodo, pon **On Error** en **Continue (using error output)**. Así, si n8n no puede renovar la autorización, el flujo sale por una segunda salida (**Error**) en vez de terminar con un fallo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o11-nodo-oauth-salida-error.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="3000" alt="Ajuste On Error con la salida de error resaltada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o11-nodo-oauth-salida-error.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ajuste On Error con la salida de error resaltada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>En <b>Settings</b>, <b>On Error</b> está en <b>Continue (using error output)</b>: si n8n no puede renovar la autorización, el flujo sale por la salida <b>Error</b> en vez de terminar con un fallo.</figcaption></figure>

4. Conecta la salida **Success** a **Responder (OAuth 2.0)**, que devuelve el resultado con el mismo código de la API (campo `autenticacion`: `oauth2`). Conecta la salida **Error** a **Responder (OAuth 2.0 sin autorización)**: un **Respond to Webhook** con código fijo `401` y un mensaje que explica que la autorización ya no sirve y hay que volver a autorizar.
5. Para la ruta de permiso insuficiente, duplica el HTTP Request y el Responder. Cambia el nombre a **Consultar con OAuth 2.0 sin permiso**, elige la credencial `Biblioteca | OAuth2 solo perfil (demo)` y pon `oauth2_sin_permiso` en el campo `autenticacion` del Responder.
6. Agrega las notas adhesivas 8 a 12 (Guía 15) y **publica** el nuevo workflow después de despublicar cualquier otro que utilice la ruta `/webhook/acceso-seguro`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o09-ruta-oauth-lienzo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1600" height="1225" alt="Rutas de OAuth 2.0 en el lienzo con sus notas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o09-ruta-oauth-lienzo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Rutas de OAuth 2.0 en el lienzo con sus notas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las dos rutas nuevas. Arriba, las notas 8, 9 y 10; en medio <b>Consultar con OAuth 2.0</b>, con sus dos salidas (<b>Success</b> y <b>Error</b>); abajo, las notas 11 y 12 y la ruta de permiso insuficiente.</figcaption></figure>

**Prueba la ruta.** Desde Postman (carpeta 10) o con `curl`, envía `{"titulo": "El faro de papel", "tipo_autenticacion": "oauth2"}` al webhook. Responde `200` con los cuatro datos del libro y no enviaste ningún token:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o12-ejecucion-oauth-200.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución por la ruta OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o12-ejecucion-oauth-200.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución por la ruta OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una consulta por la ruta OAuth 2.0. Es una ejecución normal: n8n puso el token por su cuenta.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o13-oauth-salida-http.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Consultar con OAuth 2.0 con statusCode 200"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o13-oauth-salida-http.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Consultar con OAuth 2.0 con statusCode 200" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La salida del nodo: <code>statusCode</code> <code>200</code> y los cuatro datos del libro (título, ejemplares totales, préstamos activos y disponibles).</figcaption></figure>

### 3.8 Qué pasa cuando vence el access token

El access token dura 5 minutos. Para no esperar, el simulador tiene una ruta solo para practicar: `POST /demo/oauth/vencer-tokens` (en Postman, la solicitud 8.1) vence todos los access tokens. Después, vuelve a llamar al webhook.

Para n8n es una ejecución normal y responde `200`. El registro del simulador cuenta lo que pasó por detrás:

<pre><code class="language-text">docker compose logs --no-log-prefix --tail 4 catalogo</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o14-registro-renovacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="642" alt="Registro del simulador con la renovación del token"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o14-registro-renovacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registro del simulador con la renovación del token" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Lo que vio el simulador al vencer el access token: <b>401</b> con motivo <code>token_vencido</code>, enseguida un <code>POST /oauth/token</code> (la renovación con el refresh token) y la consulta repetida con <b>200</b>.</figcaption></figure>

La API respondió `401` (`token_vencido`), n8n usó el refresh token en `POST /oauth/token` y repitió la consulta con el token nuevo. **La persona no tuvo que hacer nada.** n8n intenta renovar cuando recibe el código que indica el campo **Token Expired Status Code** de la credencial, que por defecto es `401`.

### 3.9 Permisos insuficientes: el error 403

Llama al webhook con `oauth2_sin_permiso`. Esa ruta usa la credencial que solo tiene `perfil.leer`:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o15-ejecucion-sin-permiso.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución por la ruta de permiso insuficiente"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o15-ejecucion-sin-permiso.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución por la ruta de permiso insuficiente" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ruta con la credencial que solo tiene <code>perfil.leer</code>. La ejecución termina bien, pero con el rechazo de la API.</figcaption></figure>

El token es válido, pero la ruta del catálogo exige `catalogo.leer`:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o16-sin-permiso-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida con statusCode 403 e insufficient_scope"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o16-sin-permiso-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida con statusCode 403 e insufficient_scope" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La API responde <b>403</b> con <code>insufficient_scope</code>: el token es válido, pero esta ruta exige <code>catalogo.leer</code> y el token solo trae <code>perfil.leer</code>.</figcaption></figure>

Compara con un `401`: aquí la API **sí sabe quién eres**. Cambiar el token no arregla nada; hay que volver a autorizar con el permiso correcto.

### 3.10 Revocación

La persona (o la aplicación) puede quitar la autorización cuando quiera. En el simulador, abre <http://localhost:8091/oauth/autorizaciones>:

<figure class="lamina-apunte" style="position:relative;max-width:760px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o17-autorizaciones.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1305" height="729" alt="Página de autorizaciones del simulador"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o17-autorizaciones.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Página de autorizaciones del simulador" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La página <code>/oauth/autorizaciones</code>: lo que la persona autorizó, con un botón <b>Revocar</b> por cada aplicación.</figcaption></figure>

Pulsa **Revocar** en la autorización de `catalogo.leer`:

<figure class="lamina-apunte" style="position:relative;max-width:760px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o18-autorizaciones-revocada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1305" height="693" alt="Página de autorizaciones con una autorización revocada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o18-autorizaciones-revocada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Página de autorizaciones con una autorización revocada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras pulsar <b>Revocar</b>, la autorización queda marcada como revocada.</figcaption></figure>

Regla del simulador: al revocar, **dejan de servir el refresh token y los access tokens** de esa autorización. En n8n no cambia nada a simple vista: la credencial sigue diciendo **Account connected**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o19-credencial-sigue-conectada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Credencial que sigue mostrando Account connected"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o19-credencial-sigue-conectada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial que sigue mostrando Account connected" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>n8n no se entera de la revocación: la credencial sigue diciendo <b>Account connected</b>. El problema aparece recién cuando se intenta usar.</figcaption></figure>

El problema aparece cuando el workflow intenta usarla. Llama al webhook con `oauth2`: n8n recibe `401`, intenta renovar, el simulador rechaza la renovación y el flujo sale por la salida **Error**:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o20-ejecucion-revocada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución con la autorización revocada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o20-ejecucion-revocada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución con la autorización revocada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La consulta tras revocar. n8n intentó renovar, no pudo, y el flujo salió por la salida <b>Error</b> hacia <b>Responder (OAuth 2.0 sin autorización)</b>.</figcaption></figure>

El nodo **Responder (OAuth 2.0 sin autorización)** recibe el error de n8n y responde `401` con el mensaje claro:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o21-revocada-respuesta.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Datos del error de renovación que recibe el Responder"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o21-revocada-respuesta.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Datos del error de renovación que recibe el Responder" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El error que entrega n8n: «Access could not be refreshed because the connected account has revoked access, the refresh token expired...». El Responder lo convierte en un <b>401</b> claro.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o22-registro-revocacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="578" alt="Registro del simulador con la revocación"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/o22-registro-revocacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registro del simulador con la revocación" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El simulador rechazó el access token (<code>autorizacion_revocada</code>) y también la renovación con el refresh token.</figcaption></figure>

Para recuperarte, abre la credencial y pulsa **Switch account**: vuelves a la pantalla de consentimiento y autorizas de nuevo. La aplicación también puede revocar con `POST /oauth/revocar` (solicitud 8.5 de la colección).

### 3.11 PKCE (opcional)

**PKCE** agrega una protección: n8n genera un secreto de un solo uso, envía su huella (`code_challenge`, método `S256`) al pedir la autorización y su valor (`code_verifier`) al canjear el código. Un código interceptado no sirve sin ese valor.

En la credencial de n8n se activa eligiendo **Grant Type** **PKCE**. En este ejercicio se comprobó con n8n 2.44.6: la credencial se conectó y el simulador verificó el desafío. La ruta principal del ejercicio usa **Authorization Code**, como el resto de la sección.

## 4. Prueba con Postman y con el webhook

Primero importa la colección `biblioteca-acceso-seguro.postman_collection.json` y el entorno `biblioteca-local.postman_environment.json` desde el paquete **avanzado**; selecciona el entorno `Biblioteca local (demo)` y comprueba los puertos `5680` y `8091`.

### 4.1 Dos consultas para comparar permisos

Con el workflow avanzado publicado, crea una petición **POST** a `http://localhost:5680/webhook/acceso-seguro` y envía `Content-Type: application/json`:

```json
{ "titulo": "El faro de papel", "tipo_autenticacion": "oauth2" }
```

Debe devolver 200 si `Biblioteca | OAuth2 (demo)` está conectada con `catalogo.leer`. Cambia solo `tipo_autenticacion` por `oauth2_sin_permiso`: la respuesta debe ser 403 porque `perfil.leer` no autoriza a consultar el catálogo.

Postman **no recibe ni envía las claves de la biblioteca al webhook**: n8n selecciona sus credenciales y realiza la solicitud protegida a la API.

### 4.2 OAuth 2.0 directo contra el simulador

Las carpetas 6 a 9 recorren OAuth 2.0 sin n8n y sin navegador: Postman hace de «aplicación» y de «persona» a la vez. Las solicitudes de las carpetas 6, 7 y 9 que piden la pantalla de consentimiento y la decisión están configuradas para **no seguir la redirección**, así puedes ver el código en la cabecera `Location`. El código y los tokens se guardan en variables de colección.

Carpeta 6: sin autorización y consentimiento. Sin token responde `401`; con una `redirect_uri` no registrada o sin `state` el simulador rechaza; si la persona rechaza, vuelve con `access_denied` y sin código; si acepta, vuelve con el código y el mismo `state`; con un Client Secret incorrecto el canje falla; con el correcto entrega los dos tokens.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p6-newman-oauth-consentimiento.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="4044" alt="Ejecución de la carpeta 6 de OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p6-newman-oauth-consentimiento.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 6 de OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 6: de la consulta sin autorización al canje del código por tokens.</figcaption></figure>

Carpeta 7: uso del token y permisos. Con `catalogo.leer` la consulta responde `200`; con un token que solo tiene `perfil.leer` responde `403`, pero ese mismo token sí sirve en la ruta de perfil.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p7-newman-oauth-permisos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2594" alt="Ejecución de la carpeta 7 de OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p7-newman-oauth-permisos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 7 de OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 7: el mismo catálogo, dos tokens con permisos distintos.</figcaption></figure>

Carpeta 8: vencimiento, renovación y revocación. Se adelanta el vencimiento con la ruta de ayuda, el access token vencido responde `401`, el refresh token entrega uno nuevo, y después de revocar la renovación responde `400` (`invalid_grant`) y el acceso `401`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p8-newman-oauth-renovacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2468" alt="Ejecución de la carpeta 8 de OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p8-newman-oauth-renovacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 8 de OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 8: el ciclo de vida de una autorización.</figcaption></figure>

Carpeta 9: el código de autorización es de un solo uso. Canjearlo por segunda vez se rechaza y, como defensa, el simulador revoca lo que ya había emitido con ese código.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p9-newman-oauth-codigo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2154" alt="Ejecución de la carpeta 9 de OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p9-newman-oauth-codigo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 9 de OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 9: reutilizar un código es señal de robo.</figcaption></figure>

### 4.3 OAuth 2.0 a través del webhook de n8n

La carpeta 10 llama al webhook con `oauth2` y `oauth2_sin_permiso`. Postman no envía ningún token: los pone n8n con sus credenciales conectadas. Antes de ejecutarla, conecta las dos credenciales OAuth (sección 3.5).

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p10-newman-oauth-webhook.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1020" alt="Ejecución de la carpeta 10 con el webhook de n8n"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p10-newman-oauth-webhook.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 10 con el webhook de n8n" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 10: la ruta OAuth 2.0 responde <code>200</code> y la ruta con permiso insuficiente, <code>403</code>.</figcaption></figure>

La carpeta 11 es una **prueba manual**: abre <http://localhost:8091/oauth/autorizaciones>, pulsa **Revocar** en la autorización de n8n y ejecuta solo la solicitud 11.1. El workflow debe responder `401` con el error `autorizacion_no_valida`. Para volver a la normalidad, usa **Switch account** en la credencial y autoriza de nuevo. Al usar **Run collection**, desmarca la carpeta 11.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p5-postman-resumen.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1524" alt="Resumen de la ejecución de las carpetas 0 a 10"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-oauth2-biblioteca/p5-postman-resumen.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Resumen de la ejecución de las carpetas 0 a 10" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Resultado de las carpetas 0 a 10: 50 solicitudes y 119 pruebas, ninguna fallida. La carpeta 11 es una prueba manual y no forma parte de esta ejecución.</figcaption></figure>

## 5. Diagnóstico y resolución de errores


### 5.1 Errores de OAuth 2.0

Estos errores salen de la pantalla de consentimiento y del canje de tokens. Tienen nombres estándar de OAuth 2.0:

| Error | Dónde aparece | Qué significa |
| --- | --- | --- |
| `access_denied` | Al volver a n8n tras la pantalla de consentimiento | La persona pulsó **Rechazar** |
| `invalid_request` | Al volver a n8n | Falta un dato obligatorio (por ejemplo `state`) o PKCE mal armado |
| `invalid_scope` | Al volver a n8n | Se pidió un permiso que no existe |
| `invalid_client` | Al canjear o renovar (`401`) | Client ID o Client Secret incorrectos |
| `invalid_grant` | Al canjear o renovar (`400`) | El código o el refresh token no sirve: venció, ya se usó, no coincide con la `redirect_uri` o fue revocado |
| «redirect_uri no registrada» | En la pantalla del simulador, sin redirigir | La dirección de vuelta no es exactamente la registrada |

### 5.2 Guía para resolver errores frecuentes

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| El webhook responde 404 | El workflow no está publicado, o usas la Test URL | Publícalo y usa `/webhook/acceso-seguro` |
| Un nodo muestra una credencial sin seleccionar | Falta crearla o elegirla en el nodo | Crea las cinco credenciales. En los dos nodos OAuth hay dos credenciales del mismo tipo: elige cada una por su nombre |
| La ruta JWT responde 500 | La credencial `Login JWT` tiene un JSON mal escrito | Revisa que sea el JSON de la Guía 15, sección 7.3, con comillas dobles |
| `ECONNREFUSED` en un nodo | n8n no encuentra el simulador | Usa `http://catalogo:8080` y el `compose.yaml` del paquete |
| **Connect** no abre la pantalla de consentimiento | La Authorization URL apunta a `catalogo` o a un puerto equivocado | Usa `http://localhost:8091/oauth/autorizar`: la abre tu navegador |
| La pantalla dice «redirect_uri no registrada» | Abriste n8n con otra dirección o cambiaste `N8N_PUERTO` sin recrear el simulador | Entra por `http://localhost:5680` y ejecuta `docker compose up -d` |
| Tras autorizar, n8n muestra «Unauthorized» | Entraste a n8n como `127.0.0.1` y el navegador no envía tu sesión a `localhost` | Abre n8n como `http://localhost:5680`, cierra sesión y vuelve a entrar |
| El nodo OAuth responde 401 `token_desconocido` | Nunca conectaste la credencial, o el simulador se reinició y olvidó las autorizaciones | Abre la credencial y pulsa **Connect** o **Switch account** |
| El nodo OAuth responde 403 `insufficient_scope` | La credencial se conectó sin `catalogo.leer` | Corrige el **Scope**, guarda y vuelve a conectar |
| La ruta OAuth responde 401 `autorizacion_no_valida` | La autorización se revocó o venció y no se puede renovar | Vuelve a autorizar: **Switch account** en la credencial |
| La credencial dice «Account connected» pero falla | n8n no se entera de una revocación hasta que intenta usarla | Vuelve a autorizar con **Switch account** |
| El puerto está ocupado | Otra aplicación lo usa | Cambia `N8N_PUERTO` y `CATALOGO_PUERTO` (sección 2) |
| Postman no conecta | Puertos o entorno equivocados | Selecciona el entorno y revisa `url_n8n`, `url_simulador` y `oauth_redirect_uri` |

## 6. Pruebas de aceptación

Estas pruebas fueron reportadas y documentadas el 25/11/2026 durante la preparación original del laboratorio, en una instalación limpia hecha solo con el ZIP del paquete (n8n 2.44.6, Docker). La columna «Obtenido» es lo que se midió, no lo que se esperaba.

| # | Prueba | Cómo se ejecuta | Esperado | Obtenido |
| --- | --- | --- | --- | --- |
| 1 | API Key anterior | Postman 2.3 (directo) y 5.1 (webhook) | Continúa funcionando | 200 directo y 200 por el webhook |
| 2 | Basic Auth anterior | Postman 3.3 y 5.2 | Continúa funcionando | 200 directo y 200 por el webhook |
| 3 | JWT anterior | Postman 4.7 y 5.3 | Continúa funcionando | 200 directo y 200 por el webhook |
| 4 | OAuth sin autorización | Postman 6.1 | Rechazo del acceso (401) | 401 `falta_credencial` |
| 5 | Consentimiento rechazado | Postman 6.6 y **Connect** > Rechazar en n8n | No se concede acceso | 302 con `access_denied` y sin código; n8n muestra «Failed to connect» y la credencial queda sin conectar |
| 6 | Consentimiento aceptado | Postman 6.8 y 6.10 y **Connect** > Autorizar en n8n | Autorización exitosa | Código y `state` de vuelta (302), canje 200 con dos tokens; n8n muestra «Account connected» |
| 7 | Token con `catalogo.leer` | Postman 7.1 y 10.1 | Consulta correcta (200) | 200 directo y 200 por el webhook |
| 8 | Token sin permiso suficiente | Postman 7.5 y 10.2 | 403 | 403 directo y 403 por el webhook, con `insufficient_scope` |
| 9 | Access Token vencido y Refresh Token vigente | Postman 8.2 a 8.4 y webhook tras vencer | Renovación exitosa | 401 `token_vencido`, renovación 200, consulta 200. En n8n: webhook 200 (secuencia en el simulador: 401, `POST /oauth/token` 200, 200) |
| 10 | Refresh Token revocado | Postman 8.5 y 8.6 | Renovación rechazada | Revocar 200, renovar 400 `invalid_grant` |
| 11 | Consulta posterior a la revocación | Postman 8.7 y 11.1 (revocando desde la página de autorizaciones) | Acceso denegado | 401 `autorizacion_revocada` directo; webhook de n8n 401 `autorizacion_no_valida` |
| 12 | Código de un solo uso | Postman 9.4 y 9.5 | Segundo canje rechazado y lo emitido se revoca | 400 `invalid_grant` y luego 401 `autorizacion_revocada` |
| 13 | `redirect_uri` no registrada | Postman 6.3 | Error en pantalla, sin redirigir | 400 sin cabecera `Location` |
| 14 | Sin `state` | Postman 6.4 | Rechazo | 302 con `error=invalid_request` |
| 15 | Las tres rutas anteriores tras revocar OAuth | Webhook con `api_key`, `basic` y `jwt` | Siguen respondiendo 200 | 200, 200 y 200 |

Colección completa (carpetas 0 a 10): 50 solicitudes, 119 pruebas, 0 fallidas. La carpeta 11 se ejecutó después de revocar a mano la autorización de n8n.

## 7. Buenas prácticas y límites del ejemplo

- **Mínimo privilegio:** solicita solo los scopes necesarios. Un token válido con `perfil.leer` no equivale a `catalogo.leer`.
- **Credenciales:** el Client Secret y los tokens se guardan en el gestor de credenciales de n8n, no en nodos ni notas. No compartas exports de ejecuciones que puedan contener tokens.
- **Retorno de OAuth:** entra en n8n con `http://localhost:5680`; con `127.0.0.1` el callback puede fallar por la sesión del navegador.
- **Caducidad:** n8n puede renovar automáticamente el access token cuando el refresh token sigue siendo válido. Revocar la autorización requiere autorizar nuevamente.
- **Seguridad:** este simulador corre localmente por HTTP, conserva autorizaciones en memoria y no limita intentos. Es para enseñanza, no para producción.
- **Separación:** OAuth 2.0 es un protocolo para delegar autorización; JWT es un formato posible de token. OAuth puede utilizar un token JWT u otro formato.

## 8. Comprueba lo aprendido

1. ¿Qué cambia entre rechazar y aceptar el consentimiento?
2. ¿Por qué `perfil.leer` produce 403 al consultar el catálogo, aunque el token sea válido?
3. ¿Qué ocurre si vence el access token y el refresh token todavía es válido?
4. ¿Qué cambia después de revocar la autorización?
5. ¿Por qué n8n usa `catalogo:8080` para el token y el navegador `localhost:8091` para el consentimiento?

## 9. Recursos y descargas del laboratorio avanzado

El paquete **avanzado** incluye el mismo caso de biblioteca, más las rutas OAuth 2.0, las credenciales de demostración, las notas del workflow y una colección de Postman ampliada. Puedes utilizarlo sin instalar previamente el paquete básico, pero no debes iniciar ambos en los mismos puertos a la vez.

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-oauth2-biblioteca/biblioteca-acceso-seguro-completo.zip" download="biblioteca-oauth2-avanzado.zip">Descargar laboratorio avanzado completo (ZIP)</a></p>

Archivos individuales:

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-oauth2-biblioteca/biblioteca-acceso-seguro-workflow.json" download="biblioteca-acceso-seguro-workflow.json">Workflow avanzado (JSON)</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-oauth2-biblioteca/compose.yaml" download="compose.yaml">Docker Compose</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-oauth2-biblioteca/simulador_catalogo_seguro.py" download="simulador_catalogo_seguro.py">Simulador OAuth y catálogo</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-oauth2-biblioteca/biblioteca-acceso-seguro.postman_collection.json" download="biblioteca-acceso-seguro.postman_collection.json">Colección de Postman</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-oauth2-biblioteca/biblioteca-local.postman_environment.json" download="biblioteca-local.postman_environment.json">Entorno de Postman</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-oauth2-biblioteca/env.example" download="env.example">Ejemplo de variables de entorno</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-oauth2-biblioteca/datos-prueba.zip" download="datos-prueba.zip">Datos de prueba</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-oauth2-biblioteca/README.md" download="README.md">README de instalación y actualización</a></p>

**Material previo:** [Guía 15 — API Key, Basic Auth y JWT](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-credenciales-autenticacion). Cada guía mantiene su propio paquete descargable.

### Documentación

- [Credenciales de n8n](https://docs.n8n.io/credentials/)
- [Nodo HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [RFC 6749: OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749)
- [RFC 7636: PKCE](https://www.rfc-editor.org/rfc/rfc7636)
- [RFC 7009: revocación de tokens](https://www.rfc-editor.org/rfc/rfc7009)
