<!-- secciones: desplegables -->
# Integraciones, APIs, JSON, rutas y calidad de datos

## Antes de comenzar

Imagina un centro comunitario que recibe inscripciones a talleres. El formulario recibe los datos, una aplicación comprueba si quedan cupos, otra guarda el registro y un correo confirma la inscripción. Si una persona tiene que copiar cada dato a mano, aparecen retrasos y errores.

El reto de hoy es comprender **cómo viajan los datos entre aplicaciones y cómo tomar decisiones seguras**. La secuencia será: conectar sistemas → pedir y recibir información → organizarla como JSON → aplicar rutas y filtros → revisar que sea válida → resolver problemas.

En estas páginas encontrarás las ideas fundamentales para comprender cómo se conectan aplicaciones, cómo se organizan los datos y cómo una automatización toma decisiones. Usaremos ejemplos cotidianos y ficticios para aprender paso a paso.

---

## 1. Integraciones y flujos de datos

### El problema de las aplicaciones separadas

Piensa en tres lugares donde podría existir una misma inscripción: un formulario, una hoja de cálculo y un calendario. Si no están conectados, alguien debe trasladar los datos de uno a otro; a esos espacios aislados se les suele llamar **silos de información**.

Una **integración** permite que distintas aplicaciones intercambien información mediante interfaces acordadas. Una **automatización** coordina los pasos para que, cuando ocurra un evento, los datos lleguen al siguiente sistema sin copiarlos manualmente.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/01-conexion-aplicaciones.webp" alt="Dibujo de una aplicación que comparte datos con otra." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/01-conexion-aplicaciones.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

**Ejemplo ficticio:** una persona completa un formulario → se consulta un calendario → se registra la reserva → se envía un mensaje de confirmación.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/api-ejemplo-formulario.webp" alt="Ejemplo visual de formulario que se conecta mediante una API para guardar un registro en una hoja de cálculo." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/api-ejemplo-formulario.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

### De dónde vienen los datos y adónde llegan

| Etapa | Pregunta útil | Ejemplo |
|---|---|---|
| **Origen o entrada** | ¿Dónde nace la información? | Formulario de inscripción. |
| **Transformación** | ¿Hay que ordenarla o adaptarla? | Convertir «Taller de pintura» en un campo `taller`. |
| **Decisión** | ¿Qué regla determina el siguiente paso? | ¿Quedan cupos? |
| **Destino o salida** | ¿Qué sistema recibe los datos? | Calendario y correo. |

Un orquestador como **Make** facilita conectar servicios mediante módulos visuales. No hace falta programar todo desde cero, pero sí hay que comprender **qué datos recibe cada módulo, qué devuelve y qué hacer cuando falla**.

> **Idea clave:** no-code elimina parte del código manual, **no** la necesidad de diseñar lógica y validar información.

---

## 2. APIs: la comunicación entre aplicaciones

### ¿Qué es una API?

Una **API** es una interfaz con reglas definidas para que un sistema solicite información o acciones a otro. No es necesariamente una base de datos: es la **forma acordada de comunicarse**.

**Analogía:** en un restaurante, tú haces un pedido según el menú y el personal te devuelve lo que pediste o te informa que no está disponible. En una API, el sistema cliente hace una **petición (request)** a un servicio y recibe una **respuesta (response)**.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/api-ciclo-peticion.webp" alt="Tres etapas de comunicación con una API: la aplicación envía la petición, el servicio la procesa y devuelve una respuesta." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/api-ciclo-peticion.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

**Ejemplo ficticio:** una automatización consulta a un servicio de bicicletas compartidas cuántas bicicletas quedan en una estación; después informa el resultado.

### Las cuatro piezas de una petición

1. **Método:** qué acción buscas. `GET` consulta; `POST` normalmente envía datos; `PUT` o `PATCH` actualizan; `DELETE` solicita eliminar.
2. **Endpoint:** dirección específica del recurso, por ejemplo `https://api.ejemplo.test/estaciones/12` (**dirección ficticia**, no un servicio real).
3. **Headers:** información adicional sobre la petición, como el tipo de contenido o la autorización.
4. **Body o payload:** datos enviados en el cuerpo, especialmente cuando se crea o modifica información.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/api-partes-url.webp" alt="Partes ilustradas de una dirección de API: protocolo HTTPS, servidor, recurso y un identificador." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/api-partes-url.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

