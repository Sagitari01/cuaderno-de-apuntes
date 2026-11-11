<!-- secciones: desplegables -->

# IA generativa y gestión cognitiva: interpretar, estructurar y verificar información

## Antes de comenzar

En el apunte anterior aprendimos a distinguir el proceso **AS-IS** (lo que ocurre hoy) del **TO-BE** (cómo debería funcionar). Ahora veremos cómo integrar un componente capaz de **leer mensajes, encontrar datos y entregarlos en un formato que otro sistema pueda procesar**.

Imagina un centro comunitario que recibe este mensaje ficticio:

> «Hola, quiero reservar la sala grande para el jueves a las 18:00. Seremos doce personas».

Una persona puede interpretarlo. Pero ¿cómo obtenemos los mismos campos en cientos de mensajes redactados de maneras distintas? Para eso estudiamos la **gestión cognitiva con IA**.

**Aprenderás:** datos estructurados y no estructurados, prompt engineering, los cinco bloques de un prompt, JSON, zero-shot, few-shot, iteración, alucinaciones, sesgos y validaciones.

**Apoyo visual: tipos de datos**

<div class="lamina-apunte" style="position:relative;display:block;width:100%;margin:18px auto 12px;line-height:0">
  <img src="contenido/construccion-agentes-ia-automatizacion/imagenes/01-tipos-de-datos.webp" alt="Ilustración en papel rayado que compara datos estructurados, semiestructurados y no estructurados." style="display:block;width:100%;height:auto;max-width:100%;border:1px solid var(--color-divider);border-radius:10px;background:#fff" loading="lazy">
  <a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/imagenes/01-tipos-de-datos.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;min-width:32px;min-height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>
  </a>
</div>

Las siguientes secciones incluyen más láminas ilustradas. Puedes abrir los apartados y sus subtítulos para verlas junto a cada explicación.

> **Importante:** el centro comunitario y sus mensajes son ejemplos inventados. La IA interpreta información, pero las decisiones de negocio y los datos críticos deben verificarse por otros mecanismos.

---

## 1. Gestión cognitiva: ¿qué hace realmente la IA?

La **carga cognitiva** es el esfuerzo de leer, comprender, comparar, clasificar y extraer información. Cuando un equipo revisa muchos correos, una parte importante del trabajo es interpretar lo que cada remitente quiso decir.

Un modelo de lenguaje puede ayudar a:

- **Clasificar:** distinguir una reserva, una consulta o una cancelación.
- **Extraer:** reconocer una sala, una hora o una cantidad dentro de un texto.
- **Resumir:** identificar lo esencial en un documento largo.
- **Señalar ausencias y dudas:** indicar qué datos faltan o son ambiguos.

Pero **extraer no es verificar**. La IA puede reconocer que alguien pide una sala a las 18:00; solo la base de reservas puede confirmar si está disponible.

### Datos estructurados, semiestructurados y no estructurados


| Tipo | Qué significa | Ejemplo |
|---|---|---|
| **Estructurados** | Campos definidos y consistentes. | Tabla de reservas con columnas sala, fecha y hora. |
| **Semiestructurados** | Tienen algunos elementos organizados, pero contenido variable. | Correo con remitente, asunto y cuerpo libre. |
| **No estructurados** | No siguen un esquema fijo fácil de procesar. | Mensajes libres, conversaciones, imágenes y ciertos documentos. |

Un PDF es un **formato de archivo**, no sinónimo automático de dato no estructurado: puede contener texto, tablas o imágenes escaneadas.

### El puente entre ambos mundos

**Mensaje recibido → extracción con IA → datos estructurados → validación → consulta al sistema → respuesta**

1. Llega el mensaje.
2. La IA identifica campos.
3. Entrega un formato definido.
4. Un validador comprueba campos, tipos y reglas.
5. El sistema consulta la disponibilidad y ejecuta una acción autorizada.
6. Si falta algo, el proceso pide aclaración o deriva a una persona.

### ¿Por qué no es simplemente un chatbot?

En un chat suele ser útil que el modelo escriba: «¡Claro! Te explico…». En una automatización eso puede ser un problema: otro programa podría estar esperando **solo datos**, no una conversación.

| Conversación | Automatización |
|---|---|
| Respuestas flexibles. | Campos y formatos previsibles. |
| La persona interpreta el resultado. | Otro programa lo procesa. |
| Una explicación adicional suele servir. | Un texto adicional puede romper el lector de datos. |
| La utilidad depende de la conversación. | La fiabilidad depende también de validaciones y manejo de errores. |

