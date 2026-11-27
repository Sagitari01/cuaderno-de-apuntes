# Webhooks seguros en n8n: túneles HTTPS y eventos externos

Una persona devuelve un libro en una sucursal. El sistema que registra la devolución necesita avisar a la biblioteca central. ¿Cómo puede hacerlo si nuestro n8n vive dentro de Docker y solo se abre con `localhost`? ¿Qué impediría que alguien que conozca la dirección envíe una devolución falsa?

En este laboratorio usaremos un evento de biblioteca ficticia y un webhook protegido con una cabecera secreta. Simularemos el sistema emisor con **Postman o PowerShell**: ambos envían la misma solicitud HTTP y permiten comprobar la misma respuesta. El túnel nos permitirá recibir el evento por HTTPS sin abrir manualmente puertos del router. **Primero protegemos el webhook y después lo exponemos.**

### ¿Para qué hacemos este laboratorio?

Hasta ahora, cuando n8n consultaba una API mediante HTTP Request, n8n iniciaba la comunicación. Con un webhook invertimos el papel: otra aplicación avisa a n8n cuando ocurre algo y el workflow comienza a trabajar. Esto permite automatizaciones dirigidas por eventos en lugar de consultar continuamente si hay novedades.

Por ejemplo, una tienda podría avisar que recibió un pedido; un sistema de soporte, que abrió un ticket; un servicio de reservas, que cambió una cita. El receptor podría validar datos, clasificar un mensaje, actualizar un registro o enviar una notificación. En esta práctica nos concentramos en el punto de entrada y la confirmación de la recepción; esos procesos de negocio adicionales no están implementados.

Al trabajar con n8n local aparece una dificultad: una URL como `http://localhost:5682` solo identifica el equipo desde el que se usa. Una aplicación remota no puede encontrar nuestro n8n con esa dirección. El túnel resuelve ese problema de conectividad. Pero publicar un servicio también amplía su superficie de exposición: por eso limitamos el acceso con un proxy y comprobamos las credenciales antes de procesar un evento.

El resultado no es solo un enlace público. Es un receptor que demuestra cuándo aceptar o rechazar una solicitud, permite observar las ejecuciones y puede dejar de ser público sin detener el trabajo local.

## 1. Objetivos y conocimientos previos

- Diferenciar evento, endpoint, webhook y polling.
- Distinguir las URL de prueba y producción.
- Configurar Header Auth en un Webhook y demostrar los rechazos.
- Exponer solo el receptor mediante Cloudflare Quick Tunnel; comparar ngrok como alternativa.
- Revisar el código HTTP, los datos de la ejecución y las limitaciones del ejercicio.

Necesitas Docker Desktop o Docker con Compose, un navegador, acceso a Internet y permiso para usar un túnel. Para enviar solicitudes elige Postman Desktop (con la colección incluida) o PowerShell y curl.exe en Windows. No necesitas utilizar ambos clientes para aprender el concepto; si una actividad solicita específicamente Postman, utiliza ese recorrido para su evidencia. No necesitas una API de IA, Google Drive, una tarjeta de crédito ni una base de datos para este ejercicio. Repasa [APIs y webhooks en n8n](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-api-webhook) y [Credenciales y autenticación](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-credenciales-autenticacion).

## 2. El problema: un sistema externo no conoce tu localhost

| Concepto | En esta biblioteca |
| --- | --- |
| Evento | `libro.devuelto`, un hecho ocurrido en una sucursal |
| Emisor | Sistema de la sucursal; aquí lo simulamos con Postman o PowerShell |
| Endpoint | Una dirección y método, por ejemplo `POST /webhook/biblioteca-evento-protegido` |
| Webhook | Entrada que inicia el workflow al recibir una solicitud válida |
| Polling | n8n consulta periódicamente si hay novedades, aunque no las haya |
| Túnel | Reenvía las solicitudes desde una URL pública hacia un servicio local |
| HTTPS | Protege el transporte público; no prueba por sí mismo la identidad del emisor |
| Header Auth | Exige una cabecera con un valor secreto antes de iniciar el workflow |

En otra máquina, `localhost` designa esa otra máquina. Un túnel resuelve la conectividad; la credencial resuelve una parte del control de acceso. Son problemas distintos.

### 2.1 Qué aporta cada herramienta

