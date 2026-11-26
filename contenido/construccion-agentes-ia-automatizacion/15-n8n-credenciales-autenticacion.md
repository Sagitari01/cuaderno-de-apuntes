# Credenciales y autenticación de APIs en n8n: API Key, Basic Auth, JWT y OAuth 2.0

Una biblioteca tiene una API que informa cuántos ejemplares de un libro están disponibles. Esa información no debería estar al alcance de cualquier aplicación. Aquí aprenderás cómo un workflow de n8n accede de forma segura a un servicio que exige autenticación: dónde se guardan las claves, cómo se configuran los cuatro mecanismos más comunes (API Key, Basic Auth, JWT y OAuth 2.0) y qué ocurre cuando las credenciales fallan o los permisos no alcanzan.

Es la continuación de la [biblioteca de manejo de errores](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-manejo-de-errores), con los mismos libros ficticios, pero es un ejercicio independiente: no necesitas haber importado nada de ese apunte.

## 1. El problema de la biblioteca

Antes aprendiste a consultar el catálogo y a manejar sus errores. Ahora el problema es otro: **¿cómo impedimos que cualquier aplicación consulte información protegida del catálogo?**

La biblioteca decide qué es público y qué no:

| Dato | Quién puede verlo |
| --- | --- |
| Títulos y total de ejemplares | Cualquiera, sin credenciales |
| Préstamos activos y ejemplares disponibles | Solo quien demuestre quién es |

Estos son los libros del catálogo ficticio:

| Libro | Total | Préstamos | Disponibles |
| --- | ---: | ---: | ---: |
| El faro de papel | 5 | 2 | 3 |
| Jardines de tinta | 4 | 4 | 0 |
| Atlas de las nubes verdes | 7 | 1 | 6 |
| La casa de los mapas | 3 | 0 | 3 |
| Viaje al bosque azul | 6 | 4 | 2 |
| Historias del reloj | 8 | 3 | 5 |

Todos los títulos, usuarios y claves de este apunte son ficticios.

## 2. Objetivos del ejercicio

Al terminar sabrás:

- crear y usar credenciales en el gestor de n8n sin escribir secretos dentro de los workflows;
- configurar una **API Key**, una **Basic Auth** y un **JWT** en un nodo HTTP Request, y una credencial **OAuth2 API** con pantalla de consentimiento;
- distinguir qué datos necesita cada mecanismo, dónde se configuran y cómo viajan;
- probar cada caso con Postman, con y sin credenciales, y leer los códigos HTTP;
- leer una ejecución rechazada con `401` dentro de n8n;
- explicar la diferencia entre autenticación y autorización, y entre un error `401` y un `403`;
- ver cómo n8n renueva un token vencido y qué ocurre cuando la persona revoca la autorización;
- revisar un workflow con una lista de control de seguridad.

Necesitas Docker con Docker Compose, Postman y haber usado antes un workflow con **Webhook** y **HTTP Request**. No necesitas Python ni Node.js.

## 3. Qué es autenticarse

**Autenticarse** es demostrar quién eres. Una **credencial** es el dato con el que lo demuestras: una clave, un usuario y una contraseña, o un token. Es algo distinto de la **autorización**, que decide qué puedes hacer una vez que sabemos quién eres.

Piensa en el carnet de la biblioteca. Mostrarlo demuestra que eres socio (autenticación). Que puedas llevarte tres libros o solo consultar el catálogo depende de tus permisos (autorización).

Cuando una API protegida recibe una solicitud, puede responder:

- `200`: la credencial es válida y te entrega el dato;
- `401`: no sabe quién eres (falta la credencial o es incorrecta);
- `403`: sabe quién eres, pero no tienes permiso para eso.

En este ejercicio la API responde `401` cuando falla la autenticación y `403` cuando el token es válido pero le falta un permiso (lo verás con OAuth 2.0 en la sección 9).

## 4. API Key, Basic Auth, JWT y OAuth 2.0: en qué se diferencian

Los cuatro permiten consultar el mismo catálogo, pero piden datos distintos, los envían de manera distinta y responden a preguntas distintas. Los tres primeros se explican aquí; OAuth 2.0 tiene su propia sección (la 9) porque cambia quién decide el acceso:

<div role="region" aria-label="Comparación de autenticación, desplázate horizontalmente para ver todas las columnas" tabindex="0" style="max-width:100%;overflow-x:auto">
<div style="min-width:900px">

| | API Key | Basic Auth | JWT (Bearer) | OAuth 2.0 |
| --- | --- | --- | --- | --- |
| Qué envías | Una clave | Usuario y contraseña | Un token temporal | Un access token temporal |
| Dónde viaja | Cabecera `X-API-Key` | Cabecera `Authorization: Basic ...` | Cabecera `Authorization: Bearer ...` | Cabecera `Authorization: Bearer ...` |
| Quién decide el acceso | Quien entrega la clave | Quien administra la cuenta | Quien administra la cuenta | La persona dueña de los datos, en la pantalla de consentimiento |
| Identifica a | Una aplicación | Una cuenta | Una sesión de una cuenta | Una aplicación autorizada por una persona |
| Permisos | Los que tenga la clave | Los de la cuenta | Los de la cuenta | Solo los que la persona autorizó (scope) |
| ¿Vence? | No, hasta que se cambie | No, hasta que se cambie | Sí, a los pocos minutos | Sí el access token; el refresh token permite renovarlo |
| Pasos previos | Ninguno | Ninguno | Pedir el token con usuario y clave | Autorizar una vez (botón Connect) |
| ¿Se quita el acceso sin cambiar la clave? | No: hay que cambiar la clave | No: hay que cambiar la contraseña | Solo esperando que venza | Sí: la persona revoca la autorización |
| Se guarda en n8n como | Header Auth | Basic Auth | Credencial de login (Custom Auth) más una expresión | OAuth2 API |

</div>
</div>

En pantallas pequeñas, desplaza la tabla horizontalmente para ver todas las columnas.

Así se ven las cabeceras. Los valores entre `<` y `>` son marcadores, no claves reales:

<pre><code class="language-text">X-API-Key: &lt;tu clave>
Authorization: Basic &lt;usuario:contraseña codificado en Base64>
Authorization: Bearer &lt;token></code></pre>

Estas ideas conviene tenerlas claras antes de seguir:

- **Base64 no es cifrado.** Es solo una forma de escribir texto. Cualquiera que vea la cabecera de Basic Auth puede recuperar el usuario y la contraseña. En sistemas reales, estos mecanismos se usan siempre sobre **HTTPS**, que cifra la conexión. Aquí usamos HTTP porque todo corre en tu computador.
- **Un token es una credencial temporal.** En un JWT, la API lo firma con una clave que solo ella conoce. Tiene tres partes separadas por puntos (cabecera, datos y firma) y una fecha de vencimiento. Los datos son legibles; lo que impide alterarlos es la firma. Cuando vence, hay que pedir otro.
- **Bearer significa «portador».** Quien presenta el token, lo usa. Por eso un token no se comparte ni se deja escrito en ningún lugar.
- **OAuth 2.0 no es otra forma de enviar una clave.** Es una forma de que una persona autorice a una aplicación sin darle su contraseña. El token que la aplicación recibe al final viaja como Bearer, igual que un JWT, pero el camino para conseguirlo es distinto.

## 5. Arquitectura del ejemplo

El ejemplo tiene dos servicios en Docker y un único workflow:

- **n8n**, donde vive el workflow **Biblioteca | Acceso seguro al catálogo** y el gestor de credenciales.
- **Catálogo seguro**, una API ficticia escrita en Python que **valida de verdad** las credenciales. Para JWT firma y verifica los tokens con HMAC-SHA256 y revisa el vencimiento. Para OAuth 2.0 actúa además como servidor de autorización educativo: muestra la pantalla de consentimiento, entrega códigos y tokens y valida los permisos. Dentro de la red de Docker se llama `catalogo`.
- **Postman**, que usarás desde tu computador para llamar al simulador y al webhook de n8n.

El workflow recibe una consulta, elige una ruta según el mecanismo y responde con lo que contestó la API:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w17-workflow-completo-notas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3600" height="3400" alt="Workflow completo con las doce notas adhesivas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w17-workflow-completo-notas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow completo con las doce notas adhesivas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El workflow terminado, con sus doce notas adhesivas: las siete de la parte básica y las cinco de OAuth 2.0 (abajo).</figcaption></figure>

| Nodo | Qué hace |
| --- | --- |
| Recibir consulta | **Webhook** que recibe un JSON con `titulo` y `tipo_autenticacion` |
| Preparar datos | **Edit Fields** que deja esos dos campos listos |
| Tipo de autenticación | **Switch** que elige la ruta: `api_key`, `basic`, `jwt`, `oauth2`, `oauth2_sin_permiso` u Otro |
| Consultar con API Key | **HTTP Request** con credencial Header Auth |
| Consultar con Basic Auth | **HTTP Request** con credencial Basic Auth |
| Obtener token | **HTTP Request** que pide un JWT con la credencial de login |
| Consultar con JWT | **HTTP Request** que envía el token en `Authorization: Bearer` |
| Consultar con OAuth 2.0 | **HTTP Request** con credencial OAuth2 API (permiso `catalogo.leer`) y salida de error |
| Consultar con OAuth 2.0 sin permiso | **HTTP Request** con una segunda credencial OAuth2 API que solo tiene `perfil.leer` |
| Responder (OAuth 2.0 sin autorización) | **Respond to Webhook** que contesta `401` cuando n8n no puede renovar la autorización |
| Responder (...) | **Respond to Webhook** que devuelve el resultado con el mismo código HTTP |
| Responder (tipo no válido) | Responde `400` si el tipo de autenticación no existe |

Un detalle importante: **proteger el webhook de n8n es un control distinto**. Aquí el webhook queda abierto porque solo se usa en tu computador. Las credenciales de este apunte protegen la **API del catálogo**, que es a la que n8n se conecta.

## 6. Prepara el entorno Docker

**¿Qué estamos haciendo?** Levantamos n8n y la API del catálogo en la misma red de Docker, sin instalar nada más.

**¿Para qué sirve?** Todo el ejercicio ocurre en tu computador. No hay servicios externos, cuentas reales ni claves personales.

**¿Cómo lo hacemos?** Descarga el paquete completo (al final del apunte), descomprímelo y abre una terminal dentro de la carpeta `biblioteca-acceso-seguro`. Contiene el `compose.yaml`, el simulador, el workflow, la colección de Postman y los datos de prueba:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d0-paquete-archivos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1334" alt="Contenido del paquete descomprimido"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d0-paquete-archivos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Contenido del paquete descomprimido" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Archivos del paquete. <code>.env.example</code> lista los valores de demostración y los puertos.</figcaption></figure>

Ejecuta:

<pre><code class="language-text">docker compose up -d</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d1-compose-up.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="768" alt="Salida de docker compose up -d"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d1-compose-up.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de docker compose up -d" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Docker crea la red, el volumen y los dos contenedores. Cada uno termina en <b>Started</b>.</figcaption></figure>

Comprueba que los dos servicios están en marcha:

<pre><code class="language-text">docker compose ps</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d2-compose-ps.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="578" alt="Contenedores en ejecución con sus puertos"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d2-compose-ps.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Contenedores en ejecución con sus puertos" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Los puertos publicados por defecto: n8n en <code>5680</code> y el simulador en <code>8091</code>, solo accesibles desde tu computador.</figcaption></figure>

**¿Usas Windows?** Abre **Docker Desktop** y comprueba que esté funcionando. Descomprime el ZIP, entra a la carpeta `biblioteca-acceso-seguro` y abre **PowerShell** en esa carpeta. El comando para iniciar los servicios es el mismo:

<pre><code class="language-powershell">docker compose up -d</code></pre>

**Si los puertos están ocupados**, en Windows PowerShell no utilices la sintaxis de variables al inicio del comando que se usa en Linux/macOS. Configúralos mediante un archivo `.env`:

1. Crea una copia de `.env.example` como `.env` con `Copy-Item .env.example .env`.
2. Abre `.env` con `notepad .env` y cambia únicamente `N8N_PUERTO=5681` y `CATALOGO_PUERTO=8092` (o elige otros puertos libres).
3. Guarda el archivo y ejecuta `docker compose up -d`.
4. Comprueba con `docker compose ps` que los dos contenedores estén iniciados. Con estos valores, abre n8n en `http://localhost:5681` y el simulador en `http://localhost:8092`.

En **Linux/macOS** también puedes cambiar los puertos directamente al ejecutar `N8N_PUERTO=5681 CATALOGO_PUERTO=8092 docker compose up -d`.

Si cambias los puertos, recuerda actualizar las variables `url_n8n`, `url_simulador` y `oauth_redirect_uri` del entorno de Postman antes de probar las solicitudes. El `compose.yaml` ajusta solo la dirección de vuelta de OAuth que acepta el simulador.

Ahora prueba el simulador con una ruta que no pide credenciales:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d3-simulador-publico.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1020" alt="Respuesta de /salud y de /catalogo/publico"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d3-simulador-publico.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Respuesta de /salud y de /catalogo/publico" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El simulador responde. <code>/catalogo/publico</code> entrega solo título y total de ejemplares, sin préstamos ni disponibilidad.</figcaption></figure>

Estas son las rutas del simulador. Las rutas protegidas aceptan `?titulo=El faro de papel`:

| Ruta | Autenticación |
| --- | --- |
| `GET /catalogo/publico` | Ninguna |
| `GET /catalogo/api-key` | Cabecera `X-API-Key` |
| `GET /catalogo/basic` | Cabecera `Authorization: Basic ...` |
| `POST /auth/token` | JSON con `usuario` y `clave`. Entrega un JWT |
| `GET /catalogo/jwt` | Cabecera `Authorization: Bearer ...` |
| `GET /catalogo/oauth` | Cabecera `Authorization: Bearer ...` con el permiso `catalogo.leer` |
| `GET /oauth/autorizar`, `POST /oauth/decidir` | OAuth: pantalla de consentimiento y decisión de la persona |
| `POST /oauth/token`, `POST /oauth/revocar` | OAuth: canje del código, renovación y revocación (piden Client ID y Client Secret) |
| `GET /oauth/autorizaciones`, `GET /oauth/perfil` | OAuth: la persona revisa y revoca lo que autorizó; ruta con el permiso `perfil.leer` |
| `GET /salud`, `GET /registro`, `GET /reiniciar`, `POST /demo/oauth/vencer-tokens` | Rutas auxiliares para las pruebas |

Si llamas a una ruta protegida sin credencial, el simulador rechaza la solicitud:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d4-sin-credencial-401.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1020" alt="Respuesta 401 de la ruta con API Key sin enviar la clave"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d4-sin-credencial-401.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Respuesta 401 de la ruta con API Key sin enviar la clave" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Sin la cabecera <code>X-API-Key</code> el simulador responde <b>401</b>. El cuerpo explica el motivo (<code>falta_credencial</code>) y la cabecera <code>WWW-Authenticate</code> indica qué mecanismo espera.</figcaption></figure>

Por último abre n8n en <http://localhost:5680>. La primera vez te pide crear una cuenta local. **Entra siempre como `localhost`** (no como `127.0.0.1`): la dirección de vuelta de OAuth es `localhost` y el navegador solo envía tu sesión a la misma dirección con la que entraste.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/n1-n8n-inicio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Pantalla de inicio de n8n"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/n1-n8n-inicio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pantalla de inicio de n8n" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>n8n listo en <code>http://localhost:5680</code>. Dentro de n8n, la API se llama <code>http://catalogo:8080</code>, no <code>localhost</code>.</figcaption></figure>

Los valores de usuario, contraseña y clave del ejercicio están en el `README.md` del paquete y en `.env.example`. **Son valores de demostración: no son seguros y no deben usarse en sistemas reales.** La clave con que el simulador firma los tokens vive solo dentro del simulador; n8n nunca la conoce.

### Si ya tenías el ejemplo instalado

Esta versión agrega OAuth 2.0 sin cambiar API Key, Basic Auth ni JWT. **No borres nada**: tus credenciales y workflows están en el volumen de n8n y se conservan.

1. No hace falta apagar el ejemplo. En tu carpeta `biblioteca-acceso-seguro`, reemplaza `simulador_catalogo_seguro.py` y `compose.yaml` por los del paquete nuevo. Si usas un archivo `.env`, agrega las líneas nuevas de `.env.example` (son opcionales).
2. Ejecuta `docker compose up -d`. Compose recrea solo el servicio `catalogo`; `n8n` y su volumen no se tocan.
3. Comprueba que lo anterior sigue funcionando: <http://localhost:8091/salud> responde `"estado": "activo"` y tu workflow responde igual que antes.
4. Importa el workflow nuevo como un workflow aparte (o reemplaza el anterior si no lo modificaste) y crea las dos credenciales OAuth de la sección 9. Las tres credenciales anteriores no cambian.

Al reiniciar el simulador se pierden las autorizaciones OAuth, porque viven en memoria: en n8n hay que volver a pulsar **Connect**. Para actualizar nunca uses `docker compose down -v`: ese comando borra el volumen de n8n.

## 7. Crea las credenciales en n8n

**¿Qué estamos haciendo?** Guardamos en el gestor de credenciales de n8n los datos que la API exige.

**¿Para qué sirve?** n8n guarda las credenciales cifradas. Los workflows no contienen el secreto: solo **seleccionan** una credencial por su nombre. Antes de compartir, exportar o fotografiar un workflow, revisa también los parámetros escritos manualmente, los datos fijados y las salidas de ejecución: pueden contener secretos.

**¿Cómo lo hacemos?** Abre **Credentials**, en la pantalla de inicio de n8n. Todavía no hay ninguna:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c01-credenciales-vacio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lista de credenciales vacía con el botón Create credential resaltado"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c01-credenciales-vacio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de credenciales vacía con el botón Create credential resaltado" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un n8n nuevo no tiene credenciales. Pulsa <b>Create credential</b>.</figcaption></figure>

Crearás tres credenciales ahora, con estos nombres. Las dos de OAuth 2.0 vienen en la sección 9, porque necesitan el paso de consentimiento:

| Credencial | Tipo | Qué guarda | La usa el nodo |
| --- | --- | --- | --- |
| Biblioteca \| API Key (demo) | Header Auth | Nombre de la cabecera y la clave | Consultar con API Key |
| Biblioteca \| Basic Auth (demo) | Basic Auth | Usuario y contraseña | Consultar con Basic Auth |
| Biblioteca \| Login JWT (demo) | Custom Auth | Usuario y clave para pedir un token | Obtener token |

### 7.1 API Key con Header Auth

Una API Key viaja en una cabecera. El tipo **Header Auth** guarda el nombre de la cabecera y su valor.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c02-tipo-header-auth.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Selector de tipo de credencial buscando Header Auth"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c02-tipo-header-auth.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Selector de tipo de credencial buscando Header Auth" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Busca <b>Header Auth</b> en el selector y continúa.</figcaption></figure>

Escribe el nombre `X-API-Key` y la clave de demostración del paquete en **Value**. n8n oculta el valor. Ponle el nombre `Biblioteca | API Key (demo)`:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c03-header-auth-formulario.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Formulario de Header Auth con los campos resaltados"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c03-header-auth-formulario.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Formulario de Header Auth con los campos resaltados" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><b>Name</b> es la cabecera que enviará n8n y <b>Value</b> es la clave. El valor queda enmascarado.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c04-header-auth-guardada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Credencial Header Auth guardada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c04-header-auth-guardada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial Header Auth guardada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras <b>Save</b>, la credencial queda guardada. Ya no necesitas volver a escribir la clave.</figcaption></figure>

Resultado esperado: una credencial llamada **Biblioteca | API Key (demo)** en la lista.

### 7.2 Basic Auth

Basic Auth envía un usuario y una contraseña. n8n los junta como `usuario:contraseña`, los codifica en Base64 y los envía en la cabecera `Authorization: Basic ...`. Recuerda que Base64 no cifra nada.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c05-tipo-basic-auth.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Selector de tipo de credencial buscando Basic Auth"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c05-tipo-basic-auth.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Selector de tipo de credencial buscando Basic Auth" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Elige <b>Basic Auth</b>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c06-basic-formulario.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Formulario de Basic Auth con usuario y contraseña"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c06-basic-formulario.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Formulario de Basic Auth con usuario y contraseña" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Escribe el usuario y la contraseña de demostración. La contraseña queda enmascarada. Nombre: <code>Biblioteca | Basic Auth (demo)</code>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c07-basic-guardada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Credencial Basic Auth guardada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c07-basic-guardada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial Basic Auth guardada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Credencial guardada.</figcaption></figure>

### 7.3 Login para JWT con Custom Auth

Para obtener un JWT hay que enviar el usuario y la clave en el cuerpo de una solicitud `POST`. Para no escribir esa clave en el workflow, la guardamos en una credencial **Custom Auth**. Este tipo permite definir cabeceras, parámetros de la URL o un **cuerpo** (`body`) que n8n agrega a la solicitud.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c08-tipo-custom-auth.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Selector de tipo de credencial buscando Custom Auth"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c08-tipo-custom-auth.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Selector de tipo de credencial buscando Custom Auth" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Elige <b>Custom Auth</b>.</figcaption></figure>