---

## 2. Prompt engineering: de preguntar a especificar

Un **prompt** es una instrucción entregada a un modelo. En una tarea automatizada debe describir **qué extraer, de dónde, cómo manejar vacíos y en qué formato responder**.

**Prompt ambiguo:**

> «Lee este correo y dime qué necesita».

La IA podría escribir un resumen, una tabla o un párrafo distinto en cada ocasión.

### Los cinco bloques de un prompt profesional


<div class="lamina-apunte" style="position:relative;display:block;width:100%;margin:18px auto 12px;line-height:0">
  <img src="contenido/construccion-agentes-ia-automatizacion/imagenes/02-cinco-bloques-prompt.webp" alt="Hoja de apuntes que resume rol, contexto, tarea, restricciones y formato de salida de un prompt." style="display:block;width:100%;height:auto;max-width:100%;border:1px solid var(--color-divider);border-radius:10px;background:#fff" loading="lazy">
  <a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/imagenes/02-cinco-bloques-prompt.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;min-width:32px;min-height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>
  </a>
</div>

| Bloque | Pregunta | Ejemplo |
|---|---|---|
| **1. Rol** | ¿Quién debe actuar? | «Eres un extractor de datos de solicitudes». |
| **2. Contexto** | ¿Por qué se necesita? | «Los campos alimentarán un registro de reservas». |
| **3. Tarea** | ¿Qué debe encontrar? | «Extrae sala, fecha, hora y asistentes». |
| **4. Restricciones** | ¿Qué no debe hacer? | «No inventes información; usa un valor nulo si falta». |
| **5. Formato** | ¿Cómo responder? | «Devuelve exclusivamente JSON con las claves indicadas». |

### Ejemplo completo, paso a paso

**Rol:** Eres un asistente que extrae datos de solicitudes de espacios.

**Contexto:** Un sistema necesita clasificar mensajes antes de consultar la disponibilidad de salas.

**Tarea:** Extrae los campos: sala, fecha, hora y asistentes.

**Restricciones:** Utiliza exclusivamente el contenido del mensaje; no inventes fechas ni cantidades; si un valor no está especificado de forma inequívoca, utiliza el valor nulo convenido; no confirmes disponibilidad y no agregues explicaciones.

**Formato:** Devuelve únicamente un objeto JSON válido con las claves exactas solicitadas.

**Contenido por analizar:**

> [INICIO] Reservemos la sala grande el jueves a las 18:00; seremos doce. [FIN]

Los delimitadores [INICIO] y [FIN] distinguen los datos del mensaje de las instrucciones principales. Esto ayuda a evitar confusiones, aunque no garantiza por sí solo protección contra instrucciones maliciosas escondidas en un documento (*prompt injection*).

### ¿Qué pasa con «jueves»?

No conocemos la fecha de envío ni una fecha de referencia. Por eso **no podemos convertir responsablemente «jueves» en una fecha exacta**. El modelo debe señalar que ese dato es ambiguo, solicitar contexto o devolver el valor de ausencia acordado.

---

## 3. JSON: la forma en que un sistema puede leer la respuesta

**JSON** (*JavaScript Object Notation*) es un formato de intercambio de datos. Utiliza pares de **clave y valor**, con las claves entre comillas dobles.


<div class="lamina-apunte" style="position:relative;display:block;width:100%;margin:18px auto 12px;line-height:0">
  <img src="contenido/construccion-agentes-ia-automatizacion/imagenes/03-json-desde-cero.webp" alt="Esquema de un objeto JSON con campos de texto, número y valor nulo." style="display:block;width:100%;height:auto;max-width:100%;border:1px solid var(--color-divider);border-radius:10px;background:#fff" loading="lazy">
  <a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/imagenes/03-json-desde-cero.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;min-width:32px;min-height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>
  </a>
</div>

Ejemplo válido:

~~~json
{
  "sala": "Sala grande",
  "fecha": null,
  "hora": "18:00",
  "asistentes": 12
}
~~~

### ¿Cómo se interpreta?

- **sala:** es un campo de texto; «Sala grande» es su valor.
- **fecha:** `null` representa un valor nulo (no tenemos una fecha determinada).
- **hora:** «18:00» es texto.
- **asistentes:** `12` es un número.