| Herramienta | Propósito | Qué no resuelve por sí sola |
| --- | --- | --- |
| Docker Compose | Levanta los servicios y sus redes con una configuración reproducible | No autentica las solicitudes |
| n8n | Recibe el evento, prepara sus datos y responde | No vuelve público localhost automáticamente |
| Postman | Permite construir, inspeccionar y repetir peticiones HTTP mediante una interfaz gráfica | No es el servidor ni el túnel |
| PowerShell / curl.exe | Permite realizar las mismas peticiones desde terminal y observar los códigos | No reemplaza las validaciones del servidor |
| Nginx | Actúa como intermediario y admite solo el método y la ruta autorizados | No sustituye Header Auth |
| Cloudflare Quick Tunnel | Genera una dirección HTTPS temporal y reenvía las solicitudes al proxy local | No decide si el emisor posee el token correcto |

### 2.2 Cómo viaja la solicitud

1. El emisor envía un POST con un cuerpo JSON y, una vez configurada la protección, la cabecera `X-Biblioteca-Token`.
2. Cloudflare recibe la solicitud HTTPS y el agente cloudflared la reenvía por su conexión de salida al proxy.
3. Nginx comprueba si el método y la ruta coinciden con los permitidos. Bloquea el editor y las demás rutas.
4. n8n comprueba la cabecera antes de iniciar el workflow. Si la credencial coincide, prepara los datos y responde.
5. La respuesta recorre el camino inverso hasta el emisor.

La conexión pública usa HTTPS; en las redes locales de Docker, el laboratorio utiliza HTTP. HTTPS cifra el transporte público, pero no convierte un webhook abierto en uno autenticado. El token demuestra posesión de un secreto compartido; no identifica necesariamente a una persona ni firma el contenido del evento.

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/diagramas/n8n-webhooks-tuneles/arquitectura-webhook.svg" style="display:block;width:100%;height:auto" alt="Cliente HTTP, túnel HTTPS, proxy local, webhook de n8n y editor separado" loading="lazy"><figcaption>Esquema conceptual del laboratorio. El túnel apunta al proxy, no directamente a la instancia de n8n.</figcaption></figure>

**Decisión de seguridad:** si un túnel se dirige a todo n8n, también podría hacer accesibles el editor, las API administrativas y otros webhooks. Usaremos un pequeño proxy Nginx que admite únicamente el método POST en la ruta de producción de este ejercicio. Es un ejemplo local de mínimo privilegio, no una configuración de producción auditada.

### 2.3 Preparación desde un equipo Windows

Si ya tienes Docker funcionando, pasa directamente a la sección 3. En un equipo Windows compatible, comprueba WSL y los requisitos de [Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/). Usa una cuenta con permisos de instalación y una red autorizada para el laboratorio.

Abre PowerShell como administrador y ejecuta:

```powershell
wsl --install --no-distribution
```

Reinicia Windows si la instalación lo solicita. No necesitas instalar una distribución Ubuntu por separado para utilizar el backend WSL de Docker Desktop.



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/01-wsl-instalado.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Instalación de WSL completada; Windows solicita reiniciar para aplicar los cambios."><figcaption>Figura 1. Instalación de WSL completada; Windows solicita reiniciar para aplicar los cambios. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/01-wsl-instalado.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

Después del reinicio, comprueba la versión:

```powershell
wsl --version
wsl --status
```



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/02-wsl-version.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Verificación posterior al reinicio: WSL 3.0.5.0 y versión predeterminada 2."><figcaption>Figura 2. Verificación posterior al reinicio: WSL 3.0.5.0 y versión predeterminada 2. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/02-wsl-version.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

Instala Docker Desktop siguiendo la documentación oficial. En la pantalla de configuración de la versión utilizada en esta prueba se seleccionó la instalación por usuario y WSL 2; las opciones pueden variar según la versión del instalador.



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/03-docker-instalador.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Configuración del instalador de Docker Desktop: instalación por usuario y WSL 2."><figcaption>Figura 3. Configuración del instalador de Docker Desktop: instalación por usuario y WSL 2. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/03-docker-instalador.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

Abre Docker Desktop y comprueba el estado del motor.



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/04-docker-motor.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Docker Desktop iniciado; Engine running confirma que el motor está disponible."><figcaption>Figura 4. Docker Desktop iniciado; Engine running confirma que el motor está disponible. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/04-docker-motor.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

En una nueva terminal, valida Docker y Compose:

```powershell
docker --version
docker compose version
docker run --rm hello-world
```



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/05-docker-hello-world.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Comprobación de Docker y Compose; hello-world se descarga y se ejecuta correctamente."><figcaption>Figura 5. Comprobación de Docker y Compose; hello-world se descarga y se ejecuta correctamente. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/05-docker-hello-world.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

El mensaje Hello from Docker confirma que el motor puede descargar y ejecutar un contenedor. Si falla, revisa los requisitos del equipo y los permisos antes de continuar.

