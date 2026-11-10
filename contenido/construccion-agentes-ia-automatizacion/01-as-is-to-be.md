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

### Simbología para representar el proceso AS-IS

Para dibujar un proceso AS-IS podemos utilizar un **diagrama de flujo**. Cada forma tiene un significado; así se distinguen las acciones, las decisiones y el recorrido de la información. **AS-IS no es una notación gráfica por sí misma**: es una forma de describir el estado actual y puede documentarse con distintas notaciones.

| Símbolo o forma | Nombre | ¿Qué representa? | Ejemplo en nuestro caso |
|---|---|---|---|
| **Óvalo** o rectángulo de extremos redondeados | Inicio / fin (terminal) | Dónde comienza o termina el proceso | «Solicitud recibida» / «Respuesta enviada» |
| **Rectángulo** | Actividad o proceso | Una tarea que se ejecuta | «Revisar correo» |
| **Rombo** | Decisión | Una condición que abre caminos alternativos | «¿Datos completos?» con salidas «Sí» y «No» |
| **Paralelogramo** | Entrada / salida | Datos que ingresan al proceso o se entregan como resultado | «Recibir datos de la solicitud» |
| **Flecha** | Línea de flujo | Orden y dirección de las actividades | De «Revisar datos» a «Consultar planilla» |
| **Círculo pequeño** | Conector | Continuidad del flujo en otro punto del mismo diagrama, cuando una línea sería extensa o confusa | Conectar dos partes del recorrido con la misma letra |
| **Rectángulo con doble borde lateral** | Subproceso predefinido | Una actividad cuyo detalle se explica en otro diagrama | «Gestionar devolución» |
| **Documento** (base ondulada) | Documento o registro | Un documento que participa en el proceso | «Correo de solicitud» o «Comprobante» |

**Representación visual de los ocho símbolos:**

<img src="contenido/construccion-agentes-ia-automatizacion/diagramas/simbologia-diagrama-flujo.svg" alt="Lámina de simbología de diagrama de flujo: óvalo de inicio y fin, rectángulo de actividad, rombo de decisión, paralelogramo de entrada y salida, flecha, círculo conector, subproceso y documento." style="display:block;width:100%;height:auto;max-width:100%;margin:16px auto;border-radius:10px" loading="lazy">

[Ver la simbología en tamaño completo](contenido/construccion-agentes-ia-automatizacion/diagramas/simbologia-diagrama-flujo.svg)

**Cómo leerlos:** el óvalo marca el comienzo; las flechas indican hacia dónde avanzar; los rectángulos son actividades; y cada rombo hace una pregunta cuyas salidas deben estar identificadas, normalmente «Sí» y «No». Un flujo puede terminar en distintos resultados.

#### Identifiquemos los símbolos en el ejemplo

- **Inicio (óvalo):** «Persona necesita reservar un equipo».
- **Entrada (paralelogramo):** «Recibir correo con datos de reserva».
- **Actividad (rectángulo):** «Revisar los datos del correo».
- **Decisión (rombo):** «¿La solicitud está completa?».
  - **No →** «Pedir información faltante» y esperar la respuesta; después, volver a revisar.
  - **Sí →** «Consultar disponibilidad en la planilla».
- **Decisión (rombo):** «¿Hay equipo disponible?».
  - **No →** «Comunicar indisponibilidad» y finalizar.
  - **Sí →** «Registrar reserva y enviar confirmación» y finalizar.

Este esquema **describe lo que sucede**, incluso la vuelta atrás y la espera: todavía no propone ninguna automatización.

```nota
Estos símbolos pertenecen a la convención habitual de diagramas de flujo. **BPMN** es otra notación para modelar procesos: utiliza eventos (círculos), actividades (rectángulos redondeados), compuertas (rombos), flujos y, cuando corresponde, carriles para identificar responsables. No conviene mezclar símbolos de ambas notaciones sin explicarlo.
```

#### Buenas prácticas al dibujar

1. Asigna a cada actividad un nombre que comience con un verbo, como «Verificar disponibilidad».
2. Escribe preguntas concretas en los rombos y etiqueta todas sus salidas.
3. Representa los ciclos de corrección y las esperas: ocultarlos impediría detectar problemas reales.
4. Señala quién realiza cada tarea si participan varias personas.
5. Usa la misma simbología en todo el diagrama y evita flechas que se crucen innecesariamente.
6. No uses un rombo para cada actividad; resérvalo para decisiones que realmente cambian el recorrido.

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