| Petición | Interpretación cotidiana |
|---|---|
| `GET /estaciones/12` | «Dime qué hay en esta estación». |
| `POST /reservas` | «Crea esta reserva». |
| `PATCH /reservas/48` | «Actualiza algunos datos de la reserva 48». |
| `DELETE /reservas/48` | «Solicita eliminar la reserva 48». |

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/api-metodos.webp" alt="GET para consultar, POST para crear, PUT para actualizar y DELETE para solicitar una eliminación." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/api-metodos.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

No todos los servicios aceptan todos los métodos: **la documentación de la API define cuáles están disponibles y sus permisos**.

### Una respuesta también trae información importante

En las respuestas HTTP es frecuente encontrar un **código de estado**:

- **200:** la solicitud se procesó correctamente.
- **201:** normalmente se creó un recurso.
- **400:** la petición tiene algún problema.
- **401:** faltan credenciales válidas.
- **404:** el recurso solicitado no se encuentra.
- **500:** ocurrió un error del lado del servidor.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/api-codigos-http-ilustrado.webp" alt="Lámina de cuaderno ilustrada con ejemplos de respuestas HTTP 200, 201, 400, 401, 404 y 500 y dibujos de peticiones, registros, errores y servidor." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/api-codigos-http-ilustrado.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

Que una solicitud sea enviada no significa que el servicio la haya aceptado. Hay que revisar su respuesta.

### Polling frente a webhooks

- **Polling (consulta periódica):** la automatización pregunta cada cierto tiempo «¿hay novedades?». Es útil si el servicio no puede avisar por sí mismo, pero genera consultas incluso cuando no hay cambios.
- **Webhook (aviso por evento):** un sistema compatible envía datos a una dirección configurada **cuando ocurre un evento**. Puede reducir esperas y consultas innecesarias.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/api-polling-webhook.webp" alt="Comparación de polling, que pregunta periódicamente, con webhook, que avisa cuando ocurre un evento." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/api-polling-webhook.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

No basta con crear una URL para que cualquier servicio envíe eventos: **el sistema de origen debe admitir la integración o mecanismo de aviso**.

### Seguridad mínima

Las API keys y los tokens son como credenciales. Deben guardarse en conexiones o gestores de secretos, **no** pegarse en documentos públicos, capturas ni ejemplos compartidos. Las acciones disponibles dependen también de los permisos de cada cuenta.

---

## 3. JSON: organizar los datos para intercambiarlos

### El mismo dato, pero estructurado

Un texto suelto puede decir: «Andrea quiere reservar dos cupos para el taller de cerámica y necesita confirmación». Para una persona es comprensible; para una automatización es más fácil trabajar con campos definidos.

~~~json
{
  "nombre": "Andrea",
  "taller": "ceramica",
  "cupos": 2,
  "confirmado": false
}
~~~

**JSON** es un formato de texto para representar datos estructurados. Sus piezas principales son:

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/03-json-claves-valores.webp" alt="Objeto JSON y sus pares clave valor." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/03-json-claves-valores.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

- **Objeto `{}`:** agrupa pares de **clave: valor**.
- **Clave:** el nombre del dato, siempre entre comillas dobles.
- **Valor:** puede ser texto, número, booleano (`true` / `false`), `null`, arreglo u otro objeto.
- **Arreglo `[]`:** representa una lista de elementos.

### ¿Cómo reconocer los tipos?

| Valor JSON | Tipo | Uso posible |
|---|---|---|
| `"Andrea"` | Texto (string) | Nombre. |
| `2` | Número (number) | Cantidad de cupos. |
| `false` | Booleano | Aún no confirmado. |
| `null` | Nulo | Dato desconocido o ausente. |
| `["lunes", "viernes"]` | Lista (array) | Días disponibles. |

### Un JSON con datos anidados

~~~json
{
  "reserva": 48,
  "persona": {
    "nombre": "Andrea",
    "correo": "andrea@ejemplo.test"
  },
  "talleres": ["ceramica", "pintura"],
  "cupos": 2,
  "confirmado": false
}
~~~