En el campo **JSON** escribe el cuerpo con el usuario y la clave de demostración. En la captura el contenido está difuminado a propósito:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c09-custom-formulario.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Formulario de Custom Auth con el JSON difuminado"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c09-custom-formulario.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Formulario de Custom Auth con el JSON difuminado" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El JSON tiene la forma <code>{"body": {"usuario": ..., "clave": ...}}</code>. Se difuminó para no mostrar la clave. Nombre: <code>Biblioteca | Login JWT (demo)</code>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c10-custom-guardada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Credencial Custom Auth guardada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c10-custom-guardada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial Custom Auth guardada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Credencial guardada.</figcaption></figure>

Al terminar tendrás las tres credenciales en la lista:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c11-lista-credenciales.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lista con las tres credenciales creadas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c11-lista-credenciales.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista con las tres credenciales creadas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las tres credenciales. La lista muestra nombre y tipo, nunca el valor secreto.</figcaption></figure>

Un ajuste de seguridad que ofrece n8n: en cada credencial, **Allowed HTTP Request Domains** limita a qué dominios se puede enviar. Por defecto permite todos (**All**). En un sistema real conviene restringirlo al dominio de la API.

## 8. Construye el workflow paso a paso

Construirás un único workflow, primero con tres rutas (en la sección 9 le sumarás las dos de OAuth 2.0). Cada etapa agrega un trozo y muestra cómo queda el lienzo.

### 8.1 Crea el workflow y recibe la consulta

**¿Qué estamos haciendo?** Creamos el punto de entrada: un webhook que recibe un JSON desde Postman.

**¿Cómo lo hacemos?** Crea un workflow nuevo con **Create workflow** y llámalo `Biblioteca | Acceso seguro al catálogo`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w01-nuevo-workflow-vacio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lienzo vacío de un workflow nuevo"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w01-nuevo-workflow-vacio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lienzo vacío de un workflow nuevo" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un workflow nuevo. Pulsa <b>Add first step</b>.</figcaption></figure>

Busca **Webhook** y agrégalo:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w02-selector-webhook.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Selector de nodos buscando Webhook"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w02-selector-webhook.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Selector de nodos buscando Webhook" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El selector de nodos con <b>Webhook</b> encontrado.</figcaption></figure>

Configura el nodo **Recibir consulta** con método **POST** y la ruta `acceso-seguro`. Como respuesta usa **Using 'Respond to Webhook' Node**, para devolver nosotros la respuesta al final:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w04-webhook-config.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Configuración del Webhook con método POST y ruta acceso-seguro"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w04-webhook-config.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Configuración del Webhook con método POST y ruta acceso-seguro" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><b>HTTP Method</b> <code>POST</code> y <b>Path</b> <code>acceso-seguro</code>. La <b>Production URL</b> será <code>http://localhost:5680/webhook/acceso-seguro</code>.</figcaption></figure>

Agrega un nodo **Edit Fields (Set)** llamado **Preparar datos** con dos campos de texto:

- `titulo`: `{{ $json.body.titulo }}`
- `tipo_autenticacion`: `{{ $json.body.tipo_autenticacion }}`

Sirve para tener los dos datos de la consulta a mano, sin el resto de la información del webhook.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w05-preparar-datos-config.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Configuración de Edit Fields con titulo y tipo_autenticacion"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w05-preparar-datos-config.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Configuración de Edit Fields con titulo y tipo_autenticacion" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El nodo <b>Preparar datos</b> toma <code>titulo</code> y <code>tipo_autenticacion</code> del cuerpo que envía Postman.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w03-etapa-1-webhook-y-preparar.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow con el Webhook y Preparar datos conectados"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w03-etapa-1-webhook-y-preparar.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow con el Webhook y Preparar datos conectados" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Etapa 1: el webhook y <b>Preparar datos</b>, conectados.</figcaption></figure>

### 8.2 Elige la ruta con un Switch

**¿Qué estamos haciendo?** Decidimos por qué mecanismo se consulta el catálogo según el valor de `tipo_autenticacion`.

**¿Cómo lo hacemos?** Agrega un nodo **Switch** llamado **Tipo de autenticación** con tres reglas. Cada una compara `{{ $json.tipo_autenticacion }}` con `api_key`, `basic` o `jwt` y tiene su salida con nombre. Activa la salida de respaldo (**Fallback Output: Extra**) y llámala **Otro**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w07-switch-reglas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Reglas del Switch con salidas API Key, Basic Auth y JWT"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w07-switch-reglas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Reglas del Switch con salidas API Key, Basic Auth y JWT" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una regla por mecanismo. <b>Rename Output</b> permite nombrar cada salida para leer el lienzo con facilidad.</figcaption></figure>

Conecta **Preparar datos** al Switch y la salida **Otro** a un **Respond to Webhook** con código `400`, para avisar que el tipo no existe:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w06-etapa-2-switch.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow con el Switch y la salida Otro"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w06-etapa-2-switch.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow con el Switch y la salida Otro" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Etapa 2: el Switch con sus cuatro salidas. Por ahora solo <b>Otro</b> está conectada.</figcaption></figure>

### 8.3 Ruta API Key

**¿Qué estamos haciendo?** Consultamos el catálogo con la clave guardada en la credencial.

**¿Cómo lo hacemos?** Agrega un **HTTP Request** llamado **Consultar con API Key**:

- **Method**: `GET`.
- **URL**: `http://catalogo:8080/catalogo/api-key`.
- **Authentication**: **Generic Credential Type**.
- **Generic Auth Type**: **Header Auth**.
- **Header Auth**: elige **Biblioteca | API Key (demo)**.
- **Send Query Parameters**: `titulo` con `{{ $('Preparar datos').item.json.titulo }}`.

La clave no aparece en ningún campo del nodo: solo se selecciona la credencial.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w09-http-api-key-autenticacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="HTTP Request con autenticación Header Auth resaltada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w09-http-api-key-autenticacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: HTTP Request con autenticación Header Auth resaltada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La autenticación se configura con <b>Generic Credential Type</b>, <b>Header Auth</b> y la credencial elegida por su nombre.</figcaption></figure>

En **Options > Response** activa **Include Response Headers and Status** y **Never Error**. Con ellas, una respuesta `401` no detiene el workflow: el nodo entrega el código y el cuerpo, y podemos devolverlos tal cual.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w10-http-api-key-opciones.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Opciones de respuesta del HTTP Request"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w10-http-api-key-opciones.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Opciones de respuesta del HTTP Request" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><b>Include Response Headers and Status</b> y <b>Never Error</b> hacen que el nodo entregue <code>statusCode</code> y <code>body</code> incluso cuando la API rechaza la solicitud.</figcaption></figure>

Agrega un **Respond to Webhook** llamado **Responder (API Key)**. Responde con **JSON**, con este cuerpo, y usa como código de respuesta el que entregó la API (`{{ $json.statusCode }}`):

<pre><code class="language-text">&#123;&#123; { "autenticacion": "api_key", "http": $json.statusCode, "resultado": $json.body } &#125;&#125;</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w16-responder-config.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Configuración de Respond to Webhook"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w16-responder-config.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Configuración de Respond to Webhook" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Responder devuelve el cuerpo en JSON y reutiliza el código HTTP de la API (<code>statusCode</code>).</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w08-etapa-3-ruta-api-key.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow con la ruta de API Key conectada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w08-etapa-3-ruta-api-key.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow con la ruta de API Key conectada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Etapa 3: la ruta de API Key conectada a la salida <b>API Key</b> del Switch.</figcaption></figure>

### 8.4 Ruta Basic Auth

La ruta es igual, con otra URL y otra credencial. Duplica los dos nodos y cambia:

- **Consultar con Basic Auth**: URL `http://catalogo:8080/catalogo/basic`, **Generic Auth Type** **Basic Auth** y la credencial **Biblioteca | Basic Auth (demo)**.
- **Responder (Basic Auth)**: el campo `autenticacion` con el valor `basic`.

Conéctalos a la salida **Basic Auth** del Switch.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w12-http-basic-autenticacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="HTTP Request con autenticación Basic Auth resaltada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w12-http-basic-autenticacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: HTTP Request con autenticación Basic Auth resaltada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Misma estructura que API Key, pero con el tipo <b>Basic Auth</b>. n8n arma la cabecera <code>Authorization: Basic ...</code> con el usuario y la contraseña de la credencial.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w11-etapa-4-ruta-basic.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow con las rutas API Key y Basic Auth"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w11-etapa-4-ruta-basic.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow con las rutas API Key y Basic Auth" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Etapa 4: dos rutas conectadas.</figcaption></figure>

**¿Qué diferencia hay entre API Key y Basic Auth?** La API Key es una sola clave que identifica a una aplicación. Basic Auth identifica a una cuenta con usuario y contraseña. En n8n se configuran igual (credencial más tipo de autenticación), pero viajan en cabeceras distintas.

### 8.5 Ruta JWT

**¿Qué estamos haciendo?** Pedimos un token a la API y lo usamos para consultar el catálogo, todo dentro de la misma ejecución.

**¿Por qué dos nodos?** Un JWT no se guarda como una credencial permanente: se obtiene al iniciar sesión y vence. Por eso la ruta tiene dos pasos.

**Paso 1: Obtener token.** Un **HTTP Request** con método `POST`, URL `http://catalogo:8080/auth/token`, **Generic Auth Type** **Custom Auth** y la credencial **Biblioteca | Login JWT (demo)**. La credencial agrega el usuario y la clave al cuerpo de la solicitud.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w14-obtener-token-config.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="HTTP Request que obtiene el token con Custom Auth"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w14-obtener-token-config.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: HTTP Request que obtiene el token con Custom Auth" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><b>Obtener token</b> envía el usuario y la clave que guarda la credencial. La API responde con un <code>access_token</code>.</figcaption></figure>

**Paso 2: Consultar con JWT.** Un **HTTP Request** con método `GET`, URL `http://catalogo:8080/catalogo/jwt`, **Authentication** en **None** (no hay credencial guardada) y una cabecera que usa el token recién obtenido:

- **Name**: `Authorization`
- **Value**: `Bearer {{ $json.access_token }}`

La expresión toma el `access_token` del nodo anterior. El workflow obtiene un token nuevo en cada ejecución; su salida puede quedar conservada en el historial de n8n. Activa también **Include Response Headers and Status** y **Never Error**, como antes.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w15-consultar-jwt-config.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="HTTP Request con la cabecera Authorization Bearer"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w15-consultar-jwt-config.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: HTTP Request con la cabecera Authorization Bearer" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La cabecera <code>Authorization</code> se arma con una expresión: la palabra <b>Bearer</b>, un espacio y el token del nodo anterior.</figcaption></figure>

Termina con **Responder (JWT)** (`autenticacion`: `jwt`) conectado a la salida **JWT** del Switch.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w13-etapa-5-ruta-jwt.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow con las tres rutas conectadas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w13-etapa-5-ruta-jwt.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow con las tres rutas conectadas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Etapa 5: las tres rutas completas.</figcaption></figure>

