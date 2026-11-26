# Paginación, procesamiento por lotes y clasificación con Groq en n8n

**Guía 17 · Semana 3 · 26 de noviembre de 2026**

Continuamos con la [Biblioteca de la guía de OAuth 2.0](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-oauth2-biblioteca). Hoy consultaremos su catálogo público mediante paginación y clasificaremos los títulos con Groq. No instalaremos otra instancia de n8n, ni agregaremos una base de datos o una hoja de cálculo.

**Objetivos:** comprender la paginación del lado del servidor, distinguir páginas de lotes, controlar la frecuencia de solicitudes, configurar reintentos y convertir texto generado por IA en datos JSON.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-17-workflow-completo-documentado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Vista final con las cinco notas adhesivas y ejecución correcta."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-17-workflow-completo-documentado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 17" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Vista final con las cinco notas adhesivas y ejecución correcta.</figcaption></figure>

## 1. Contexto: biblioteca inteligente

La biblioteca tiene seis libros ficticios. Si el catálogo creciera a miles de registros, recuperar todo en una sola respuesta podría aumentar el consumo de memoria, el tamaño de las respuestas y el tiempo de transferencia. La API puede ofrecer páginas pequeñas; n8n debe saber cómo solicitar la siguiente y cuándo detenerse.

La clasificación literaria será orientativa, pues solo conocemos el título y la cantidad de ejemplares. No disponemos de autor ni sinopsis. El resultado requerirá revisión humana.

| Libro | Ejemplares |
|---|---:|
| El faro de papel | 5 |
| Jardines de tinta | 4 |
| Atlas de las nubes verdes | 7 |
| La casa de los mapas | 3 |
| Viaje al bosque azul | 6 |
| Historias del reloj | 8 |

## 2. La API pagina; n8n consume las páginas

La responsabilidad del servidor es definir los parámetros, devolver una parte del conjunto e informar cómo continuar. La responsabilidad del cliente es interpretar ese contrato. No existe una configuración universal: cada API puede usar número de página, desplazamiento (`offset`), cursor o enlace a la siguiente página. Si la API no ofrece paginación, dividir los resultados en n8n es procesamiento local, no paginación real.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-01-catalogo-sin-paginacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Consulta pública original: el catálogo devuelve los seis libros juntos."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-01-catalogo-sin-paginacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 1" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Consulta pública original: el catálogo devuelve los seis libros juntos.</figcaption></figure>

Nuestro simulador original entregaba los seis libros juntos. Para esta guía añadimos soporte opcional para `pagina` y `limite`. Las rutas anteriores permanecen disponibles. Sin esos parámetros la respuesta mantiene su forma original.

## 3. Preparación del entorno existente

Reutiliza el paquete avanzado de la guía 16. Si aún no lo tienes, sigue primero esa guía. Abre PowerShell en la carpeta de `compose.yaml` y `simulador_catalogo_seguro.py`. Comprueba el catálogo en <http://localhost:8091/catalogo/publico>.

Descarga el actualizador al final del apunte y colócalo en la misma carpeta. No necesitas instalar Python en Windows: aprovecharemos el servicio de Docker.

```powershell
docker compose run --rm --no-deps -v "${PWD}:/trabajo" -w /trabajo catalogo python preparar_paginacion.py
docker compose restart catalogo
```

El script guarda el original como `simulador_catalogo_seguro.py.g17.bak`, verifica la sintaxis antes de escribir y no modifica versiones incompatibles. No elimines el volumen de n8n. Reiniciar el catálogo puede invalidar las autorizaciones OAuth que mantenía en memoria; vuelve a conectar las credenciales de la guía anterior si las necesitas.

Abre <http://localhost:8091/catalogo/publico?pagina=1&limite=2>. La respuesta debe contener los dos primeros títulos:

```json
{
  "acceso": "publico",
  "libros": [
    {"titulo": "El faro de papel", "ejemplares_totales": 5},
    {"titulo": "Jardines de tinta", "ejemplares_totales": 4}
  ],
  "pagina": 1,
  "limite": 2,
  "total": 6,
  "hay_mas": true
}
```

