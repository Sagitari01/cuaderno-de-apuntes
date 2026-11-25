# Biblioteca: acceso seguro al catálogo (API Key, Basic Auth, JWT y OAuth 2.0 en n8n)

Ejemplo independiente para practicar credenciales y autenticación de APIs en n8n. Todo corre en tu computador con Docker:
n8n y una API ficticia del catálogo de una biblioteca que **valida de verdad** las credenciales. No usa servicios externos
ni cuentas reales. **Todos los valores de este paquete son de demostración y no deben usarse en sistemas reales.**

## Contenido

| Archivo | Para qué sirve |
| --- | --- |
| `compose.yaml` | Levanta n8n y el simulador en la misma red de Docker. |
| `.env.example` | Valores de demostración y puertos configurables (copia a `.env` solo si quieres cambiarlos). |
| `simulador_catalogo_seguro.py` | API ficticia con endpoint público, API Key, Basic Auth, JWT y un servidor OAuth 2.0 educativo con pantalla de consentimiento (Python, solo biblioteca estándar). |
| `biblioteca-acceso-seguro-workflow.json` | Workflow de n8n «Biblioteca \| Acceso seguro al catálogo», con sus 12 notas adhesivas y cuatro mecanismos de autenticación. |
| `biblioteca-acceso-seguro.postman_collection.json` | Colección de Postman: 51 solicitudes con pruebas automáticas (API directa y webhook de n8n). |
| `biblioteca-local.postman_environment.json` | Entorno de Postman con las direcciones locales y los valores de demostración. |
| `datos-prueba/` | Cuerpos JSON de ejemplo para el webhook (los cinco tipos de autenticación) y para pedir un token. |

## Requisitos

Docker con Docker Compose. Para las pruebas visuales, Postman. No necesitas Python ni Node.js en tu equipo.

## Puesta en marcha

1. Descomprime el paquete y abre una terminal dentro de la carpeta `biblioteca-acceso-seguro`.
2. Ejecuta `docker compose up -d`. Direcciones por defecto: n8n en <http://localhost:5680> y el simulador en <http://localhost:8091>.
   Si un puerto está ocupado, cámbialo así: `N8N_PUERTO=5681 CATALOGO_PUERTO=8092 docker compose up -d`.
3. Comprueba el simulador: <http://localhost:8091/salud> debe responder `"estado": "activo"`.
4. Abre n8n y crea tu cuenta local la primera vez.

Dentro de n8n, el simulador se llama `catalogo`: la dirección es `http://catalogo:8080` (no `localhost`).

## Si ya tenías el ejemplo instalado (actualización)

Esta versión agrega OAuth 2.0 sin cambiar API Key, Basic Auth ni JWT. **No borres nada:** tus credenciales y workflows están en el
volumen de n8n y se conservan.

1. No hace falta apagar el ejemplo. Reemplaza en tu carpeta `biblioteca-acceso-seguro` los archivos
   `simulador_catalogo_seguro.py` y `compose.yaml` por los de este paquete. Si usas un `.env`, agrega las líneas nuevas de `.env.example`
   (son opcionales: sin ellas se usan los valores de demostración).
2. Ejecuta `docker compose up -d`. Compose recrea solo el servicio `catalogo` (el simulador). `n8n` y su volumen no se tocan.
3. Comprueba que lo anterior sigue funcionando: <http://localhost:8091/salud> responde `"estado": "activo"` y el workflow que ya tenías
   responde igual que antes.
4. Importa el workflow nuevo como un workflow aparte (menú `...` > **Import from file**), o reemplaza el anterior si no lo modificaste.
   Crea las dos credenciales OAuth de la sección siguiente; las tres credenciales anteriores no cambian.

Al reiniciar el simulador se pierden las autorizaciones OAuth (viven en memoria): en n8n hay que volver a pulsar **Connect**.
Nunca ejecutes `docker compose down -v` para actualizar: ese comando borra el volumen de n8n.

## Credenciales de demostración