Aquí, `persona` contiene **otro objeto**, y `talleres` contiene **una lista**. Esta estructura permite que una aplicación extraiga por separado `persona.correo` o `cupos`.

### Errores de sintaxis comunes

| Error | Por qué falla | Forma correcta |
|---|---|---|
| `{'nombre':'Andrea'}` | JSON exige comillas **dobles**. | `{"nombre":"Andrea"}` |
| `{"cupos":"2"}` | Es JSON válido, pero `"2"` es **texto**, no número. | `{"cupos":2}` |
| `{"confirmado":True}` | El booleano JSON va en minúsculas. | `{"confirmado":true}` |
| `{"cupos":2,}` | Sobra una coma final. | `{"cupos":2}` |

Cuando un sistema recibe **texto que contiene JSON**, puede necesitar analizarlo o **parsearlo** para acceder a cada campo. Validar la sintaxis no garantiza, por sí solo, que los valores sean correctos.

---

## 4. ¿Qué es una ruta?

Una **ruta** es un camino de ejecución por el que puede continuar la información dentro de una automatización. En Make, un **Router (enrutador)** permite dividir un flujo en varias ramas.

Por ejemplo:

**Correo recibido → Router → Ruta de consultas / Ruta de renovaciones / Ruta de incidencias**

Cada ruta puede terminar en una acción diferente: crear una fila, enviar una notificación, solicitar información o derivar el caso para revisión.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/router-filtros-correcto.webp" alt="Ejemplo de un router con dos filtros: el verdadero permite registrar la reserva y el falso bloquea la otra ruta." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/router-filtros-correcto.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

El router **no adivina cuál es la ruta correcta**. Son las condiciones asociadas a cada salida las que determinan si los datos continúan por ella.

### Una ruta no significa necesariamente una sola opción

Si varias rutas cumplen sus filtros, un router puede permitir que **más de una ruta** se ejecute para la misma entrada. No todos los routers funcionan como un interruptor exclusivo de «una opción u otra».

Esto importa cuando, por ejemplo, un mensaje debe **registrarse** y además **enviar una alerta**: ambas rutas podrían ser válidas simultáneamente.

---

## 5. ¿Qué es un filtro?

Un **filtro** es una regla que se evalúa antes de que los datos avancen por una ruta. La pregunta que hace es sencilla: **¿se cumple la condición?**

- Si la respuesta es **verdadera**, esa ruta permite continuar.
- Si la respuesta es **falsa**, esa ruta no ejecuta sus pasos para esos datos.

Ejemplo: una ruta recibe solo solicitudes cuyo campo `categoria` es exactamente `"renovacion"`.

| Dato recibido | Filtro `categoria = "renovacion"` | Resultado |
|---|---|---|
| `"renovacion"` | Verdadero | La ruta continúa. |
| `"consulta"` | Falso | La ruta se bloquea. |
| Campo ausente | No cumple la condición esperada | Se necesita control de datos faltantes. |

Es importante que el sistema distinga entre **texto**, **números**, **booleanos** y **valores nulos**. Comparar un número puede ser diferente de comparar una cadena que contiene dígitos.

### Ruta y filtro no son lo mismo

| Concepto | Su función | Imagen mental |
|---|---|---|
| **Router** | Crea una bifurcación con varios caminos. | Una intersección. |
| **Ruta** | Es uno de esos caminos. | Una carretera. |
| **Filtro** | Comprueba si la entrada puede recorrer la ruta. | Un control de acceso. |
| **Acción** | Hace algo después de superar el filtro. | Llegar a un destino y realizar una tarea. |

**Recuerda:** que una ruta exista no significa que siempre se ejecute.

---

## 6. Comparadores: cómo expresar una condición

Un filtro examina un **dato**, aplica un **operador** y lo compara con un **valor**.

Ejemplo: `personas >= 10` pregunta si el número de personas es mayor o igual a diez.

| Operador | Significa | Ejemplo |
|---|---|---|
| `>` | Mayor que | `edad > 18` |
| `<` | Menor que | `temperatura < 25` |
| `>=` | Mayor o igual que | `personas >= 10` |
| `<=` | Menor o igual que | `monto <= 5000` |
| `==` | Igual a | `tipo == "consulta"` |
| `!=` | Distinto de | `estado != "cerrado"` |

