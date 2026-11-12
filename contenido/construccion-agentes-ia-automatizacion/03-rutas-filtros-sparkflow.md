<!-- secciones: desplegables -->
# Integraciones, APIs, JSON, rutas y calidad de datos

## Antes de comenzar

Imagina un centro comunitario que recibe inscripciones a talleres. El formulario recibe los datos, una aplicación comprueba si quedan cupos, otra guarda el registro y un correo confirma la inscripción. Si una persona tiene que copiar cada dato a mano, aparecen retrasos y errores.

El reto de hoy es comprender **cómo viajan los datos entre aplicaciones y cómo tomar decisiones seguras**. La secuencia será: conectar sistemas → pedir y recibir información → organizarla como JSON → aplicar rutas y filtros → revisar que sea válida → resolver problemas.

En estas páginas encontrarás las ideas fundamentales para comprender cómo se conectan aplicaciones, cómo se organizan los datos y cómo una automatización toma decisiones. Usaremos ejemplos cotidianos y ficticios para aprender paso a paso.

### Mapa visual del tema

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0">
<img src="contenido/construccion-agentes-ia-automatizacion/imagenes/05-integraciones-json-cuaderno.webp" alt="Lámina de cuaderno sobre integración de aplicaciones, APIs, JSON, routers, filtros y calidad de datos, con diagramas dibujados a mano." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy">
<a href="contenido/construccion-agentes-ia-automatizacion/imagenes/05-integraciones-json-cuaderno.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a>
</div>

*La lámina sirve para visualizar los conceptos; las reglas y ejemplos escritos a continuación son la referencia para los detalles técnicos.*

---

## 1. Integraciones y flujos de datos

### El problema de las aplicaciones separadas

Piensa en tres lugares donde podría existir una misma inscripción: un formulario, una hoja de cálculo y un calendario. Si no están conectados, alguien debe trasladar los datos de uno a otro; a esos espacios aislados se les suele llamar **silos de información**.

Una **integración** permite que distintas aplicaciones intercambien información mediante interfaces acordadas. Una **automatización** coordina los pasos para que, cuando ocurra un evento, los datos lleguen al siguiente sistema sin copiarlos manualmente.

**Ejemplo ficticio:** una persona completa un formulario → se consulta un calendario → se registra la reserva → se envía un mensaje de confirmación.

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

**Ejemplo ficticio:** una automatización consulta a un servicio de bicicletas compartidas cuántas bicicletas quedan en una estación; después informa el resultado.

### Las cuatro piezas de una petición

1. **Método:** qué acción buscas. `GET` consulta; `POST` normalmente envía datos; `PUT` o `PATCH` actualizan; `DELETE` solicita eliminar.
2. **Endpoint:** dirección específica del recurso, por ejemplo `https://api.ejemplo.test/estaciones/12` (**dirección ficticia**, no un servicio real).
3. **Headers:** información adicional sobre la petición, como el tipo de contenido o la autorización.
4. **Body o payload:** datos enviados en el cuerpo, especialmente cuando se crea o modifica información.

| Petición | Interpretación cotidiana |
|---|---|
| `GET /estaciones/12` | «Dime qué hay en esta estación». |
| `POST /reservas` | «Crea esta reserva». |
| `PATCH /reservas/48` | «Actualiza algunos datos de la reserva 48». |
| `DELETE /reservas/48` | «Solicita eliminar la reserva 48». |

No todos los servicios aceptan todos los métodos: **la documentación de la API define cuáles están disponibles y sus permisos**.

### Una respuesta también trae información importante

En las respuestas HTTP es frecuente encontrar un **código de estado**:

- **200:** la solicitud se procesó correctamente.
- **201:** normalmente se creó un recurso.
- **400:** la petición tiene algún problema.
- **401:** faltan credenciales válidas.
- **404:** el recurso solicitado no se encuentra.
- **500:** ocurrió un error del lado del servidor.

Que una solicitud sea enviada no significa que el servicio la haya aceptado. Hay que revisar su respuesta.

### Polling frente a webhooks

- **Polling (consulta periódica):** la automatización pregunta cada cierto tiempo «¿hay novedades?». Es útil si el servicio no puede avisar por sí mismo, pero genera consultas incluso cuando no hay cambios.
- **Webhook (aviso por evento):** un sistema compatible envía datos a una dirección configurada **cuando ocurre un evento**. Puede reducir esperas y consultas innecesarias.

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

El router **no adivina cuál es la ruta correcta**. Son las condiciones asociadas a cada salida las que determinan si los datos continúan por ella.

### Una ruta no significa necesariamente una sola opción

Si varias rutas cumplen sus filtros, un router puede permitir que **más de una ruta** se ejecute para la misma entrada. No todos los routers funcionan como un interruptor exclusivo de «una opción u otra».

Esto importa cuando, por ejemplo, un mensaje debe **registrarse** y además **enviar una alerta**: ambas rutas podrían ser válidas simultáneamente.

