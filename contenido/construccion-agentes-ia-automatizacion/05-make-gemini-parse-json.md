# Automatizaciones con IA en Make: Gemini, JSON y decisiones

En la lectura anterior construimos un circuito de **Google Sheets → Router → Google Sheets**. Allí una columna ya contenía la prioridad. Pero ¿qué pasa si las solicitudes llegan escritas libremente, como correos o mensajes, y nadie ha definido todavía su categoría?

En este segundo módulo veremos **dónde encaja la inteligencia artificial** y por qué una respuesta de Gemini debe transformarse y validarse antes de que un Router pueda utilizarla.

> **Estado del material:** esta lectura explica la arquitectura de una automatización con IA. El tutorial práctico de Gemini, Google AI Studio y **JSON → Parse JSON**, con capturas reales y pruebas, se añadirá cuando se complete y verifique el segundo laboratorio. No confundas los ejemplos con una implementación ya realizada.

---

## 1. Del flujo con reglas a un flujo con IA

En el primer laboratorio construimos un flujo **determinista**: si la columna `Prioridad` dice `Alta`, el filtro envía la fila a `Urgentes`. No necesita interpretar un mensaje ambiguo, porque el dato ya viene clasificado. Esto es automatización **sin un modelo de IA**, y sigue siendo una base importante.

Pero muchas situaciones laborales empiezan con un correo o documento que **no trae las columnas listas**. Por ejemplo, alguien escribe: «Hola, necesito cambiar mi reserva para mañana; ¿me pueden confirmar?». Antes de decidir el destino, hace falta identificar qué solicita la persona.

En un flujo más completo, **la inteligencia artificial puede ayudar a interpretar o extraer información**. Make coordina el proceso; no es el Router quien piensa ni la IA quien configura los filtros.

### Imagina este recorrido

**1. Correo de entrada → 2. IA interpreta → 3. JSON organiza → 4. Router evalúa → 5. Sheets o correo ejecuta una acción.**

| Etapa | ¿Qué recibe o hace? | ¿Es IA? |
|---|---|---|
| **Gmail** | Detecta un correo nuevo. | No; es el disparador. |
| **Modelo de IA** | Interpreta el mensaje y propone campos como tipo de solicitud y prioridad. | **Sí**; usa un modelo generativo. |
| **Parse JSON** | Convierte un texto JSON válido en datos que se pueden mapear. | No; transforma una estructura de datos. |
| **Router y filtros** | Comprueba condiciones explícitas sobre los campos obtenidos. | No; aplica reglas. |
| **Google Sheets / Gmail** | Registra un resultado o envía una comunicación. | No; realiza acciones. |

### Ejemplo de salida que podríamos solicitarle a una IA

Imagina que llega un correo ficticio solicitando modificar una reserva. El modelo podría devolver:

```json
{
  "tipo_solicitud": "cambio_de_reserva",
  "prioridad": "Normal",
  "requiere_revision": true
}
```

Este JSON **es un ejemplo ilustrativo, no la respuesta de una ejecución real**. El módulo `Parse JSON` permitiría acceder a los campos por separado. Después, un filtro podría comprobar `requiere_revision == true` y enviar el caso a revisión humana.

**Lo importante:** una respuesta de IA puede equivocarse, omitir campos o generar un JSON inválido. Por eso, en un flujo real debemos comprobar que la salida tenga la estructura esperada, validar valores y definir qué hacer si falta información. Elegir temperatura 0 o pedir «solo JSON» **no garantiza** una respuesta perfecta.

### ¿Qué cambia respecto a nuestra práctica?

- En el primer laboratorio, la prioridad viene **escrita directamente en una columna**; por eso el Router puede leerla sin IA.
- En una automatización con IA, la prioridad podría ser una **propuesta extraída de un texto** y necesitar validación antes de activar las rutas.
- El principio del mapeo es igual en ambos casos: seleccionar el campo correcto del módulo anterior y enviarlo al destino adecuado.
- Los **bundles**, las **collections** (objetos con varios campos) y los **arrays** (listas de elementos) permiten trabajar con información más compleja. Cuando una lista contiene varios elementos, puede ser necesario usar un **Iterator** para tratarlos individualmente.