En Make, los comparadores se seleccionan desde la interfaz del filtro y pueden aparecer con palabras como *Equal to*, *Greater than* o *Contains*. No es necesario escribir exactamente estos símbolos en todos los campos de la interfaz.

### Atención a los límites

Si una ruta permite `monto < 5000` y otra usa `monto > 5000`, ¿qué ocurre cuando el monto es **exactamente 5000**?

**No entra en ninguna.** Para cubrir ese límite debes definir, por ejemplo, `monto <= 5000` y `monto > 5000`, después de comprobar que el dato sea numérico.

### Texto, números y booleanos

Imagina esta entrada:

~~~json
{
  "tipo": "consulta",
  "personas": 12,
  "urgente": false
}
~~~

- `"consulta"` es un **texto**.
- `12` es un **número**.
- `false` es un **booleano**.

Una condición como `urgente == true` **no se cumple** con este ejemplo. Y `"12"` (texto) no debe confundirse con `12` (número) al diseñar reglas numéricas.

---

## 7. AND y OR: combinar condiciones

A veces una sola regla no basta. Para decidir se combinan varias mediante **AND (Y)** y **OR (O)**.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/05-and-or.webp" alt="Comparación visual entre condiciones AND y OR." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/05-and-or.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

### AND: todo debe cumplirse

Supongamos que una sala puede reservarse automáticamente únicamente cuando:

- Está disponible.
- La persona entregó sus datos obligatorios.

La autorización ocurre cuando **ambas condiciones son verdaderas**.

| Disponible | Datos completos | AND |
|---|---|---|
| Verdadero | Verdadero | **Verdadero** |
| Verdadero | Falso | Falso |
| Falso | Verdadero | Falso |
| Falso | Falso | Falso |

### OR: basta una condición

Supongamos que una alerta se activa cuando:

- La temperatura es excesiva, **o**
- El sensor informa una falla.

Con OR es suficiente que **una de las dos condiciones** sea verdadera.

| Temperatura excesiva | Falla detectada | OR |
|---|---|---|
| Verdadero | Verdadero | **Verdadero** |
| Verdadero | Falso | **Verdadero** |
| Falso | Verdadero | **Verdadero** |
| Falso | Falso | Falso |

**Error frecuente:** utilizar OR cuando en realidad se necesitan dos requisitos simultáneos. Una ruta podría activarse con información incompleta.

### Ejemplo con dos rutas

Un sistema ficticio recibe `{"temperatura": 30, "alarma": false}`.

- **Ruta de alerta:** `temperatura >= 35 OR alarma == true` → **No se activa**.
- **Ruta normal:** `temperatura < 35 AND alarma == false` → **Sí se activa**.

Si cambias solo la temperatura a `38`, el resultado es distinto. Por eso las pruebas deben incluir casos límite y distintas combinaciones.

---

## 8. ¿Pueden activarse varias rutas a la vez?

Sí. En una bifurcación, cada filtro puede evaluarse de forma independiente.

Supongamos que una solicitud tiene:

~~~json
{
  "tipo": "renovacion",
  "urgente": true
}
~~~

Si existe una ruta que registra todas las renovaciones y otra que alerta sobre solicitudes urgentes, **las dos pueden recibir la misma entrada**.

Esto es diferente de un sistema que obliga a seleccionar exactamente un destino. La posibilidad de ejecución paralela requiere considerar duplicidades, orden de operaciones, errores y acciones repetidas.

En SparkFlow podrás **ver** este comportamiento con circuitos en los que una chispa puede atravesar más de una ruta.

---

## 9. Validar los datos antes de tomar decisiones

Si una IA extrae información de un mensaje, no basta con que entregue algo parecido a JSON. Las condiciones deben utilizar **valores confiables**.

Controles útiles:

1. **Existencia:** comprobar que un campo obligatorio esté presente.
2. **Tipo:** verificar que el monto sea numérico, no texto libre.
3. **Rango:** evitar cantidades imposibles o fechas inválidas.
4. **Significado:** distinguir valores ausentes, desconocidos o ambiguos.
5. **Destino seguro:** si algo falla, no continuar automáticamente con una acción sensible.

### ¿Qué pasa con NULL?

