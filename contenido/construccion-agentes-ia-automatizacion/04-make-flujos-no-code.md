# Tu primera automatización en Make: de una solicitud a su destino

¿Te ha pasado que recibes solicitudes en una hoja y luego tienes que copiarlas manualmente a distintas listas? Además de consumir tiempo, ese trabajo puede generar errores. En este apunte vamos a transformar ese problema en un **flujo visual que trabaja con datos reales de prueba**.

**Lo que aprenderás:** reconocer un disparador, seguir el recorrido de una fila, configurar un Router, comparar un dato con un filtro, mapear columnas y comprobar el resultado. No necesitas saber programar.

> **Sobre las imágenes:** son capturas reales de un laboratorio de ejemplo en Make y Google Sheets. Según la evidencia del laboratorio, se completaron las pruebas indicadas; aquí explicamos lo que muestran las capturas, sin afirmar haber ejecutado nosotros mismos el escenario en la cuenta original. La interfaz puede cambiar de nombre o posición con el tiempo.

---

## 1. Primero entendamos el flujo

Una aplicación recibe la solicitud y otra la organiza. **Make** actúa como coordinador: detecta un dato nuevo, evalúa su prioridad y lo envía al destino adecuado.

**Recorrido:** `Solicitudes (Google Sheets) → Watch New Rows → Router → filtro Alta / filtro Normal → Add a Row (Google Sheets)`.

- **Disparador (trigger):** inicia el trabajo cuando se detecta una nueva fila.
- **Router:** abre varias rutas que pueden ejecutarse de forma independiente.
- **Filtro:** decide si una solicitud puede pasar por una ruta determinada.
- **Acción:** realiza el trabajo final, por ejemplo agregar una fila.
- **Bundle:** conjunto de datos de una fila que Make entrega a los siguientes módulos.

**Importante:** este ejemplo utiliza *Watch New Rows*, que consulta periódicamente Google Sheets cuando el escenario está programado. No es un webhook instantáneo. Para esta práctica lo ejecutaremos manualmente con **Run once**, sin dejar el escenario activo.

---

## 2. Prepara la hoja que recibirá las solicitudes

Crea una hoja de cálculo de laboratorio llamada **Laboratorio Make - Solicitudes**, con tres pestañas: `Solicitudes`, `Urgentes` y `Normales`. Evita utilizar datos de clientes o información personal real.

En **Solicitudes**, escribe exactamente estos encabezados en A1:E1:

| A · ID | B · Nombre | C · Area | D · Prioridad | E · Descripcion |
|---|---|---|---|---|
| SOL-000 | Eva Ruiz | Soporte | Alta | Ensayo del disparador. |

La fila `SOL-000` nos servirá para observar el primer **bundle**. Luego incorporaremos estos casos para probar el escenario:

| ID | Área | Prioridad | Destino esperado |
|---|---|---|---|
| SOL-001 | Soporte | Alta | Urgentes |
| SOL-002 | Ventas | Normal | Normales |
| SOL-003 | Finanzas | Alta | Urgentes |
| SOL-004 | Soporte | Normal | Normales |

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-01.webp" alt="Hoja Solicitudes con columnas ID, Nombre, Area, Prioridad y Descripcion, y fila de ensayo SOL-000." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-01.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 01. Prepara los nombres de columnas y una fila de ensayo en la pestaña de origen.*

En **Urgentes** y **Normales** repite los mismos cinco encabezados y agrega uno más: **F · Estado**. Antes de las pruebas, ambas pestañas deben estar vacías bajo sus encabezados.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-02.webp" alt="Pestañas Urgentes y Normales con seis columnas, incluida Estado, todavía vacías." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-02.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 02. Los destinos tienen una columna extra para registrar el estado asignado automáticamente.*

---

## 3. Abre Make y crea el escenario

