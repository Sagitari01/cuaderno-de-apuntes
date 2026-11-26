# Credenciales y autenticación de APIs en n8n: API Key, Basic Auth y JWT

Una biblioteca tiene una API que informa cuántos ejemplares de un libro están disponibles. Esa información no debería estar al alcance de cualquier aplicación. Aquí aprenderás cómo un workflow de n8n accede de forma segura a un servicio que exige autenticación: dónde se guardan las claves, cómo se configuran los tres mecanismos más comunes y qué ocurre cuando las credenciales fallan.

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
- configurar una **API Key**, una **Basic Auth** y un **JWT** en un nodo HTTP Request;
- distinguir qué datos necesita cada mecanismo, dónde se configuran y cómo viajan;
- probar cada caso con Postman, con y sin credenciales, y leer los códigos HTTP;
- leer una ejecución rechazada con `401` dentro de n8n;
- revisar un workflow con una lista de control de seguridad.

Necesitas Docker con Docker Compose, Postman y haber usado antes un workflow con **Webhook** y **HTTP Request**. No necesitas Python ni Node.js.

## 3. Qué es autenticarse

**Autenticarse** es demostrar quién eres. Una **credencial** es el dato con el que lo demuestras: una clave, un usuario y una contraseña, o un token. Es algo distinto de la **autorización**, que decide qué puedes hacer una vez que sabemos quién eres.

Piensa en el carnet de la biblioteca. Mostrarlo demuestra que eres socio (autenticación). Que puedas llevarte tres libros o solo consultar el catálogo depende de tus permisos (autorización).

Cuando una API protegida recibe una solicitud, puede responder:

- `200`: la credencial es válida y te entrega el dato;
- `401`: no sabe quién eres (falta la credencial o es incorrecta);
- `403`: sabe quién eres, pero no tienes permiso para eso.

En este ejercicio la API responde `401` cuando falla la autenticación.

## 4. API Key, Basic Auth y JWT: en qué se diferencian

Los tres permiten consultar el mismo catálogo, pero piden datos distintos y los envían de manera distinta:

<div role="region" aria-label="Comparación de autenticación, desplázate horizontalmente para ver todas las columnas" tabindex="0" style="max-width:100%;overflow-x:auto">
<div style="min-width:640px">

| | API Key | Basic Auth | JWT (Bearer) |
| --- | --- | --- | --- |
| Qué envías | Una clave | Usuario y contraseña | Un token temporal |
| Dónde viaja | Cabecera `X-API-Key` | Cabecera `Authorization: Basic ...` | Cabecera `Authorization: Bearer ...` |
| Identifica a | Una aplicación | Una cuenta | Una sesión de una cuenta |
| ¿Vence? | No, hasta que se cambie | No, hasta que se cambie | Sí, a los pocos minutos |
| Pasos previos | Ninguno | Ninguno | Pedir el token con usuario y clave |
| Se guarda en n8n como | Header Auth | Basic Auth | Credencial de login (Custom Auth) más una expresión |

</div>
</div>

En pantallas pequeñas, desplaza la tabla horizontalmente para ver todas las columnas.

Así se ven las cabeceras. Los valores entre `<` y `>` son marcadores, no claves reales:

<pre><code class="language-text">X-API-Key: &lt;tu clave>
Authorization: Basic &lt;usuario:contraseña codificado en Base64>
Authorization: Bearer &lt;token></code></pre>

Tres ideas que conviene tener claras:

- **Base64 no es cifrado.** Es solo una forma de escribir texto. Cualquiera que vea la cabecera de Basic Auth puede recuperar el usuario y la contraseña. En sistemas reales, estos mecanismos se usan siempre sobre **HTTPS**, que cifra la conexión. Aquí usamos HTTP porque todo corre en tu computador.
- **Un token es una credencial temporal.** En un JWT, la API lo firma con una clave que solo ella conoce. Tiene tres partes separadas por puntos (cabecera, datos y firma) y una fecha de vencimiento. Los datos son legibles; lo que impide alterarlos es la firma. Cuando vence, hay que pedir otro.
- **Bearer significa «portador».** Quien presenta el token, lo usa. Por eso un token no se comparte ni se deja escrito en ningún lugar.

## 5. Arquitectura del ejemplo

El ejemplo tiene dos servicios en Docker y un único workflow:

- **n8n**, donde vive el workflow **Biblioteca | Acceso seguro al catálogo** y el gestor de credenciales.
- **Catálogo seguro**, una API ficticia escrita en Python que **valida de verdad** las credenciales. Para JWT firma y verifica los tokens con HMAC-SHA256 y revisa el vencimiento. Dentro de la red de Docker se llama `catalogo`.
- **Postman**, que usarás desde tu computador para llamar al simulador y al webhook de n8n.

El workflow recibe una consulta, elige una ruta según el mecanismo y responde con lo que contestó la API:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w17-workflow-completo-notas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow completo con tres rutas de autenticación y notas adhesivas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w17-workflow-completo-notas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow completo con tres rutas de autenticación y notas adhesivas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El workflow terminado. De izquierda a derecha: <b>Recibir consulta</b>, <b>Preparar datos</b>, el <b>Switch</b> y las tres rutas (API Key, Basic Auth y JWT). La salida <b>Otro</b> atiende los tipos desconocidos.</figcaption></figure>

| Nodo | Qué hace |
| --- | --- |
| Recibir consulta | **Webhook** que recibe un JSON con `titulo` y `tipo_autenticacion` |
| Preparar datos | **Edit Fields** que deja esos dos campos listos |
| Tipo de autenticación | **Switch** que elige la ruta: `api_key`, `basic`, `jwt` u Otro |
| Consultar con API Key | **HTTP Request** con credencial Header Auth |
| Consultar con Basic Auth | **HTTP Request** con credencial Basic Auth |
| Obtener token | **HTTP Request** que pide un JWT con la credencial de login |
| Consultar con JWT | **HTTP Request** que envía el token en `Authorization: Bearer` |
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

Si cambias los puertos, recuerda actualizar las variables `url_n8n` y `url_simulador` del entorno de Postman antes de probar las solicitudes.

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
| `GET /salud`, `GET /registro`, `GET /reiniciar` | Rutas auxiliares para las pruebas |

Si llamas a una ruta protegida sin credencial, el simulador rechaza la solicitud:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d4-sin-credencial-401.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1020" alt="Respuesta 401 de la ruta con API Key sin enviar la clave"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d4-sin-credencial-401.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Respuesta 401 de la ruta con API Key sin enviar la clave" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Sin la cabecera <code>X-API-Key</code> el simulador responde <b>401</b>. El cuerpo explica el motivo (<code>falta_credencial</code>) y la cabecera <code>WWW-Authenticate</code> indica qué mecanismo espera.</figcaption></figure>

Por último abre n8n en <http://localhost:5680>. La primera vez te pide crear una cuenta local.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/n1-n8n-inicio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Pantalla de inicio de n8n"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/n1-n8n-inicio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Pantalla de inicio de n8n" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>n8n listo en <code>http://localhost:5680</code>. Dentro de n8n, la API se llama <code>http://catalogo:8080</code>, no <code>localhost</code>.</figcaption></figure>

Los valores de usuario, contraseña y clave del ejercicio están en el `README.md` del paquete y en `.env.example`. **Son valores de demostración: no son seguros y no deben usarse en sistemas reales.** La clave con que el simulador firma los tokens vive solo dentro del simulador; n8n nunca la conoce.

## 7. Crea las credenciales en n8n

**¿Qué estamos haciendo?** Guardamos en el gestor de credenciales de n8n los datos que la API exige.

**¿Para qué sirve?** n8n guarda las credenciales cifradas. Los workflows no contienen el secreto: solo **seleccionan** una credencial por su nombre. Antes de compartir, exportar o fotografiar un workflow, revisa también los parámetros escritos manualmente, los datos fijados y las salidas de ejecución: pueden contener secretos.

**¿Cómo lo hacemos?** Abre **Credentials**, en la pantalla de inicio de n8n. Todavía no hay ninguna:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c01-credenciales-vacio.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Lista de credenciales vacía con el botón Create credential resaltado"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/c01-credenciales-vacio.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Lista de credenciales vacía con el botón Create credential resaltado" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Un n8n nuevo no tiene credenciales. Pulsa <b>Create credential</b>.</figcaption></figure>

Crearás tres credenciales con estos nombres:

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

Construirás un único workflow con tres rutas. Cada etapa agrega un trozo y muestra cómo queda el lienzo.

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

**¿Cómo lo hacemos?** Agrega notas adhesivas (**Sticky Note**) cerca de cada parte, cortas y sin tapar las conexiones. Las notas se guardan dentro del JSON del workflow: cuando alguien lo importe, las verá. Este ejemplo trae siete:

| Nota | Qué explica |
| --- | --- |
| 1 Entrada | Qué llega desde Postman y que ahí no se envía ninguna clave |
| 2 Switch | Cómo el Switch elige la ruta y qué hace la salida Otro |
| 3 API Key | La clave vive en la credencial Header Auth, no en el workflow |
| 4 Basic Auth | Usuario y contraseña en Base64, que no cifra |
| 5 JWT | Por qué se pide un token y se envía como Bearer |
| 6 Rechazo | Qué pasa cuando la API responde 401 |
| 7 Otro | Qué responde el workflow ante un tipo desconocido |

Escribe en las notas explicaciones, **nunca valores secretos**. En la nota JWT del archivo descargable se aclara que el token puede quedar en el historial de ejecuciones. Las capturas conservan la versión anterior de esa nota; que un token sea temporal no significa que no se almacene.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w17-workflow-completo-notas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow completo con las siete notas adhesivas"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w17-workflow-completo-notas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow completo con las siete notas adhesivas" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El workflow terminado, con sus notas adhesivas legibles y fuera de las conexiones.</figcaption></figure>

### 8.7 Publica el workflow

Para que el webhook de producción responda hay que **publicar** el workflow. Pulsa **Publish** y escribe un nombre de versión:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w18-publicar-modal.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ventana para publicar el workflow con nombre de versión"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w18-publicar-modal.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ventana para publicar el workflow con nombre de versión" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>n8n pide un nombre para la versión que se publica.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w19-workflow-publicado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow publicado"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/w19-workflow-publicado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow publicado" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Con el workflow publicado, la <b>Production URL</b> del webhook responde.</figcaption></figure>

Mientras no esté publicado, esa dirección responde `404`.

## 9. Prueba con Postman

**¿Qué estamos haciendo?** Enviamos las mismas consultas con y sin credenciales para ver la diferencia entre `200` y `401`.

**¿Cómo lo hacemos?** En Postman elige **Import** y carga la colección `biblioteca-acceso-seguro.postman_collection.json` y el entorno `biblioteca-local.postman_environment.json`. Selecciona el entorno **Biblioteca local (demo)** arriba a la derecha. Sus variables son:

| Variable | Valor por defecto |
| --- | --- |
| `url_n8n` | `http://localhost:5680` |
| `url_simulador` | `http://localhost:8091` |
| `api_key`, `basic_usuario`, `basic_clave`, `jwt_usuario`, `jwt_clave` | Valores de demostración del paquete |

Postman corre en tu computador, así que usa `localhost` y los puertos publicados, no los nombres `n8n` ni `catalogo`, que solo existen dentro de Docker.

La colección tiene 20 solicitudes en seis carpetas, y cada una trae una prueba automática en **Scripts > Post-response**. Estas son las principales:

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

### 9.1 API Key y Basic Auth

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p1-postman-api-key.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1334" alt="Ejecución de la carpeta API Key"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p1-postman-api-key.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta API Key" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>API Key: sin clave y con clave incorrecta responden <code>401</code>, con la clave válida responde <code>200</code>. Las pruebas (✓) confirman el código y el motivo.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p2-postman-basic.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1334" alt="Ejecución de la carpeta Basic Auth"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p2-postman-basic.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta Basic Auth" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Basic Auth: sin credenciales y con contraseña incorrecta responden <code>401</code>; con las credenciales válidas, <code>200</code>.</figcaption></figure>

### 9.2 JWT

La carpeta de JWT sigue un orden: pedir un token, probar los casos que fallan y, al final, usar el token válido. La solicitud de login guarda el token en una variable de colección. Newman no exporta su valor al terminar salvo que se solicite; en Postman revisa las variables y los datos de ejecución antes de compartir o exportar:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p3-postman-jwt.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2342" alt="Ejecución de la carpeta JWT"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p3-postman-jwt.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta JWT" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>JWT: el token se obtiene con las credenciales válidas. Sin token, con un token inválido o vencido responde <code>401</code>. Con el token válido, <code>200</code>.</figcaption></figure>

### 9.3 El webhook de n8n

La carpeta 5 llama al **webhook del workflow**. Fíjate en que Postman **no envía ninguna clave**: la pone n8n con las credenciales guardadas. El cuerpo solo indica con qué mecanismo consultar:

<pre><code class="language-text">{
  "titulo": "El faro de papel",
  "tipo_autenticacion": "api_key"
}</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p4-postman-webhook.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1712" alt="Ejecución de la carpeta del webhook de n8n"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p4-postman-webhook.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución de la carpeta del webhook de n8n" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Las tres rutas responden <code>200</code> y un tipo desconocido responde <code>400</code>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p5-postman-resumen.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="1586" alt="Resumen de la ejecución de la colección completa"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/p5-postman-resumen.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Resumen de la ejecución de la colección completa" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Resultado de la colección completa: 20 solicitudes y 46 pruebas, ninguna fallida.</figcaption></figure>

### 9.4 Qué ves dentro de n8n

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

### 9.5 Qué ocurre cuando la API rechaza una solicitud

Para verlo, vamos a romper a propósito la credencial de API Key: en **Credentials** abre **Biblioteca | API Key (demo)** y cambia el valor por otro, por ejemplo `clave-incorrecta-demo`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r1-credencial-valor-incorrecto.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Credencial Header Auth editada con un valor incorrecto"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r1-credencial-valor-incorrecto.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Credencial Header Auth editada con un valor incorrecto" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Se cambia el valor de la credencial (queda enmascarado). Después, restáurala con el valor correcto.</figcaption></figure>

Vuelve a enviar la consulta de API Key desde Postman. El webhook responde **401**. Abre la ejecución:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r2-ejecucion-rechazada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Ejecución con rechazo 401"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r2-ejecucion-rechazada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Ejecución con rechazo 401" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>La ejecución aparece como <b>Succeeded</b> aunque la API respondió <code>401</code>: gracias a <b>Never Error</b>, el workflow siguió y devolvió el rechazo.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r3-rechazo-salida-http.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Consultar con API Key con statusCode 401"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r3-rechazo-salida-http.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Consultar con API Key con statusCode 401" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El HTTP Request entrega <code>statusCode</code> <code>401</code>, el cuerpo con el motivo <code>credencial_incorrecta</code> y la cabecera <code>www-authenticate</code>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r4-rechazo-respuesta.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Salida de Responder (API Key) con el código 401"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/r4-rechazo-respuesta.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Salida de Responder (API Key) con el código 401" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>El Responder devuelve a Postman el mismo código <code>401</code> y el motivo.</figcaption></figure>

Si **Never Error** estuviera apagado, el HTTP Request fallaría con el `401` y la ejecución terminaría en error. Cuál de los dos comportamientos conviene depende de lo que quieras hacer con el rechazo. Es el mismo tema del apunte de [manejo de errores](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-manejo-de-errores).

Restaura el valor correcto de la credencial para seguir.

### 9.6 Qué ve el simulador

El simulador anota cada petición que recibe, sin mostrar claves, contraseñas ni tokens. Lo ves en los registros de Docker:

<pre><code class="language-text">docker compose logs --no-log-prefix --tail 8 catalogo</code></pre>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d5-logs-simulador.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="894" alt="Registros del simulador con respuestas 401 y 200"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/d5-logs-simulador.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registros del simulador con respuestas 401 y 200" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Cada línea indica la ruta, el código, el mecanismo y el motivo del rechazo. Nunca el valor de la credencial.</figcaption></figure>

También puedes abrir <http://localhost:8091/registro> en el navegador:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/s1-simulador-registro.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Registro de peticiones del simulador en el navegador"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/s1-simulador-registro.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Registro de peticiones del simulador en el navegador" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption><code>/registro</code> muestra las últimas peticiones: ruta, mecanismo, si se envió credencial, código y motivo.</figcaption></figure>

## 10. Interpreta los códigos HTTP y las respuestas

| Código | Significado en este ejercicio | Qué revisar |
| --- | --- | --- |
| `200` | La credencial es válida y la API entregó el dato | Nada: es el resultado esperado |
| `400` | La solicitud está mal armada (falta usuario o clave, o el tipo de autenticación no existe) | El cuerpo JSON que se envía |
| `401` | Falta la credencial, es incorrecta o el token no sirve | El campo `motivo` de la respuesta |
| `404` | La ruta o el libro no existen | La URL y el título |
| `500` | Falló el workflow de n8n | La ejecución en **Executions** |

Cuando la API responde `401`, el campo `motivo` ayuda a encontrar la causa:

| Motivo | Qué ocurrió | Cómo se arregla |
| --- | --- | --- |
| `falta_credencial` | No se envió la cabecera | Revisa que el nodo o la solicitud tengan la autenticación configurada |
| `credencial_incorrecta` | La clave, el usuario o la contraseña no coinciden | Revisa el valor de la credencial |
| `token_malformado` | El texto no tiene forma de JWT | Revisa que envíes el token completo |
| `firma_invalida` | El token fue alterado o lo firmó otro servicio | Pide un token nuevo |
| `token_vencido` | El token ya no es válido por la hora | Pide un token nuevo |

La respuesta `401` incluye la cabecera `WWW-Authenticate`, con la que la API indica qué mecanismo espera.

## 11. Buenas prácticas de seguridad

- **Usa el gestor de credenciales.** Un secreto escrito en un nodo, una expresión o una nota adhesiva queda a la vista de quien abra el workflow, de quien lo exporte y de quien vea una captura.
- **No pegues claves en capturas, chats ni repositorios.** Si una clave se expone, se cambia.
- **Una credencial por servicio y por propósito.** Así puedes cambiarla o revocarla sin afectar otros flujos.
- **Menos permisos son mejores.** Usa credenciales con acceso solo de lectura si el workflow solo lee.
- **Usa HTTPS.** Base64 y las cabeceras viajan en texto legible por HTTP.
- **Prefiere credenciales temporales.** Un token que vence limita el daño si se filtra.
- **Restringe los dominios** a los que se puede enviar una credencial (**Allowed HTTP Request Domains**).
- **Los secretos de firma no salen del servidor.** n8n nunca debe conocer la clave con que la API firma los tokens.
- **Proteger el webhook es otro control.** Autenticarse contra una API externa no protege tu propio webhook de n8n.
- **Cambia las claves de demostración.** Los valores de este apunte son públicos.

## 12. Checklist de revisión

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
| Las credenciales tienen nombres claros | Que se sepa para qué sirve cada una |
| El workflow está publicado y probado por la Production URL | Llama al webhook desde Postman |
| Fuera de este ejercicio, las llamadas usan HTTPS | Revisa que la URL empiece con `https://` |

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
```

## Documentación

- [Credenciales en n8n](https://docs.n8n.io/credentials/)
- [Nodo HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)
- [Nodo Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [RFC 7519: JSON Web Token](https://www.rfc-editor.org/rfc/rfc7519)
- [RFC 7617: esquema de autenticación Basic](https://www.rfc-editor.org/rfc/rfc7617)
- [Biblioteca de manejo de errores](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-manejo-de-errores)

## Descarga e importación del ejemplo

Estos archivos incluyen el workflow con sus notas, el simulador de la API, la colección y el entorno de Postman y los datos de prueba. **Todos los valores son de demostración y ningún archivo contiene secretos reales.** Las capturas y las pruebas corresponden a **n8n 2.44.6**.

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

Se importan los 11 nodos con sus **7 notas adhesivas**. Los nodos que usan credenciales aparecen con un triángulo de aviso, porque **este JSON no incluye los valores del gestor de credenciales**:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x3-importado-con-notas.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Workflow importado con las notas y avisos de credencial"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x3-importado-con-notas.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Workflow importado con las notas y avisos de credencial" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tras importar: el workflow, las notas y los avisos en los nodos con credenciales por enlazar.</figcaption></figure>

### Configuración manual después de importar

1. **Crea las tres credenciales** con los nombres de la sección 7 (la lista está también en el `README.md`).
2. **Abre cada nodo** con aviso: **Consultar con API Key**, **Consultar con Basic Auth** y **Obtener token**. Si solo existe una credencial de ese tipo, n8n la propone sola. Comprueba que sea la correcta y guarda:

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x4-abrir-nodo-credencial.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="3200" height="2000" alt="Nodo HTTP Request con su credencial seleccionada"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-credenciales-autenticacion/x4-abrir-nodo-credencial.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura: Nodo HTTP Request con su credencial seleccionada" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Al abrir el nodo, n8n propone la credencial. Verifica el nombre.</figcaption></figure>

3. **Publica** el workflow con **Publish**.
4. **Prueba** con Postman: importa la colección y el entorno, selecciona el entorno y ejecuta las carpetas en orden.

El nodo **Consultar con JWT** no usa una credencial guardada: recibe el token por una expresión y no necesita configuración.

Para limpiar todo al terminar: `docker compose down -v`. El `-v` borra los datos de n8n, incluidas tus credenciales y workflows.