| Valor JSON | Significado | Ejemplo |
|---|---|---|
| Texto | Cadena de caracteres. | `"Sala grande"` |
| Número | Cantidad numérica. | `12` |
| Booleano | Verdadero o falso. | `true` |
| Nulo | No hay valor. | `null` |

### Tres confusiones frecuentes

1. **El número no es una frase:** `12` no es igual a `"12 personas"`.
2. **No se agrega conversación:** «Aquí está tu JSON» fuera del objeto puede provocar un error en un lector estricto.
3. **La ausencia tiene tipos distintos:** `null` (sin comillas), `"NULL"` (cadena de texto) y `0` (número) **no significan lo mismo**.

En algunas actividades se solicita devolver la palabra `NULL`; si se trabaja en JSON hay que definir expresamente si el sistema receptor espera el texto `"NULL"` o el valor nulo `null`. Es una decisión del **contrato de datos**, no algo que se deba cambiar silenciosamente.

### JSON válido no significa dato correcto

Un objeto puede tener sintaxis perfecta y contener una fecha inventada. Valida por separado:

1. Sintaxis JSON.
2. Presencia de las claves exactas.
3. Tipos de datos.
4. Valores obligatorios.
5. Reglas del negocio.
6. Coincidencia con la fuente de información autorizada.

---

## 4. Zero-shot, few-shot e iteración

### Zero-shot: sin ejemplos


<div class="lamina-apunte" style="position:relative;display:block;width:100%;margin:18px auto 12px;line-height:0">
  <img src="contenido/construccion-agentes-ia-automatizacion/imagenes/04-zero-shot-few-shot.webp" alt="Comparación visual entre zero-shot sin ejemplos y few-shot con ejemplos previos." style="display:block;width:100%;height:auto;max-width:100%;border:1px solid var(--color-divider);border-radius:10px;background:#fff" loading="lazy">
  <a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/imagenes/04-zero-shot-few-shot.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;min-width:32px;min-height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>
  </a>
</div>

En **zero-shot** indicamos la tarea sin incluir ejemplos previos de entrada y salida. Sirve como primera versión para observar cómo responde el modelo.

### Few-shot: con ejemplos claros

En **few-shot** agregamos unos pocos ejemplos de entrada y su resultado esperado, antes de entregar el nuevo documento. **No es un entrenamiento permanente del modelo**, sino una demostración dentro del prompt.

**Ejemplo 1 — solicitud parcialmente completa**

Entrada: «Quiero la Sala Norte a las 15:00 para ocho personas».

Salida esperada:

~~~json
{
  "sala": "Sala Norte",
  "fecha": null,
  "hora": "15:00",
  "asistentes": 8
}
~~~

**Ejemplo 2 — información insuficiente**

Entrada: «Hola, quisiera consultar cómo reservar una sala».

Salida esperada:

~~~json
{
  "sala": null,
  "fecha": null,
  "hora": null,
  "asistentes": null
}
~~~

Estos ejemplos enseñan tanto el formato como la regla de **no inventar valores ausentes**.

### ¿Qué significa iterar?

Iterar es **probar, observar el error, ajustar y volver a probar**.

1. Escribe una versión inicial de cinco bloques.
2. Prueba con un documento y guarda la respuesta exacta.
3. Contrasta con los valores que deberían aparecer.
4. Detecta problemas de formato o contenido.
5. Modifica la instrucción o agrega ejemplos.
6. Repite con textos distintos y casos difíciles.

No basta con probar una sola entrada. Un prompt debe evaluarse también con información incompleta, formatos distintos y documentos que mencionen varios números.

### ¿Por qué usar primero un entorno de pruebas?

Un chat o *playground* permite revisar el prompt **antes** de conectarlo a un flujo real. Así no se envían correos ni se registran datos erróneos mientras se experimenta.

No utilices documentos con datos personales o información confidencial en servicios de prueba sin autorización y controles adecuados.

---

## 5. Alucinaciones y sesgos: por qué no debemos confiar a ciegas

### Alucinación


<div class="lamina-apunte" style="position:relative;display:block;width:100%;margin:18px auto 12px;line-height:0">
  <img src="contenido/construccion-agentes-ia-automatizacion/imagenes/05-alucinaciones-sesgos.svg" alt="Comparación ilustrada de alucinación, sesgo y controles de calidad en la IA." style="display:block;width:100%;height:auto;max-width:100%;border:1px solid var(--color-divider);border-radius:10px;background:#fff" loading="lazy">
  <a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/imagenes/05-alucinaciones-sesgos.svg" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;min-width:32px;min-height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>
  </a>
