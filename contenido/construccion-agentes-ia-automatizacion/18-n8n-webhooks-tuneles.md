# Webhooks seguros en n8n: túneles HTTPS y eventos externos

Una persona devuelve un libro en una sucursal. El sistema que registra la devolución necesita avisar a la biblioteca central. ¿Cómo puede hacerlo si nuestro n8n vive dentro de Docker y solo se abre con `localhost`? ¿Qué impediría que alguien que conozca la dirección envíe una devolución falsa?

En este laboratorio usaremos un evento de biblioteca ficticia, Postman y un webhook protegido con una cabecera secreta. El túnel nos permitirá recibir el evento por HTTPS sin abrir manualmente puertos del router. **Primero protegemos el webhook y después lo exponemos.**

## 1. Objetivos y conocimientos previos

- Diferenciar evento, endpoint, webhook y polling.
- Distinguir las URL de prueba y producción.
- Configurar Header Auth en un Webhook y demostrar los rechazos.
- Exponer solo el receptor mediante Cloudflare Quick Tunnel; comparar ngrok como alternativa.
- Revisar el código HTTP, los datos de la ejecución y las limitaciones del ejercicio.

Necesitas Docker Desktop o Docker con Compose, Postman, un navegador y permiso para usar un túnel. No necesitas una API de IA, Google Drive, una tarjeta de crédito ni una base de datos para este ejercicio. Repasa [APIs y webhooks en n8n](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-api-webhook) y [Credenciales y autenticación](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-credenciales-autenticacion).

## 2. El problema: un sistema externo no conoce tu localhost

| Concepto | En esta biblioteca |
| --- | --- |
| Evento | `libro.devuelto`, un hecho ocurrido en una sucursal |
| Emisor | Sistema de la sucursal; aquí lo simulamos con Postman |
| Endpoint | Una dirección y método, por ejemplo `POST /webhook/biblioteca-evento-protegido` |
| Webhook | Entrada que inicia el workflow al recibir una solicitud válida |
| Polling | n8n consulta periódicamente si hay novedades, aunque no las haya |
| Túnel | Reenvía las solicitudes desde una URL pública hacia un servicio local |
| HTTPS | Protege el transporte público; no prueba por sí mismo la identidad del emisor |
| Header Auth | Exige una cabecera con un valor secreto antes de iniciar el workflow |

En otra máquina, `localhost` designa esa otra máquina. Un túnel resuelve la conectividad; la credencial resuelve una parte del control de acceso. Son problemas distintos.

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/diagramas/n8n-webhooks-tuneles/arquitectura-webhook.svg" style="display:block;width:100%;height:auto" alt="Postman, túnel HTTPS, proxy local, webhook de n8n y editor separado" loading="lazy"><figcaption>Esquema conceptual del laboratorio. El túnel apunta al proxy, no directamente a la instancia de n8n.</figcaption></figure>

**Decisión de seguridad:** si un túnel se dirige a todo n8n, también podría hacer accesibles el editor, las API administrativas y otros webhooks. Usaremos un pequeño proxy Nginx que admite únicamente el método POST en la ruta de producción de este ejercicio. Es un ejemplo local de mínimo privilegio, no una configuración de producción auditada.

## 3. Prepara Docker sin modificar tus otros laboratorios

Descarga los archivos al final de esta guía y guárdalos juntos en una carpeta nueva `biblioteca-webhooks`. La instancia es independiente de las prácticas anteriores: usa n8n 2.44.6, un volumen propio y otros puertos.

| Servicio | Puerto del equipo | Puerto del contenedor | Uso |
| --- | --- | --- | --- |
| n8n | 5682 | 5678 | Editor privado y pruebas locales |
| Proxy | 8092 | 8080 | Único punto al que apuntará el túnel |

Abre PowerShell en la carpeta y ejecuta:

```powershell
docker compose config --quiet
docker compose up -d
docker compose ps
```