**Sobre las imágenes:** las capturas de esta guía proceden de la ejecución real del laboratorio. Se han recortado o cubierto datos personales, credenciales y detalles de conexión cuando fue necesario. Conservan su resolución disponible; los elementos cubiertos no representan comandos que debas introducir. Postman dispone de instrucciones escritas y su propia colección descargable.

## 3. Prepara Docker sin modificar tus otros laboratorios

Descarga los archivos al final de esta guía y guárdalos juntos en una carpeta nueva `biblioteca-webhooks`. La instancia es independiente de las prácticas anteriores: usa n8n 2.44.6, un volumen propio y otros puertos.



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/06-archivos-laboratorio.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Archivos descargados del laboratorio: Compose, proxy, workflow, colección y evento de ejemplo."><figcaption>Figura 6. Archivos descargados del laboratorio: Compose, proxy, workflow, colección y evento de ejemplo. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/06-archivos-laboratorio.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

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



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/07-contenedores.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Docker Compose crea redes y volumen; n8n y Nginx quedan en ejecución, sin el túnel."><figcaption>Figura 7. Docker Compose crea redes y volumen; n8n y Nginx quedan en ejecución, sin el túnel. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/07-contenedores.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

Importa `biblioteca-webhook-semicompletado.json` desde el menú de tres puntos de un workflow nuevo, y guarda. El workflow contiene:

| Nodo | Responsabilidad |
| --- | --- |
| Recibir evento (Webhook) | Recibe el POST; al principio la autenticación está desactivada para observar el problema |
| Preparar evento (Edit Fields) | Extrae evento, id_evento, título, sucursal y hora |
| Confirmar recepción (Respond to Webhook) | Devuelve solo esos datos como JSON con código 200 |



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/08-workflow-importado.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Workflow importado con tres nodos funcionales y tres notas adhesivas."><figcaption>Figura 8. Workflow importado con tres nodos funcionales y tres notas adhesivas. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/08-workflow-importado.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

Este laboratorio prepara información en memoria de la ejecución. **No guarda préstamos ni modifica un catálogo.** Las tres notas adhesivas explican la entrada, el tratamiento y la respuesta.

## 3.1 Elige tu cliente HTTP

La configuración de n8n, Nginx y Cloudflare es la misma en ambos caminos. Solo cambia cómo construimos y enviamos las peticiones.

### Camino A — Postman