</div>

Una **alucinación** es una afirmación o dato generado sin respaldo suficiente en la información proporcionada.

Si el correo dice «No se distingue la cantidad de asistentes» y la IA responde `"asistentes": 20`, el dato puede ser plausible, pero **no está sustentado**.

En una automatización, esa respuesta inventada podría terminar guardada en una base de datos y generar decisiones incorrectas.

### Sesgo

Un **sesgo** es una distorsión sistemática que puede generar resultados desiguales o injustos. Aparece especialmente en tareas de clasificación o evaluación de personas.

Si un sistema toma decisiones que afectan a alguien, debe haber criterios verificables y una supervisión humana apropiada.

### Barreras técnicas

| Problema | Control |
|---|---|
| Dato ausente | Instruir valor de ausencia y activar revisión si es obligatorio. |
| Dato inventado | Comparar con el documento original; evitar inferencias injustificadas. |
| Texto conversacional | Exigir JSON estricto y verificar que se pueda analizar. |
| Tipo incorrecto | Validar campos, números, textos y rangos permitidos. |
| Documento ambiguo | Solicitar aclaración o revisión humana. |
| Sesgo en una clasificación | Revisar criterios y resultados; incorporar supervisión. |
| Instrucciones dentro del texto analizado | Tratarlas como datos no confiables, no como órdenes. |

### La temperatura

Algunos modelos permiten ajustar un parámetro llamado **temperatura**, que influye en la variabilidad de la generación. Un valor bajo suele ser apropiado para tareas de extracción repetitiva, cuando el proveedor admite ese control.

**Importante:** temperatura `0` **no garantiza** respuestas idénticas ni elimina las alucinaciones. Se necesita validar cada salida, independientemente de ese ajuste.

### ¿Qué es un fallback?

Un **fallback** es una ruta de contingencia cuando una automatización no puede continuar de forma segura.

Por ejemplo:

1. La IA no encuentra la cantidad de personas y entrega `null`.
2. El validador reconoce que el campo es obligatorio.
3. La reserva **no se registra ni confirma automáticamente**.
4. Se solicita aclaración o se deriva el caso.
5. Se conserva un registro del incidente.

El sistema no debe completar un dato inexistente únicamente para que el flujo no se detenga.

---

## 6. Conexión con AS-IS y TO-BE


<div class="lamina-apunte" style="position:relative;display:block;width:100%;margin:18px auto 12px;line-height:0">
  <img src="contenido/construccion-agentes-ia-automatizacion/imagenes/06-flujo-ia-automatizacion.webp" alt="Secuencia desde mensaje hasta interpretación con IA, JSON, validación y acción del sistema." style="display:block;width:100%;height:auto;max-width:100%;border:1px solid var(--color-divider);border-radius:10px;background:#fff" loading="lazy">
  <a class="btn btn-secondary" href="contenido/construccion-agentes-ia-automatizacion/imagenes/06-flujo-ia-automatizacion.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;min-width:32px;min-height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>
  </a>
</div>

Con el centro comunitario podemos comparar los procesos.

**AS-IS — Actual:** una persona recibe el mensaje, lo lee, extrae los datos, pide aclaraciones si falta algo, revisa la agenda y responde.

**TO-BE — Propuesto:** el mensaje se recibe automáticamente, la IA extrae campos, el sistema valida el resultado, pide aclaraciones si es necesario y consulta la agenda real antes de confirmar.

**Responsabilidades separadas:**

- **IA:** interpretar información escrita en lenguaje natural.
- **Orquestador:** conectar herramientas y aplicar las condiciones del flujo.
- **Fuente de verdad:** determinar disponibilidad o valores operativos reales.
- **Persona responsable:** resolver excepciones y decisiones que exijan criterio humano.

El modelo de lenguaje no debe asumir todas esas funciones a la vez.

---

## 7. Preparación para el laboratorio y la auditoría

### Laboratorio de prompt iterativo

El trabajo práctico plantea construir una primera instrucción **zero-shot** y mejorarla incorporando ejemplos **few-shot**. Para prepararte:

- Reconoce los cinco bloques de la instrucción.
- Especifica con claridad los campos y su formato.
- Define qué ocurre si un valor falta.
- Incorpora al menos dos ejemplos de entrada y salida.
- Prueba casos fáciles y casos límite.
- Guarda la instrucción final y la respuesta **tal como la devolvió el modelo**.

### Auditoría crítica de resultados

La segunda actividad se concentra en identificar fallas de extracción y formato, proponer correcciones y documentar la trazabilidad del trabajo.

Para analizar una respuesta, pregúntate:

1. ¿La información realmente aparece en el documento?
2. ¿Los nombres de campos y los tipos son correctos?
3. ¿La salida es JSON válido sin texto extra?
4. ¿La IA inventó algo o dejó un dato ambiguo como si fuera seguro?
5. ¿Qué instrucción podría mejorar el comportamiento?
6. ¿Qué verificación debería aplicar el sistema **después** del modelo?
7. ¿Qué ruta de contingencia se ejecutaría si falla?

**Distingue siempre** el diagnóstico del error, la corrección del prompt y la validación técnica del sistema: son tres capas distintas.

---

## 8. Resumen rápido

| Concepto | Idea que debes recordar |
|---|---|
| Gestión cognitiva | Interpretar y clasificar información con ayuda de IA. |
| Datos estructurados | Campos y formatos definidos. |
| Prompt engineering | Diseñar instrucciones claras, restrictivas y probadas. |
| JSON | Formato de intercambio con sintaxis y tipos. |
| Zero-shot | Instrucción sin ejemplos. |
| Few-shot | Instrucción acompañada de ejemplos. |
| Iteración | Probar, detectar fallas y mejorar. |
| Alucinación | Información falsa o no respaldada. |
| Sesgo | Distorsión sistemática en el resultado. |
| Validación | Comprobación externa de la respuesta. |
| Fallback | Ruta segura ante datos incompletos o fallos. |

> **Para recordar:** un buen prompt es importante, pero **no reemplaza las validaciones**, los datos confiables ni la revisión humana cuando sea necesaria.

---

## 9. Autoevaluación

Responde y después revisa la explicación. Son preguntas de repaso; no incluyen las soluciones de las actividades.

~~~quiz
{"pregunta":"¿Cuál es la función apropiada de la IA al leer una solicitud de reserva?","opciones":[{"texto":"Confirmar disponibilidad sin consultar el registro.","ok":false},{"texto":"Extraer los datos indicados y señalar los que falten.","ok":true},{"texto":"Inventar la información necesaria para completar el formulario.","ok":false}],"exp":"La IA interpreta el mensaje; la disponibilidad real y la decisión final requieren verificaciones externas."}
~~~

~~~quiz
{"pregunta":"¿Qué bloque del prompt especifica qué hacer cuando falta un dato?","opciones":[{"texto":"Las reglas y restricciones.","ok":true},{"texto":"Solo el rol.","ok":false},{"texto":"El saludo inicial.","ok":false}],"exp":"Las restricciones pueden indicar explícitamente que nunca se inventen valores y que se utilice un valor de ausencia acordado."}
~~~

~~~quiz
{"pregunta":"¿Qué distingue few-shot de zero-shot?","opciones":[{"texto":"Few-shot incluye pares de ejemplos; zero-shot no.","ok":true},{"texto":"Zero-shot necesita una base de datos nueva.","ok":false},{"texto":"Few-shot garantiza exactitud absoluta.","ok":false}],"exp":"Few-shot ayuda a ilustrar el formato esperado; no elimina por sí solo la necesidad de validar."}
~~~

~~~quiz
{"pregunta":"En JSON, ¿son equivalentes null, \"NULL\" y 0?","opciones":[{"texto":"Sí, representan exactamente lo mismo.","ok":false},{"texto":"No: son nulo, texto y número, respectivamente.","ok":true},{"texto":"Solo si la temperatura vale cero.","ok":false}],"exp":"Los tipos importan: el sistema receptor debe esperar un formato definido de antemano."}
~~~

~~~quiz
{"pregunta":"¿La temperatura cero impide que un modelo invente datos?","opciones":[{"texto":"Sí, elimina todas las alucinaciones.","ok":false},{"texto":"No. Puede reducir variabilidad, pero siguen siendo necesarias las comprobaciones.","ok":true},{"texto":"Sí, porque verifica la información con una base de datos.","ok":false}],"exp":"Los parámetros de generación no sustituyen el contraste con el documento ni las validaciones de negocio."}
~~~