En [Make](https://www.make.com/), abre la sección **Scenarios**. Puedes organizar tus pruebas en una carpeta independiente. Pulsa **Create scenario** y comienza con un lienzo vacío.

**Un escenario** es el conjunto completo de módulos conectados: un disparador, una o más decisiones y las acciones que se realizan después.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-03.webp" alt="Menú de Make con la opción Scenarios en la barra lateral." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-03.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 03. Ubica la sección Scenarios.*

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-04.webp" alt="Editor de Make mostrando el lienzo vacío y el botón central para agregar el primer módulo." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-04.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 04. Inicia el escenario desde el botón central, no desde un módulo desconectado.*

Pulsa el **+** central, busca **Google Sheets** y selecciona la aplicación. No elijas todavía una acción de salida: primero necesitamos el disparador.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-05.webp" alt="Selector de aplicaciones de Make con Google Sheets entre las opciones." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-05.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 05. Busca Google Sheets como primer módulo.*

---

## 4. Configura el disparador Watch New Rows

Selecciona **Watch New Rows**. Este módulo vigila las filas nuevas de una pestaña y entrega cada fila como un bundle separado. Su función es **leer**, no escribir.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-06.webp" alt="Lista de módulos de Google Sheets en Make, con Watch New Rows resaltado." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-06.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 06. Selecciona Watch New Rows en lugar de Add a Row.*

En la configuración del disparador:

1. Selecciona una **conexión de Google Sheets autorizada**. Si Make solicita permisos, revisa el consentimiento; puede involucrar más acceso que el archivo concreto del escenario.
2. Busca el archivo de laboratorio y elige la pestaña **Solicitudes**.
3. Configura `Table contains headers = Yes`, `Row with headers = A1:E1` y un límite pequeño de filas para pruebas (por ejemplo, **5**).
4. Revisa **Choose where to start**. El punto inicial determina qué filas considera el escenario como nuevas. Si preparaste las filas antes de activarlo, podrías necesitar seleccionar una fila existente o ajustar ese inicio para la prueba.

No confundas la conexión autorizada (permiso de acceso) con el nombre de la pestaña (qué datos leer).

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-07.webp" alt="Panel de configuración de Watch New Rows con conexión, pestaña Solicitudes, encabezados A1:E1 y límite 5." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-07.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 07. Estos ajustes especifican dónde mirar y cómo interpretar las columnas.*

Ejecuta una prueba con la fila `SOL-000`. Abre el resultado del módulo: verás **ID**, **Nombre**, **Area**, **Prioridad** y **Descripcion**. Make muestra cada campo disponible para usarlo después, por ejemplo en un filtro.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-08.webp" alt="Inspector de ejecución con el bundle de SOL-000 y sus cinco campos." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-08.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 08. El bundle contiene los valores de una fila; todavía no ha sido enviado a ningún destino.*

---

## 5. Divide el trabajo con un Router

Ahora queremos dos destinos: las solicitudes **Alta** irán a `Urgentes` y las **Normal** a `Normales`. En el lienzo, pulsa el **+** que aparece a la salida de **Watch New Rows**. En el selector de aplicaciones que se abre, busca o selecciona **Flow Control** y después elige **Router**. El Router debe quedar conectado al disparador, no suelto en el lienzo.

El Router **no es un interruptor que elige una sola salida por definición**: cada ruta tiene su propio filtro y, si se cumplen varios, pueden ejecutarse varias. En nuestro ejemplo usamos valores excluyentes para que cada solicitud coincida solo con una.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-09.webp" alt="Selector general de aplicaciones de Make: se ve la opción Flow Control; el módulo Router todavía no está seleccionado." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-09.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 09. Este es el selector general de aplicaciones. El siguiente paso es abrir **Flow Control** y escoger **Router**; esta captura todavía no muestra ese clic. Si el menú cambia, puedes buscar «Router» en el cuadro superior.*

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-10.webp" alt="Escenario visual con Google Sheets Watch New Rows, Router y dos salidas." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-10.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 10. Ahora sí aparece el **Router conectado** a Watch New Rows, con dos salidas. Los botones **+** grises indican que todavía falta agregar una acción en cada rama.*

### Configura el primer filtro: Alta prioridad

Abre **Set up a filter** sobre la conexión de la primera rama. Como valor izquierdo, elige el campo **Prioridad** que entrega Watch New Rows (es un valor **dinámico**). El operador será **Text operators → Equal to** y el texto fijo será **Alta**. Nombra la ruta `Alta prioridad`.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-11.webp" alt="Filtro Alta prioridad con el campo Prioridad del disparador, operador Equal to y valor Alta." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-11.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 11. El valor izquierdo cambia para cada fila; Alta es la comparación fija.*

### Configura el segundo filtro: Prioridad normal

Repite el proceso en la segunda ruta, pero compara **Prioridad = Normal**. Nombra la ruta `Prioridad normal`.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-12.webp" alt="Filtro Prioridad normal con Prioridad Equal to Normal." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-12.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 12. Una fila con Alta no debe pasar por esta ruta.*

| Dato recibido | Ruta Alta | Ruta Normal |
|---|---|---|
| `Alta` | Pasa | No pasa |
| `Normal` | No pasa | Pasa |
| `Media` | No pasa | No pasa |

Si la prioridad es `Media`, **ninguna ruta se ejecuta** porque no hemos configurado una ruta de respaldo (*fallback*). Esto no es un error de la aplicación: es una decisión de diseño. En una situación real conviene definir qué hacer con valores inesperados.

---

## 6. Agrega acciones y mapea los datos

En cada rama incorpora **Google Sheets → Add a Row**. A diferencia del disparador, este módulo **escribe una fila** en la pestaña que elijas.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-13.webp" alt="Selector de Google Sheets que resalta el módulo Add a Row." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-13.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 13. Add a Row crea el registro en la hoja de destino.*

En la primera ruta, elige la pestaña **Urgentes**. En los campos `ID`, `Nombre`, `Area`, `Prioridad` y `Descripcion`, selecciona los valores que vienen del bundle de Watch New Rows. En **Estado**, escribe el texto fijo **Urgente**.

**Mapear** significa conectar el dato del origen con su columna equivalente del destino. Por ejemplo, `ID (origen) → ID (destino)`. Un campo verde que representa un dato anterior no es lo mismo que escribir la palabra literal `ID`.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-14.webp" alt="Acción Add a Row configurada para Urgentes con cinco valores dinámicos y Estado fijo Urgente." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-14.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 14. Primera acción: conserva los datos de origen y agrega Estado = Urgente.*

Para la segunda ruta, repite el mapeo en **Normales**, pero establece **Estado = Normal**. No cambies los datos de la solicitud: solo su destino y el estado añadido.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-15.webp" alt="Acción Add a Row hacia Normales con campos dinámicos y Estado fijo Normal." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-15.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 15. Segunda acción: mismas columnas, distinto destino y estado.*

### Revisa el circuito completo

Antes de ejecutar, comprueba que el recorrido vaya de izquierda a derecha y que **Watch New Rows sea el primer módulo** (con el indicador de programación sobre él). Si un módulo queda aislado, Make puede no procesar la ruta prevista.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-16.webp" alt="Vista general de Make con Watch New Rows conectado al Router y dos módulos Add a Row, con el escenario inactivo." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-16.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 16. Vista esperada: un disparador, un Router y dos acciones finales.*

---

## 7. Ejecuta, observa y comprueba

Una automatización no está terminada solo porque el dibujo de los módulos se vea correcto. Tiene que **producir el resultado esperado**.

Agrega las cuatro solicitudes `SOL-001` a `SOL-004` en el origen, sin saltar filas vacías. Pulsa **Run once**, abre el historial de la ejecución y comprueba que los bundles recorrieron las rutas correctas.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-17.webp" alt="Ejecución de escenario en Make con dos acciones Add a Row procesando las rutas." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-17.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 17. La simulación muestra actividad en ambos caminos; confirma luego el contenido de las hojas.*

En `Urgentes` deben aparecer `SOL-001` y `SOL-003`, ambos con **Estado = Urgente**. En `Normales` deben aparecer `SOL-002` y `SOL-004`, ambos con **Estado = Normal**.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-18.webp" alt="Google Sheets pestaña Urgentes con SOL-001 y SOL-003 y estado Urgente." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-18.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 18. Resultado observado para las solicitudes de prioridad Alta.*

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-19.webp" alt="Google Sheets pestaña Normales con SOL-002 y SOL-004 y estado Normal." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-19.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 19. Resultado observado para las solicitudes de prioridad Normal.*

### ¿Qué ocurre si aparece una prioridad desconocida?

Agrega una quinta solicitud `SOL-005` con prioridad `Media`. La hoja de origen la recibe, pero los filtros `Alta` y `Normal` no coinciden; por eso no debe registrarse en ninguna pestaña de destino.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-20.webp" alt="Comparación entre fila SOL-005 con Media y resultado de ejecución que no pasa filtros." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-20.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 20. La fila llega al disparador, pero no cumple las condiciones de las dos rutas.*

Ejecuta nuevamente **sin agregar filas nuevas**. El resultado esperado es que `Urgentes` y `Normales` permanezcan con dos registros cada una. Esto valida el seguimiento de filas nuevas en esta prueba, **pero no garantiza por sí solo protección contra duplicados**.

<div class="lamina-apunte" style="position:relative;display:block;width:100%;max-width:760px;margin:18px auto 10px;line-height:0"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-21.webp" alt="Escenario después de una ejecución sin registros nuevos, sin escrituras adicionales en las acciones." style="display:block;width:100%;height:auto;border:1px solid var(--color-divider);border-radius:12px;background:#fff" loading="lazy"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/make-laboratorio/make-21.webp" target="_blank" rel="noopener noreferrer" title="Ampliar captura" aria-label="Ampliar lámina en una pestaña nueva" style="position:absolute;top:10px;right:10px;display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c9d3df;border-radius:8px;background:#fff;color:#244264;text-decoration:none;line-height:1"><svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 3h6v6M21 3l-8 8M9 21H3v-6M3 21l8-8"/></svg></a></div>

*Captura 21. Ejecutar sin nuevos registros no debería añadir filas de salida.*

### Una limitación importante: Add a Row no detecta duplicados

`Add a Row` agrega registros; **no verifica si el ID ya existe**. Si cambias el punto inicial, reprocesas datos antiguos o creas dos rutas que coinciden, podrían aparecer copias. Para una solución más robusta se puede incorporar una búsqueda previa de ID y decidir si insertar o actualizar; eso es una extensión, no parte de este primer escenario.

---

## 8. ¿Dónde entra la inteligencia artificial?

Hasta aquí construimos un flujo **determinista**: si la columna `Prioridad` dice `Alta`, el filtro envía la fila a `Urgentes`. No necesita interpretar un mensaje ambiguo, porque el dato ya viene clasificado. Esto es automatización **sin un modelo de IA**, y sigue siendo una base importante.

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

- En el laboratorio de hoy, la prioridad viene **escrita directamente en una columna**; por eso el Router puede leerla sin IA.
- En una automatización con IA, la prioridad podría ser una **propuesta extraída de un texto** y necesitar validación antes de activar las rutas.
- El principio del mapeo es igual en ambos casos: seleccionar el campo correcto del módulo anterior y enviarlo al destino adecuado.
- Los **bundles**, las **collections** (objetos con varios campos) y los **arrays** (listas de elementos) permiten trabajar con información más compleja. Cuando una lista contiene varios elementos, puede ser necesario usar un **Iterator** para tratarlos individualmente.

**Este apartado explica la arquitectura conceptual. Las capturas anteriores documentan únicamente el escenario probado con Google Sheets y Router; no muestran un modelo de IA configurado ni probado.** Para incorporar IA de verdad harían falta una conexión autorizada, un modelo disponible, pruebas, validaciones y revisión de permisos y costos.

---

## 9. Qué revisar si algo no funciona

| Síntoma | Qué revisar primero |
|---|---|
| No aparecen filas en el disparador | Que el nombre de la pestaña sea `Solicitudes`, que el rango sea `A1:E1` y que el punto inicial detecte datos nuevos. |
| El escenario parece conectado, pero no ejecuta los módulos | Que el primer módulo sea realmente Watch New Rows y no exista una rama o módulo aislado. |
| La ruta Alta no procesa datos | Que el campo de la izquierda sea **Prioridad** del bundle y el valor fijo sea `Alta`, sin espacios extra. |
| Se escriben campos vacíos | Que estés mapeando **variables dinámicas**, no valores escritos a mano ni columnas equivocadas. |
| Aparecen registros repetidos | Que no hayas reanudado desde el principio ni activado dos filtros coincidentes. `Add a Row` no elimina duplicados. |
| Make pide permisos | Revisa cuidadosamente la cuenta y el alcance del acceso a Google Sheets; utiliza una conexión de laboratorio autorizada. |

**Seguridad y costos:** nunca compartas contraseñas o tokens en las capturas. Comprueba los permisos de Google y el consumo de operaciones/créditos de Make, especialmente cuando un disparador consulta periódicamente. Deja la programación del escenario **inactiva** al terminar las pruebas.

---

## Para recordar

- **El disparador lee** filas nuevas y entrega bundles.
- **El Router divide** el flujo en rutas independientes.
- **El filtro permite o bloquea** cada ruta según una condición.
- **El mapeo transmite** datos dinámicos y agrega valores fijos cuando hace falta.
- **La prueba final revisa las hojas**, no solo las marcas verdes del escenario.
- **Una IA puede interpretar** contenido no estructurado; el Router **sigue aplicando reglas** sobre los datos resultantes.

Con estas bases, ya puedes empezar a diseñar flujos visuales más grandes con diferentes aplicaciones. Aprende a leer primero el dato de entrada, luego el criterio de decisión y finalmente el resultado esperado.