`null` es un valor nulo de JSON; `"NULL"` es texto. Ambos pueden representar ausencia en un diseño determinado, pero **no son intercambiables automáticamente**. El filtro debe evaluar el tipo y formato que realmente entrega el sistema anterior.

### Ruta de contingencia

Una **ruta de contingencia** (fallback) permite pedir aclaraciones, registrar un problema o derivar a revisión humana cuando faltan datos. Su objetivo es que una falla no se convierta en una acción incorrecta.

---

## 10. Mapeo JSON y diseño lógico

### El problema del mismo dato con nombres diferentes

Un formulario puede llamar al campo `nombreCompleto` y la aplicación de destino puede esperar `cliente`. Aunque ambos hablen de lo mismo, los sistemas no siempre hacen esa asociación solos.

**Mapear datos** es indicar qué información del origen corresponde a cada campo del destino; a veces también hay que **transformarla**, por ejemplo, convertir texto en número, ajustar una fecha o separar un nombre.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/06-mapeo-campos.webp" alt="Correspondencia de campos entre aplicaciones." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/06-mapeo-campos.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

| Formulario (origen) | Registro (destino) | Transformación necesaria |
|---|---|---|
| `nombreCompleto` | `cliente` | Copiar el texto. |
| `cantidad` = `"3"` | `cupos` = `3` | Convertir texto numérico a número, previa validación. |
| `fecha` = `"12/11/2026"` | `fechaISO` | Convertir a `"2026-11-12"`, comprobando el formato. |
| `correo` | `email` | Validar y copiar. |

**Ejemplo de datos que recibe el destino:**

~~~json
{
  "cliente": "Andrea",
  "cupos": 3,
  "fechaISO": "2026-11-12",
  "email": "andrea@ejemplo.test"
}
~~~

**Importante:** el mapeo define correspondencias, pero no vuelve confiable cualquier dato de manera automática. Las conversiones deben comprobar si el valor realmente puede transformarse.

### Diseñar la matriz lógica antes de usar Make

Supongamos que una sala tiene **20 cupos disponibles** y debemos registrar nuevas reservas.

| Ruta | Condición | Acción |
|---|---|---|
| **Contingencia** | Cupos solicitados ausentes, no numéricos o menores o iguales a cero. | Solicitar corrección; no registrar la reserva. |
| **Confirmación** | Datos válidos **AND** cupos solicitados menores o iguales a 20. | Registrar y confirmar. |
| **Lista de espera** | Datos válidos **AND** cupos solicitados mayores que 20. | Notificar que no hay suficientes cupos. |

Esta tabla es una **matriz de decisiones**: ayuda a evitar solapamientos y vacíos antes de configurar las rutas en el programa.

**Comprobación mental:** si solicitan exactamente **20 cupos**, corresponde **Confirmación**. Si solicitan **21**, corresponde **Lista de espera**.

---

## 11. Debugging, limpieza y manejo de errores

**Debugging** significa localizar y entender por qué un flujo no funcionó como se esperaba. **Limpieza de datos** significa corregir o estandarizar información antes de utilizarla.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/07-debugging.webp" alt="Datos con un error identificados mediante una lupa y revisados." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/07-debugging.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

### Un caso fácil de reconocer

El sistema de inscripciones espera recibir un número de cupos:

~~~json
{
  "nombre": "Andrea",
  "cupos": "3 personas"
}
~~~

Aquí `cupos` es **texto**, no número. Si el módulo de destino espera un número entero, el registro podría fallar o interpretarse incorrectamente.

### Cómo investigar el error

1. **Identifica el resultado esperado:** registrar tres cupos.
2. **Observa qué se recibió:** el texto `"3 personas"`.
3. **Revisa el punto donde falló:** por ejemplo, la validación del número o la escritura en la tabla.
4. **Busca la causa:** formato y tipo incorrectos.
5. **Corrige y vuelve a probar:** transforma de manera segura a `3`, comprueba el rango y ejecuta otra prueba.
6. **Prevé reincidencias:** valida futuros datos antes de guardar.

### Limpiar datos no significa borrar a ciegas

Algunas transformaciones frecuentes:

| Entrada | Posible tratamiento | Precaución |
|---|---|---|
| `"  Andrea  "` | Quitar espacios exteriores. | No eliminar espacios internos del nombre. |
| `"3"` | Convertir a número `3`. | Comprobar que sean dígitos válidos. |
| `"3 personas"` | Extraer la cantidad si el formato es conocido. | Evitar interpretar cualquier texto como un número. |
| `"12/11/2026"` | Normalizar fecha. | Confirmar si el orden es día/mes/año. |
| `""` | Tratar como campo vacío. | No inventar un valor. |

### ¿Cómo evitar que el flujo pierda información?

Si el módulo de destino falla, es útil tener una **estrategia de contingencia**. Por ejemplo:

**Nueva reserva → Validación → Intento de guardar → ¿Funcionó?**

- **Sí:** confirmar el registro.
- **No:** guardar la solicitud original en un registro temporal seguro, anotar el error y avisar a una persona responsable.

En Make, la configuración concreta del manejo de errores depende de los módulos y del escenario. **Un filtro de router para datos inválidos** y **un manejador de errores de ejecución** no son exactamente lo mismo: uno decide según condiciones previstas; el otro reacciona ante un fallo durante la ejecución.

### Para comprobar que comprendiste el tema

Sin resolver ejercicios oficiales, prueba explicarte estas tres preguntas: ¿qué dato recibió el sistema?, ¿cuál era el tipo esperado?, ¿qué harías para no perder el registro si vuelve a fallar?

---

## 12. SparkFlow: organiza las solicitudes de una oficina

**SparkFlow** es un juego educativo de lógica, rutas, filtros y datos JSON. Ahora la historia transcurre en una **oficina**: una coordinadora presenta situaciones y tú ayudas a distribuir solicitudes entre áreas como Ventas, Soporte, Finanzas, Archivo, Jefatura y Gerencia.

El objetivo no es programar ni construir las conexiones desde cero. Debes interpretar los datos que llegan, decidir **qué filtro necesita cada ruta** y comprobar que las solicitudes alcancen únicamente los destinos correctos. El juego cuenta con **13 misiones**, desde comparaciones sencillas hasta decisiones con varios revisores y creación de JSON.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/08-sparkflow-icono.webp" alt="Pequeño apoyo visual del juego SparkFlow." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/08-sparkflow-icono.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Ilustración conceptual del juego. Los controles reales y los objetivos aparecen dentro de SparkFlow.*

### ¿Cómo se juega?

1. **Registra a los participantes.** Puedes jugar individualmente o con un equipo; los nombres aparecerán en el reporte.
2. **Lee el caso que presenta la coordinadora.** Cada misión explica el objetivo y qué destinos deberían recibir cada solicitud.
3. **Mira el circuito de la pizarra.** Las rutas están conectadas. Selecciona la línea o el botón de una ruta para editar su filtro.
4. **Configura las condiciones.** Elige el campo, el comparador y el valor. En algunas misiones necesitarás combinar reglas con **AND (Y)** u **OR (O)**.
5. **Revisa los JSON de prueba.** Observa campos como `monto`, `prioridad`, `area`, `aprobado`, `completo`, `urgente` o `copia`.
6. **Pulsa «Ejecutar simulación».** El juego comprueba los casos y muestra qué rutas permiten pasar la solicitud y cuáles la retienen.
7. **Compara, corrige y repite.** Puedes revisar el diagnóstico, usar una pista y ajustar los filtros sin necesitar la respuesta completa.
8. **Desbloquea nuevas misiones.** Tu progreso se conserva en el navegador, mientras no borres sus datos.

### ¿Qué partes encontrarás en la pantalla?

| Elemento | Para qué sirve |
|---|---|
| **Objetivo principal** | Explica el caso de la oficina, la tarea y los resultados esperados. |
| **Pizarra o circuito** | Muestra el router, sus rutas, los revisores y los destinos de las solicitudes. |
| **Datos de entrada** | Permite revisar los diferentes JSON que se usarán en las pruebas. |
| **Editor de rutas y filtros** | Permite seleccionar campos, operadores y valores de cada condición. |
| **Ejecutar simulación** | Comprueba los distintos casos y muestra resultados y errores. |
| **Tutorial de operadores** | Ayuda a comprender comparadores, **AND** y **OR** mediante ejemplos. |
| **Pistas y diagnósticos** | Orientan sobre qué revisar cuando una misión falla. |
| **Reporte** | Guarda el avance y las evidencias de tu partida. |