Los servicios n8n y proxy deben estar en ejecución. El servicio `tunnel` no debe aparecer todavía: es opcional y está en el perfil `publico`. Abre `http://localhost:5682` y crea el usuario propietario de **esta instancia de laboratorio** si se solicita. Utiliza una contraseña única y privada. No reutilices tus credenciales corporativas.

Importa `biblioteca-webhook-semicompletado.json` desde el menú de tres puntos de un workflow nuevo, y guarda. El workflow contiene:

| Nodo | Responsabilidad |
| --- | --- |
| Recibir evento (Webhook) | Recibe el POST; al principio la autenticación está desactivada para observar el problema |
| Preparar evento (Edit Fields) | Extrae evento, id_evento, título, sucursal y hora |
| Confirmar recepción (Respond to Webhook) | Devuelve solo esos datos como JSON con código 200 |

Este laboratorio prepara información en memoria de la ejecución. **No guarda préstamos ni modifica un catálogo.** Las tres notas adhesivas explican la entrada, el tratamiento y la respuesta.

## 4. Demostración local: antes de proteger

En el Webhook comprueba el método `POST`, el Path `biblioteca-evento-protegido`, `Authentication: None` y `Respond: Using 'Respond to Webhook' Node`.

| Tipo de URL | Dirección en esta práctica | Cuándo funciona |
| --- | --- | --- |
| Test | `http://localhost:5682/webhook-test/biblioteca-evento-protegido` | Tras pulsar Listen for test event; vuelve a escuchar si la prueba se consume o vence |
| Production | `http://localhost:5682/webhook/biblioteca-evento-protegido` | Después de publicar el workflow |

En Postman crea una solicitud POST con `Content-Type: application/json` y el cuerpo siguiente, o importa la colección de descargas:

```json
{
  "evento": "libro.devuelto",
  "id_evento": "DEV-0001",
  "titulo": "El faro de papel",
  "sucursal": "Centro"
}
```

1. Pulsa **Listen for test event**, envía el POST a la Test URL local y observa el JSON de entrada.
2. Publica el workflow y llama a la Production URL sin token. En la colección, usa la carpeta 1 con `baseUrl` igual a `http://localhost:5682`.
3. Observa el 200 y el cuerpo devuelto. Abre **Executions** para ver la ejecución.

**Pregunta:** si este receptor estuviera en Internet, ¿qué impediría que otra persona enviara la misma devolución? Todavía nada en la entrada.

**No inicies ningún túnel durante esta etapa.**

## 5. Cierra el webhook con Header Auth

**¿Qué estamos haciendo?** Exigimos un secreto compartido entre emisor y receptor, utilizando el gestor de credenciales de n8n. A diferencia de la práctica de OAuth 2.0, aquí no hay pantalla de consentimiento ni tokens renovables.

Genera un token aleatorio largo en tu gestor de contraseñas. No uses `1234`, el nombre de la biblioteca ni el authtoken de ngrok. Guárdalo en un lugar privado.

| Campo de n8n | Valor |
| --- | --- |
| Tipo de credencial | Header Auth |
| Nombre de credencial | `Biblioteca – Token webhook (demo)` |
| Name | `X-Biblioteca-Token` |
| Value | Tu token aleatorio privado |

En el nodo **Recibir evento**, cambia **Authentication** a **Header Auth** y selecciona la credencial. Guarda y publica la versión protegida. No coloques el secreto en el nombre, el JSON, las notas, un nodo IF, la URL ni el repositorio.

En Postman configura el valor **local** de `tokenBiblioteca` con tu token y conserva `baseUrl=http://localhost:5682`. Usa la carpeta 2 de la colección, o crea tres solicitudes idénticas excepto por la cabecera:

| Caso | Cabecera | Resultado esperado |
| --- | --- | --- |
| Sin token | No enviar `X-Biblioteca-Token` | Rechazo 403 en la versión de referencia; 401 en otras versiones |
| Incorrecto | `X-Biblioteca-Token: valor-incorrecto-demo` | Rechazo 403 o 401 |
| Correcto | `X-Biblioteca-Token: TU_TOKEN_PRIVADO` | 200 y una ejecución del flujo |