**Este apartado explica la arquitectura conceptual. El primer laboratorio documenta un escenario con Google Sheets y Router; esta segunda lectura aún no presenta una conexión Gemini verificada.** Para incorporar IA de verdad harían falta una conexión autorizada, un modelo disponible, pruebas, validaciones y revisión de permisos y costos.

---



## 2. Qué cambia al conectar Gemini desde Make

**Google AI Studio** permite gestionar el acceso a modelos Gemini mediante claves API para un proyecto. **Make** utiliza una conexión autorizada para comunicarse con ese servicio. La clave es una credencial: no debe mostrarse en capturas, documentos, archivos públicos ni mensajes.

En el nuevo laboratorio trabajaremos con **una hoja de cálculo y un escenario independientes**, reutilizando la misma cuenta de Google del entorno de prueba. Eso permite comparar ambos métodos sin alterar los registros y filtros del primer ejercicio.

El recorrido propuesto para practicar es:

`Google Sheets (Watch New Rows) → Google Gemini AI → JSON (Parse JSON) → Router → Google Sheets (Add a Row)`

La diferencia crucial es que **Gemini recibe una descripción en lenguaje natural**, mientras que **Parse JSON convierte su respuesta en campos individuales**. Solo entonces el Router compara condiciones como `prioridad = Alta` o `prioridad = Normal`.

## 3. Para qué sirve Parse JSON

Una respuesta con aspecto de JSON todavía puede ser **texto**. Por ejemplo:

```json
{
  "categoria": "soporte",
  "prioridad": "Alta",
  "resumen": "No puedo acceder a la cuenta",
  "requiere_revision": true
}
```

El módulo **JSON → Parse JSON** interpreta ese texto y, con una estructura de datos apropiada, pone a disposición cuatro variables:

| Campo | Tipo esperado | Uso en el flujo |
|---|---|---|
| `categoria` | Texto | Identificar el tipo de solicitud |
| `prioridad` | Texto | Aplicar filtros de las rutas |
| `resumen` | Texto | Registrar una explicación breve |
| `requiere_revision` | Booleano | Señalar los casos que requieren intervención humana |

El módulo debe aparecer **después de Gemini y antes del Router**. Si el modelo devuelve texto extra, campos faltantes o un JSON inválido, el resultado necesita corrección o un manejo de errores; no debemos darlo por válido automáticamente.

## 4. Cómo comprobar si la automatización funciona

No basta con que el escenario se vea conectado. En la práctica se debe comprobar que:

1. El disparador detecte una fila ficticia nueva.
2. Gemini reciba la descripción correcta y entregue una respuesta.
3. Parse JSON extraiga `categoria`, `prioridad`, `resumen` y `requiere_revision` con los tipos adecuados.
4. Los filtros del Router utilicen **campos obtenidos del módulo Parse JSON**, no texto escrito manualmente como sustituto.
5. Google Sheets registre los valores en la pestaña correspondiente.
6. Los casos ambiguos, con información insuficiente o con errores de formato no terminen clasificados silenciosamente.

**Diferencia para recordar:** la IA propone una interpretación; las reglas del Router determinan qué acción ejecutar. La supervisión y validación siguen siendo necesarias.

---

## Para recordar

- **Gemini interpreta** información que puede llegar como texto libre.
- **Parse JSON estructura** el resultado en variables independientes.
- **Router evalúa** condiciones explícitas sobre esas variables.
- **Google Sheets registra** los resultados.
- **Una salida estructurada no es garantía de exactitud:** hay que validar datos, gestionar errores y proteger credenciales.

El tutorial paso a paso de este laboratorio se integrará aquí cuando sus configuraciones y capturas estén verificadas.