**Credencial guardada y token temporal.** Las credenciales de API Key, Basic Auth y login se guardan en n8n y se reutilizan siempre. El workflow pide el token en cada ejecución y lo utiliza mediante una expresión, sin fijarlo en la configuración del nodo. El token vence a los pocos minutos, pero la salida del nodo que lo obtiene puede quedar guardada en el historial de ejecuciones de n8n. El vencimiento no elimina ese registro. Evita compartir ejecuciones o capturas con el token visible y revisa la conservación de datos de ejecución. Si se vence entre dos usos, la API responde `401` y basta con pedir otro.

### 8.6 Agrega las notas adhesivas

**¿Qué estamos haciendo?** Documentamos el workflow dentro del propio lienzo, para quien lo abra después.

**¿Cómo lo hacemos?** Agrega notas adhesivas (**Sticky Note**) cerca de cada parte, cortas y sin tapar las conexiones. Las notas se guardan dentro del JSON del workflow: cuando alguien lo importe, las verá. El archivo descargable trae doce: las siete siguientes y cinco más de OAuth 2.0 (sección 9.7):

| Nota | Qué explica |
| --- | --- |
| 1 Entrada | Qué llega desde Postman y que ahí no se envía ninguna clave |
| 2 Switch | Cómo el Switch elige la ruta y qué hace la salida Otro |
| 3 API Key | La clave vive en la credencial Header Auth, no en el workflow |
| 4 Basic Auth | Usuario y contraseña en Base64, que no cifra |
| 5 JWT | Por qué se pide un token y se envía como Bearer |
| 6 Rechazo | Qué pasa cuando la API responde 401 |
| 7 Otro | Qué responde el workflow ante un tipo desconocido |
| 8 OAuth 2.0: autorización | Dónde ocurre la autorización: una vez, en la credencial, con Connect |
| 9 OAuth 2.0: el token | Cómo se obtiene el token y cómo se usa |
| 10 OAuth 2.0: cuando vence | Qué pasa cuando vence el access token |
| 11 OAuth 2.0: permisos insuficientes | Por qué una credencial válida puede recibir un 403 |
| 12 OAuth 2.0: revocación | Qué pasa cuando la persona revoca la autorización |

Escribe en las notas explicaciones, **nunca valores secretos**. En la nota JWT del archivo descargable se aclara que el token puede quedar en el historial de ejecuciones. Las capturas conservan la versión anterior de esa nota; que un token sea temporal no significa que no se almacene.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w17-workflow-completo-notas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow completo con las siete notas adhesivas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w17-workflow-completo-notas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow completo con las siete notas adhesivas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El workflow terminado, con sus notas adhesivas legibles y fuera de las conexiones.</figcaption></figure>

### 8.7 Publica el workflow

Para que el webhook de producción responda hay que **publicar** el workflow. Pulsa **Publish** y escribe un nombre de versión:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w18-publicar-modal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ventana para publicar el workflow con nombre de versión"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w18-publicar-modal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana para publicar el workflow con nombre de versión" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>n8n pide un nombre para la versión que se publica.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w19-workflow-publicado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow publicado"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w19-workflow-publicado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow publicado" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Con el workflow publicado, la <b>Production URL</b> del webhook responde.</figcaption></figure>

Mientras no esté publicado, esa dirección responde `404`. Si ya lo habías publicado antes de agregar OAuth, vuelve a publicarlo para que los cambios queden activos.

## 9. OAuth 2.0: autorización con consentimiento

Hasta aquí, quien llama a la API **tiene** un secreto propio: una clave, un usuario con su contraseña o un token que pidió con ellos. OAuth 2.0 resuelve otro problema: **una persona autoriza a una aplicación** a acceder a sus datos, con permisos limitados, sin darle su contraseña y pudiendo quitar el permiso cuando quiera.

Las capturas de esta sección se tomaron en una instalación de prueba paralela, con n8n en el puerto `5710` y el simulador en el `5711`. Con los valores por defecto del paquete verás `5680` y `8091`. Todo lo demás es igual.

### 9.1 La idea, sin jerga

Imagina que eres socia de la biblioteca y quieres que una amiga consulte por ti cuántos ejemplares hay disponibles.

- Si le das tu carnet y tu clave (**Basic Auth**), ella puede hacer todo lo que tú haces, y para quitarle el acceso tienes que cambiar tu clave.
- Con **OAuth 2.0**, la biblioteca te muestra una pantalla que dice «esta aplicación pide permiso para consultar el catálogo». Tú eliges **Autorizar** o **Rechazar**. La aplicación recibe un permiso limitado y temporal, nunca tu clave, y tú puedes anularlo cuando quieras sin cambiar nada más.

Así se explican los cuatro mecanismos, de menos a más:

1. **API Key**: la aplicación se identifica con una clave, como una llave de la sala. Quien la tenga, entra.
2. **Basic Auth**: la aplicación usa el usuario y la contraseña de una cuenta, y los envía en cada solicitud. Por eso necesita HTTPS.
3. **JWT**: la aplicación cambia su usuario y su clave por un token que vence. Debe controlar ese vencimiento.
4. **OAuth 2.0**: una persona autoriza a la aplicación, con permisos limitados. La aplicación recibe tokens y la persona puede revocarlos.

### 9.2 Los términos, uno por uno

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

### 9.3 El recorrido, paso a paso

Participan tres: **la persona** (con su navegador), **n8n** y **el simulador** del catálogo, que hace de servidor de autorización y de API.

1. n8n abre en tu navegador la **Authorization URL** del simulador, con el Client ID, el permiso pedido, la dirección de vuelta (`redirect_uri`) y un valor aleatorio llamado `state`.
2. El simulador muestra la **pantalla de consentimiento**. La persona elige **Autorizar** o **Rechazar**.
3. Si autoriza, el simulador devuelve el navegador a n8n con un **código** (y el mismo `state`). Si rechaza, lo devuelve con `error=access_denied`.
4. n8n, desde su propio servidor y sin pasar por el navegador, **canjea el código por tokens** en la **Access Token URL**, mostrando su Client ID y su Client Secret.
5. Para consultar, n8n envía `Authorization: Bearer <access token>`.
6. Cuando el access token vence, n8n usa el **refresh token** y recibe uno nuevo.
7. Si la persona **revoca** la autorización, la renovación falla y hay que volver a autorizar.

Hay dos direcciones del mismo servidor, vistas desde dos lugares distintos. La **Authorization URL** (`http://localhost:8091/oauth/autorizar`) la abre **tu navegador**, que está en tu computador, por eso es `localhost`. La **Access Token URL** (`http://catalogo:8080/oauth/token`) la llama **n8n**, que corre dentro de Docker y conoce al simulador por su nombre.

### 9.4 Qué controles de seguridad tiene el simulador

El simulador es **educativo**, pero valida lo básico de un servidor de autorización:

- La `redirect_uri` debe ser **exactamente** la registrada. Si no lo es, no redirige a ningún lado y muestra el error en pantalla.
- El `state` es obligatorio y se devuelve intacto, para que n8n compruebe que la respuesta corresponde a su solicitud.
- El código vive 60 segundos y se usa **una sola vez**. Si alguien lo reutiliza, el simulador lo rechaza y revoca lo que ya había emitido con él.
- Para canjear el código hace falta el **Client Secret**.
- El permiso (scope) se valida en cada ruta: sin `catalogo.leer`, el catálogo responde `403`.
- **PKCE** (opcional): si la solicitud trae un `code_challenge` con método `S256`, el canje exige el verificador correcto.
- Ni el registro del simulador (`/registro`) ni sus mensajes en consola muestran códigos ni tokens.

**No es un servidor listo para producción:** guarda todo en memoria (al reiniciarlo se pierden las autorizaciones), no pide una contraseña real, no limita intentos y no usa HTTPS.

### 9.5 Crea las credenciales OAuth2 API en n8n

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

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o01-credencial-oauth2-formulario.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="2400" height="1690" alt="Formulario de la credencial OAuth2 API con las direcciones resaltadas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o01-credencial-oauth2-formulario.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Formulario de la credencial OAuth2 API con las direcciones resaltadas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La credencial <b>OAuth2 API</b>. Resaltadas: la <b>Authorization URL</b> (la abre tu navegador) y la <b>Access Token URL</b> (la llama n8n) y el <b>Scope</b>. El Client Secret queda enmascarado.</figcaption></figure>

Pulsa **Save**. n8n avisa que falta conectar la cuenta:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o02-credencial-sin-conectar.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="2400" height="1690" alt="Credencial OAuth2 API guardada y sin conectar"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o02-credencial-sin-conectar.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial OAuth2 API guardada y sin conectar" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras <b>Save</b>, n8n avisa «Connect your account to use this credential». La <b>OAuth Redirect URL</b> es la dirección a la que el simulador devuelve el navegador.</figcaption></figure>

La segunda credencial se llama `Biblioteca | OAuth2 solo perfil (demo)` y es igual, pero con **Scope** `perfil.leer`.

### 9.6 Primero rechaza el consentimiento y después autoriza

**¿Qué estamos haciendo?** Vemos las dos decisiones posibles de la persona.

**¿Cómo lo hacemos?** En `Biblioteca | OAuth2 (demo)` pulsa **Connect**. Se abre una ventana con la pantalla de consentimiento:

<figure class="lamina-apunte" style="position:relative;max-width:760px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o03-pantalla-consentimiento.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1305" height="939" alt="Pantalla de consentimiento del simulador con los botones Autorizar y Rechazar"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o03-pantalla-consentimiento.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pantalla de consentimiento del simulador con los botones Autorizar y Rechazar" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La pantalla de consentimiento. Dice qué aplicación pide permiso, con qué cuenta (ficticia) y qué permiso (<code>catalogo.leer</code>). La persona elige <b>Autorizar</b> o <b>Rechazar</b>.</figcaption></figure>

Lee qué aplicación pide permiso y qué permiso. **Primero pulsa Rechazar.** El simulador devuelve el navegador a n8n con `error=access_denied`:

<figure class="lamina-apunte" style="position:relative;max-width:560px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o04-rechazo-mensaje-n8n.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="925" height="320" alt="Mensaje de n8n tras rechazar el consentimiento"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o04-rechazo-mensaje-n8n.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Mensaje de n8n tras rechazar el consentimiento" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Después de <b>Rechazar</b>, el simulador vuelve a n8n con <code>error=access_denied</code>. n8n muestra «Failed to connect» y no guarda ningún token.</figcaption></figure>

Cierra esa ventana. La credencial sigue sin conectar:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o05-credencial-tras-rechazo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="2400" height="1690" alt="Credencial sin conectar después de rechazar"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o05-credencial-tras-rechazo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial sin conectar después de rechazar" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La credencial sigue sin conectar: sin autorización no hay token.</figcaption></figure>