El valor `TU_TOKEN_PRIVADO` es un marcador, no una clave. Los rechazos deben ocurrir **antes** de los nodos de tratamiento. Comprueba el número de ejecuciones, no solo el código HTTP.

En n8n 2.44.6 el material de referencia de la práctica documenta 403 para Header Auth ausente o incorrecto. La colección admite 401 o 403 porque la implementación puede cambiar entre versiones. Un rechazo de Header Auth no equivale necesariamente a un scope insuficiente de OAuth.

## 6. Verifica la frontera antes de abrir el túnel

Cambia `baseUrl` a `http://localhost:8092` (proxy local). Repite la carpeta 2: los intentos no autorizados deben rechazarse y el válido responder 200. Después ejecuta la carpeta 3:

| Solicitud al proxy local | Resultado esperado |
| --- | --- |
| GET `/` | 404, el editor no está expuesto |
| POST `/webhook-test/biblioteca-evento-protegido` | 404, ruta de prueba bloqueada |
| POST `/webhook/no-publicar` | 404, otras rutas bloqueadas |
| GET `/webhook/biblioteca-evento-protegido` | 405, método no permitido |

**No continúes si el editor carga por el puerto 8092 o si una llamada sin token obtiene 200.** Revisa primero la credencial, la publicación y el archivo `nginx.conf`. No apuntes el túnel al puerto 5682 ni al 5678.

## 7. Abre el túnel con Cloudflare Quick Tunnel

| Característica | ngrok | Cloudflare Quick Tunnel |
| --- | --- | --- |
| Cuenta | Requiere cuenta y authtoken | No requiere cuenta ni dominio propio |
| Dirección pública | Puede usar el dominio de desarrollo asignado a tu cuenta | Host temporal `trycloudflare.com` que cambia al reiniciar |
| Uso en esta práctica | Alternativa para demos con URL de desarrollo | Alternativa rápida para una prueba temporal |
| Límites | Dependen del plan; consulta el panel | Sin garantía de disponibilidad; límite documentado de solicitudes simultáneas, sin SSE |

El authtoken de ngrok identifica tu agente ante ngrok. El token `X-Biblioteca-Token` protege el webhook. **Son dos secretos distintos.** **Cloudflare Quick Tunnel será el camino principal:** no exige cuenta, dominio ni authtoken. Es temporal, no tiene garantía de disponibilidad y admite hasta 200 solicitudes en curso, sin SSE. ngrok queda como comparación o alternativa si la red lo permite.

### 7.1 Cloudflare en Docker — camino recomendado

El Compose incluye `cloudflared` como servicio opcional: **no necesitas instalar otro programa en Windows**. El agente solo comparte la red de entrada del proxy, no la red backend de n8n. No habilites el túnel hasta superar las pruebas locales de la sección 6.

En una segunda terminal, dentro de la carpeta del laboratorio, ejecuta:

```powershell
docker compose run --rm --no-deps tunnel
```

El comando descarga la imagen oficial de cloudflared si hace falta y muestra una URL temporal `https://...trycloudflare.com`. Mantén la terminal abierta. No requiere cuenta ni authtoken de Cloudflare. El agente apunta a `http://proxy:8080`, no a n8n ni a localhost, porque corre dentro de Docker.

La imagen del agente usa `latest`; registra la versión durante la validación con `docker compose run --rm --no-deps tunnel --version` y fija la imagen que hayas probado. n8n mantiene su versión fija 2.44.6.

Si no conecta, revisa los logs y los permisos de red. No desactives controles corporativos ni intentes eludir restricciones. Si la red bloquea los túneles, completa la parte local y deja la prueba pública pendiente.

### 7.2 Alternativa: cloudflared instalado en el equipo