### ¿Qué cambia a medida que avanzas?

- **Misiones 1 a 4:** comparaciones simples, texto exacto, rutas paralelas y valores límite.
- **Misiones 5 a 8:** requisitos combinados con AND y OR, varias bandejas y decisiones simultáneas.
- **Misiones 9 y 10:** varios revisores deben dar su visto bueno para que una solicitud alcance Gerencia.
- **Misiones 11 a 13:** los filtros ya están configurados; ahora tienes que **escribir un JSON válido** que active solo las rutas solicitadas.

El tutorial interactivo se presenta como apoyo especial para las condiciones AND y OR. Los campos y valores deben escribirse tal como aparecen en el juego: `"ventas"` y `"soporte"`, por ejemplo, son textos distintos y se comparan exactamente.

### Consejos antes de empezar

- **Primero lee las condiciones; después ejecuta.** La respuesta no siempre consiste en activar una sola ruta.
- Comprueba cuidadosamente los límites: `>= 70` incluye 70, pero `> 70` no.
- Diferencia números, texto y booleanos: `50`, `"50"` y `true` no son el mismo tipo de dato.
- En pantallas pequeñas puedes utilizar las pestañas **Circuito**, **Filtros** y **JSON** para navegar entre las áreas del juego.
- El progreso se guarda localmente. La versión nueva contempla la recuperación del progreso anterior y la adaptación de los nombres de los campos.
- Cuando termines, puedes usar **«Descargar reporte cifrado»** para obtener un archivo `.sfr` con el nombre del primer participante; no modifiques su extensión. **«Vista previa / imprimir»** ofrece otra manera de revisar tus resultados.
- SparkFlow simula decisiones lógicas: las firmas de varios revisores son una metáfora educativa, no una reproducción exacta de una herramienta de automatización.

<div style="margin:20px 0;padding:20px;border:1px solid #b6c5e6;border-radius:15px;background:linear-gradient(125deg,#eeeaff,#e8f7ff)">
  <strong style="display:block;font-size:1.2rem;color:#35236d;margin-bottom:8px">🏢 ¿Preparado para organizar la oficina?</strong>
  <p style="margin:0 0 15px;color:#33405d">Lee cada solicitud, configura sus filtros y comprueba qué equipos deben recibirla. ¡Las trece misiones te esperan!</p>
  <a href="https://sagitari01.github.io/sparkflow/" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#6435b8;color:white;border-radius:11px;padding:12px 22px;text-decoration:none;font-weight:800;box-shadow:0 4px 9px #31205d33">🎮 Abrir SparkFlow ↗</a>
</div>

---

## 13. Solucionario actualizado — solo después de jugar

**⚠️ Advertencia:** aquí encontrarás los filtros y ejemplos de JSON de las **13 misiones de la oficina**. No abras este apartado antes de intentar resolverlas: las pistas y el tutorial permiten aprender sin mirar las respuestas.