Ahora pulsa **Connect** otra vez y esta vez **Autorizar**. La ventana se cierra sola y la credencial queda conectada:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o06-credencial-conectada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="2400" height="1690" alt="Credencial conectada con el aviso Account connected"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o06-credencial-conectada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial conectada con el aviso Account connected" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras <b>Autorizar</b>, la credencial muestra <b>Account connected</b>. n8n canjeó el código por un access token y un refresh token, y los guardó cifrados.</figcaption></figure>

Nota lo que **no** ocurrió: no escribiste ningún token ni la contraseña de nadie. n8n obtuvo los tokens, los guardó cifrados y los usará por su cuenta.

Repite con la segunda credencial. La pantalla de consentimiento ahora muestra otro permiso:

<figure class="lamina-apunte" style="position:relative;max-width:760px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o07-consentimiento-solo-perfil.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1305" height="895" alt="Pantalla de consentimiento para el permiso perfil.leer"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o07-consentimiento-solo-perfil.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pantalla de consentimiento para el permiso perfil.leer" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Con la segunda credencial (Scope <code>perfil.leer</code>) la pantalla pide un permiso distinto: solo ver el nombre de la cuenta.</figcaption></figure>

Al terminar tienes cinco credenciales:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o08-lista-credenciales.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1500" alt="Lista con las cinco credenciales"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o08-lista-credenciales.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista con las cinco credenciales" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las cinco credenciales del ejercicio, con sus nombres. Las dos de tipo <b>OAuth2 API</b> son las nuevas.</figcaption></figure>

### 9.7 Agrega las rutas OAuth 2.0 al workflow

**¿Qué estamos haciendo?** Sumamos la cuarta ruta (y una quinta para ver el `403`) sin tocar las tres anteriores.

**¿Cómo lo hacemos?**

1. En el **Switch** **Tipo de autenticación** agrega dos reglas **antes** de la salida de respaldo: `oauth2` (salida «OAuth 2.0») y `oauth2_sin_permiso` (salida «OAuth 2.0 sin permiso»).
2. Agrega un **HTTP Request** llamado **Consultar con OAuth 2.0**: método `GET`, URL `http://catalogo:8080/catalogo/oauth`, **Authentication** **Generic Credential Type**, **Generic Auth Type** **OAuth2 API** y la credencial `Biblioteca | OAuth2 (demo)`. Envía el parámetro `titulo` como en las otras rutas y activa **Include Response Headers and Status** y **Never Error**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o10-nodo-consultar-oauth.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="3000" alt="Nodo Consultar con OAuth 2.0 con la credencial OAuth2 API"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o10-nodo-consultar-oauth.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo Consultar con OAuth 2.0 con la credencial OAuth2 API" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El HTTP Request de la ruta OAuth: <b>Generic Credential Type</b>, <b>OAuth2 API</b> y la credencial elegida por su nombre. No hay ningún token escrito en el nodo.</figcaption></figure>

3. En **Settings** del mismo nodo, pon **On Error** en **Continue (using error output)**. Así, si n8n no puede renovar la autorización, el flujo sale por una segunda salida (**Error**) en vez de terminar con un fallo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o11-nodo-oauth-salida-error.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="3000" alt="Ajuste On Error con la salida de error resaltada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o11-nodo-oauth-salida-error.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ajuste On Error con la salida de error resaltada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>En <b>Settings</b>, <b>On Error</b> está en <b>Continue (using error output)</b>: si n8n no puede renovar la autorización, el flujo sale por la salida <b>Error</b> en vez de terminar con un fallo.</figcaption></figure>

4. Conecta la salida **Success** a **Responder (OAuth 2.0)**, que devuelve el resultado con el mismo código de la API (campo `autenticacion`: `oauth2`). Conecta la salida **Error** a **Responder (OAuth 2.0 sin autorización)**: un **Respond to Webhook** con código fijo `401` y un mensaje que explica que la autorización ya no sirve y hay que volver a autorizar.
5. Para la ruta de permiso insuficiente, duplica el HTTP Request y el Responder. Cambia el nombre a **Consultar con OAuth 2.0 sin permiso**, elige la credencial `Biblioteca | OAuth2 solo perfil (demo)` y pon `oauth2_sin_permiso` en el campo `autenticacion` del Responder.
6. Agrega las notas adhesivas 8 a 12 (sección 8.6) y **publica** el workflow de nuevo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o09-ruta-oauth-lienzo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1600" height="1225" alt="Rutas de OAuth 2.0 en el lienzo con sus notas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o09-ruta-oauth-lienzo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Rutas de OAuth 2.0 en el lienzo con sus notas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las dos rutas nuevas. Arriba, las notas 8, 9 y 10; en medio <b>Consultar con OAuth 2.0</b>, con sus dos salidas (<b>Success</b> y <b>Error</b>); abajo, las notas 11 y 12 y la ruta de permiso insuficiente.</figcaption></figure>

**Prueba la ruta.** Desde Postman (carpeta 10) o con `curl`, envía `{"titulo": "El faro de papel", "tipo_autenticacion": "oauth2"}` al webhook. Responde `200` con los cuatro datos del libro y no enviaste ningún token:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o12-ejecucion-oauth-200.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución por la ruta OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o12-ejecucion-oauth-200.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución por la ruta OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una consulta por la ruta OAuth 2.0. Es una ejecución normal: n8n puso el token por su cuenta.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o13-oauth-salida-http.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Consultar con OAuth 2.0 con statusCode 200"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o13-oauth-salida-http.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Consultar con OAuth 2.0 con statusCode 200" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La salida del nodo: <code>statusCode</code> <code>200</code> y los cuatro datos del libro (título, ejemplares totales, préstamos activos y disponibles).</figcaption></figure>

### 9.8 Qué pasa cuando vence el access token

El access token dura 5 minutos. Para no esperar, el simulador tiene una ruta solo para practicar: `POST /demo/oauth/vencer-tokens` (en Postman, la solicitud 8.1) vence todos los access tokens. Después, vuelve a llamar al webhook.

Para n8n es una ejecución normal y responde `200`. El registro del simulador cuenta lo que pasó por detrás:

<pre><code class="language-text">docker compose logs --no-log-prefix --tail 4 catalogo</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o14-registro-renovacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="642" alt="Registro del simulador con la renovación del token"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o14-registro-renovacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registro del simulador con la renovación del token" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Lo que vio el simulador al vencer el access token: <b>401</b> con motivo <code>token_vencido</code>, enseguida un <code>POST /oauth/token</code> (la renovación con el refresh token) y la consulta repetida con <b>200</b>.</figcaption></figure>

La API respondió `401` (`token_vencido`), n8n usó el refresh token en `POST /oauth/token` y repitió la consulta con el token nuevo. **La persona no tuvo que hacer nada.** n8n intenta renovar cuando recibe el código que indica el campo **Token Expired Status Code** de la credencial, que por defecto es `401`.

### 9.9 Permisos insuficientes: el error 403

Llama al webhook con `oauth2_sin_permiso`. Esa ruta usa la credencial que solo tiene `perfil.leer`:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o15-ejecucion-sin-permiso.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución por la ruta de permiso insuficiente"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o15-ejecucion-sin-permiso.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución por la ruta de permiso insuficiente" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ruta con la credencial que solo tiene <code>perfil.leer</code>. La ejecución termina bien, pero con el rechazo de la API.</figcaption></figure>

El token es válido, pero la ruta del catálogo exige `catalogo.leer`:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o16-sin-permiso-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida con statusCode 403 e insufficient_scope"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o16-sin-permiso-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida con statusCode 403 e insufficient_scope" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La API responde <b>403</b> con <code>insufficient_scope</code>: el token es válido, pero esta ruta exige <code>catalogo.leer</code> y el token solo trae <code>perfil.leer</code>.</figcaption></figure>

Compara con un `401`: aquí la API **sí sabe quién eres**. Cambiar el token no arregla nada; hay que volver a autorizar con el permiso correcto.

### 9.10 Revocación

La persona (o la aplicación) puede quitar la autorización cuando quiera. En el simulador, abre <http://localhost:8091/oauth/autorizaciones>:

<figure class="lamina-apunte" style="position:relative;max-width:760px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o17-autorizaciones.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1305" height="729" alt="Página de autorizaciones del simulador"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o17-autorizaciones.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Página de autorizaciones del simulador" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La página <code>/oauth/autorizaciones</code>: lo que la persona autorizó, con un botón <b>Revocar</b> por cada aplicación.</figcaption></figure>

Pulsa **Revocar** en la autorización de `catalogo.leer`:

<figure class="lamina-apunte" style="position:relative;max-width:760px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o18-autorizaciones-revocada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1305" height="693" alt="Página de autorizaciones con una autorización revocada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o18-autorizaciones-revocada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Página de autorizaciones con una autorización revocada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras pulsar <b>Revocar</b>, la autorización queda marcada como revocada.</figcaption></figure>

Regla del simulador: al revocar, **dejan de servir el refresh token y los access tokens** de esa autorización. En n8n no cambia nada a simple vista: la credencial sigue diciendo **Account connected**.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o19-credencial-sigue-conectada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Credencial que sigue mostrando Account connected"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o19-credencial-sigue-conectada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial que sigue mostrando Account connected" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>n8n no se entera de la revocación: la credencial sigue diciendo <b>Account connected</b>. El problema aparece recién cuando se intenta usar.</figcaption></figure>

El problema aparece cuando el workflow intenta usarla. Llama al webhook con `oauth2`: n8n recibe `401`, intenta renovar, el simulador rechaza la renovación y el flujo sale por la salida **Error**:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o20-ejecucion-revocada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución con la autorización revocada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o20-ejecucion-revocada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución con la autorización revocada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La consulta tras revocar. n8n intentó renovar, no pudo, y el flujo salió por la salida <b>Error</b> hacia <b>Responder (OAuth 2.0 sin autorización)</b>.</figcaption></figure>

El nodo **Responder (OAuth 2.0 sin autorización)** recibe el error de n8n y responde `401` con el mensaje claro:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o21-revocada-respuesta.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Datos del error de renovación que recibe el Responder"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o21-revocada-respuesta.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Datos del error de renovación que recibe el Responder" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El error que entrega n8n: «Access could not be refreshed because the connected account has revoked access, the refresh token expired...». El Responder lo convierte en un <b>401</b> claro.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o22-registro-revocacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="578" alt="Registro del simulador con la revocación"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/o22-registro-revocacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registro del simulador con la revocación" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El simulador rechazó el access token (<code>autorizacion_revocada</code>) y también la renovación con el refresh token.</figcaption></figure>

Para recuperarte, abre la credencial y pulsa **Switch account**: vuelves a la pantalla de consentimiento y autorizas de nuevo. La aplicación también puede revocar con `POST /oauth/revocar` (solicitud 8.5 de la colección).

### 9.11 PKCE (opcional)