<figure class="lamina-apunte" style="position:relative;max-width:570px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-02-catalogo-con-paginacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Primera página: dos libros, total de seis y hay_mas en true."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-02-catalogo-con-paginacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 2" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Primera página: dos libros, total de seis y hay_mas en true.</figcaption></figure>

Comprueba también las páginas 2 y 3: la última tiene `hay_mas: false`. Una página contiene un arreglo de libros, no un libro por item.

## 4. El workflow

Importa el JSON descargable en un workflow vacío, selecciona tu credencial de Groq y guarda. Son cinco nodos principales y un subnodo de modelo.

**Inicio → Consultar catalogo → Separar libros → Clasificar con Groq → Resultado JSON**

Groq Chat Model se conecta al puerto Model de Basic LLM Chain. Las cinco notas adhesivas documentan cada etapa. No es necesario crear un agente.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-03-workflow-completo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Workflow importado: cinco nodos principales y Groq Chat Model como subnodo."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-03-workflow-completo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 3" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Workflow importado: cinco nodos principales y Groq Chat Model como subnodo.</figcaption></figure>

## 5. Consultar catalogo (HTTP Request)

| Campo | Valor |
|---|---|
| Method | GET |
| URL | `http://catalogo:8080/catalogo/publico` |
| Authentication | None (ruta pública) |
| Send Query Parameters | Activado |
| Name / Value | `limite` / `2` |
| Options → Pagination Mode | Update a Parameter in Each Request |
| Type / Name | Query / `pagina` |
| Value (Expression) | `{{ $pageCount + 1 }}` |
| Pagination Complete When | Other |
| Complete Expression | `{{ $response.body.hay_mas === false }}` |
| Limit Pages Fetched | Activado |
| Max Pages | 10 |
| Interval Between Requests | 500 ms |

Dentro de Docker n8n se comunica con el servicio por `catalogo:8080`; desde el navegador se utiliza `localhost:8091`. No confundas ambas direcciones.

<figure class="lamina-apunte" style="position:relative;max-width:570px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-04-configuracion-paginacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="n8n modifica el parámetro Query pagina con $pageCount + 1."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-04-configuracion-paginacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 4" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>n8n modifica el parámetro Query pagina con $pageCount + 1.</figcaption></figure>

`$pageCount` comienza en cero; sumamos uno porque nuestra API comienza en la página 1. La condición de término lee la respuesta de la API y detiene la consulta cuando no quedan registros.

| Solicitud | Página | Libros | hay_mas |
|---|---:|---:|---|
| 1 | 1 | 2 | true |
| 2 | 2 | 2 | true |
| 3 | 3 | 2 | false |

<figure class="lamina-apunte" style="position:relative;max-width:570px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-05-condicion-paginacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Condición de término, máximo de páginas e intervalo de 500 ms."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-05-condicion-paginacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 5" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Condición de término, máximo de páginas e intervalo de 500 ms.</figcaption></figure>

El límite de diez páginas es una protección adicional ante errores de la condición. Si el catálogo supera 20 libros, deberá ajustarse: alcanzar el límite no garantiza que se haya recuperado todo. La pausa de 500 ms reduce la frecuencia de solicitudes, pero no garantiza cumplir cualquier cuota.

**Ejecuta el nodo:** el resultado comprobado en clase fue de tres items, con seis libros en total.

<figure class="lamina-apunte" style="position:relative;max-width:570px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-06-resultado-paginacion.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Resultado real: tres items, dos libros por página; la última indica hay_mas false."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-06-resultado-paginacion.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 6" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Resultado real: tres items, dos libros por página; la última indica hay_mas false.</figcaption></figure>

## 6. Separar libros (Split Out)

Configura **Fields To Split Out** = `libros`, **Include** = No Other Fields y **Destination Field Name** = `libro`.

<figure class="lamina-apunte" style="position:relative;max-width:570px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-07-configuracion-split-out.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Split Out separa libros y utiliza libro como nombre del campo de salida."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-07-configuracion-split-out.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 7" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Split Out separa libros y utiliza libro como nombre del campo de salida.</figcaption></figure>

Pasamos de tres items con arreglos a seis items independientes, descartando los metadatos de paginación:

```json
{"libro":{"titulo":"El faro de papel","ejemplares_totales":5}}
```

