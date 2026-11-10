# Modelamiento de procesos: comprender el presente y diseñar el futuro

## Antes de comenzar

Un proceso es una secuencia de actividades que transforma una entrada en un resultado. Para mejorarlo, primero hay que comprender cómo funciona realmente, incluso cuando existen demoras, excepciones o trabajo informal.

En este apunte veremos dos modelos complementarios: **AS-IS** (situación actual) y **TO-BE** (situación propuesta). Usaremos un único caso **hipotético**, independiente de cualquier organización real: la **reserva de equipos audiovisuales en un centro comunitario**.

> **Importante:** los tiempos y cantidades de este ejemplo son inventados con fines didácticos. No son mediciones reales.

---

## 1. AS-IS: ¿cómo funciona hoy?

**AS-IS** significa «tal como es». Es la representación del proceso **actual**, no de cómo nos gustaría que fuera.

Su utilidad es hacer visible el trabajo cotidiano: quién interviene, qué datos recibe, qué decisiones toma, qué tareas realiza, qué herramientas utiliza y dónde aparecen retrasos.

En un levantamiento AS-IS conviene identificar:

- **Inicio y resultado:** qué dispara el proceso y cuándo se considera completado.
- **Actores y responsabilidades:** quién realiza cada actividad.
- **Actividades y decisiones:** pasos, bifurcaciones y condiciones.
- **Entradas y salidas:** formularios, mensajes, registros y respuestas.
- **Esperas y traspasos:** cuándo una solicitud queda detenida o cambia de responsable.
- **Excepciones:** información incompleta, equipos no disponibles o solicitudes duplicadas.

### Caso hipotético: préstamo de equipos

Una persona solicita por correo un proyector o una cámara. Una encargada revisa su mensaje, busca la disponibilidad en una planilla, solicita datos faltantes, confirma la reserva y actualiza el registro.

**Flujo AS-IS observado:**

1. La persona envía un correo con su solicitud.
2. La encargada abre el correo y revisa los datos.
3. Si faltan datos, escribe solicitando aclaraciones y espera respuesta.
4. Consulta manualmente la planilla de disponibilidad.
5. Si hay equipo, anota la reserva; de lo contrario, comunica que no está disponible.
6. Redacta y envía una respuesta de confirmación o rechazo.

**Representación resumida:**

`Inicio → Recibir correo → ¿Datos completos? → Consultar disponibilidad → ¿Equipo libre? → Registrar reserva → Responder`

Las respuestas negativas y los datos incompletos generan ramas y posibles esperas. Un diagrama de flujo ayuda a mostrarlas explícitamente.

### ¿Qué es un cuello de botella?

Un **cuello de botella** es una etapa cuya capacidad limita el flujo del proceso o provoca que las solicitudes se acumulen antes de ella. No necesariamente es la tarea más difícil: a veces es una aprobación que se hace una vez al día o una sola persona que revisa todo.

**Ejemplo con números hipotéticos:**

| Etapa | Capacidad estimada |
|---|---:|
| Recepción de solicitudes | 40 por día |
| Revisión manual y consulta de planilla | 15 por día |
| Registro y envío de confirmaciones | 30 por día |

Si llegan 25 solicitudes al día, pero solo pueden revisarse 15, se acumulan **10 solicitudes diarias** mientras las condiciones se mantengan. En este escenario, la revisión manual es el principal **candidato a cuello de botella**.

La capacidad de una etapa orienta el diagnóstico, pero para confirmarlo deben observarse colas, tiempos y variación de la demanda.

### ¿Cómo identificarlo sin pasar todavía al TO-BE?

1. **Observar el recorrido real:** seguir varias solicitudes desde su llegada hasta la respuesta.
2. **Medir tiempos de trabajo y de espera por separado:** una revisión puede durar 5 minutos, pero permanecer 6 horas en cola.
3. **Contar solicitudes pendientes:** registrar en qué etapa se acumulan y durante cuánto tiempo.
4. **Revisar retrabajo:** observar cuántas solicitudes vuelven atrás por información incompleta.
5. **Comparar capacidad y demanda:** distinguir una sobrecarga sostenida de un aumento puntual de solicitudes.
6. **Validar con quienes ejecutan el proceso:** contrastar lo dibujado con lo que sucede realmente.

### Otros hallazgos útiles en el AS-IS

**Tiempo de ciclo y tiempo total:** el primero mide cuánto tarda una actividad; el segundo, cuánto transcurre desde la solicitud hasta el resultado, incluidas las esperas.

**Puntos de decisión:** preguntas como «¿faltan datos?» o «¿hay disponibilidad?» permiten dibujar ramas que suelen ocultarse en listas lineales.

**Traspasos entre personas:** cada cambio de responsable puede introducir espera, pérdida de contexto o duplicación de información.

**Retrabajo y errores:** volver a solicitar datos o corregir reservas son señales que vale la pena registrar.

**Causa raíz:** preguntar sucesivamente «¿por qué ocurre?» ayuda a no confundir un síntoma (la cola) con su causa (datos incompletos, una planilla desactualizada o disponibilidad de personal).

**Indicadores de referencia:** cantidad de solicitudes por día, porcentaje de casos incompletos, tiempo de respuesta y tamaño de la cola. Son el punto de comparación para evaluar una mejora más adelante.

