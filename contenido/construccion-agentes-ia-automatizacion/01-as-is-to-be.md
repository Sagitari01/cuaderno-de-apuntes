<!-- secciones: desplegables -->

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

### Simbología para modelar procesos (BPMN)

Para representar el estado **AS-IS** de un proceso podemos utilizar la notación **BPMN**. AS-IS describe lo que ocurre actualmente; BPMN proporciona elementos visuales para representar sus participantes, actividades, decisiones e intercambios de información.

#### Primero, observa la simbología

La lámina está dividida en tres grupos: **contenedores**, **elementos del proceso** y **conexiones**. Observa las formas y los trazos antes de revisar sus significados.

<img src="contenido/construccion-agentes-ia-automatizacion/diagramas/simbologia-bpmn.svg" alt="Simbología BPMN organizada en tres secciones: pool y carriles; eventos de inicio y fin, actividad y compuerta; flujo de secuencia, flujo de mensaje y asociación." style="display:block;width:100%;max-width:100%;height:auto;margin:22px auto 26px;border-radius:12px" loading="lazy">

[Ver la simbología en tamaño completo](contenido/construccion-agentes-ia-automatizacion/diagramas/simbologia-bpmn.svg)

#### Después, interpreta la leyenda

**Contenedores y responsables**

| Elemento | ¿Para qué sirve? | Ejemplo en el caso |
|---|---|---|
| **Pool** | Representa a un participante del proceso y delimita su espacio. | Centro comunitario. |
| **Carril** | Divide el trabajo del participante según sus roles o responsables. | Encargada de reservas. |

**Elementos del proceso**

| Elemento | ¿Para qué sirve? | Ejemplo en el caso |
|---|---|---|
| **Evento de inicio** (círculo de borde fino) | Indica qué desencadena el proceso. | Llega una solicitud de reserva. |
| **Evento de fin** (círculo de borde grueso) | Indica la conclusión de una ruta. | Se confirma o rechaza la reserva. |
| **Actividad** (rectángulo redondeado) | Representa una tarea realizada por alguien. | Revisar solicitud o consultar disponibilidad. |
| **Compuerta exclusiva** (rombo con X) | Dirige el recorrido hacia una alternativa según una condición. | ¿El equipo está disponible? |

**Conexiones**

| Elemento | Representación y uso |
|---|---|
| **Flujo de secuencia** | Línea continua con flecha sólida. Indica el orden en que se ejecutan actividades y eventos. |
| **Flujo de mensaje** | Línea discontinua con punta de flecha abierta. Representa mensajes entre participantes distintos; **no se utiliza para conectar actividades dentro del mismo pool**. |
| **Asociación** | Línea punteada. Relaciona anotaciones o información con elementos sin alterar el orden de ejecución. |

#### Cómo aplicar la simbología al AS-IS

En nuestro caso, el **centro comunitario** puede modelarse como participante con un pool, y la **encargada de reservas** como responsable dentro de un carril. La persona solicitante puede representarse como otro participante si necesitamos mostrar explícitamente el intercambio entre ambos.

Al llegar una solicitud ocurre un **evento de inicio**. Luego se ejecutan **actividades** para revisar datos y consultar disponibilidad. Una **compuerta exclusiva** decide si se registra una reserva o se comunica que el equipo no está disponible. Las actividades del mismo participante se enlazan con **flujos de secuencia**, mientras que las comunicaciones con otro participante se pueden mostrar mediante **flujos de mensaje**. Una ruta termina con su correspondiente **evento de fin**.

```nota
Esta es una selección introductoria de BPMN. Existen otros tipos de eventos, compuertas, actividades y conexiones. Para evitar confusiones, no hay que tratar el flujo de mensaje como una flecha de secuencia ni dibujar mensajes entre carriles del mismo participante.
```

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

<iframe src="contenido/construccion-agentes-ia-automatizacion/diagramas/visor-bpmn.html?src=as-is-solicitudes.bpmn" title="Diagrama BPMN AS-IS del proceso de reserva de equipos" loading="lazy" style="width:100%;height:340px;border:1px solid var(--color-divider)"></iframe>

<a href="contenido/construccion-agentes-ia-automatizacion/diagramas/visor-bpmn.html?src=as-is-solicitudes.bpmn" target="_blank" rel="noopener">Abrir en pantalla completa</a>

Las respuestas negativas y los datos incompletos generan ramas y posibles esperas, y el diagrama las muestra explícitamente.

### ¿Qué es un cuello de botella?