<details style="margin:17px 0;padding:14px;border:1px solid #efb65b;border-radius:12px;background:#fff8e8;color:#403322">
  <summary style="cursor:pointer;font-weight:800;padding:6px">🔒 Primera confirmación: ¿estás seguro de querer ver las respuestas antes de jugar?</summary>
  <p>Probar por tu cuenta ayuda a comprender los filtros. Si todavía no lo intentaste, puedes <a href="https://sagitari01.github.io/sparkflow/" target="_blank" rel="noopener noreferrer">ir al juego</a>.</p>
  <details style="padding:12px;border:1px solid #d8b1e6;border-radius:10px;background:#fcf6ff">
    <summary style="cursor:pointer;font-weight:800;padding:6px">¿Seguro, seguro? Segunda confirmación</summary>
    <p>El solucionario muestra las condiciones exactas. Incluso una lectura rápida podría quitarte el desafío.</p>
    <details style="padding:12px;border:1px solid #e4a4ba;border-radius:10px;background:#fff2f6">
      <summary style="cursor:pointer;font-weight:800;padding:6px">¿Seguro, seguro, seguro? Tercera confirmación</summary>
      <p>Última oportunidad para practicar primero con el tutorial y las pistas del juego.</p>
      <details style="padding:12px;border:1px solid #e08b95;border-radius:10px;background:#fffafa">
        <summary style="cursor:pointer;font-weight:800;padding:6px">⚠️ Última confirmación: mostrar el solucionario completo</summary>
        <div style="margin-top:12px;padding:13px;background:#ffffff;border:1px solid #ebd6d8;border-radius:10px;line-height:1.7;color:#283246">
          <h4>Misiones 1 a 10: configuración de filtros</h4>
          <ol>
            <li><strong>Primer día en la oficina:</strong> Finanzas recibe cuando <code>monto &gt;= 50</code>.</li>
            <li><strong>Dos áreas, dos bandejas:</strong> Ventas: <code>area == "ventas"</code>. Soporte: <code>area == "soporte"</code>.</li>
            <li><strong>Una solicitud, dos destinos:</strong> Finanzas: <code>monto &gt;= 50</code>. Archivo: <code>completo == true</code>. Ambas rutas pueden activarse.</li>
            <li><strong>La mesa de prioridades:</strong> Jefatura: <code>prioridad &gt;= 70</code>. Atención normal: <code>prioridad &lt; 70</code>.</li>
            <li><strong>La doble firma:</strong> <code>aprobado == true</code> <strong>AND</strong> <code>monto &gt;= 50</code>.</li>
            <li><strong>Original y copia:</strong> Ventas: <code>area == "ventas"</code>. Archivo: <code>copia == true</code>.</li>
            <li><strong>Cuatro bandejas de atención:</strong> Normal: <code>prioridad &lt; 88</code> <strong>AND</strong> <code>urgente == false</code>. Urgencias: <code>prioridad &gt;= 88</code> <strong>OR</strong> <code>urgente == true</code>. Archivo: <code>copia == true</code>. Auditoría: <code>aprobado == false</code>.</li>
            <li><strong>Cuatro revisiones independientes:</strong> Conforme: <code>monto &gt;= 60</code> <strong>AND</strong> <code>completo == true</code>. Observada: <code>monto &lt; 60</code> <strong>OR</strong> <code>completo == false</code>. Baja: <code>prioridad &lt;= 25</code>. Crítica: <code>prioridad &gt; 25</code> <strong>AND</strong> <code>urgente == true</code>.</li>
            <li><strong>Cuatro vistos buenos:</strong> Revisor A: <code>monto &lt;= 90</code>. B: <code>aprobado == true</code>. C: <code>completo != false</code>. D: <code>prioridad &lt; 40</code>. La firma final requiere los cuatro vistos buenos.</li>
            <li><strong>El circuito de Gerencia:</strong> Entrada al segundo router: <code>monto &gt; 40</code>. Los cinco revisores exigen, respectivamente: <code>area == "ventas"</code>, <code>aprobado == true</code>, <code>completo == true</code>, <code>prioridad &lt;= 75</code> y <code>copia == false</code>.</li>
          </ol>
          <h4>Misiones 11 a 13: ejemplos válidos de JSON</h4>
          <p>En los últimos niveles puede haber varias respuestas correctas. Estas son <strong>soluciones de ejemplo</strong> con los campos y tipos de datos que exige la versión actual.</p>
          <p><strong>11. Redacta la solicitud:</strong> activar Ventas y Baja, pero no Gerencia.</p>
          <pre style="white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5fb;padding:10px;border-radius:7px">{"area":"ventas","monto":60,"prioridad":15}</pre>
          <p><strong>12. JSON de decisiones:</strong> activar únicamente Control C y Control D.</p>
          <pre style="white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5fb;padding:10px;border-radius:7px">{"area":"soporte","monto":60,"prioridad":30,"urgente":false,"completo":true,"aprobado":false}</pre>
          <p><strong>13. El JSON maestro:</strong> activar solo A, C y E, dejando B y D bloqueadas.</p>
          <pre style="white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5fb;padding:10px;border-radius:7px">{"area":"soporte","monto":85,"prioridad":30,"urgente":false,"completo":true,"aprobado":true,"copia":false}</pre>
          <p><em>Solucionario contrastado con la versión de SparkFlow publicada el 12 de noviembre de 2026. Los nombres de campo corresponden a la nueva temática de oficina.</em></p>
        </div>
      </details>
    </details>
  </details>
</details>