### Lámina de rutas y filtros

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0">
  <img src="contenido/construccion-agentes-ia-automatizacion/imagenes/03-rutas-filtros-hoja.webp" alt="Dos hojas ilustradas de cuaderno sobre rutas, filtros, su comparación y un ejemplo de bifurcación condicional en un flujo." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy">
  <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/03-rutas-filtros-hoja.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>
  </a>
</div>

*Apoyo visual elaborado para estudiar. Los iconos y escenarios de la lámina son ilustrativos; la configuración exacta se realiza en la herramienta utilizada.*

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

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0">
<img src="contenido/construccion-agentes-ia-automatizacion/imagenes/06-debugging-mapeo-cuaderno.webp" alt="Ilustración tipo cuaderno con ejemplos de mapeo entre sistemas, errores de datos, proceso de limpieza y rutas de contingencia." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy">
<a href="contenido/construccion-agentes-ia-automatizacion/imagenes/06-debugging-mapeo-cuaderno.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a>
</div>

*La ilustración ayuda a visualizar el proceso. Revisa siempre las reglas específicas escritas en los ejemplos de este apunte.*

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

## 12. SparkFlow: un juego para entender rutas y filtros

**SparkFlow** es un juego educativo de lógica y simulación de flujos. Tu misión es ayudar a restaurar una central de energía configurando rutas y filtros para que cada «chispa» llegue únicamente a los destinos permitidos.

No necesitas programar ni instalar Make. El juego está disponible en el navegador y presenta **13 misiones progresivas**.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0">
  <img src="contenido/construccion-agentes-ia-automatizacion/imagenes/04-sparkflow-hoja.webp" alt="Hoja ilustrada del cuaderno con una introducción a SparkFlow, pasos generales para jugar, rutas y un recordatorio sobre el solucionario. Es una ilustración, no una captura literal del programa." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy">
  <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/04-sparkflow-hoja.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>
  </a>
</div>

*Esta hoja es una guía visual conceptual, **no una captura de la interfaz real**. Las instrucciones verificadas del juego aparecen a continuación.*

### ¿Cómo se juega?

1. **Abre SparkFlow:** inicia con una pantalla en la que puedes registrar tu nombre o los integrantes de tu equipo.
2. **Lee el objetivo de la misión:** encontrarás una situación, las entradas que se evalúan y los destinos a los que deberían llegar.
3. **Observa el circuito:** las rutas ya están dibujadas. Selecciona una haciendo clic en su línea o botón.
4. **Revisa el filtro:** cuando la misión lo permite, elige un campo, operador y valor. Puedes agregar condiciones y combinarlas con **AND** o **OR**.
5. **Revisa los datos JSON:** algunas misiones muestran entradas de prueba; en los desafíos de construcción debes escribir tu propio objeto JSON con los tipos correctos.
6. **Ejecuta la simulación:** pulsa **Ejecutar simulación** y observa qué rutas reciben energía y cuáles no.
7. **Corrige y vuelve a probar:** puedes utilizar las pistas para comprender el error sin recibir directamente el resultado.
8. **Avanza:** cuando superas la misión se desbloquea la siguiente. El juego conserva tu progreso en ese navegador.

### ¿Qué encontrarás en la interfaz?

| Parte | Para qué sirve |
|---|---|
| **Objetivo principal** | Describe lo que debe ocurrir con cada entrada. |
| **Circuito** | Muestra routers, rutas, destinos y el recorrido de las chispas. |
| **Editor de rutas y filtros** | Permite configurar condiciones cuando la misión lo admite. |
| **Datos JSON** | Permite inspeccionar o construir las entradas. |
| **Ejecutar simulación** | Comprueba el comportamiento de las rutas. |
| **Tutorial de operadores** | Explica comparadores, AND y OR de forma interactiva. |
| **Pista** | Orienta la revisión de errores. |
| **Reporte** | Permite guardar los resultados obtenidos. |

### ¿Qué cambia en las últimas misiones?

En las **misiones 11, 12 y 13**, los filtros están preparados de antemano. El desafío consiste en **escribir un JSON válido** que active las rutas solicitadas y mantenga bloqueadas las demás. Es un ejercicio de pensar la condición «al revés»: desde el resultado esperado hacia los datos de entrada.

### Consejos de uso

- Puedes jugar de manera individual o grupal.
- El progreso se guarda localmente en el navegador; si cambias de dispositivo o borras los datos del sitio podrías perderlo.
- Al finalizar, descarga el **reporte cifrado** del propio juego o usa la opción de vista previa/impresión para conservar evidencia personal.
- La versión descargable también funciona sin conexión. El juego es una **simulación didáctica**: por ejemplo, las compuertas con varios generadores no son una representación literal de la unión de rutas en Make.