**PKCE** agrega una protección: n8n genera un secreto de un solo uso, envía su huella (`code_challenge`, método `S256`) al pedir la autorización y su valor (`code_verifier`) al canjear el código. Un código interceptado no sirve sin ese valor.

En la credencial de n8n se activa eligiendo **Grant Type** **PKCE**. En este ejercicio se comprobó con n8n 2.44.6: la credencial se conectó y el simulador verificó el desafío. La ruta principal del ejercicio usa **Authorization Code**, como el resto de la sección.

## 10. Prueba con Postman

**¿Qué estamos haciendo?** Enviamos las mismas consultas con y sin credenciales para ver la diferencia entre `200` y `401`.

**¿Cómo lo hacemos?** En Postman elige **Import** y carga la colección `biblioteca-acceso-seguro.postman_collection.json` y el entorno `biblioteca-local.postman_environment.json`. Selecciona el entorno **Biblioteca local (demo)** arriba a la derecha. Sus variables son:

| Variable | Valor por defecto |
| --- | --- |
| `url_n8n` | `http://localhost:5680` |
| `url_simulador` | `http://localhost:8091` |
| `oauth_redirect_uri` | `http://localhost:5680/rest/oauth2-credential/callback` |
| `api_key`, `basic_usuario`, `basic_clave`, `jwt_usuario`, `jwt_clave`, `oauth_client_id`, `oauth_client_secret` | Valores de demostración del paquete |

Postman corre en tu computador, así que usa `localhost` y los puertos publicados, no los nombres `n8n` ni `catalogo`, que solo existen dentro de Docker.

La colección tiene 51 solicitudes en doce carpetas (de la 0 a la 11), y cada una trae pruebas automáticas en **Scripts > Post-response**. Las carpetas 1 a 4 y 6 a 9 llaman **directo a la API**; las carpetas 5, 10 y 11 llaman **al webhook del workflow de n8n**. Estas son las principales de los tres primeros mecanismos (las de OAuth 2.0 están en las secciones 10.7 y 10.8):

| Prueba | Resultado esperado |
| --- | --- |
| Consultar endpoint público | `200` |
| API Key sin clave | `401` |
| API Key incorrecta | `401` |
| API Key válida | `200` |
| Basic Auth incorrecto | `401` |
| Basic Auth válido | `200` |
| Solicitar JWT con credenciales válidas | `200` con token generado |
| JWT sin token | `401` |
| JWT inválido o vencido | `401` |
| JWT válido | `200` |

Postman arma la autenticación en la pestaña **Authorization** de cada solicitud: **API Key** (clave `X-API-Key`, en la cabecera), **Basic Auth** (usuario y contraseña) y **Bearer Token** (el token que guardó la solicitud de login). Compáralas: son los mismos datos que configuraste en n8n.

Las siguientes capturas muestran la colección ejecutada con **Newman**, el ejecutor de línea de comandos de Postman. En Postman verás los mismos resultados en la pestaña **Test Results** de cada respuesta.

### 10.1 API Key y Basic Auth

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p1-postman-api-key.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1334" alt="Ejecución de la carpeta API Key"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p1-postman-api-key.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta API Key" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>API Key: sin clave y con clave incorrecta responden <code>401</code>, con la clave válida responde <code>200</code>. Las pruebas (✓) confirman el código y el motivo.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p2-postman-basic.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1334" alt="Ejecución de la carpeta Basic Auth"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p2-postman-basic.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta Basic Auth" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Basic Auth: sin credenciales y con contraseña incorrecta responden <code>401</code>; con las credenciales válidas, <code>200</code>.</figcaption></figure>

### 10.2 JWT

La carpeta de JWT sigue un orden: pedir un token, probar los casos que fallan y, al final, usar el token válido. La solicitud de login guarda el token en una variable de colección. Newman no exporta su valor al terminar salvo que se solicite; en Postman revisa las variables y los datos de ejecución antes de compartir o exportar:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p3-postman-jwt.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2342" alt="Ejecución de la carpeta JWT"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p3-postman-jwt.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta JWT" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>JWT: el token se obtiene con las credenciales válidas. Sin token, con un token inválido o vencido responde <code>401</code>. Con el token válido, <code>200</code>.</figcaption></figure>

### 10.3 El webhook de n8n

La carpeta 5 llama al **webhook del workflow**. Fíjate en que Postman **no envía ninguna clave**: la pone n8n con las credenciales guardadas. El cuerpo solo indica con qué mecanismo consultar:

<pre><code class="language-text">{
  "titulo": "El faro de papel",
  "tipo_autenticacion": "api_key"
}</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p4-postman-webhook.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1712" alt="Ejecución de la carpeta del webhook de n8n"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p4-postman-webhook.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta del webhook de n8n" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las tres rutas responden <code>200</code> y un tipo desconocido responde <code>400</code>.</figcaption></figure>


### 10.4 Qué ves dentro de n8n

Cada llamada al webhook deja una ejecución en la pestaña **Executions** del workflow:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e1-lista-ejecuciones.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lista de ejecuciones del workflow"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e1-lista-ejecuciones.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de ejecuciones del workflow" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Una ejecución por cada llamada al webhook. Todas aparecen como <b>Succeeded</b>.</figcaption></figure>

Abre una para ver por dónde pasó. En esta, la consulta usó la ruta de API Key y los nodos recorridos se marcan en verde:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e2-ejecucion-api-key.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución por la ruta API Key"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e2-ejecucion-api-key.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución por la ruta API Key" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ejecución recorrió la ruta de API Key. Las demás rutas quedan sin marcar.</figcaption></figure>

Al abrir **Consultar con API Key** ves lo que contestó la API: `statusCode` `200` y los datos del libro:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e3-api-key-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida del nodo Consultar con API Key"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e3-api-key-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida del nodo Consultar con API Key" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Salida en formato JSON: el código, las cabeceras de respuesta y el cuerpo con los ejemplares disponibles.</figcaption></figure>

En la ruta JWT se recorren los dos pasos:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e4-ejecucion-jwt.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución por la ruta JWT"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e4-ejecucion-jwt.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución por la ruta JWT" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ruta JWT pasa por <b>Obtener token</b> y luego por <b>Consultar con JWT</b>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e5-jwt-token-salida.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida del nodo Obtener token con el token oculto"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e5-jwt-token-salida.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida del nodo Obtener token con el token oculto" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><b>Obtener token</b> devuelve <code>access_token</code>, <code>token_type</code> y <code>expires_in</code>. El valor del token se ocultó en la captura: no lo publiques ni lo guardes.</figcaption></figure>

Un tipo desconocido sale por **Otro** y responde `400` sin llamar a la API:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e6-ejecucion-tipo-no-valido.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución por la salida Otro"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/e6-ejecucion-tipo-no-valido.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución por la salida Otro" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Switch envía la consulta a la salida <b>Otro</b>.</figcaption></figure>

### 10.5 Qué ocurre cuando la API rechaza una solicitud

Para verlo, vamos a romper a propósito la credencial de API Key: en **Credentials** abre **Biblioteca | API Key (demo)** y cambia el valor por otro, por ejemplo `clave-incorrecta-demo`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r1-credencial-valor-incorrecto.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Credencial Header Auth editada con un valor incorrecto"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r1-credencial-valor-incorrecto.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial Header Auth editada con un valor incorrecto" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Se cambia el valor de la credencial (queda enmascarado). Después, restáurala con el valor correcto.</figcaption></figure>

Vuelve a enviar la consulta de API Key desde Postman. El webhook responde **401**. Abre la ejecución:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r2-ejecucion-rechazada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución con rechazo 401"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r2-ejecucion-rechazada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución con rechazo 401" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ejecución aparece como <b>Succeeded</b> aunque la API respondió <code>401</code>: gracias a <b>Never Error</b>, el workflow siguió y devolvió el rechazo.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r3-rechazo-salida-http.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Consultar con API Key con statusCode 401"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r3-rechazo-salida-http.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Consultar con API Key con statusCode 401" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El HTTP Request entrega <code>statusCode</code> <code>401</code>, el cuerpo con el motivo <code>credencial_incorrecta</code> y la cabecera <code>www-authenticate</code>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r4-rechazo-respuesta.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Responder (API Key) con el código 401"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r4-rechazo-respuesta.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Responder (API Key) con el código 401" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Responder devuelve a Postman el mismo código <code>401</code> y el motivo.</figcaption></figure>

Si **Never Error** estuviera apagado, el HTTP Request fallaría con el `401` y la ejecución terminaría en error. Cuál de los dos comportamientos conviene depende de lo que quieras hacer con el rechazo. Es el mismo tema del apunte de [manejo de errores](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-manejo-de-errores).

Restaura el valor correcto de la credencial para seguir.

### 10.6 Qué ve el simulador

El simulador anota cada petición que recibe, sin mostrar claves, contraseñas ni tokens. Lo ves en los registros de Docker:

<pre><code class="language-text">docker compose logs --no-log-prefix --tail 8 catalogo</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d5-logs-simulador.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="894" alt="Registros del simulador con respuestas 401 y 200"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d5-logs-simulador.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registros del simulador con respuestas 401 y 200" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada línea indica la ruta, el código, el mecanismo y el motivo del rechazo. Nunca el valor de la credencial.</figcaption></figure>

También puedes abrir <http://localhost:8091/registro> en el navegador:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/s1-simulador-registro.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Registro de peticiones del simulador en el navegador"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/s1-simulador-registro.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registro de peticiones del simulador en el navegador" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><code>/registro</code> muestra las últimas peticiones: ruta, mecanismo, si se envió credencial, código y motivo.</figcaption></figure>

### 10.7 OAuth 2.0 directo contra el simulador

Las carpetas 6 a 9 recorren OAuth 2.0 sin n8n y sin navegador: Postman hace de «aplicación» y de «persona» a la vez. Las solicitudes de las carpetas 6, 7 y 9 que piden la pantalla de consentimiento y la decisión están configuradas para **no seguir la redirección**, así puedes ver el código en la cabecera `Location`. El código y los tokens se guardan en variables de colección.

Carpeta 6: sin autorización y consentimiento. Sin token responde `401`; con una `redirect_uri` no registrada o sin `state` el simulador rechaza; si la persona rechaza, vuelve con `access_denied` y sin código; si acepta, vuelve con el código y el mismo `state`; con un Client Secret incorrecto el canje falla; con el correcto entrega los dos tokens.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p6-newman-oauth-consentimiento.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="4044" alt="Ejecución de la carpeta 6 de OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p6-newman-oauth-consentimiento.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 6 de OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 6: de la consulta sin autorización al canje del código por tokens.</figcaption></figure>