Un **cuello de botella** es una etapa cuya capacidad limita el flujo del proceso o provoca que las solicitudes se acumulen antes de ella. No necesariamente es la tarea más difícil: a veces es una aprobación que se hace una vez al día o una sola persona que revisa todo.

**Ejemplo con números hipotéticos, a pequeña escala:**

| Etapa | Tiempo de trabajo aproximado por solicitud |
|---|---:|
| Leer el correo y comprobar los datos | 1–2 minutos |
| Consultar disponibilidad en la planilla | 2–3 minutos |
| Registrar la reserva y responder | 2–3 minutos |

Una solicitud completa puede requerir **5–8 minutos de trabajo activo**. Sin embargo, eso no significa que se responda inmediatamente: puede pasar **10–15 minutos esperando** a que la persona encargada termine otra tarea.

Imaginemos que llegan **10 solicitudes durante un día**, pero la encargada solo dispone de un bloque de **40 minutos** para revisar reservas. Si cada revisión con sus verificaciones le toma aproximadamente **5 minutos**, alcanza a procesar **8 solicitudes** en ese bloque y **2 quedan pendientes**. Esto sugiere un posible cuello de botella por **tiempo disponible para la revisión**, no porque cada solicitud sea especialmente compleja.

Esta acumulación es ilustrativa: no implica que todos los días se sumen exactamente dos solicitudes, porque la demanda y el tiempo disponible pueden cambiar.

La capacidad de una etapa orienta el diagnóstico, pero para confirmarlo deben observarse colas, tiempos y variación de la demanda.

### ¿Cómo identificarlo sin pasar todavía al TO-BE?

1. **Observar el recorrido real:** seguir varias solicitudes desde su llegada hasta la respuesta.
2. **Medir tiempos de trabajo y de espera por separado:** una revisión puede durar 5 minutos, pero pasar otros 10–15 minutos esperando a ser atendida.
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

<iframe src="contenido/construccion-agentes-ia-automatizacion/diagramas/visor-bpmn.html?src=to-be-solicitudes.bpmn" title="Diagrama BPMN TO-BE del proceso de reserva de equipos con IA" loading="lazy" style="width:100%;height:420px;border:1px solid var(--color-divider)"></iframe>

<a href="contenido/construccion-agentes-ia-automatizacion/diagramas/visor-bpmn.html?src=to-be-solicitudes.bpmn" target="_blank" rel="noopener">Abrir en pantalla completa</a>

Las ramas de información incompleta, indisponibilidad y revisión humana se mantienen visibles en el diagrama.

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

---

## 4. Autoevaluación

Estas preguntas permiten comprobar la comprensión de los conceptos después de revisar todo el apunte. No forman parte de una evaluación calificada.

```quiz
? ¿Cuál es el objetivo principal de un modelo AS-IS?
+ Representar cómo funciona realmente el proceso actual, con sus decisiones y problemas.
- Describir únicamente cómo debería funcionar el proceso después de automatizarlo.
- Elegir de inmediato una herramienta de inteligencia artificial.
> AS-IS documenta la situación presente antes de diseñar mejoras.
```

```quiz
? ¿Qué figura se utiliza normalmente para representar una decisión en un diagrama de flujo tradicional?
- Rectángulo.
+ Rombo.
- Paralelogramo.
> El rombo representa una condición con caminos alternativos, como «Sí» y «No».
```

```quiz
? Si una solicitud tarda 5 minutos en revisarse, pero espera otros 15 minutos antes de ser atendida, ¿qué dato ayuda a detectar una posible acumulación?
- Solo el tiempo de ejecución de la revisión.
+ El tiempo de espera y la cantidad de solicitudes pendientes.
- Únicamente la cantidad de correos enviados.
> Separar tiempo activo y espera permite identificar dónde se forman colas.
```

```quiz
? ¿Cuál de estas propuestas corresponde a un modelo TO-BE?
- Dibujar únicamente el recorrido que se ejecuta hoy.
+ Proponer un flujo mejorado, con controles y criterios para medir resultados.
- Omitir las excepciones y los responsables.
> TO-BE representa la situación futura propuesta, no solo una descripción del estado actual.
```

```quiz
? En el TO-BE del caso, ¿qué componente debe verificar que un equipo esté realmente disponible?
- El modelo de IA basándose únicamente en el texto del mensaje.
+ El sistema que consulta el registro de disponibilidad autorizado.
- La persona solicitante, sin comprobación.
> La IA puede interpretar solicitudes, pero la disponibilidad real debe comprobarse con una fuente confiable.
```