<div style="margin:20px 0;padding:20px;border:1px solid #b6c5e6;border-radius:15px;background:linear-gradient(125deg,#eeeaff,#e8f7ff)">
  <strong style="display:block;font-size:1.2rem;color:#35236d;margin-bottom:8px">⚡ ¿Preparado para restaurar la central?</strong>
  <p style="margin:0 0 15px;color:#33405d">Empieza por el tutorial, observa las rutas y descubre cómo funcionan los filtros en cada misión.</p>
  <a href="https://sagitari01.github.io/sparkflow/" target="_blank" rel="noopener noreferrer" style="display:inline-block;background:#6435b8;color:white;border-radius:11px;padding:12px 22px;text-decoration:none;font-weight:800;box-shadow:0 4px 9px #31205d33">🎮 Abrir SparkFlow ↗</a>
</div>

---

## 13. Solucionario de las 13 misiones — solo después de intentar el juego

**⚠️ Advertencia:** esta sección contiene las condiciones y ejemplos de respuesta de SparkFlow. Te recomendamos **no abrirla** antes de intentar resolver las misiones. Las pistas del propio juego están pensadas para ayudarte a avanzar sin consultar respuestas.

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
          <h4>Misiones 1 a 10: filtros de cada ruta</h4>
          <ol>
            <li><strong>El despertar:</strong> potencia mayor o igual que 50 (<code>potencia &gt;= 50</code>).</li>
            <li><strong>La bifurcación:</strong> Solar si <code>tipo == "solar"</code>; Eólica si <code>tipo == "eolica"</code>.</li>
            <li><strong>Energía compartida:</strong> receptor A si <code>potencia &gt;= 50</code>; receptor B si <code>estable == true</code>. Ambas rutas pueden activarse.</li>
            <li><strong>La cámara de selección:</strong> Refrigeración si <code>temperatura &gt;= 70</code>; Normal si <code>temperatura &lt; 70</code>.</li>
            <li><strong>El escudo de seguridad:</strong> <code>autorizado == true</code> <strong>AND</strong> <code>potencia &gt;= 50</code>.</li>
            <li><strong>Las compuertas gemelas:</strong> Principal si <code>tipo == "solar"</code>; Respaldo si <code>respaldo == true</code>.</li>
            <li><strong>Cuatro rutas de emergencia:</strong> Normal: <code>temperatura &lt; 88</code> <strong>AND</strong> <code>alarma == false</code>. Emergencia: <code>temperatura &gt;= 88</code> <strong>OR</strong> <code>alarma == true</code>. Respaldo: <code>respaldo == true</code>. Auditoría: <code>autorizado == false</code>.</li>
            <li><strong>Cuatro controles independientes:</strong> Calidad: <code>potencia &gt;= 60</code> <strong>AND</strong> <code>estable == true</code>. Falla: <code>potencia &lt; 60</code> <strong>OR</strong> <code>estable == false</code>. Frío: <code>temperatura &lt;= 25</code>. Riesgo: <code>temperatura &gt; 25</code> <strong>AND</strong> <code>alarma == true</code>.</li>
            <li><strong>Cuatro generadores:</strong> A: <code>potencia &lt;= 90</code>. B: <code>autorizado == true</code>. C: <code>estable != false</code>. D: <code>temperatura &lt; 40</code>.</li>
            <li><strong>Cinco rutas del núcleo:</strong> Entrada al segundo router: <code>potencia &gt; 40</code>. Luego, respectivamente: <code>tipo == "solar"</code>, <code>autorizado == true</code>, <code>estable == true</code>, <code>temperatura &lt;= 75</code>, <code>respaldo == false</code>.</li>
          </ol>
          <h4>Misiones 11 a 13: ejemplos válidos de JSON</h4>
          <p>En estos niveles pueden existir <strong>varias respuestas correctas</strong>; los siguientes son ejemplos que satisfacen los filtros de las rutas solicitadas.</p>
          <p><strong>11. Construye el mensaje:</strong> activar Solar y Frío, pero no Alerta.</p>
          <pre style="white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5fb;padding:10px;border-radius:7px">{"tipo":"solar","potencia":60,"temperatura":15}</pre>
          <p><strong>12. JSON de decisiones:</strong> activar solo Control C y Control D.</p>
          <pre style="white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5fb;padding:10px;border-radius:7px">{"tipo":"eolica","potencia":60,"temperatura":30,"alarma":false,"estable":true,"autorizado":false}</pre>
          <p><strong>13. El JSON maestro:</strong> activar solo A, C y E.</p>
          <pre style="white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f5fb;padding:10px;border-radius:7px">{"tipo":"eolica","potencia":85,"temperatura":30,"alarma":false,"estable":true,"autorizado":true,"respaldo":false}</pre>
          <p><em>Las condiciones se derivan de la versión publicada del código del juego. Si SparkFlow cambia sus misiones, este solucionario también necesitará revisión.</em></p>
        </div>
      </details>
    </details>
  </details>
</details>