Si ya tienes cloudflared desde [las descargas oficiales](https://developers.cloudflare.com/tunnel/downloads/), también puedes usar PowerShell:

```powershell
cloudflared tunnel --url http://localhost:8092
```

Elige un solo método. Copia la URL HTTPS generada y mantenla privada. No actives la autenticación interactiva por correo: esta prueba usa Postman y Header Auth. El hostname cambia al iniciar otro Quick Tunnel.

### 7.3 ngrok — referencia opcional

ngrok requiere cuenta y authtoken privado. Si ya lo tienes configurado según [la documentación oficial](https://ngrok.com/docs/start), la alternativa es `ngrok http 8092`. Su authtoken no es `X-Biblioteca-Token`. No se exige implementar los dos proveedores.

## 8. Prueba el evento a través de Internet

En Postman cambia `baseUrl` por tu dirección HTTPS sin barra final, manteniendo la ruta `/webhook/biblioteca-evento-protegido`. La URL completa tendrá esta forma ficticia:

`https://tu-dominio.example/webhook/biblioteca-evento-protegido`

Ejecuta otra vez la carpeta 2 (sin cabecera, valor incorrecto, valor válido) y la carpeta 3 (editor y otras rutas bloqueadas). Si tienes autorización, repite el caso válido desde otro dispositivo o red usando solo datos ficticios. Abre **Executions** desde el editor local para confirmar la recepción.

Una respuesta válida esperada (la hora será distinta):

```json
{
  "recibido": true,
  "evento": "libro.devuelto",
  "id_evento": "DEV-0001",
  "titulo": "El faro de papel",
  "sucursal": "Centro",
  "recibido_en": "2026-01-01T12:00:00.000-03:00"
}
```

### 8.1 Cómo hacer que n8n anuncie la URL pública

Para una prueba manual puedes construir la URL en Postman, sin recrear el contenedor. Cuando necesites que n8n muestre la base pública en la interfaz, copia `env.example` como `.env` en la misma carpeta y configura `URL_PUBLICA=https://tu-dominio.example/` con tu dirección real. El `compose.yaml` ya la pasa a `N8N_WEBHOOK_URL`, conserva el editor local mediante `N8N_EDITOR_BASE_URL` y configura `N8N_PROXY_HOPS` para el proxy inmediato.

```powershell
docker compose config --quiet
docker compose up -d --force-recreate n8n proxy
```

El volumen persistente conserva la configuración de la instancia. Verifica que el webhook siga publicado y protegido, y repite las pruebas del proxy y del túnel. No utilices la Test URL anunciada por el editor desde Internet: el proxy deliberadamente la bloquea.

**Nota:** para una integración real, configura correctamente la cadena de proxies y cabeceras de reenvío según la arquitectura del proveedor. En este ejemplo no tomamos decisiones de seguridad a partir de la IP del cliente o de cabeceras de reenvío; usamos Header Auth y una ruta permitida explícitamente.

## 9. Diagnóstico y control de errores

| Resultado | Qué revisar |
| --- | --- |
| 200 | Inspecciona el JSON y la ejecución; no significa que se guardó un préstamo |
| 401/403 | Header Auth, nombre de cabecera y token; no desactives la protección para solucionar el error |
| 404 en n8n | Publicación, método y ruta; para test, que el nodo esté escuchando |
| 404 en proxy | Puede ser un bloqueo intencional; comprueba que usas la ruta exacta de producción |
| 405 en proxy | Usa POST |
| 413 | Cuerpo demasiado grande para el proxy (límite 64 KiB) |
| 429 | Límite del proveedor; revisa la política y espera antes de repetir |
| 502/504 | Comprueba los contenedores y el destino local del túnel |

Prueba enviar dos veces el mismo `id_evento`. Habrá dos ejecuciones: esta demostración no deduplica eventos. Antes de crear registros reales se necesitaría un identificador estable y una comprobación persistente de idempotencia. Tampoco valida formalmente todos los campos ni firma el contenido. La firma de webhooks corresponde a una práctica posterior.

## 10. Actividad práctica y evidencias

Construye y explica el receptor con **Cloudflare Quick Tunnel** como recorrido principal. ngrok queda como alternativa, no como segundo requisito. Registra los casos de prueba esperados y observados, diferenciando local, proxy local y HTTPS.

| Evidencia | Qué debe mostrar |
| --- | --- |
| A | Webhook local abierto: respuesta y explicación del riesgo |
| B | Header Auth configurado (oculta el secreto) |
| C | Postman por HTTPS: token ausente e incorrecto rechazados, token válido aceptado |
| D | Ejecución válida: datos preparados y hora, sin cabeceras privadas |
| E | Editor y ruta de prueba bloqueados por el proxy |
| F | Export JSON sin secretos y comparación breve de ngrok y Cloudflare |

En la comparación incluye requisitos, persistencia de URL y límites; indica cuál probaste realmente y cuál consultaste en documentación. No inventes resultados. Verifica que tu export no tenga credenciales ni datos fijados que revelen el token. Las ejecuciones o inspectores de tráfico pueden almacenar cabeceras; no compartas capturas de esa entrada ni exportaciones de ejecución sin revisarlas.

### Al terminar

1. Detén el agente del túnel con Ctrl+C en su terminal y confirma que la dirección pública dejó de reenviar tráfico. Si sigue apareciendo un contenedor del servicio, identifícalo con `docker compose ps -a` y detenlo.
2. Despublica el workflow de laboratorio, elimina ejecuciones de prueba que contengan cabeceras y cambia o elimina el token de la credencial.
3. Si configuraste `URL_PUBLICA`, vuelve al valor local en `.env` y ejecuta `docker compose up -d --force-recreate n8n proxy`.
4. Para detener el laboratorio: `docker compose down`. **No agregues `-v` si quieres conservar tus workflows y credenciales.**

## 11. Comprueba lo que entendiste

- ¿Por qué un servicio remoto no puede usar tu localhost?
- ¿HTTPS reemplaza a Header Auth?
- ¿Qué diferencia hay entre el authtoken de ngrok y el token del webhook?
- ¿Qué confirma un HTTP 200 y qué no confirma?
- ¿Por qué el túnel se dirige al 8092 y no al editor de n8n?
- ¿Qué control faltaría si un emisor repitiera un evento con consecuencias reales?

## 12. Descargas y documentación

Guarda `compose.yaml` y `nginx.conf` juntos. Los otros archivos sirven para importar el workflow, probar en Postman y configurar opcionalmente la dirección pública. Todos los datos son ficticios; ninguna descarga contiene un token real. El workflow se entrega semicompletado para observar la diferencia entre una entrada abierta y una protegida; no lo publiques por Internet sin completar la autenticación.

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/compose.yaml" download="compose.yaml">Docker Compose — instancia aislada</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/nginx.conf" download="nginx.conf">Configuración del proxy — solo webhook autorizado</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/env.example" download=".env.example">Variables de entorno de ejemplo</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/biblioteca-webhook-semicompletado.json" download="biblioteca-webhook-semicompletado.json">Workflow semicompletado para n8n</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/biblioteca-webhooks.postman_collection.json" download="biblioteca-webhooks.postman_collection.json">Colección de Postman con pruebas</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/evento-biblioteca.json" download="evento-biblioteca.json">Evento ficticio de ejemplo</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/README.md" download="README.md">Resumen de instalación y pruebas</a></p>

Documentación técnica:

- [Webhook de n8n](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [Respond to Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/)
- [Configurar URL de webhook detrás de un proxy](https://docs.n8n.io/hosting/configuration/configuration-examples/webhook-url/)
- [Primeros pasos con ngrok](https://ngrok.com/docs/start)
- [Cloudflare Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)

**Estado de validación:** revisión documental y estática. Las tablas muestran resultados esperados y el diagrama es conceptual. Faltan pruebas reales de Docker, Postman y Quick Tunnel, capturas completas sin secretos, validación visual del visor y registro de versión del agente.
