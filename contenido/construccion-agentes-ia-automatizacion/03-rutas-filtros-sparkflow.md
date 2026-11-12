<!-- secciones: desplegables -->

# Rutas y filtros: cómo tomar decisiones en una automatización

## Antes de comenzar

Imagina que una biblioteca recibe solicitudes por correo. Unas personas preguntan por horarios, otras quieren renovar un préstamo y otras informan de un problema. Si todas las solicitudes siguen el mismo camino, alguien tendrá que revisarlas y clasificarlas manualmente.

Para construir un flujo que pueda **decidir adónde enviar cada mensaje** necesitamos dos conceptos: **rutas** y **filtros**. También necesitamos saber qué sucede cuando hay varias condiciones verdaderas y cómo evitar que un dato erróneo llegue al siguiente sistema.

En este apunte aprenderás a interpretar esos elementos con ejemplos ficticios, sin necesidad de escribir código. Al final encontrarás el juego interactivo **SparkFlow** para practicar estas ideas con circuitos, datos JSON y misiones progresivas.

> **Idea principal:** la ruta representa un camino posible; el filtro determina cuándo los datos pueden recorrerlo.

---

## 1. ¿Qué es una ruta?

Una **ruta** es un camino de ejecución por el que puede continuar la información dentro de una automatización. En Make, un **Router (enrutador)** permite dividir un flujo en varias ramas.

Por ejemplo:

**Correo recibido → Router → Ruta de consultas / Ruta de renovaciones / Ruta de incidencias**

Cada ruta puede terminar en una acción diferente: crear una fila, enviar una notificación, solicitar información o derivar el caso para revisión.

El router **no adivina cuál es la ruta correcta**. Son las condiciones asociadas a cada salida las que determinan si los datos continúan por ella.

### Una ruta no significa necesariamente una sola opción

Si varias rutas cumplen sus filtros, un router puede permitir que **más de una ruta** se ejecute para la misma entrada. No todos los routers funcionan como un interruptor exclusivo de «una opción u otra».

Esto importa cuando, por ejemplo, un mensaje debe **registrarse** y además **enviar una alerta**: ambas rutas podrían ser válidas simultáneamente.

### Primera lámina: rutas y filtros

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 14px;line-height:0">
  <img src="contenido/construccion-agentes-ia-automatizacion/imagenes/03-rutas-filtros-hoja.webp" alt="Dos hojas ilustradas de cuaderno sobre rutas, filtros, su comparación y un ejemplo de bifurcación condicional en un flujo." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy">
  <a href="contenido/construccion-agentes-ia-automatizacion/imagenes/03-rutas-filtros-hoja.webp" target="_blank" rel="noopener noreferrer" title="Ampliar lámina" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;padding:0;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;box-shadow:0 2px 8px rgba(0,0,0,.14);text-decoration:none;line-height:1">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg>
  </a>
</div>

*Apoyo visual elaborado para estudiar. Los iconos y escenarios de la lámina son ilustrativos; la configuración exacta se realiza en la herramienta utilizada.*

---

## 2. ¿Qué es un filtro?

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

## 3. Comparadores: cómo expresar una condición

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

## 4. AND y OR: combinar condiciones

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

## 5. ¿Pueden activarse varias rutas a la vez?

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

## 6. Validar los datos antes de tomar decisiones

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

## 7. SparkFlow: un juego para entender rutas y filtros

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

## 8. Solucionario de las 13 misiones — solo después de intentar el juego

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