```nota
En la etapa AS-IS el objetivo es comprender y medir, no proponer automatizaciones de inmediato. Un diagnóstico equivocado puede llevar a automatizar la parte incorrecta.
```

```ejercicio
Sin diseñar todavía una solución, observa el caso de préstamo de equipos. Identifica: (1) el inicio y el final, (2) dos decisiones, (3) un posible cuello de botella, (4) una excepción y (5) tres datos que medirías para comprobar tu diagnóstico.
```

---

## 2. TO-BE: ¿cómo queremos que funcione?

**TO-BE** significa «como debería ser». Se construye **después** del análisis AS-IS para describir un proceso futuro que responda a problemas y objetivos concretos.

No consiste simplemente en agregar tecnología: también puede significar eliminar pasos redundantes, aclarar responsabilidades, estandarizar formularios o mejorar controles.

Para diseñarlo conviene definir:

- **Objetivo medible:** por ejemplo, reducir el tiempo de respuesta y los registros duplicados.
- **Cambios propuestos:** qué pasos se eliminan, simplifican o automatizan.
- **Responsable de excepciones:** qué decisiones quedan a cargo de una persona.
- **Datos y controles:** cómo se verifica la disponibilidad y se evita una reserva incorrecta.
- **Indicadores de éxito:** qué valores se compararán con la línea base AS-IS.

### Mismo caso, ahora con IA y automatización

El centro comunitario propone recibir las solicitudes a través de un formulario o correo. Una herramienta con IA puede **interpretar el texto** de una solicitud, identificar equipo, fecha y horario, y detectar información faltante. Después, un sistema consulta la disponibilidad en una fuente de datos confiable.

**Posible flujo TO-BE:**

1. La persona envía la solicitud.
2. Un componente de IA extrae los datos relevantes y señala ambigüedades.
3. Una validación comprueba que los campos obligatorios estén completos.
4. Si faltan datos, se solicita una aclaración; si el caso es ambiguo, pasa a revisión humana.
5. El sistema consulta la disponibilidad **en el registro oficial**, no en la respuesta generada por la IA.
6. Si el equipo está disponible, una operación controlada registra la reserva y evita duplicados.
7. Se envía la confirmación; las solicitudes rechazadas o excepcionales quedan registradas.

**Representación resumida:**

`Solicitud → Interpretación con IA → Validación → Consulta de disponibilidad → Registro controlado → Confirmación`

Las ramas de información incompleta, indisponibilidad y revisión humana deben permanecer visibles en el diagrama.

### ¿Qué hace la IA y qué NO debería hacer?

| Puede aportar la IA | Debe resolverlo un sistema o una persona |
|---|---|
| Extraer equipo, fecha y horario del texto | Verificar disponibilidad real |
| Detectar solicitudes ambiguas | Aplicar reglas y permisos de reserva |
| Sugerir una respuesta clara | Registrar una transacción sin duplicarla |
| Clasificar una incidencia | Resolver conflictos excepcionales |

La IA **no debe inventar disponibilidad** ni confirmar una reserva sin verificarla. La automatización y la IA son componentes distintos: la primera ejecuta reglas y acciones; la segunda ayuda con información poco estructurada o ambigua.

### ¿Cómo comprobar si el TO-BE mejora el proceso?

Comparar antes y después con los mismos indicadores:

- Tiempo total hasta la respuesta.
- Cantidad de solicitudes pendientes.
- Porcentaje de reservas que requieren corrección.
- Porcentaje de solicitudes derivadas a revisión humana.
- Porcentaje de respuestas correctas y verificables.

No se deben prometer reducciones específicas sin probar el sistema con casos representativos. Una prueba piloto permite descubrir fallas antes de ampliar su uso.

```nota
Primero se identifica el problema y se define una mejora comprobable; después se elige la tecnología. Una automatización rápida que registra información incorrecta no representa una mejora.
```

---

## 3. Comparar ambos modelos

| Pregunta | AS-IS | TO-BE |
|---|---|---|
| ¿Qué describe? | Cómo ocurre hoy | Cómo se propone que ocurra |
| ¿Para qué sirve? | Entender, medir y detectar problemas | Diseñar y evaluar mejoras |
| ¿Qué evidencia utiliza? | Observación, entrevistas, tiempos y registros | Objetivos, reglas, pruebas y comparación |
| ¿Qué lugar ocupa la IA? | No es necesaria para describirlo | Puede ser útil si aporta valor al caso |

```quiz
? ¿Qué harías primero si observas que muchas solicitudes quedan pendientes en la revisión?
+ Medir la llegada de solicitudes, la capacidad de revisión y los tiempos de espera.
- Agregar un modelo de IA sin analizar la etapa.
- Eliminar todas las revisiones humanas.
> El diagnóstico AS-IS necesita evidencia antes de decidir una mejora TO-BE.
```

```quiz
? En el TO-BE del ejemplo, ¿quién debería confirmar la disponibilidad real?
- El modelo de IA, basándose solo en el texto recibido.
+ El sistema que consulta el registro de disponibilidad autorizado.
- La persona solicitante, sin comprobación.
> La IA puede interpretar texto, pero la disponibilidad debe verificarse en una fuente confiable.
```

```ejercicio
Diseña el TO-BE del caso después de terminar su diagnóstico AS-IS. Explica qué tarea podría apoyar la IA, qué validaciones serían deterministas, dónde mantendrías revisión humana y qué indicadores usarías para comprobar la mejora.
```