Así podemos utilizar `{{ $json.libro.titulo }}` para acceder dinámicamente al título. Ejecuta el nodo y verifica seis items.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-08-resultado-split-out.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Entrada de tres páginas y salida de seis libros individuales."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-08-resultado-split-out.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 8" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Entrada de tres páginas y salida de seis libros individuales.</figcaption></figure>

## 7. Clasificar con Groq (Basic LLM Chain)

Conecta **Groq Chat Model**, selecciona tu credencial y utiliza `openai/gpt-oss-20b` con Sampling Temperature **0.0**. El modelo y la credencial deben estar disponibles en tu cuenta. Una temperatura baja favorece consistencia en tareas de clasificación; cero no garantiza resultados idénticos, correctos ni JSON válido.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-09-configuracion-groq.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Groq Chat Model con openai/gpt-oss-20b y temperatura 0.0; la clave no está visible."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-09-configuracion-groq.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 9" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Groq Chat Model con openai/gpt-oss-20b y temperatura 0.0; la clave no está visible.</figcaption></figure>

En Basic LLM Chain selecciona Define below como fuente del prompt. El workflow contiene este prompt (modo Expression):

```text
Eres un bibliotecario digital. Clasifica el titulo ficticio en Fantasía, Ciencia ficción, Aventura, Misterio, Historia, Poesía, Literatura general u Otro. No inventes autores ni sinopsis. Devuelve exclusivamente un objeto JSON válido, sin Markdown, con categoria (texto), justificacion (texto breve) y requiere_revision (booleano true). Libro: {{ JSON.stringify($json.libro ?? $json) }}
```

El rol, la tarea, las categorías permitidas, las restricciones y el formato de salida se expresan en el prompt. La expresión final aporta el objeto de cada libro. No inventamos autores ni sinopsis. Dejamos Require Specific Output Format desactivado en esta demostración, por lo que el JSON llegará como texto y se analizará en el siguiente nodo.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-10-configuracion-prompt.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Basic LLM Chain con el prompt en modo Expression y seis items de entrada."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-10-configuracion-prompt.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 10" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Basic LLM Chain con el prompt en modo Expression y seis items de entrada.</figcaption></figure>

### 7.1 Procesamiento por lotes

En **Batch Processing** configura Batch Size = 1 y Delay Between Batches = 2000 ms. Un lote de un item permite controlar cuántos libros se envían al modelo de una vez. Hay una pausa de dos segundos entre lotes, además del tiempo de procesamiento.

<figure class="lamina-apunte" style="position:relative;max-width:570px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-12-configuracion-batch-processing.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Batch Processing: un item por lote y 2000 ms de espera."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-12-configuracion-batch-processing.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 12" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Batch Processing: un item por lote y 2000 ms de espera.</figcaption></figure>

No confundas paginación con batching: la primera regula cómo obtenemos los datos; el segundo regula cómo los procesamos.

### 7.2 Rate limits y reintentos

Los proveedores pueden limitar las solicitudes o tokens por minuto y por día. HTTP 429 indica que se excedió un límite. Espaciar solicitudes ayuda a prevenirlo, pero las cuotas dependen del proveedor, modelo y cuenta; no es una garantía.

En Settings: Execute Once desactivado, Retry On Fail activado, Max. Tries = 3, Wait Between Tries = 5000 ms, On Error = Stop Workflow. Son tres intentos totales, incluido el inicial. El reintento puede repetir trabajo ya realizado; en flujos con escrituras hay que considerar idempotencia. Para producción, respeta Retry-After si existe y considera backoff progresivo, no reintentos indiscriminados de errores de autenticación o validación.

<figure class="lamina-apunte" style="position:relative;max-width:570px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-11-configuracion-reintentos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Retry On Fail activado, máximo de tres intentos y espera de 5000 ms."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-11-configuracion-reintentos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 11" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Retry On Fail activado, máximo de tres intentos y espera de 5000 ms.</figcaption></figure>

La espera fija de cinco segundos no es backoff exponencial. No provocamos un error 429 real en esta sesión: validamos la configuración de reintentos y la ejecución normal.

Ejecuta Basic LLM Chain. La evidencia de clase mostró seis respuestas, cada una dentro de un campo `text`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-13-resultado-clasificacion-groq.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Seis clasificaciones de Groq: cada respuesta llega como texto JSON."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-13-resultado-clasificacion-groq.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 13" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Seis clasificaciones de Groq: cada respuesta llega como texto JSON.</figcaption></figure>