| Mecanismo | Dato | Valor de demostración |
| --- | --- | --- |
| API Key | Cabecera | `X-API-Key` |
| API Key | Valor | `demo-clave-api-biblioteca` |
| Basic Auth | Usuario | `lector-demo` |
| Basic Auth | Contraseña | `demo-clave-basic` |
| JWT | Usuario | `lector-demo` |
| JWT | Clave | `demo-clave-jwt` |
| OAuth 2.0 | Client ID | `biblioteca-n8n` |
| OAuth 2.0 | Client Secret | `demo-secreto-oauth-biblioteca` |
| OAuth 2.0 | Permisos (scopes) | `catalogo.leer` (consultar el catálogo) y `perfil.leer` (ver el nombre de la cuenta) |

La clave con que el simulador firma los tokens (`JWT_SECRETO`) vive solo dentro del simulador. n8n nunca la conoce y no está en el workflow.
En OAuth 2.0 la persona no tiene una contraseña que n8n deba conocer: autoriza en la pantalla de consentimiento y n8n recibe solo tokens.

## Crear las credenciales en n8n

Este workflow **no trae los valores del gestor de credenciales**. Un JSON puede contener secretos escritos manualmente en parámetros o datos fijados; revisa siempre el archivo antes de compartirlo. Créalas antes de usarlo, con estos nombres exactos
(en **Credentials > Create credential**):

1. **Header Auth** llamada `Biblioteca | API Key (demo)`. Name: `X-API-Key`. Value: la clave de la tabla.
2. **Basic Auth** llamada `Biblioteca | Basic Auth (demo)`. User y Password de la tabla.
3. **Custom Auth** llamada `Biblioteca | Login JWT (demo)`. En JSON escribe:
   `{"body": {"usuario": "lector-demo", "clave": "demo-clave-jwt"}}`
4. **OAuth2 API** llamada `Biblioteca | OAuth2 (demo)`:
   - **Grant Type:** Authorization Code (viene por defecto).
   - **Authorization URL:** `http://localhost:8091/oauth/autorizar` (la abre tu navegador, por eso es `localhost`).
   - **Access Token URL:** `http://catalogo:8080/oauth/token` (la llama n8n por dentro de Docker, por eso es `catalogo`).
   - **Client ID** y **Client Secret:** los de la tabla.
   - **Scope:** `catalogo.leer`. Deja **Authentication** en Header.
   - Comprueba que **OAuth Redirect URL** diga `http://localhost:5680/rest/oauth2-credential/callback`. Si no, abriste n8n por otra dirección.
   - Pulsa **Save** y luego **Connect**. En la pantalla de consentimiento pulsa **Autorizar**. Debe aparecer «Account connected».
5. Otra **OAuth2 API** llamada `Biblioteca | OAuth2 solo perfil (demo)`, igual que la anterior pero con **Scope** `perfil.leer`. Conéctala también.
   Sirve para ver el error 403.

**Abre n8n siempre como `http://localhost:5680`** (no `127.0.0.1`): la dirección de vuelta de OAuth es `localhost` y el navegador solo
envía tu sesión a la misma dirección con la que entraste.

## Importar y publicar el workflow

1. En un workflow vacío abre el menú `...` > **Import from file** y elige `biblioteca-acceso-seguro-workflow.json`. Se conservan las 12 notas adhesivas.
2. Los nodos **Consultar con API Key**, **Consultar con Basic Auth**, **Obtener token**, **Consultar con OAuth 2.0** y **Consultar con OAuth 2.0 sin permiso** aparecen con un triángulo de aviso: la credencial no está enlazada. Abre cada uno. Si solo existe una credencial de ese tipo, n8n la propone sola; comprueba que sea la correcta (o elígela en la lista) y guarda. En los dos nodos de OAuth hay **dos** credenciales del mismo tipo (OAuth2 API): elige cada una por su nombre (`Biblioteca | OAuth2 (demo)` en **Consultar con OAuth 2.0** y `Biblioteca | OAuth2 solo perfil (demo)` en **Consultar con OAuth 2.0 sin permiso**). El nodo **Consultar con JWT** no usa credencial guardada: recibe el token por una expresión.
3. Guarda con `Ctrl+S` y pulsa **Publish** (n8n pide un nombre de versión). Hasta publicar, el webhook de producción responde 404.