Carpeta 7: uso del token y permisos. Con `catalogo.leer` la consulta responde `200`; con un token que solo tiene `perfil.leer` responde `403`, pero ese mismo token sí sirve en la ruta de perfil.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p7-newman-oauth-permisos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2594" alt="Ejecución de la carpeta 7 de OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p7-newman-oauth-permisos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 7 de OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 7: el mismo catálogo, dos tokens con permisos distintos.</figcaption></figure>

Carpeta 8: vencimiento, renovación y revocación. Se adelanta el vencimiento con la ruta de ayuda, el access token vencido responde `401`, el refresh token entrega uno nuevo, y después de revocar la renovación responde `400` (`invalid_grant`) y el acceso `401`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p8-newman-oauth-renovacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2468" alt="Ejecución de la carpeta 8 de OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p8-newman-oauth-renovacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 8 de OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 8: el ciclo de vida de una autorización.</figcaption></figure>

Carpeta 9: el código de autorización es de un solo uso. Canjearlo por segunda vez se rechaza y, como defensa, el simulador revoca lo que ya había emitido con ese código.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p9-newman-oauth-codigo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2154" alt="Ejecución de la carpeta 9 de OAuth 2.0"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p9-newman-oauth-codigo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 9 de OAuth 2.0" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 9: reutilizar un código es señal de robo.</figcaption></figure>

### 10.8 OAuth 2.0 a través del webhook de n8n

La carpeta 10 llama al webhook con `oauth2` y `oauth2_sin_permiso`. Postman no envía ningún token: los pone n8n con sus credenciales conectadas. Antes de ejecutarla, conecta las dos credenciales OAuth (sección 9.5).

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p10-newman-oauth-webhook.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1020" alt="Ejecución de la carpeta 10 con el webhook de n8n"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p10-newman-oauth-webhook.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta 10 con el webhook de n8n" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Carpeta 10: la ruta OAuth 2.0 responde <code>200</code> y la ruta con permiso insuficiente, <code>403</code>.</figcaption></figure>

La carpeta 11 es una **prueba manual**: abre <http://localhost:8091/oauth/autorizaciones>, pulsa **Revocar** en la autorización de n8n y ejecuta solo la solicitud 11.1. El workflow debe responder `401` con el error `autorizacion_no_valida`. Para volver a la normalidad, usa **Switch account** en la credencial y autoriza de nuevo. Al usar **Run collection**, desmarca la carpeta 11.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p5-postman-resumen.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1524" alt="Resumen de la ejecución de las carpetas 0 a 10"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p5-postman-resumen.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Resumen de la ejecución de las carpetas 0 a 10" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Resultado de las carpetas 0 a 10: 50 solicitudes y 119 pruebas, ninguna fallida. La carpeta 11 es una prueba manual y no forma parte de esta ejecución.</figcaption></figure>

## 11. Interpreta los códigos HTTP y las respuestas

| Código | Significado en este ejercicio | Qué revisar |
| --- | --- | --- |
| `200` | La credencial es válida y la API entregó el dato | Nada: es el resultado esperado |
| `400` | La solicitud está mal armada (falta usuario o clave, o el tipo de autenticación no existe) | El cuerpo JSON que se envía |
| `401` | Falta la credencial, es incorrecta o el token no sirve (falta, vencido, inventado o revocado) | El campo `motivo` de la respuesta |
| `403` | El token es válido, pero no tiene el permiso (scope) que exige la ruta | El campo `requerido` frente a `concedidos` |
| `404` | La ruta o el libro no existen | La URL y el título |
| `500` | Falló el workflow de n8n | La ejecución en **Executions** |

Cuando la API responde `401`, el campo `motivo` ayuda a encontrar la causa:

| Motivo | Qué ocurrió | Cómo se arregla |
| --- | --- | --- |
| `falta_credencial` | No se envió la cabecera | Revisa que el nodo o la solicitud tengan la autenticación configurada |
| `credencial_incorrecta` | La clave, el usuario o la contraseña no coinciden | Revisa el valor de la credencial |
| `token_malformado` | El texto no tiene forma de JWT | Revisa que envíes el token completo |
| `firma_invalida` | El token fue alterado o lo firmó otro servicio | Pide un token nuevo |
| `token_vencido` | El token ya no es válido por la hora | Pide un token nuevo (en OAuth 2.0, renueva con el refresh token) |
| `token_desconocido` | El access token OAuth no existe (por ejemplo, el simulador se reinició) | Autoriza de nuevo con **Connect** |
| `autorizacion_revocada` | La persona revocó la autorización | Vuelve a autorizar con **Switch account** |

La respuesta `401` incluye la cabecera `WWW-Authenticate`, con la que la API indica qué mecanismo espera. En OAuth 2.0, un `403` trae además `insufficient_scope` y el permiso que falta.

### 11.1 Errores de OAuth 2.0

Estos errores salen de la pantalla de consentimiento y del canje de tokens. Tienen nombres estándar de OAuth 2.0:

| Error | Dónde aparece | Qué significa |
| --- | --- | --- |
| `access_denied` | Al volver a n8n tras la pantalla de consentimiento | La persona pulsó **Rechazar** |
| `invalid_request` | Al volver a n8n | Falta un dato obligatorio (por ejemplo `state`) o PKCE mal armado |
| `invalid_scope` | Al volver a n8n | Se pidió un permiso que no existe |
| `invalid_client` | Al canjear o renovar (`401`) | Client ID o Client Secret incorrectos |
| `invalid_grant` | Al canjear o renovar (`400`) | El código o el refresh token no sirve: venció, ya se usó, no coincide con la `redirect_uri` o fue revocado |
| «redirect_uri no registrada» | En la pantalla del simulador, sin redirigir | La dirección de vuelta no es exactamente la registrada |

### 11.2 Guía para resolver errores frecuentes

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| El webhook responde 404 | El workflow no está publicado, o usas la Test URL | Publícalo y usa `/webhook/acceso-seguro` |
| Un nodo muestra una credencial sin seleccionar | Falta crearla o elegirla en el nodo | Crea las cinco credenciales. En los dos nodos OAuth hay dos credenciales del mismo tipo: elige cada una por su nombre |
| La ruta JWT responde 500 | La credencial `Login JWT` tiene un JSON mal escrito | Revisa que sea el JSON de la sección 7.3, con comillas dobles |
| `ECONNREFUSED` en un nodo | n8n no encuentra el simulador | Usa `http://catalogo:8080` y el `compose.yaml` del paquete |
| **Connect** no abre la pantalla de consentimiento | La Authorization URL apunta a `catalogo` o a un puerto equivocado | Usa `http://localhost:8091/oauth/autorizar`: la abre tu navegador |
| La pantalla dice «redirect_uri no registrada» | Abriste n8n con otra dirección o cambiaste `N8N_PUERTO` sin recrear el simulador | Entra por `http://localhost:5680` y ejecuta `docker compose up -d` |
| Tras autorizar, n8n muestra «Unauthorized» | Entraste a n8n como `127.0.0.1` y el navegador no envía tu sesión a `localhost` | Abre n8n como `http://localhost:5680`, cierra sesión y vuelve a entrar |
| El nodo OAuth responde 401 `token_desconocido` | Nunca conectaste la credencial, o el simulador se reinició y olvidó las autorizaciones | Abre la credencial y pulsa **Connect** o **Switch account** |
| El nodo OAuth responde 403 `insufficient_scope` | La credencial se conectó sin `catalogo.leer` | Corrige el **Scope**, guarda y vuelve a conectar |
| La ruta OAuth responde 401 `autorizacion_no_valida` | La autorización se revocó o venció y no se puede renovar | Vuelve a autorizar: **Switch account** en la credencial |
| La credencial dice «Account connected» pero falla | n8n no se entera de una revocación hasta que intenta usarla | Vuelve a autorizar con **Switch account** |
| El puerto está ocupado | Otra aplicación lo usa | Cambia `N8N_PUERTO` y `CATALOGO_PUERTO` (sección 6) |
| Postman no conecta | Puertos o entorno equivocados | Selecciona el entorno y revisa `url_n8n`, `url_simulador` y `oauth_redirect_uri` |

## 12. Buenas prácticas de seguridad

- **Usa el gestor de credenciales.** Un secreto escrito en un nodo, una expresión o una nota adhesiva queda a la vista de quien abra el workflow, de quien lo exporte y de quien vea una captura.
- **No pegues claves en capturas, chats ni repositorios.** Si una clave se expone, se cambia.
- **Una credencial por servicio y por propósito.** Así puedes cambiarla o revocarla sin afectar otros flujos.
- **Menos permisos son mejores.** Usa credenciales con acceso solo de lectura si el workflow solo lee.
- **Usa HTTPS.** Base64 y las cabeceras viajan en texto legible por HTTP.
- **Prefiere credenciales temporales.** Un token que vence limita el daño si se filtra.
- **Restringe los dominios** a los que se puede enviar una credencial (**Allowed HTTP Request Domains**).
- **Los secretos de firma no salen del servidor.** n8n nunca debe conocer la clave con que la API firma los tokens.
- **Proteger el webhook es otro control.** Autenticarse contra una API externa no protege tu propio webhook de n8n.
- **Pide el mínimo permiso (scope).** Si el workflow solo lee el catálogo, autoriza solo `catalogo.leer`.
- **El Client Secret y los tokens son secretos.** Viven en la credencial de n8n, nunca en un nodo, una nota o una captura.
- **La dirección de vuelta debe ser exactamente la registrada** y el `state` es obligatorio: así nadie desvía ni falsifica la autorización.
- **Un código de autorización se usa una sola vez.** Si alguien lo reutiliza, se rechaza y se revoca lo emitido.
- **Planifica la revocación.** Quien autoriza puede quitar el acceso en cualquier momento. Un workflow con OAuth necesita a alguien que vuelva a autorizar y que sepa que eso puede pasar.
- **Considera PKCE** cuando la aplicación no pueda guardar un secreto con seguridad.
- **Un simulador no es un servidor real.** El de este ejercicio guarda todo en memoria y no limita intentos. En producción usa un proveedor OAuth 2.0 real y HTTPS.
- **Cambia las claves de demostración.** Los valores de este apunte son públicos.

## 13. Checklist de revisión

Antes de dar por terminado un workflow que usa una API protegida, revísalo con esta lista:

| Revisión | Cómo comprobarlo |
| --- | --- |
| Ningún secreto escrito en los nodos | Abre cada nodo: la autenticación debe ser una credencial seleccionada |
| Ningún secreto en expresiones ni notas | Busca claves o tokens en campos, cabeceras y notas adhesivas |
| El JSON exportado no trae secretos | Ábrelo con un editor de texto y busca claves o contraseñas |
| Las capturas no muestran valores secretos | Revisa cada imagen, incluidas las ejecuciones |
| Los tokens no se guardan como valores fijos | La cabecera Bearer usa una expresión, no un texto pegado |
| Las llamadas sin credencial responden 401 | Pruébalo en Postman |
| Las credenciales incorrectas responden 401 | Pruébalo con una clave equivocada |
| Un token vencido responde 401 | Pruébalo con la ruta de ayuda del simulador |
| OAuth: la credencial pide solo el scope necesario | Abre la credencial y revisa el campo **Scope** |
| OAuth: el workflow resiste una revocación | Revoca la autorización y comprueba que la salida de error responde 401 |
| OAuth: sin permiso, 403; sin autorización, 401 | Pruébalo con la credencial de solo `perfil.leer` y sin conectar |
| Las credenciales tienen nombres claros | Que se sepa para qué sirve cada una |
| El workflow está publicado y probado por la Production URL | Llama al webhook desde Postman |
| Fuera de este ejercicio, las llamadas usan HTTPS | Revisa que la URL empiece con `https://` |

## 14. Pruebas de aceptación

Estas pruebas se ejecutaron de verdad el 25/11/2026, en una instalación limpia hecha solo con el ZIP del paquete (n8n 2.44.6, Docker). La columna «Obtenido» es lo que se midió, no lo que se esperaba.

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

## Comprueba lo que entendiste

```quiz
? Un workflow consulta una API con una clave escrita directamente en un campo del nodo HTTP Request. ¿Cuál es el problema principal?
- La API no acepta claves escritas en un campo.
+ Cualquiera que abra, exporte o fotografíe el workflow ve la clave.
- n8n no permite usar claves en un workflow.
> Las credenciales se guardan cifradas en el gestor de n8n y los workflows solo las seleccionan. Así el secreto no viaja con el workflow.
? Llamas a la ruta de API Key sin enviar la clave. ¿Qué responde la API?
- 200, porque la ruta existe.
+ 401, porque falta la credencial.
- 404, porque no encuentra el libro.
> 401 significa que la API no sabe quién eres. 404 indicaría una ruta o un libro inexistentes.
? ¿Por qué no basta Base64 para proteger un usuario y una contraseña?
- Porque Base64 solo funciona con API Keys.
+ Porque Base64 solo codifica el texto y cualquiera puede decodificarlo.
- Porque n8n no permite Base64.
> Base64 no es cifrado. Por eso Basic Auth se usa siempre sobre HTTPS.
? En la ruta JWT, ¿por qué hay un nodo para obtener el token antes de consultar el catálogo?
- Porque el catálogo cambia de URL en cada consulta.
+ Porque el token es temporal: se pide con el login y se usa en la misma ejecución.
- Porque un JWT solo funciona con el nodo Switch.
> El JWT se obtiene al iniciar sesión, vence y se envía como Bearer. No se guarda como una credencial permanente.
? ¿Qué significa Bearer en la cabecera Authorization?
- Que la API cifra el token.
+ Que quien presenta el token (el portador) obtiene el acceso.
- Que el token solo sirve una vez.
> Bearer significa portador. Por eso el token no se comparte ni se deja escrito.
? Un token JWT vencido todavía tiene una firma correcta. ¿Qué responde la API?
- 200, porque la firma es válida.
+ 401, porque ya venció.
- 403, porque no tiene permisos.
> La API revisa la firma y también la fecha de vencimiento. Un token bien firmado pero vencido se rechaza.
? Cambias a propósito la clave de la credencial por un valor incorrecto y el HTTP Request tiene activado Never Error. ¿Qué ocurre?
- La ejecución falla y no hay respuesta.
+ El workflow sigue y devuelve el 401 de la API a quien llamó.
- n8n corrige la clave solo.
> Never Error deja pasar la respuesta con su código. Sin esa opción, el nodo fallaría con el 401.
? Protegiste la API del catálogo con credenciales. ¿Eso protege también el webhook de tu workflow?
- Sí, el webhook hereda la protección de la API.
+ No, son controles distintos: el webhook se protege por separado.
- Solo si usas JWT.
> Las credenciales de este ejercicio protegen la API a la que n8n se conecta. Quién puede llamar al webhook es otra decisión.
? Una credencial OAuth2 de n8n está conectada con el permiso perfil.leer y la API responde 403 al consultar el catálogo. ¿Qué significa?
- Que el token venció y hay que pedir otro.
+ Que el token es válido, pero no tiene el permiso catalogo.leer que exige la ruta.
- Que la contraseña de la persona es incorrecta.
> El 403 indica que la API sabe quién eres, pero te falta un permiso. Se arregla autorizando de nuevo con el scope correcto, no cambiando el token.
? El access token de OAuth venció. ¿Qué hace n8n si la autorización sigue vigente?
- Falla la ejecución y la persona debe volver a autorizar.
+ Usa el refresh token para pedir uno nuevo, sin molestar a la persona.
- Guarda la contraseña de la persona para pedir otro.
> La renovación con el refresh token es automática mientras la autorización siga vigente.
? ¿Por qué el código de autorización viaja por el navegador, pero el canje por tokens lo hace n8n directamente con el Client Secret?
- Porque el navegador es más rápido.
+ Porque el código solo sirve a quien además conoce el Client Secret, y ese secreto no debe pasar por el navegador.
- Porque los tokens no pueden mostrarse en pantalla.
> El navegador es un lugar menos seguro. Por eso el secreto viaja solo entre servidores.
? La persona revoca la autorización en la página del simulador. ¿Qué muestra la credencial de n8n y qué pasa al ejecutar el workflow?
- La credencial pasa sola a «sin conectar» y el workflow no se ejecuta.
+ Sigue diciendo «Account connected», pero al usarla la renovación falla y hay que volver a autorizar.
- Nada: el access token sigue funcionando para siempre.
> n8n no sabe de la revocación hasta que intenta usar o renovar el token.
? ¿Qué ventaja tiene OAuth 2.0 frente a compartir el usuario y la contraseña con una aplicación?
- Que la contraseña viaja cifrada con Base64.
+ Que la aplicación recibe un permiso limitado que la persona puede revocar, sin conocer su contraseña.
- Que el token no vence nunca.
> OAuth 2.0 separa la autorización de la contraseña: se limita con el scope y se quita revocando.
```

## Documentación

- [Credenciales en n8n](https://docs.n8n.io/credentials/)
- [Nodo HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [Nodo Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [RFC 7519: JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519)
- [RFC 7617: esquema de autenticación Basic](https://www.rfc-editor.org/rfc/rfc7617)
- [RFC 6749: OAuth 2.0](https://www.rfc-editor.org/rfc/rfc6749)
- [RFC 7636: PKCE](https://www.rfc-editor.org/rfc/rfc7636)
- [RFC 7009: revocación de tokens](https://www.rfc-editor.org/rfc/rfc7009)
- [Biblioteca de manejo de errores](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-manejo-de-errores)

## Descarga e importación del ejemplo

Estos archivos incluyen el workflow con sus doce notas, el simulador de la API (con el servidor OAuth 2.0 educativo), la colección y el entorno de Postman y los datos de prueba. **Todos los valores son de demostración y ningún archivo contiene secretos reales.** Las capturas y las pruebas corresponden a **n8n 2.44.6**.

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-credenciales-autenticacion/biblioteca-acceso-seguro-completo.zip" download="biblioteca-acceso-seguro-completo.zip">Descargar el paquete completo (ZIP)</a></p>

O descarga cada archivo por separado:

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-credenciales-autenticacion/biblioteca-acceso-seguro-workflow.json" download="biblioteca-acceso-seguro-workflow.json">Workflow de n8n</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-credenciales-autenticacion/compose.yaml" download="compose.yaml">Docker Compose (n8n y simulador)</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-credenciales-autenticacion/simulador_catalogo_seguro.py" download="simulador_catalogo_seguro.py">Simulador de la API del catálogo</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-credenciales-autenticacion/biblioteca-acceso-seguro.postman_collection.json" download="biblioteca-acceso-seguro.postman_collection.json">Colección de Postman</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-credenciales-autenticacion/biblioteca-local.postman_environment.json" download="biblioteca-local.postman_environment.json">Entorno de Postman</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-credenciales-autenticacion/env.example" download=".env.example">Valores de demostración (.env.example)</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-credenciales-autenticacion/datos-prueba.zip" download="datos-prueba.zip">Datos de prueba</a></p>

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-credenciales-autenticacion/README.md" download="README.md">README de instalación</a></p>

### Importa el workflow

**Exporta e importa.** En el menú `...` del workflow, **Export JSON** guarda el archivo. Para importarlo, abre un workflow vacío, usa `...` > **Import** > **From file** y elige el archivo:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x1-menu-exportar.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Menú del workflow con la opción Export JSON"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x1-menu-exportar.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Menú del workflow con la opción Export JSON" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El menú <code>...</code> del workflow permite <b>Export JSON</b>. El archivo exportado no incluye los valores de las credenciales.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x2-importar-menu.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Menú del workflow con Import y From file"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x2-importar-menu.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Menú del workflow con Import y From file" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>En un workflow nuevo: <code>...</code> > <b>Import</b> > <b>From file</b>.</figcaption></figure>

Se importan los 16 nodos de flujo con sus **12 notas adhesivas**. Los nodos que usan credenciales aparecen con un triángulo de aviso, porque **este JSON no incluye los valores del gestor de credenciales**:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x3-importado-con-notas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3600" height="3400" alt="Workflow importado con las notas y avisos de credencial"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x3-importado-con-notas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow importado con las notas y avisos de credencial" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras importar: el workflow, las notas y los avisos en los nodos con credenciales por enlazar.</figcaption></figure>

### Configuración manual después de importar

1. **Crea las cinco credenciales**: las tres de la sección 7 y las dos de OAuth 2.0 de la sección 9.5, con esos nombres exactos (la lista está también en el `README.md`). Conecta las dos de OAuth con **Connect**.
2. **Abre cada nodo** con aviso: **Consultar con API Key**, **Consultar con Basic Auth**, **Obtener token**, **Consultar con OAuth 2.0** y **Consultar con OAuth 2.0 sin permiso**. Si solo existe una credencial de ese tipo, n8n la propone sola. Como hay **dos** credenciales OAuth2 API, en los dos nodos de OAuth debes elegir cada una por su nombre. Comprueba que sea la correcta y guarda:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x4-abrir-nodo-credencial.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo HTTP Request con su credencial seleccionada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x4-abrir-nodo-credencial.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo HTTP Request con su credencial seleccionada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Al abrir el nodo, n8n propone la credencial. Verifica el nombre.</figcaption></figure>

3. **Publica** el workflow con **Publish**.
4. **Prueba** con Postman: importa la colección y el entorno, selecciona el entorno y ejecuta las carpetas en orden.

El nodo **Consultar con JWT** no usa una credencial guardada: recibe el token por una expresión y no necesita configuración.

Para limpiar todo al terminar: `docker compose down -v`. El `-v` borra los datos de n8n, incluidas tus credenciales y workflows. Para actualizar un ejemplo ya instalado, no lo uses (sección 6).