1. Instala [Postman Desktop](https://www.postman.com/downloads/) y ábrelo. Utiliza la aplicación de escritorio para poder llamar a localhost.
2. En un workspace, pulsa **Import** y selecciona `biblioteca-webhooks.postman_collection.json` desde la carpeta del laboratorio.
3. En **Collections**, abre **Biblioteca | Webhooks y túneles HTTPS**. Selecciona la colección y entra en **Variables**.
4. En `baseUrl` deja `http://localhost:5682`, sin barra al final. Mantén `tokenBiblioteca` vacío hasta crear la credencial. Guarda los cambios. Utiliza el valor local de la variable y evita compartir o sincronizar el token.
5. Abre una solicitud. Observa su método, URL, pestaña **Headers** y **Body > raw > JSON**. La colección ya prepara los datos ficticios. Pulsa **Send** para enviar una solicitud; inspecciona el código de estado, **Body** y **Test Results** (el nombre de esta vista puede variar según la versión).

Las expresiones `{{baseUrl}}` y `{{tokenBiblioteca}}` son variables de Postman. Al cambiar solo la base podemos repetir la misma prueba localmente, por Nginx y por HTTPS sin duplicar las solicitudes. Las pruebas automáticas verifican los resultados esperados; un rechazo esperado puede ser una prueba exitosa.

### Camino B — PowerShell y curl.exe

Abre PowerShell dentro de la carpeta que contiene `evento-biblioteca.json` y carga el cuerpo una sola vez:

```powershell
$body = Get-Content ".\evento-biblioteca.json" -Raw
$base = "http://localhost:5682"
```

`Invoke-RestMethod` envía las peticiones y convierte la respuesta JSON en propiedades legibles. `curl.exe` permite mostrar el código HTTP de forma compacta, incluso cuando el servidor rechaza la solicitud. Usamos el nombre `curl.exe` para llamar al ejecutable y no al alias de PowerShell.

## 4. Demostración local: antes de proteger

En el Webhook comprueba el método `POST`, el Path `biblioteca-evento-protegido`, `Authentication: None` y `Respond: Using 'Respond to Webhook' Node`.

| Tipo de URL | Dirección en esta práctica | Cuándo funciona |
| --- | --- | --- |
| Test | `http://localhost:5682/webhook-test/biblioteca-evento-protegido` | Tras pulsar Listen for test event; vuelve a escuchar si la prueba se consume o vence |
| Production | `http://localhost:5682/webhook/biblioteca-evento-protegido` | Después de publicar el workflow |

El cuerpo de la solicitud es el mismo en ambos clientes. La cabecera `Content-Type: application/json` indica al receptor cómo interpretar estos datos:

```json
{
  "evento": "libro.devuelto",
  "id_evento": "DEV-0001",
  "titulo": "El faro de papel",
  "sucursal": "Centro"
}
```

Pulsa **Listen for test event** en el nodo o **Execute** en el lienzo. Envía una sola solicitud mientras la escucha esté activa.

**Camino A — Postman:** abre la carpeta **1. Demostración abierta (solo local)** y ejecuta **Test URL — evento sin token** con Send. La URL es `{{baseUrl}}/webhook-test/biblioteca-evento-protegido`. Si repites la llamada, activa otra vez la escucha. La solicitud de producción abierta de esa carpeta es una demostración opcional: solo úsala en localhost, con el workflow publicado, antes de configurar la credencial.

**Camino B — PowerShell:**

```powershell
Invoke-RestMethod -Uri "$base/webhook-test/biblioteca-evento-protegido" -Method POST -ContentType "application/json" -Body $body
```

Observa la confirmación y el paso de datos por los tres nodos. Si recibes 404, activa la escucha y repite. La prueba no necesita publicar el workflow abierto.



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/09-test-url-404.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Una petición a la URL de prueba sin escucha activa devuelve 404: la ruta no está registrada."><figcaption>Figura 9. Una petición a la URL de prueba sin escucha activa devuelve 404: la ruta no está registrada. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/09-test-url-404.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/10-evento-local.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="La URL de prueba con escucha activa recibe el evento y devuelve la confirmación JSON."><figcaption>Figura 10. La URL de prueba con escucha activa recibe el evento y devuelve la confirmación JSON. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/10-evento-local.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

### 4.1 Qué estamos observando

El Webhook recibe el objeto en `$json.body`; por ejemplo, `{{ $json.body.titulo }}` recupera el título del libro. Edit Fields selecciona las propiedades que necesitamos y agrega la hora de recepción. Respond to Webhook devuelve un JSON con `recibido: true`. Un 200 indica que el flujo respondió correctamente, no que haya actualizado un inventario real.

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



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/11-header-auth.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Configuración real de la credencial Header Auth con X-Biblioteca-Token. El valor permanece oculto."><figcaption>Figura 11. Configuración real de la credencial Header Auth con X-Biblioteca-Token. El valor permanece oculto. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/11-header-auth.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

Guarda la credencial, comprueba que el nodo la tiene seleccionada y pulsa **Publish** para registrar la ruta de producción protegida. Si el flujo estaba escuchando una prueba, detén la escucha primero. Ahora haremos tres solicitudes iguales, cambiando únicamente la cabecera de autenticación:

| Caso | Cabecera | Resultado esperado |
| --- | --- | --- |
| Sin token | No enviar `X-Biblioteca-Token` | Rechazo 403 en la versión de referencia; 401 en otras versiones |
| Incorrecto | `X-Biblioteca-Token: valor-incorrecto-demo` | Rechazo 403 o 401 |
| Correcto | `X-Biblioteca-Token: TU_TOKEN_PRIVADO` | 200 y una ejecución del flujo |

El valor `TU_TOKEN_PRIVADO` es un marcador, no una clave. Los rechazos deben ocurrir **antes** de los nodos de tratamiento. Comprueba el número de ejecuciones, no solo el código HTTP.

**Camino A — Postman:** vuelve a **Variables** de la colección y configura el valor local de `tokenBiblioteca` con el mismo token que guardaste en n8n. Conserva `baseUrl=http://localhost:5682`. Ejecuta en orden las tres solicitudes de **2. Receptor protegido**. Observa que las dos primeras son rechazadas y la tercera devuelve la confirmación JSON. También puedes usar **Run folder** para ejecutar únicamente esa carpeta y consultar sus pruebas.

**Camino B — PowerShell:** carga tu token una sola vez. Ejecuta los dos rechazos y la petición válida:

```powershell
$token = [System.Net.NetworkCredential]::new("", (Read-Host "Token del laboratorio" -AsSecureString)).Password
$base = "http://localhost:5682"

curl.exe -sS -o NUL -w "Sin token: %{http_code}\n" -X POST "$base/webhook/biblioteca-evento-protegido"
curl.exe -sS -o NUL -w "Token incorrecto: %{http_code}\n" -X POST "$base/webhook/biblioteca-evento-protegido" -H "X-Biblioteca-Token: incorrecto"

Invoke-RestMethod -Uri "$base/webhook/biblioteca-evento-protegido" -Method POST -ContentType "application/json" -Headers @{"X-Biblioteca-Token"=$token} -Body $body
```

Las peticiones de rechazo de este bloque omiten el cuerpo porque Header Auth debe bloquearlas antes de procesarlo. En Postman se mantiene el mismo cuerpo JSON para los tres casos. No utilices la cabecera válida en las solicitudes negativas.

En n8n 2.44.6 el material de referencia de la práctica documenta 403 para Header Auth ausente o incorrecto. La colección admite 401 o 403 porque la implementación puede cambiar entre versiones. Un rechazo de Header Auth no equivale necesariamente a un scope insuficiente de OAuth.



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/12-rechazo-sin-token.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="La URL de producción local rechaza una solicitud sin token con HTTP 403."><figcaption>Figura 12. La URL de producción local rechaza una solicitud sin token con HTTP 403. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/12-rechazo-sin-token.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/13-rechazo-token-incorrecto.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="La misma ruta rechaza una solicitud con token incorrecto, HTTP 403."><figcaption>Figura 13. La misma ruta rechaza una solicitud con token incorrecto, HTTP 403. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/13-rechazo-token-incorrecto.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/14-token-valido.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="La URL de producción local acepta el token correcto y devuelve los datos del evento."><figcaption>Figura 14. La URL de producción local acepta el token correcto y devuelve los datos del evento. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/14-token-valido.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

## 6. Verifica la frontera antes de abrir el túnel

El puerto 5682 es la entrada local a n8n. El 8092 es el punto de entrada del proxy. Antes de utilizar Cloudflare, debemos demostrar que Nginx reenvía únicamente la solicitud permitida y que la autenticación de n8n sigue funcionando.

**Camino A — Postman:** cambia `baseUrl` a `http://localhost:8092`, guarda la variable y ejecuta la carpeta 2 y después la carpeta 3. No ejecutes toda la colección de una vez: la carpeta 1 corresponde al webhook todavía abierto.

**Camino B — PowerShell:** cambia `$base = "http://localhost:8092"` y repite el bloque de la sección 5 desde la misma terminal (sin restablecer la variable a 5682). Luego ejecuta:

```powershell
curl.exe -sS -o NUL -w "Editor: %{http_code}\n" "$base/"
curl.exe -sS -o NUL -w "Ruta de prueba: %{http_code}\n" -X POST "$base/webhook-test/biblioteca-evento-protegido"
curl.exe -sS -o NUL -w "Otro webhook: %{http_code}\n" -X POST "$base/webhook/no-publicar"
curl.exe -sS -o NUL -w "Metodo GET: %{http_code}\n" "$base/webhook/biblioteca-evento-protegido"
```

La raíz del proxy debe devolver 404, mientras que el editor continúa disponible en localhost:5682. Obtén los resultados de esta tabla antes de abrir el túnel:

| Solicitud al proxy local | Resultado esperado |
| --- | --- |
| GET `/` | 404, el editor no está expuesto |
| POST `/webhook-test/biblioteca-evento-protegido` | 404, ruta de prueba bloqueada |
| POST `/webhook/no-publicar` | 404, otras rutas bloqueadas |
| GET `/webhook/biblioteca-evento-protegido` | 405, método no permitido |

**No continúes si el editor carga por el puerto 8092 o si una llamada sin token obtiene 200.** Revisa primero la credencial, la publicación y el archivo `nginx.conf`. No apuntes el túnel al puerto 5682 ni al 5678.



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/15-proxy-evento.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="El proxy local, puerto 8092, reenvía la solicitud autorizada a n8n y devuelve la confirmación."><figcaption>Figura 15. El proxy local, puerto 8092, reenvía la solicitud autorizada a n8n y devuelve la confirmación. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/15-proxy-evento.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/16-proxy-editor-bloqueado.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Al abrir la raíz del proxy en el navegador, Nginx responde 404; no se accede al editor."><figcaption>Figura 16. Al abrir la raíz del proxy en el navegador, Nginx responde 404; no se accede al editor. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/16-proxy-editor-bloqueado.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/17-proxy-rechazos.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Controles del proxy local: 403 para token incorrecto, 404 para rutas no permitidas y 405 para GET."><figcaption>Figura 17. Controles del proxy local: 403 para token incorrecto, 404 para rutas no permitidas y 405 para GET. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/17-proxy-rechazos.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

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

En la prueba real del 27/11/2026 la imagen `latest` ejecutó cloudflared **2026.11.2**. Para repetir en otro equipo, consulta la versión con `docker compose run --rm --no-deps tunnel --version`. El tag `latest` puede cambiar; queda pendiente verificar y fijar un tag o digest inmutable del agente. n8n mantiene su versión fija 2.44.6.

Si no conecta, revisa los logs y los permisos de red. No desactives controles corporativos ni intentes eludir restricciones. Si la red bloquea los túneles, completa la parte local y deja la prueba pública pendiente.



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/18-quick-tunnel.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Inicio real de Cloudflare Quick Tunnel desde Docker; versión 2026.11.2 y comprobaciones de conectividad PASS. La URL temporal y datos de conexión están ocultos."><figcaption>Figura 18. Inicio real de Cloudflare Quick Tunnel desde Docker; versión 2026.11.2 y comprobaciones de conectividad PASS. La URL temporal y datos de conexión están ocultos. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/18-quick-tunnel.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

### 7.2 Alternativa: cloudflared instalado en el equipo

Si ya tienes cloudflared desde [las descargas oficiales](https://developers.cloudflare.com/tunnel/downloads/), también puedes usar PowerShell:

```powershell
cloudflared tunnel --url http://localhost:8092
```

Elige un solo método. Copia la URL HTTPS generada y mantenla privada. No actives la autenticación interactiva por correo: esta prueba usa un cliente HTTP y Header Auth. El hostname cambia al iniciar otro Quick Tunnel.

### 7.3 ngrok — referencia opcional

ngrok requiere cuenta y authtoken privado. Si ya lo tienes configurado según [la documentación oficial](https://ngrok.com/docs/start), la alternativa es `ngrok http 8092`. Su authtoken no es `X-Biblioteca-Token`. No se exige implementar los dos proveedores.

## 8. Prueba el evento a través de Internet

Con el túnel en ejecución, el emisor ya no utiliza localhost. Conserva la misma ruta y el mismo token; solo cambia la dirección base. La URL completa tendrá esta forma ficticia:

`https://tu-dominio.example/webhook/biblioteca-evento-protegido`

**Camino A — Postman:** en las variables de la colección reemplaza `baseUrl` por la URL HTTPS generada, sin barra final. Guarda y ejecuta otra vez las carpetas 2 y 3. No ejecutes la carpeta 1 por Internet. Comprueba códigos, Body y Test Results.

**Camino B — PowerShell:** en la terminal donde guardaste el token y el cuerpo, reemplaza `$base` por la URL HTTPS generada. Repite las peticiones válidas y los rechazos de la sección 5, y los cuatro controles del proxy de la sección 6, sin volver a asignar la base local.

En ambos caminos abre **Executions** en el editor local para identificar una ejecución aceptada. El mismo endpoint recibe los datos sin importar qué cliente envió la petición. Si tienes autorización, puedes repetir el caso válido desde otro dispositivo o red usando solo datos ficticios.

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



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/19-https-evento.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Petición autorizada a través del túnel HTTPS: el mismo evento llega al workflow y devuelve su confirmación."><figcaption>Figura 19. Petición autorizada a través del túnel HTTPS: el mismo evento llega al workflow y devuelve su confirmación. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/19-https-evento.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/20-https-controles.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Pruebas por HTTPS: 403 sin token o con token incorrecto, 404 para rutas bloqueadas y 405 para método GET."><figcaption>Figura 20. Pruebas por HTTPS: 403 sin token o con token incorrecto, 404 para rutas bloqueadas y 405 para método GET. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/20-https-controles.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

### 8.1 Cómo hacer que n8n anuncie la URL pública

Para una prueba manual puedes construir la URL en Postman o PowerShell, sin recrear el contenedor. Cuando necesites que n8n muestre la base pública en la interfaz, copia `env.example` como `.env` en la misma carpeta y configura `URL_PUBLICA=https://tu-dominio.example/` con tu dirección real. El `compose.yaml` ya la pasa a `N8N_WEBHOOK_URL`, conserva el editor local mediante `N8N_EDITOR_BASE_URL` y configura `N8N_PROXY_HOPS` para el proxy inmediato.

```powershell
docker compose config --quiet
docker compose up -d --force-recreate n8n proxy
```

El volumen persistente conserva la configuración de la instancia. Verifica que el webhook siga publicado y protegido, y repite las pruebas del proxy y del túnel. No utilices la Test URL anunciada por el editor desde Internet: el proxy deliberadamente la bloquea.

**Nota:** para una integración real, configura correctamente la cadena de proxies y cabeceras de reenvío según la arquitectura del proveedor. En este ejemplo no tomamos decisiones de seguridad a partir de la IP del cliente o de cabeceras de reenvío; usamos Header Auth y una ruta permitida explícitamente.

### 8.2 Cómo interpretar los resultados de Postman o PowerShell

| Situación | Respuesta esperada | Qué demuestra |
| --- | --- | --- |
| Token correcto y POST permitido | 200 y JSON de confirmación | El evento llegó al workflow y se obtuvo su respuesta |
| Token ausente o incorrecto | 403 en n8n 2.44.6 | Header Auth impide el acceso |
| Raíz, URL de prueba u otro webhook a través del proxy | 404 | Nginx no publica esas rutas |
| GET en la ruta permitida | 405 | El proxy limita también el método HTTP |

No confundas el éxito de una prueba con un código 200: si esperas un 403 y recibes un 403, el control de seguridad superó la prueba. Una respuesta de error tampoco garantiza que un proceso posterior haya concluido; revisa siempre su ejecución.

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
| C | Postman o PowerShell por HTTPS: token ausente e incorrecto rechazados, token válido aceptado. Si la consigna exige Postman, utiliza esa herramienta para la evidencia. |
| D | Ejecución válida: datos preparados y hora, sin cabeceras privadas |
| E | Editor y ruta de prueba bloqueados por el proxy |
| F | Export JSON sin secretos y comparación breve de ngrok y Cloudflare |
| G | Túnel cerrado, acceso público no disponible y confirmación local todavía exitosa |

En la comparación incluye requisitos, persistencia de URL y límites; indica cuál probaste realmente y cuál consultaste en documentación. No inventes resultados. Verifica que tu export no tenga credenciales ni datos fijados que revelen el token. Las ejecuciones o inspectores de tráfico pueden almacenar cabeceras; no compartas capturas de esa entrada ni exportaciones de ejecución sin revisarlas.

### Al terminar

1. Pulsa Ctrl+C en la terminal del túnel y ejecuta `docker compose ps -a`. En la prueba real, Ctrl+C no bastó: el contenedor seguía Up y el endpoint devolvía 403 sin token. Si el contenedor `biblioteca-webhooks-tunnel-run-...` continúa en ejecución, ejecuta `docker stop NOMBRE_DEL_CONTENEDOR`, sustituyendo el marcador por el nombre mostrado. No detengas n8n ni Nginx. Repite `docker compose ps -a` y verifica la URL pública con `curl.exe -sS --max-time 15 -o NUL -w "HTTP: %{http_code}\n" -X POST "$base/webhook/biblioteca-evento-protegido"`. En la prueba se obtuvo 000 (sin respuesta HTTP), no un código HTTP real. Vuelve a probar con token válido por `http://localhost:8092` para comprobar continuidad local.
   En Postman también puedes repetir la solicitud **Token válido** de la carpeta 2 contra la antigua URL pública y observar que la conexión falla o el proveedor informa que no está disponible. Después cambia `baseUrl` a `http://localhost:8092` y repite la misma petición: debe devolver 200. Un 403 sin token, por sí solo, no prueba que el túnel se cerró.
2. Despublica el workflow de laboratorio, elimina ejecuciones de prueba que contengan cabeceras y cambia o elimina el token de la credencial.
3. Si configuraste `URL_PUBLICA`, vuelve al valor local en `.env` y ejecuta `docker compose up -d --force-recreate n8n proxy`.
4. Para detener el laboratorio: `docker compose down`. **No agregues `-v` si quieres conservar tus workflows y credenciales.**



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/21-tunel-aun-activo.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Comprobación del incidente de cierre: el contenedor de Cloudflare aún figuraba Up."><figcaption>Figura 21. Comprobación del incidente de cierre: el contenedor de Cloudflare aún figuraba Up. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/21-tunel-aun-activo.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/22-tunel-detenido.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Tras detener el contenedor del túnel, solo n8n y Nginx permanecen en ejecución."><figcaption>Figura 22. Tras detener el contenedor del túnel, solo n8n y Nginx permanecen en ejecución. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/22-tunel-detenido.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>



<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/23-cierre-continuidad.webp" style="display:block;max-width:100%;height:auto;margin:0 auto;border:1px solid #d4d9e1" loading="lazy" alt="Cierre comprobado: curl no recibe respuesta HTTP (000) por la URL pública; el proxy local continúa devolviendo el evento."><figcaption>Figura 23. Cierre comprobado: curl no recibe respuesta HTTP (000) por la URL pública; el proxy local continúa devolviendo el evento. <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-webhooks-tuneles/23-cierre-continuidad.webp" target="_blank" rel="noopener noreferrer">Ampliar captura</a></figcaption></figure>

## 11. Resultados de validación práctica

Prueba del **27/11/2026** en Windows 10 (compilación 19045), con WSL 3.0.5.0 (WSL 2 predeterminado), Docker Desktop 4.100.1, Docker Engine 29.9.3, Compose 5.7.1, n8n 2.44.6, Nginx 1.28-alpine y cloudflared 2026.11.2. El entorno se instaló desde cero. Registro de referencia obtenido con PowerShell y curl.exe. Los dos recorridos de la guía utilizan el mismo contrato HTTP.

| Prueba | Resultado observado |
| --- | --- |
| Docker hello-world e inicio de n8n y proxy | Correctos |
| Test URL sin escucha | 404 de n8n |
| Test URL con escucha, sin protección | Confirmación del evento con fecha y hora |
| Producción local sin token y token incorrecto | 403 en ambos casos |
| Producción local con token válido | Confirmación del evento |
| Proxy local: token válido | Confirmación del evento |
| Proxy local: sin token o token incorrecto | 403 en ambos casos |
| Proxy local: raíz, ruta de prueba y otro webhook | 404 en los tres casos |
| Proxy local: GET en el endpoint | 405 |
| Quick Tunnel por Docker | URL HTTPS generada; precomprobaciones DNS, UDP y TCP correctas |
| HTTPS: token válido | Confirmación del evento |
| HTTPS: sin token o token incorrecto | 403 en ambos casos |
| HTTPS: raíz, ruta de prueba y otro webhook | 404 en los tres casos |
| HTTPS: GET en el endpoint | 405 |
| Ctrl+C sin detener el contenedor | Contenedor seguía Up; petición sin token devolvió 403 |
| Tras detener el contenedor del túnel | Desapareció del listado; curl mostró 000, sin respuesta HTTP |
| Proxy local después del cierre | Confirmación del evento con token válido |

Las confirmaciones JSON se observaron en `Invoke-RestMethod`, que completó las solicitudes sin excepción. Los códigos 403, 404, 405 y 000 se observaron explícitamente. El 000 no es un código de estado HTTP. El alcance de este registro corresponde al recorrido de referencia; no es una garantía de funcionamiento en todas las redes o versiones de los clientes HTTP.

## 12. Comprueba lo que entendiste

- ¿Por qué un servicio remoto no puede usar tu localhost?
- ¿HTTPS reemplaza a Header Auth?
- ¿Cuándo resulta mejor recibir un evento mediante webhook en vez de hacer polling?
- ¿Por qué podemos repetir la misma petición con Postman y PowerShell?
- ¿Qué diferencia hay entre el authtoken de ngrok y el token del webhook?
- ¿Qué confirma un HTTP 200 y qué no confirma?
- ¿Por qué el túnel se dirige al 8092 y no al editor de n8n?
- ¿Qué control faltaría si un emisor repitiera un evento con consecuencias reales?

## 13. Descargas y documentación

Guarda `compose.yaml` y `nginx.conf` juntos. Los otros archivos sirven para importar el workflow, probar en Postman y configurar opcionalmente la dirección pública. Todos los datos son ficticios; ninguna descarga contiene un token real. El workflow se entrega semicompletado para observar la diferencia entre una entrada abierta y una protegida; no lo publiques por Internet sin completar la autenticación.

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/compose.yaml" download="compose.yaml">Docker Compose — instancia aislada</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/nginx.conf" download="nginx.conf">Configuración del proxy — solo webhook autorizado</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/env.example" download=".env.example">Variables de entorno de ejemplo</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/biblioteca-webhook-semicompletado.json" download="biblioteca-webhook-semicompletado.json">Workflow semicompletado para n8n</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/biblioteca-webhooks.postman_collection.json" download="biblioteca-webhooks.postman_collection.json">Colección de Postman con pruebas</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/evento-biblioteca.json" download="evento-biblioteca.json">Evento ficticio de ejemplo</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-webhooks-tuneles/README.md" download="README.md">Resumen de instalación y pruebas</a></p>

Documentación técnica:

- [Documentación de Postman](https://learning.postman.com/docs/)

- [Webhook de n8n](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [Respond to Webhook](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.respondtowebhook/)
- [Configurar URL de webhook detrás de un proxy](https://docs.n8n.io/hosting/configuration/configuration-examples/webhook-url/)
- [Primeros pasos con ngrok](https://ngrok.com/docs/start)
- [Cloudflare Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)

**Referencia de validación:** consulta los resultados observados en la sección 11. La colección Postman y los comandos de PowerShell permiten reproducir el contrato HTTP descrito. El diagrama es conceptual.