## Probar con Postman

1. En Postman elige **Import** y carga la colección y el entorno. Selecciona el entorno **Biblioteca local (demo)** (arriba a la derecha).
2. Si cambiaste los puertos, edita `url_n8n`, `url_simulador` y `oauth_redirect_uri` en el entorno.
3. Ejecuta las carpetas en orden. Las carpetas 1 a 4 llaman directo al simulador y muestran qué ocurre con y sin credenciales (200 o 401). La carpeta 5 llama al webhook del workflow de n8n: **ahí no envías ninguna clave**, la pone n8n con su credencial guardada.
4. Las carpetas 6 a 9 recorren OAuth 2.0 directo contra el simulador: consentimiento rechazado y aceptado, canje del código, permisos (scopes), vencimiento, renovación, revocación y código de un solo uso. Aquí Postman hace de «aplicación» y de «persona» a la vez, sin navegador.
5. La carpeta 10 llama al webhook de n8n con OAuth 2.0 (necesita las dos credenciales OAuth conectadas). La carpeta 11 es una **prueba manual**:
   revoca la autorización de n8n en <http://localhost:8091/oauth/autorizaciones> y ejecuta solo esa solicitud (debe responder 401).
   Al usar **Run collection**, desmarca la carpeta 11.

Resultados esperados: público 200; API Key sin clave 401, incorrecta 401, válida 200; Basic incorrecto 401, válido 200; token con credenciales válidas
(200 con `access_token`); JWT sin token 401, inválido 401, vencido 401, válido 200; webhook de n8n 200 en las tres rutas y 400 con un tipo no válido.
OAuth 2.0: sin token 401; `redirect_uri` no registrada 400 (sin redirigir); sin `state` error; consentimiento rechazado `access_denied` y sin código;
aceptado, código y `state` de vuelta; canje con secreto incorrecto 401; canje correcto 200 con dos tokens; `catalogo.leer` 200; solo `perfil.leer` 403;
token vencido 401, renovación 200; autorización revocada, renovación 400 y consulta 401; código reutilizado 400; webhook de n8n 200 y, sin permiso, 403.

Los tokens que pide la colección se guardan en variables de colección. Newman no los escribe en los archivos de entrada; en Postman revisa las variables antes de exportar o compartir. Las salidas con tokens también pueden conservarse en el historial de ejecuciones de n8n.

## Rutas del simulador

| Ruta | Autenticación |
| --- | --- |
| `GET /salud` | Ninguna |
| `GET /catalogo/publico` | Ninguna. Solo títulos y total de ejemplares |
| `GET /catalogo/api-key` | Cabecera `X-API-Key` |
| `GET /catalogo/basic` | Cabecera `Authorization: Basic <usuario:clave en Base64>` |
| `POST /auth/token` | JSON con `usuario` y `clave`. Entrega un JWT firmado (HS256) que vence en 300 segundos |
| `GET /catalogo/jwt` | Cabecera `Authorization: Bearer <token>` |
| `GET /demo/token-vencido` | Solo para la clase: entrega un token ya vencido |
| `GET /registro` | Últimas peticiones recibidas (sin valores secretos) |
| `GET /reiniciar` | Borra el registro |
| `GET /oauth/autorizar` | OAuth: pantalla de consentimiento (`client_id`, `redirect_uri`, `scope`, `state`; `code_challenge` opcional) |
| `POST /oauth/decidir` | OAuth: la persona pulsa Autorizar o Rechazar. Vuelve a la aplicación con `code` o con `error=access_denied` |
| `POST /oauth/token` | OAuth: canjea el código por tokens (`authorization_code`) o renueva (`refresh_token`). Pide Client ID y Client Secret |
| `POST /oauth/revocar` | OAuth: la aplicación revoca una autorización (con Client ID y Client Secret) |
| `GET /oauth/autorizaciones` | OAuth: la persona ve y revoca las autorizaciones que dio |
| `GET /catalogo/oauth` | Cabecera `Authorization: Bearer <access token>` con el scope `catalogo.leer` |
| `GET /oauth/perfil` | Cabecera `Authorization: Bearer <access token>` con el scope `perfil.leer` |
| `POST /demo/oauth/vencer-tokens` | Solo para practicar: vence todos los access tokens sin esperar 5 minutos |

