# Biblioteca: manejo de errores en n8n

Paquete para reproducir el ejemplo del apunte «Cómo manejar errores y leer ejecuciones en n8n».
Una biblioteca ficticia consulta la disponibilidad de un libro en un catálogo que puede fallar. El workflow
reintenta, continúa con una contingencia o detiene la ejecución y registra el incidente.
Todos los títulos y datos son ficticios. No se necesitan credenciales ni servicios externos.

Probado con **n8n 2.44.6** y Docker Compose. En otras versiones los nombres de los botones pueden cambiar.

## Qué incluye

| Archivo | Para qué sirve |
| --- | --- |
| `compose.yaml` | Levanta n8n y el simulador del catálogo en la misma red de Docker. |
| `simulador_catalogo.py` | Servicio HTTP que responde 200 o 503 según el escenario. Usa solo la biblioteca estándar de Python. |
| `biblioteca-manejo-errores-principal.json` | Workflow **Biblioteca \| Consulta resiliente del catálogo**. |
| `biblioteca-error-workflow.json` | Workflow **Biblioteca \| Registro de incidentes** (Error Workflow). |
| `datos-prueba/` | Un JSON de entrada por escenario. |
| `probar_escenarios.py` | Envía los cinco casos y compara con los resultados esperados. |

El simulador forma parte del paquete: arranca solo con `docker compose up`. No tienes que crearlo ni construirlo.

## Puesta en marcha

1. Abre una terminal en esta carpeta y ejecuta `docker compose up -d`.
   Si el puerto 5678 ya está ocupado, usa otro: `N8N_PUERTO=5679 docker compose up -d`.
2. Abre n8n en `http://localhost:5678` y crea tu cuenta local la primera vez.
3. En **Workflows** crea un workflow vacío, abre el menú `...`, elige **Import > From file** y selecciona
   `biblioteca-manejo-errores-principal.json`. Guarda con `Ctrl+S`. Repite con `biblioteca-error-workflow.json`.
4. Abre **Biblioteca | Registro de incidentes**, pulsa **Publish**, escribe un nombre de versión y confirma.
   El manejador debe estar publicado para aparecer en la lista del paso siguiente.
5. Abre **Biblioteca | Consulta resiliente del catálogo**. En el menú `...` elige **Settings**, en
   **Error Workflow** selecciona **Biblioteca | Registro de incidentes** y pulsa **Save**.
6. Pulsa **Publish** en el workflow principal.
7. Prueba los escenarios con el script:
   `python3 probar_escenarios.py http://localhost:5678/webhook/consulta-disponibilidad http://localhost:8081`

El webhook de producción es el que muestra el nodo **Recibir consulta** en la pestaña **Production URL**.
La **Test URL** solo funciona mientras el editor escucha un evento y no dispara el Error Workflow.

## Resultados esperados

| Caso | Entrada | Respuesta del webhook | Peticiones que recibe el simulador |
| --- | --- | --- | --- |
| `01-exito.json` | exito | 200, `estado: confirmado`, `disponibles: 3` | 200 |
| `02-temporal.json` | temporal | 200, `confirmado`, `disponibles: 6` | 503, 200 |
| `03-caida-opcional.json` | caida, opcional | 200, `estado: degradado`, `disponibles: null` | 503, 503, 503 |
| `04-caida-obligatoria.json` | caida, obligatoria | 503, `estado: error`. La ejecución queda fallida y el manejador registra el incidente | 503, 503, 503 |
| `05-sin-stock.json` | sin_stock | 200, `confirmado`, `disponibles: 0` | 200 |

Para revisar a mano un caso: `curl -X POST URL -H "Content-Type: application/json" -d @datos-prueba/01-exito.json`.
Las peticiones recibidas por el simulador se leen en `http://localhost:8081/intentos?solicitud_id=LIB-201`
y todas en `http://localhost:8081/registro`. `http://localhost:8081/reiniciar` borra los contadores.

El escenario `temporal` falla en las peticiones impares de cada solicitud. Si repites el mismo `solicitud_id`
sin reiniciar el simulador, la secuencia sigue alternando: usa otro identificador o reinicia.

## Si ya tienes n8n instalado

El nodo **Consultar catálogo** llama a `http://catalogo:8080/disponibilidad`. Ese nombre solo existe dentro de la red
del `compose.yaml` de este paquete. Elige una de estas opciones:

1. **Usar el compose del paquete** (recomendado). Es lo que describe la puesta en marcha.
2. **Conectar el simulador a la red de tu n8n.** Levanta solo el simulador con `docker compose up -d catalogo` y
   ejecuta `docker network connect --alias catalogo NOMBRE_DE_LA_RED NOMBRE_DEL_CONTENEDOR_DEL_SIMULADOR`.
   Averigua los nombres con `docker network ls` y `docker ps`. No cambias nada en el workflow.
3. **Ejecutar el simulador fuera de Docker** con `python3 simulador_catalogo.py` (escucha en el puerto 8080;
   usa `PUERTO=8081` para cambiarlo). Entonces cambia la URL del nodo **Consultar catálogo**:
   si tu n8n está instalado sin Docker, `http://localhost:8081/disponibilidad`; si tu n8n está en Docker, usa
   `http://host.docker.internal:8081/disponibilidad`. En Linux ese nombre solo existe si agregas
   `extra_hosts: ["host.docker.internal:host-gateway"]` al servicio de n8n y tu cortafuegos permite la conexión.
   En un equipo de prueba con Linux el nombre se resolvió, pero el cortafuegos bloqueó la conexión, así que prefiere
   las opciones 1 y 2.

`localhost` dentro de un contenedor apunta al propio contenedor, no a tu computador.

## Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
| --- | --- | --- |
| `404 The requested webhook "POST consulta-disponibilidad" is not registered` | El workflow principal no está publicado o usaste la Test URL. | Publica el workflow y usa la Production URL. Si acabas de publicar, espera unos segundos. |
| El manejador aparece en gris en la lista de **Error Workflow** | No está publicado. | Publica **Registro de incidentes** y vuelve a abrir **Settings**. |
| No aparece ninguna ejecución del manejador | El vínculo no se guardó, o ejecutaste el flujo a mano desde el editor. | Revisa **Settings** del principal y prueba por la Production URL. |
| `ECONNREFUSED` o `ENOTFOUND` en **Consultar catálogo** | n8n no encuentra el simulador. | Revisa la URL del nodo y la sección anterior. |
| `probar_escenarios.py` marca `FALLA` en `temporal` | El simulador ya había recibido peticiones con ese identificador. | El script reinicia el simulador al empezar. Si lo ejecutas dos veces seguidas, reinicia a mano con `/reiniciar`. |
| El puerto ya está ocupado | Otro servicio usa el 5678 o el 8081. | Define `N8N_PUERTO` y `CATALOGO_PUERTO` al ejecutar `docker compose up -d`. |

## Limpieza

`docker compose down -v` detiene los contenedores y borra la red y los datos de n8n creados por este paquete.