## 8. Resultado JSON (Edit Fields)

Groq puede devolver un texto que contiene JSON, por ejemplo:

```json
{"text":"{\"categoria\":\"Literatura general\",\"justificacion\":\"El título no indica claramente un género específico.\",\"requiere_revision\":true}"}
```

Un texto con llaves no es todavía un objeto. Usamos `JSON.parse()` para interpretarlo, recuperamos los datos originales del nodo Separar libros mediante item linking y utilizamos `JSON.stringify()` para entregar el objeto al editor en modo JSON. Se retiran cercos Markdown si el modelo los añade.

Configura Mode = JSON, Include Other Input Fields desactivado y utiliza la expresión que viene en el recurso:

```javascript
{{ JSON.stringify({titulo: $('Separar libros').item.json.libro?.titulo ?? $('Separar libros').item.json.titulo, ejemplares_totales: $('Separar libros').item.json.libro?.ejemplares_totales ?? $('Separar libros').item.json.ejemplares_totales, categoria: JSON.parse($json.text.trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '')).categoria, justificacion: JSON.parse($json.text.trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '')).justificacion, requiere_revision: true}) }}
```

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-14-configuracion-resultado-json.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Edit Fields en modo JSON: combina los datos originales y la clasificación."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-14-configuracion-resultado-json.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 14" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Edit Fields en modo JSON: combina los datos originales y la clasificación.</figcaption></figure>

Conservamos el título y la cantidad original; no dependemos de que la IA los reproduzca. `requiere_revision` se fija a true deliberadamente por falta de información. Si el modelo devuelve JSON inválido, JSON.parse puede fallar; en un flujo de producción conviene validar el esquema y tratar el error.

Salida observada para el primer libro:

```json
{
  "titulo": "El faro de papel",
  "ejemplares_totales": 5,
  "categoria": "Literatura general",
  "justificacion": "El título no indica claramente un género específico.",
  "requiere_revision": true
}
```

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-15-resultado-json-final.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Salida real de seis objetos JSON; título, ejemplares, categoría, justificación y revisión."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-15-resultado-json-final.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 15" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Salida real de seis objetos JSON; título, ejemplares, categoría, justificación y revisión.</figcaption></figure>

## 9. Prueba integral

Guarda y ejecuta el workflow completo. En la sesión se comprobó: Inicio 1 item → HTTP Request 3 items → Split Out 6 items → Basic LLM Chain 6 items → Edit Fields 6 items. Los cinco nodos y el modelo finalizaron correctamente.

| Libro | Categoría observada |
|---|---|
| El faro de papel | Literatura general |
| Jardines de tinta | Poesía |
| Atlas de las nubes verdes | Fantasía |
| La casa de los mapas | Fantasía |
| Viaje al bosque azul | Fantasía |
| Historias del reloj | Literatura general |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-16-ejecucion-completa.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" alt="Prueba integral: todos los nodos completados, con seis libros clasificados."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-paginacion-groq/g17-16-ejecucion-completa.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar captura 16" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Prueba integral: todos los nodos completados, con seis libros clasificados.</figcaption></figure>

Estas categorías son propuestas, no géneros verificados. El flujo termina en n8n; no escribe en otro servicio.

## 10. Repaso

- ¿Quién implementa la paginación, la API o n8n?
- ¿Qué diferencia hay entre una página y un lote?
- ¿Por qué se usa un límite máximo de páginas?
- ¿Qué diferencia existe entre prevenir un exceso de solicitudes y reintentar un fallo?
- ¿Por qué una respuesta de IA con apariencia de JSON puede seguir siendo texto?
- ¿Por qué dejamos la revisión humana activa?

## 11. Recursos descargables

<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-paginacion-groq/biblioteca-paginacion-groq.json" download="biblioteca-paginacion-groq.json">Workflow de biblioteca con Groq y notas</a></p>
<p><a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/recursos/n8n-paginacion-groq/preparar_paginacion.py" download="preparar_paginacion.py">Actualizador del simulador</a></p>

El JSON no incluye referencias a credenciales privadas. Selecciona tu propia credencial al importarlo.
