# Biblioteca: acceso seguro al catálogo (API Key, Basic Auth y JWT en n8n)

Ejemplo independiente para practicar credenciales y autenticación de APIs en n8n. Todo corre en tu computador con Docker:
n8n y una API ficticia del catálogo de una biblioteca que **valida de verdad** las credenciales. No usa servicios externos
ni cuentas reales. **Todos los valores de este paquete son de demostración y no deben usarse en sistemas reales.**

## Contenido

| Archivo | Para qué sirve |
| --- | --- |
| `compose.yaml` | Levanta n8n y el simulador en la misma red de Docker. |
| `.env.example` | Valores de demostración y puertos configurables (copia a `.env` solo si quieres cambiarlos). |
| `simulador_catalogo_seguro.py` | API ficticia con endpoint público, API Key, Basic Auth y JWT (Python, solo biblioteca estándar). |
| `biblioteca-acceso-seguro-workflow.json` | Workflow de n8n «Biblioteca \| Acceso seguro al catálogo», con sus notas adhesivas. |
| `biblioteca-acceso-seguro.postman_collection.json` | Colección de Postman: 20 solicitudes con pruebas automáticas. |
| `biblioteca-local.postman_environment.json` | Entorno de Postman con las direcciones locales y los valores de demostración. |
| `datos-prueba/` | Cuerpos JSON de ejemplo para el webhook y para pedir un token. |

## Requisitos

Docker con Docker Compose. Para las pruebas visuales, Postman. No necesitas Python ni Node.js en tu equipo.

## Puesta en marcha

1. Descomprime el paquete y abre una terminal dentro de la carpeta `biblioteca-acceso-seguro`.
2. Ejecuta `docker compose up -d`. Direcciones por defecto: n8n en <http://localhost:5680> y el simulador en <http://localhost:8091>.
   Si un puerto está ocupado, cámbialo así: `N8N_PUERTO=5681 CATALOGO_PUERTO=8092 docker compose up -d`.
3. Comprueba el simulador: <http://localhost:8091/salud> debe responder `"estado": "activo"`.
4. Abre n8n y crea tu cuenta local la primera vez.

Dentro de n8n, el simulador se llama `catalogo`: la dirección es `http://catalogo:8080` (no `localhost`).

## Credenciales de demostración

| Mecanismo | Dato | Valor de demostración |
| --- | --- | --- |
| API Key | Cabecera | `X-API-Key` |
| API Key | Valor | `demo-clave-api-biblioteca` |
| Basic Auth | Usuario | `lector-demo` |
| Basic Auth | Contraseña | `demo-clave-basic` |
| JWT | Usuario | `lector-demo` |
| JWT | Clave | `demo-clave-jwt` |

La clave con que el simulador firma los tokens (`JWT_SECRETO`) vive solo dentro del simulador. n8n nunca la conoce y no está en el workflow.

## Crear las credenciales en n8n

Este workflow **no trae los valores del gestor de credenciales**. Un JSON puede contener secretos escritos manualmente en parámetros o datos fijados; revisa siempre el archivo antes de compartirlo. Créalas antes de usarlo, con estos nombres exactos
(en **Credentials > Create credential**):

1. **Header Auth** llamada `Biblioteca | API Key (demo)`. Name: `X-API-Key`. Value: la clave de la tabla.
2. **Basic Auth** llamada `Biblioteca | Basic Auth (demo)`. User y Password de la tabla.
3. **Custom Auth** llamada `Biblioteca | Login JWT (demo)`. En JSON escribe:
   `{"body": {"usuario": "lector-demo", "clave": "demo-clave-jwt"}}`

## Importar y publicar el workflow

1. En un workflow vacío abre el menú `...` > **Import from file** y elige `biblioteca-acceso-seguro-workflow.json`. Se conservan las 7 notas adhesivas.
2. Los nodos **Consultar con API Key**, **Consultar con Basic Auth** y **Obtener token** aparecen con un triángulo de aviso: la credencial no está enlazada. Abre cada uno. Si solo existe una credencial de ese tipo, n8n la propone sola; comprueba que sea la correcta (o elígela en la lista) y guarda. El nodo **Consultar con JWT** no usa credencial guardada: recibe el token por una expresión.
3. Guarda con `Ctrl+S` y pulsa **Publish** (n8n pide un nombre de versión). Hasta publicar, el webhook de producción responde 404.

## Probar con Postman

1. En Postman elige **Import** y carga la colección y el entorno. Selecciona el entorno **Biblioteca local (demo)** (arriba a la derecha).
2. Si cambiaste los puertos, edita `url_n8n` y `url_simulador` en el entorno.
3. Ejecuta las carpetas en orden. Las carpetas 1 a 4 llaman directo al simulador y muestran qué ocurre con y sin credenciales (200 o 401). La carpeta 5 llama al webhook del workflow de n8n: **ahí no envías ninguna clave**, la pone n8n con su credencial guardada.
4. Con **Run collection** corres todo y ves las pruebas en verde o rojo.

Resultados esperados: público 200; API Key sin clave 401, incorrecta 401, válida 200; Basic incorrecto 401, válido 200; token con credenciales válidas
(200 con `access_token`); JWT sin token 401, inválido 401, vencido 401, válido 200; webhook de n8n 200 en las tres rutas y 400 con un tipo no válido.

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

Las rutas protegidas aceptan `?titulo=El faro de papel`. Responden `401` con un `motivo` (`falta_credencial`, `credencial_incorrecta`,
`token_malformado`, `firma_invalida`, `token_vencido`...). Para ver las peticiones en vivo: `docker compose logs -f catalogo`.

## Seguridad: lo que conviene recordar

- Una credencial se guarda en n8n, cifrada, y los workflows solo la **seleccionan**. No escribas claves dentro de nodos, expresiones ni notas.
- Base64 no es cifrado. Con Basic Auth y API Key, usa siempre HTTPS fuera de este ejercicio.
- Un token JWT es temporal: se pide, se usa y vence. No lo guardes como valor fijo.
- Proteger el **webhook de n8n** (quién puede llamar a tu workflow) es otro control distinto de autenticarse contra una API externa.
- Cambia todos los valores de este paquete antes de usar algo parecido en un sistema real.

## Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| El webhook responde 404 | El workflow no está publicado, o usas la Test URL | Publícalo y usa `/webhook/acceso-seguro` |
| `Credential not found` o credencial sin seleccionar | Falta crearla o elegirla en el nodo | Crea las tres credenciales y selecciónalas |
| La ruta JWT responde 500 | La credencial `Login JWT` tiene un JSON mal escrito | Revisa que sea el JSON de arriba, con comillas dobles |
| `ECONNREFUSED` en un nodo | n8n no encuentra el simulador | Usa `http://catalogo:8080` y el `compose.yaml` del paquete |
| El puerto está ocupado | Otra aplicación lo usa | `N8N_PUERTO=5681 CATALOGO_PUERTO=8092 docker compose up -d` |
| Postman no conecta | Puertos o entorno equivocados | Selecciona el entorno y revisa `url_n8n` y `url_simulador` |

## Limpieza

`docker compose down -v` detiene los contenedores y borra los datos de n8n (incluidas tus credenciales y workflows).