Las rutas protegidas aceptan `?titulo=El faro de papel`. Responden `401` con un `motivo` (`falta_credencial`, `credencial_incorrecta`,
`token_malformado`, `firma_invalida`, `token_vencido`...). En OAuth, `401` significa que el token falta, no existe, venció o fue revocado, y `403`
(`insufficient_scope`) que el token es válido pero no tiene el permiso de esa ruta. Para ver las peticiones en vivo: `docker compose logs -f catalogo`.

## Seguridad: lo que conviene recordar

- Una credencial se guarda en n8n, cifrada, y los workflows solo la **seleccionan**. No escribas claves dentro de nodos, expresiones ni notas.
- Base64 no es cifrado. Con Basic Auth y API Key, usa siempre HTTPS fuera de este ejercicio.
- Un token JWT es temporal: se pide, se usa y vence. No lo guardes como valor fijo.
- Proteger el **webhook de n8n** (quién puede llamar a tu workflow) es otro control distinto de autenticarse contra una API externa.
- OAuth 2.0 permite que una aplicación acceda con permisos limitados, sin conocer tu contraseña, y que tú los quites cuando quieras. Pide solo el scope que necesitas.
- El **Client Secret** y los tokens son secretos: viven en la credencial de n8n, nunca en el workflow ni en una nota. Un export del workflow no los incluye.
- El código de autorización es temporal y de un solo uso, y la `redirect_uri` debe ser exactamente la registrada. `state` evita solicitudes falsificadas.
- El simulador OAuth es **educativo**: guarda todo en memoria, no pide una contraseña real, no limita intentos y no usa HTTPS. No lo uses como servidor de autorización real.
- Cambia todos los valores de este paquete antes de usar algo parecido en un sistema real.

## Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| El webhook responde 404 | El workflow no está publicado, o usas la Test URL | Publícalo y usa `/webhook/acceso-seguro` |
| `Credential not found` o credencial sin seleccionar | Falta crearla o elegirla en el nodo | Crea las tres credenciales y selecciónalas |
| La ruta JWT responde 500 | La credencial `Login JWT` tiene un JSON mal escrito | Revisa que sea el JSON de arriba, con comillas dobles |
| `ECONNREFUSED` en un nodo | n8n no encuentra el simulador | Usa `http://catalogo:8080` y el `compose.yaml` del paquete |
| El puerto está ocupado | Otra aplicación lo usa | `N8N_PUERTO=5681 CATALOGO_PUERTO=8092 docker compose up -d` |
| «Connect» no abre la pantalla de consentimiento | La Authorization URL apunta a `catalogo` o el puerto es otro | Usa `http://localhost:8091/oauth/autorizar` (la abre tu navegador) |
| La pantalla dice «redirect_uri no registrada» | Abriste n8n con otra dirección o cambiaste `N8N_PUERTO` sin recrear el simulador | Entra por `http://localhost:5680` y ejecuta `docker compose up -d` |
| Tras autorizar, n8n muestra «Unauthorized» | Entraste a n8n como `127.0.0.1` y el callback vuelve a `localhost` (otra sesión) | Abre n8n como `http://localhost:5680`, cierra sesión y vuelve a entrar |
| El nodo OAuth responde 401 | Nunca conectaste la credencial, o el simulador se reinició y olvidó las autorizaciones | Abre la credencial y pulsa **Connect** o **Switch account** |
| El nodo OAuth responde 403 `insufficient_scope` | La credencial se conectó sin `catalogo.leer` | Corrige el Scope, guarda y vuelve a conectar |
| La ruta OAuth responde 401 «autorizacion_no_valida» | La autorización se revocó o venció y no se puede renovar | Vuelve a autorizar: **Switch account** en la credencial |
| Postman no conecta | Puertos o entorno equivocados | Selecciona el entorno y revisa `url_n8n` y `url_simulador` |

## Limpieza

`docker compose down -v` detiene los contenedores y borra los datos de n8n (incluidas tus credenciales y workflows).
