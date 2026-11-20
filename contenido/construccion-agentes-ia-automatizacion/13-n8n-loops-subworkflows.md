# Loops y subworkflows en n8n

Una distribuidora ficticia, Calbuco, recibe diez documentos de compra y necesita calcular el neto y el IVA de cada uno, descartar los que no traen monto y decidir a qué ruta va cada documento. En este apunte construyes ese flujo en n8n con dos ideas nuevas: procesar los documentos **de a cinco** con un loop y mover el cálculo a un **subworkflow** que cualquier otro flujo puede reutilizar.

El apunte tiene tres partes. Primero entiendes el loop, luego el subworkflow, y al final armas todo paso a paso y compruebas que el resultado coincide con el esperado. Si todavía no manejas expresiones, filtros ni el Switch, parte por [Cómo transformar y encaminar datos en n8n](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/n8n-transformar-encaminar-datos). Aquí damos por hecho que ya sabes abrir un nodo y leer sus paneles INPUT y OUTPUT.

Las capturas son de n8n 2.44.6. Si usas otra versión, los nombres de algunos menús pueden variar un poco.

## Antes de empezar: recursos y caso

### Descarga los recursos

Los archivos de este apunte están en una carpeta de Drive. Puedes abrirla sin iniciar sesión y descargar lo que necesites.

**[Abrir la carpeta de recursos 6.6](https://drive.google.com/drive/folders/1ZnjLzuOobFr9YqHUL8a-tp3Iq4B5LU9f)**

| Archivo | Para qué sirve |
| --- | --- |
| `u21-clase10-subworkflow-vacio.json` | El subworkflow con solo su disparador. El cálculo lo agregas tú. |
| `u21-clase10-principal-referencia.json` | El flujo principal completo. Solo falta indicarle a qué subworkflow debe llamar. |
| `documentos/lote-10-documentos.json` | Los diez documentos de prueba. Ya vienen dentro del flujo principal. |
| `documentos/lote-10-salida-esperada.json` | El resultado correcto por ruta, para comparar al final. |
| `compose.yaml` | Levanta n8n con Docker. Con este archivo, n8n queda en `http://localhost:5690`. |

Los archivos `.json` se importan desde el menú del editor, como verás en la parte práctica. Descárgalos tal cual: si los abres y los guardas desde un procesador de texto, dejan de importar.

### Los diez documentos

Cada fila será un ítem en n8n. Dos documentos, Corrupto y Factura 4541, vienen sin monto a propósito, para que el flujo tenga algo que descartar.

| Documento | Proveedor | `monto_total` |
| --- | --- | --- |
| Factura 4521 | P-101 | 1250000 |
| OC-9102 | P-101 | 320000 |
| Borde | P-102 | 500000 |
| Corrupto | P-101 | sin monto |
| Factura 4530 | P-102 | 89990 |
| Factura 4533 | P-103 | 450000 |
| OC-9110 | P-101 | 1000000 |
| Factura 4541 | P-102 | sin monto |
| OC-9115 | P-103 | 2100000 |
| Factura 4550 | P-999 | 76000 |

El flujo también trae una tabla de tres proveedores: P-101 Ferretería Andes (vigente), P-102 Transportes del Sur (vigente) y P-103 Insumos Norte (suspendido). El proveedor P-999 no está en esa tabla.

### Las reglas

| Regla | Detalle |
| --- | --- |
| Neto e IVA | El monto total incluye un 19 % de IVA. El neto es el monto total dividido por 1,19 y redondeado. El IVA es el monto total menos el neto. |
| Documento válido | El monto debe ser mayor que 0. Los demás se descartan. |
| Ruta | **Contingencia** si el proveedor está suspendido. **Revisión humana** si el monto es de 1000000 o más. **Automático** en cualquier otro caso. Las reglas se evalúan en ese orden. |

### El recorrido completo

Esta tabla resume qué hace cada nodo del flujo principal con los datos del caso. Úsala como mapa mientras avanzas.

| Nodo | Tipo | Recibe | Entrega |
| --- | --- | --- | --- |
| Inicio manual | Manual Trigger | Nada | 1 ítem vacío. |
| Lote de documentos | Edit Fields | 1 ítem | 1 ítem con la lista `documentos`, de diez elementos. |
| Separar documentos | Split Out | 1 ítem | 10 ítems, uno por documento. |
| Recorrer de a cinco | Loop Over Items | 10 ítems | Por `loop`, 5 ítems en cada una de las dos primeras pasadas. Por `done`, los 10 al final. |
| Normalizar documento | Execute Workflow | 5 ítems por pasada | Los mismos 5, con `monto_neto` e `iva`. |
| Solo con monto | Filter | 10 ítems | 8 por Kept y 2 por Discarded. |
| Tabla de proveedores y Separar proveedores | Edit Fields y Split Out | 1 ítem | 3 ítems, uno por proveedor. |
| Unir con proveedores | Merge | 8 + 3 ítems | 8 ítems con el nombre y el estado de su proveedor. |
| Decidir ruta | Switch | 8 ítems | 2 por Contingencia, 2 por Revisión humana y 4 por Automático. |
| Ruta contingencia, Ruta revisión y Ruta automática | Edit Fields | 2, 2 y 4 ítems | Los mismos ítems, con el campo `ruta`. |

## 6.4 · Loops en n8n

Normalmente un nodo de n8n se ejecuta una vez por cada ítem que recibe, así que muchas veces no necesitas un loop. El propio nodo **Loop Over Items** lo recuerda en su panel: «You may not need this node». Sirve cuando quieres **procesar los ítems por grupos**, por ejemplo para llamar a otro flujo o a un servicio con un lote a la vez en lugar de con todos de golpe. Con diez documentos el lote es pequeño, pero sirve para ver el patrón completo.

### Cómo funciona

El nodo tiene una entrada y dos salidas:

- **`loop`** entrega el siguiente grupo de ítems. Al grupo lo llamamos lote, y su tamaño lo define **Batch Size**.
- **`done`** se activa cuando ya no quedan ítems por entregar, y entrega juntos todos los ítems que fueron regresando al loop.

Para que funcione, el último nodo del tramo que procesa cada lote debe **volver a conectarse a la entrada del loop**. Esa conexión de regreso es la que le avisa al loop que terminó con el lote y puede entregar el siguiente.

En el flujo de Calbuco, `loop` va a «Normalizar documento» y desde ahí el flujo regresa al loop. La salida `done` va a «Solo con monto».

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/01-lienzo-loop-y-regreso.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1700" height="965" alt="Zona del loop en el lienzo de n8n después de ejecutar: el nodo Recorrer de a cinco con sus salidas done y loop, y la conexión que regresa desde Normalizar documento."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/01-lienzo-loop-y-regreso.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Zona del loop en el lienzo de n8n después de ejecutar: el no" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Zona del loop, ya ejecutada. <strong>①</strong> Salida <code>done</code>, que va a «Solo con monto». <strong>②</strong> Salida <code>loop</code>, que va a «Normalizar documento». <strong>③</strong> Conexión de regreso: sale de «Normalizar documento» y vuelve a la entrada del loop. <strong>④</strong> El 3 junto a la marca verde indica que el loop se ejecutó tres veces.</figcaption></figure>

El lienzo muestra «10 items total» sobre las conexiones del loop. Ese número **suma las pasadas** de cinco ítems, por eso no dice 5. Para ver cuántos ítems entregó cada pasada hay que abrir el nodo, como en las figuras que siguen.

### Las tres pasadas

Con diez documentos y **Batch Size = 5**, el loop se ejecuta tres veces. En el panel del nodo, el selector **Run** te deja ver cada pasada. Esto es lo que ocurre:

| Pasada | Salida | Ítems | Qué entrega |
| --- | --- | --- | --- |
| 1 de 3 | `loop` | 5 | Los cinco primeros documentos. |
| 2 de 3 | `loop` | 5 | Los cinco siguientes. |
| 3 de 3 | `done` | 10 | Los diez documentos, ya normalizados. |

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/02-loop-lote-1.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="537" alt="Panel de Recorrer de a cinco en la pasada 1 de 3: Batch Size 5 y la pestaña Loop Branch con cinco documentos."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/02-loop-lote-1.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel de Recorrer de a cinco en la pasada 1 de 3: Batch Size" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Primera pasada. <strong>①</strong> <strong>Batch Size</strong> en 5. <strong>②</strong> <strong>Run</strong> en 1 of 3. <strong>③</strong> La pestaña <strong>Loop Branch</strong> dice 5 items. <strong>④</strong> Los cinco primeros documentos. Corrupto trae <code>monto_total</code> en <code>null</code>.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/03-loop-lote-2.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="537" alt="Panel de Recorrer de a cinco en la pasada 2 de 3 con otros cinco documentos en Loop Branch."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/03-loop-lote-2.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel de Recorrer de a cinco en la pasada 2 de 3 con otros c" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Segunda pasada. <strong>①</strong> Batch Size sigue en 5. <strong>②</strong> <strong>Run</strong> en 2 of 3. <strong>③</strong> Loop Branch vuelve a mostrar 5 items. <strong>④</strong> Los cinco documentos que faltaban. Factura 4541 trae <code>monto_total</code> en <code>null</code>.</figcaption></figure>

En la tercera pasada ya no queda ningún documento por entregar. El loop pasa a la salida `done` y entrega todos los ítems que regresaron, ahora con `monto_neto` e `iva`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/04-loop-done-diez.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="744" alt="Panel de Recorrer de a cinco en la pasada 3 de 3: la pestaña Done Branch con los diez documentos y sus columnas monto_neto e iva."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/04-loop-done-diez.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel de Recorrer de a cinco en la pasada 3 de 3: la pestaña" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Tercera pasada. <strong>①</strong> Batch Size, sin cambios. <strong>②</strong> <strong>Run</strong> en 3 of 3. <strong>③</strong> La pestaña <strong>Done Branch</strong> dice 10 items. <strong>④</strong> Los diez documentos ya normalizados, con <code>monto_neto</code> e <code>iva</code>. Corrupto y Factura 4541 los llevan en <code>null</code>.</figcaption></figure>

**Dos consecuencias prácticas.** La primera: la cantidad de ejecuciones de «Normalizar documento» es la de lotes, dos en este caso, no la de documentos. La segunda: si falta la conexión de regreso, el loop entrega el primer lote y el flujo se detiene sin llegar nunca a `done`.

## 6.5 · Subworkflows

### Qué separamos del flujo principal

En el flujo de Calbuco, calcular el neto y el IVA es una tarea con una entrada y una salida claras: recibe un documento y devuelve el mismo documento con dos campos más. Esa tarea se puede sacar del flujo principal y guardar como un **subworkflow**: un workflow independiente, pensado para que otro lo llame.

Separarlo tiene tres ventajas:

- **Un solo lugar para el cálculo.** Si el IVA cambia, corriges una fórmula y todos los flujos que llaman al subworkflow quedan al día.
- **Un flujo principal más corto.** El principal cuenta el proceso, y el detalle del cálculo vive aparte.
- **Reutilización.** Otro flujo puede llamar al mismo subworkflow sin copiar nodos. Lo harás al final de este apunte.

La contraparte es que ahora hay dos workflows que mantener y un acuerdo que respetar entre ambos. Antes de cambiar la fórmula de un subworkflow que usan varios flujos, conviene probarla con los casos de cada uno.

### El contrato: qué entra y qué sale

El subworkflow se llama **Normalizar documento**. Su acuerdo con quien lo llama es este:

| | Campos |
| --- | --- |
| Entrada | `documento` (texto), `proveedor` (texto) y `monto_total` (número). |
| Salida | Los tres anteriores más `monto_neto` e `iva`, cinco campos en total. |

La entrada se declara en el disparador del subworkflow, **Cuando lo llaman** (el Execute Workflow Trigger). Con **Input data mode** en «Define using fields below» escribes el nombre y el tipo de cada campo. Esos nombres deben ser **idénticos** a los que entrega el nodo que lo llama.

<figure class="lamina-apunte" style="position:relative;max-width:560px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/05-contrato-entrada.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1000" height="1227" alt="Panel de parámetros del disparador Cuando lo llaman con tres campos declarados: documento, proveedor y monto_total."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/05-contrato-entrada.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel de parámetros del disparador Cuando lo llaman con tres" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Disparador del subworkflow. <strong>①</strong> <strong>Input data mode</strong> en «Define using fields below». <strong>②</strong> Los tres campos del contrato: <code>documento</code> y <code>proveedor</code> (String) y <code>monto_total</code> (Allow Any Type).</figcaption></figure>

En ese panel, el lado derecho (OUTPUT) queda vacío: el disparador solo entrega datos cuando otro workflow lo llama.

La salida la define el último nodo del subworkflow. Aquí es un **Edit Fields** llamado «Normalizar montos», con **Include Other Input Fields** desactivado para que devuelva exactamente los cinco campos del contrato.

### Las expresiones del cálculo

Estas son las expresiones de los campos de «Normalizar montos». Cópialas tal cual.

| Campo | Tipo | Expresión |
| --- | --- | --- |
| `documento` | String | <code>&#123;&#123; $json.documento &#125;&#125;</code> |
| `proveedor` | String | <code>&#123;&#123; $json.proveedor &#125;&#125;</code> |
| `monto_total` | Number | <code>&#123;&#123; $json.monto_total &#125;&#125;</code> |
| `monto_neto` | Number | <code>&#123;&#123; $json.monto_total ? Math.round($json.monto_total / 1.19) : null &#125;&#125;</code> |
| `iva` | Number | <code>&#123;&#123; $json.monto_total ? $json.monto_total - Math.round($json.monto_total / 1.19) : null &#125;&#125;</code> |

Para copiarlas con comodidad, aquí van las dos expresiones del cálculo en un bloque cada una.

<pre><code class="language-text">&#123;&#123; $json.monto_total ? Math.round($json.monto_total / 1.19) : null &#125;&#125;</code></pre>

<pre><code class="language-text">&#123;&#123; $json.monto_total ? $json.monto_total - Math.round($json.monto_total / 1.19) : null &#125;&#125;</code></pre>

La parte `$json.monto_total ? ... : null` evita calcular cuando no hay monto: en ese caso el campo queda en `null`. En JavaScript el valor 0 también cuenta como «sin monto», así que un documento con monto 0 devuelve `null`. Aquí no cambia el resultado, porque el Filter «Solo con monto» ya descarta los montos que no son mayores que 0. Si en otro proceso necesitas distinguir un cero real de un monto ausente, compara de forma explícita con `null`.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/06-edit-fields-expresiones.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="1663" alt="Nodo Edit Fields llamado Normalizar montos con cinco campos y las expresiones de monto_neto e iva, con Include Other Input Fields desactivado."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/06-edit-fields-expresiones.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Edit Fields llamado Normalizar montos con cinco campos " style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo «Normalizar montos». <strong>①</strong> Expresión de <code>monto_neto</code>. <strong>②</strong> Expresión de <code>iva</code>. <strong>③</strong> <strong>Include Other Input Fields</strong> desactivado: la salida son solo los cinco campos. Bajo cada expresión, n8n muestra el resultado con el dato de prueba (1050420 y 199580).</figcaption></figure>

### Entrada y salida con la Factura 4521

Para ver el contrato en acción, la Factura 4521 (proveedor P-101, monto 1250000) entra con tres campos y sale con cinco.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/07-prueba-factura-4521.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1700" height="605" alt="Prueba del nodo Normalizar montos: a la izquierda el JSON de entrada con tres campos y a la derecha el JSON de salida con cinco."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/07-prueba-factura-4521.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Prueba del nodo Normalizar montos: a la izquierda el JSON de" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Prueba con la Factura 4521. <strong>①</strong> INPUT en JSON: los tres campos que llegan. <strong>②</strong> OUTPUT en JSON: los cinco campos que salen. <strong>③</strong> <code>monto_neto</code> 1050420 e <code>iva</code> 199580.</figcaption></figure>

El resultado se puede comprobar a mano: 1250000 dividido por 1,19 da 1050420,17, que se redondea a **1050420**, y 1250000 menos 1050420 da **199580**. Neto más IVA suman otra vez el monto total.

## 6.6 · Laboratorio Calbuco paso a paso

Ahora armas todo. Necesitas n8n funcionando (si usas el `compose.yaml` de la carpeta de recursos, está en `http://localhost:5690`) y los archivos descargados. El orden importa: primero el subworkflow, porque el flujo principal necesita elegirlo.

Antes de ejecutar nada, haz una predicción y anótala. Con diez documentos y lotes de cinco, ¿cuántas veces esperas que se ejecute el subworkflow? ¿Cuántos documentos esperas que se descarten? ¿En qué rutas esperas que caiga cada uno? Las compararás con el resultado al final.

Las notas verdes de las capturas son de apoyo: se agregaron para este apunte y los archivos que descargas no las traen.

### Parte 1: crear el subworkflow

**Paso 1. Importar el archivo.** Crea un workflow nuevo. Abre el menú de tres puntos junto al nombre, elige **Import** y luego **From file**. Selecciona `u21-clase10-subworkflow-vacio.json`.

<figure class="lamina-apunte" style="position:relative;max-width:700px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/08-menu-import.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1100" height="721" alt="Menú de tres puntos de un workflow en n8n con la opción Import y su submenú From URL y From file."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/08-menu-import.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Menú de tres puntos de un workflow en n8n con la opción Impo" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Menú de tres puntos del workflow. <strong>①</strong> <strong>Import</strong> abre un submenú. <strong>②</strong> <strong>From file</strong> abre el selector de archivos.</figcaption></figure>

**Paso 2. Revisar y renombrar.** Debe aparecer el disparador «Cuando lo llaman» y una nota amarilla. Arriba a la izquierda, el workflow se llama «Normalizar documento (vacío)». Cámbiale el nombre a **Normalizar documento**: con ese nombre lo encontrarás desde el flujo principal.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/09-subworkflow-importado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1700" height="1057" alt="Subworkflow recién importado: el nodo Cuando lo llaman y una nota amarilla, con el nombre Normalizar documento (vacío)."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/09-subworkflow-importado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Subworkflow recién importado: el nodo Cuando lo llaman y una" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Subworkflow recién importado. <strong>①</strong> El nombre dice «Normalizar documento (vacío)»: cámbialo a «Normalizar documento». <strong>②</strong> El disparador «Cuando lo llaman». <strong>③</strong> La nota amarilla viene en el archivo. Todavía no hay ningún nodo de cálculo.</figcaption></figure>

**Paso 3. Revisar el contrato.** Haz doble clic en «Cuando lo llaman». Comprueba que **Input data mode** diga «Define using fields below» y que haya tres campos: `documento`, `proveedor` y `monto_total`, como en la figura de la sección 6.5.

**Paso 4. Agregar el cálculo.** Cierra el nodo y agrega un **Edit Fields** conectado a la salida del disparador. Ponle el nombre **Normalizar montos** y mantén **Manual Mapping**. Con **Add Field** crea los cinco campos de la tabla de expresiones de la sección 6.5, cada uno con su tipo y su expresión. Deja **Include Other Input Fields** desactivado. Guarda con Ctrl+S (n8n 2.44.6 también guarda los cambios automáticamente).

**Paso 5. Probar el nodo (opcional).** Para ver el resultado sin esperar al flujo principal, abre «Cuando lo llaman», elige **set mock data** y pega este documento de prueba:

```json
[{"documento": "Factura 4521", "proveedor": "P-101", "monto_total": 1250000}]
```

Guárdalo, abre «Normalizar montos» y pulsa **Execute step**. En OUTPUT debes ver `monto_neto` 1050420 e `iva` 199580, como en la figura anterior. Cuando termines, abre otra vez el disparador y pulsa **Unpin** para quitar los datos de prueba.

### Parte 2: importar el flujo principal y enlazarlo

**Paso 6. Importar el principal.** Crea otro workflow nuevo, elige **Import** y luego **From file**, y selecciona `u21-clase10-principal-referencia.json`. Se llama «Calbuco 6.6 Flujo principal». Debes ver el flujo completo, con el nodo «Recorrer de a cinco» (el Loop Over Items) y el nodo «Normalizar documento» (un Execute Workflow).

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/10-principal-importado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1700" height="1057" alt="Flujo principal Calbuco 6.6 recién importado, con trece nodos y notas de apoyo; el nodo Normalizar documento todavía muestra un marcador como subworkflow."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/10-principal-importado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Flujo principal Calbuco 6.6 recién importado, con trece nodo" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Flujo principal recién importado (las notas verdes son de apoyo y tu archivo no las trae). <strong>①</strong> «Normalizar documento» todavía dice «Workflow: SUBWORKFLOW_ID»: aún no apunta a tu subworkflow. <strong>②</strong> «Recorrer de a cinco», el Loop Over Items. <strong>③</strong> La nota 3 recuerda qué hacer en el nodo de la llamada.</figcaption></figure>

El nodo «Normalizar documento» aún no apunta a tu subworkflow. Cada instalación de n8n le da su propio identificador a cada workflow, así que el archivo trae un marcador en su lugar.

**Paso 7. Elegir el subworkflow.** Haz doble clic en «Normalizar documento». Deja **Source** en Database y abre la lista del campo **Workflow**. Pueden aparecer **dos entradas con el mismo nombre**:

- La primera, resaltada en naranja, es el **valor que traía el archivo importado**, el marcador.
- La segunda es el **subworkflow que creaste en la Parte 1**.

Elige la **segunda**. Para comprobar que elegiste bien, abre la lista otra vez: debe quedar una sola entrada, la marcada.

<figure class="lamina-apunte" style="position:relative;max-width:720px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/11-lista-dos-opciones.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1100" height="775" alt="Lista del campo Workflow con dos entradas llamadas Normalizar documento, la primera resaltada en naranja."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/11-lista-dos-opciones.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Lista del campo Workflow con dos entradas llamadas Normaliza" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Lista del campo Workflow. <strong>①</strong> El campo, en «From list». <strong>②</strong> Primera entrada, resaltada: es el valor que traía el archivo importado. <strong>③</strong> Segunda entrada: el subworkflow que creaste. Elige esta.</figcaption></figure>

**Paso 8. Ver el mapeo.** Después de elegir el subworkflow, **cierra el nodo y vuelve a abrirlo**: en n8n 2.44.6 el mapeo no aparece en el mismo panel donde elegiste, sino al reabrir el nodo. Ahora la sección **Workflow Inputs** debe mostrar los tres campos, cada uno con una expresión que toma su valor del documento actual. Si no aparecen, revisa que el subworkflow esté guardado y que se llame «Normalizar documento».

<figure class="lamina-apunte" style="position:relative;max-width:580px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/12-mapeo-tres-campos.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1000" height="948" alt="Nodo Execute Workflow con el subworkflow Normalizar documento elegido y los tres campos de Workflow Inputs mapeados con expresiones."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/12-mapeo-tres-campos.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Execute Workflow con el subworkflow Normalizar document" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo «Normalizar documento» ya enlazado. <strong>①</strong> El subworkflow elegido. <strong>②</strong> <strong>Workflow Inputs</strong>, con los tres campos mapeados. Si no los ves, cierra el nodo y ábrelo otra vez.</figcaption></figure>

Las tres expresiones son estas. Cada nombre coincide con un campo del contrato de entrada.

<pre><code class="language-text">&#123;&#123; $json.documento &#125;&#125;
&#123;&#123; $json.proveedor &#125;&#125;
&#123;&#123; $json.monto_total &#125;&#125;</code></pre>

**Paso 9. Esperar al subworkflow.** Despliega **Options** y pulsa **Add option**. Elige **Wait For Sub-Workflow Completion** y comprueba que quede **activada** (interruptor verde). Con esta opción el flujo principal espera a que el subworkflow termine y recibe lo que devuelve. Su valor por defecto es activado, pero no aparece en la lista hasta que la agregas, y así dejas la decisión a la vista.

<figure class="lamina-apunte" style="position:relative;max-width:580px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/13-wait-for-subworkflow.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1000" height="451" alt="Sección Options del nodo Execute Workflow con la opción Wait For Sub-Workflow Completion activada."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/13-wait-for-subworkflow.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Sección Options del nodo Execute Workflow con la opción Wait" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Opciones del nodo. <strong>①</strong> <strong>Wait For Sub-Workflow Completion</strong>, agregada con <strong>Add option</strong> y activada (interruptor verde).</figcaption></figure>

**Paso 10. Revisar el loop.** Abre «Recorrer de a cinco» y comprueba que **Batch Size** sea 5. En el lienzo, comprueba también las tres conexiones que hacen funcionar el loop: `done` va a «Solo con monto», `loop` va a «Normalizar documento», y de «Normalizar documento» sale una conexión que regresa al loop. Si `done` y `loop` estuvieran cambiadas, el flujo mandaría los documentos al filtro antes de calcularlos.

Guarda el flujo principal.

### Parte 3: ejecutar y verificar

**Paso 11. Ejecutar.** En el flujo principal pulsa **Execute workflow**. Mira los contadores sobre las conexiones.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/14-lienzo-resultado.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1700" height="1057" alt="Flujo principal ejecutado: contadores de ítems sobre cada conexión, con el loop ejecutado tres veces y las tres rutas finales."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/14-lienzo-resultado.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Flujo principal ejecutado: contadores de ítems sobre cada co" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Flujo completo, ya ejecutado. <strong>①</strong> El loop marca 3 ejecuciones. <strong>②</strong> «Normalizar documento» marca 2. <strong>③</strong> «Solo con monto» deja pasar 8 ítems. <strong>④</strong> Las tres rutas reciben 2, 2 y 4. Los «10 items total» de las conexiones del loop suman las dos pasadas de cinco.</figcaption></figure>

Los contadores deben decir:

- **10** ítems después de «Separar documentos».
- **✓3** en «Recorrer de a cinco» y **✓2** en «Normalizar documento».
- **8** ítems después de «Solo con monto».
- **2**, **2** y **4** en las tres rutas.

Recuerda que sobre las conexiones del loop el lienzo muestra «10 items total»: es la suma de las dos pasadas. Los 5 ítems de cada pasada están en el panel del loop (sección 6.4).

**Paso 12. Revisar los descartados.** Abre «Solo con monto». El nodo Filter deja pasar 8 ítems por **Kept** y manda 2 a **Discarded**. En el lienzo solo se ve la salida Kept, así que los descartados se revisan en esta pestaña.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/15-filtro-descartados.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="328" alt="Panel del Filter Solo con monto con la pestaña Discarded: dos documentos descartados, Corrupto y Factura 4541."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/15-filtro-descartados.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel del Filter Solo con monto con la pestaña Discarded: do" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo «Solo con monto». <strong>①</strong> Condición: <code>monto_total</code> mayor que 0. <strong>②</strong> Pestañas <strong>Kept</strong> (8 items) y <strong>Discarded</strong> (2 items). <strong>③</strong> Los dos descartados, Corrupto y Factura 4541, con el monto en <code>null</code>.</figcaption></figure>

**Paso 13. Revisar las tres rutas.** Abre «Ruta contingencia», «Ruta revisión» y «Ruta automática». Cada una agrega el campo `ruta` a los ítems que recibe.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/16-ruta-contingencia.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="487" alt="Panel de Ruta contingencia con el campo ruta igual a Contingencia y dos documentos: Factura 4533 y OC-9115."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/16-ruta-contingencia.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel de Ruta contingencia con el campo ruta igual a Conting" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>«Ruta contingencia». <strong>①</strong> El campo <code>ruta</code> vale Contingencia. <strong>②</strong> Factura 4533 y OC-9115, los dos del proveedor P-103, que está suspendido.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/17-ruta-revision.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="487" alt="Panel de Ruta revisión con el campo ruta igual a Revisión humana y dos documentos: Factura 4521 y OC-9110."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/17-ruta-revision.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel de Ruta revisión con el campo ruta igual a Revisión hu" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>«Ruta revisión». <strong>①</strong> El campo <code>ruta</code> vale Revisión humana. <strong>②</strong> Factura 4521 y OC-9110, los dos con monto de 1000000 o más.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/18-ruta-automatico.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="487" alt="Panel de Ruta automática con el campo ruta igual a Automático y cuatro documentos; Factura 4550 muestra undefined en las columnas del proveedor."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/18-ruta-automatico.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel de Ruta automática con el campo ruta igual a Automátic" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>«Ruta automática». <strong>①</strong> El campo <code>ruta</code> vale Automático. <strong>②</strong> Cuatro documentos: OC-9102, Borde, Factura 4530 y Factura 4550. En la última fila, <code>undefined</code> indica que el proveedor P-999 no tiene datos en la tabla.</figcaption></figure>

En «Ruta automática» fíjate en Factura 4550: las columnas con datos del proveedor aparecen como `undefined`. Su proveedor, P-999, no está en la tabla de proveedores, así que el Merge no le encontró datos. Como no está suspendido y su monto es menor que 1000000, las reglas la mandan a Automático.

**Paso 14. Comparar con el resultado esperado.** Compara lo que viste con esta tabla y con `lote-10-salida-esperada.json`. Si tu predicción difería en algo, anota por qué.

| Documento | Resultado | Por qué |
| --- | --- | --- |
| Factura 4521 | Revisión humana | Proveedor vigente y monto de 1250000. |
| OC-9102 | Automático | Proveedor vigente y monto menor que 1000000. |
| Borde | Automático | Proveedor vigente y monto menor que 1000000. |
| Corrupto | Descartado | No trae monto. |
| Factura 4530 | Automático | Proveedor vigente y monto menor que 1000000. |
| Factura 4533 | Contingencia | El proveedor P-103 está suspendido. |
| OC-9110 | Revisión humana | El monto es exactamente 1000000 y la regla dice «1000000 o más». |
| Factura 4541 | Descartado | No trae monto. |
| OC-9115 | Contingencia | El proveedor P-103 está suspendido. Esa regla se evalúa primero, aunque el monto sea alto. |
| Factura 4550 | Automático | Sin datos de proveedor y monto menor que 1000000. |

En resumen: 2 descartados, 2 en Contingencia, 2 en Revisión humana y 4 en Automático.

**Paso 15. Contar las llamadas al subworkflow.** Abre el workflow «Normalizar documento» y entra a la pestaña **Executions**. Debes ver **dos ejecuciones exitosas**, una por cada lote de cinco. Al abrir una, el disparador muestra 5 ítems que entregó al nodo «Normalizar montos».

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/19-ejecuciones-subworkflow.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1400" height="600" alt="Pestaña Executions del subworkflow Normalizar documento con dos ejecuciones exitosas y la vista de una de ellas."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/19-ejecuciones-subworkflow.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Pestaña Executions del subworkflow Normalizar documento con " style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Pestaña <strong>Executions</strong> del subworkflow. <strong>①</strong> Dos ejecuciones exitosas, una por cada lote de cinco. <strong>②</strong> La vista de una ejecución: el disparador entregó 5 ítems a «Normalizar montos».</figcaption></figure>

El loop tuvo tres pasadas y el subworkflow solo dos ejecuciones, porque la tercera pasada no llama a nada: entrega los diez por `done`. Es un dato que se ve aquí y no en el flujo principal.

### Parte 4: reutilizar el subworkflow

El mismo subworkflow puede usarlo cualquier otro flujo. Para comprobarlo, arma un segundo flujo mínimo que normalice una sola factura.

**Paso 16. Crear el segundo flujo.** Crea un workflow nuevo y llámalo **Calbuco 6.6 Segundo llamador**. Agrega tres nodos y conéctalos en este orden:

1. Un **Manual Trigger**.
2. Un **Edit Fields** llamado **Un documento**, con tres campos: `documento` (String) con el texto `Factura 9999`, `proveedor` (String) con el texto `P-101` y `monto_total` (Number) con el valor `595000`.
3. Un **Execute Workflow** llamado **Normalizar documento**, con **Source** en Database y **Workflow** elegido desde la lista: «Normalizar documento». Esta vez la lista tiene una sola entrada. Cierra y vuelve a abrir el nodo para ver **Workflow Inputs** y completa los tres campos con las mismas expresiones de antes.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/20-segundo-llamador-lienzo.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1500" height="570" alt="Segundo flujo con tres nodos conectados: Inicio manual, Un documento y Normalizar documento."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/20-segundo-llamador-lienzo.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Segundo flujo con tres nodos conectados: Inicio manual, Un d" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Segundo flujo. <strong>①</strong> «Un documento» crea la factura de prueba. <strong>②</strong> «Normalizar documento» llama al mismo subworkflow del flujo principal. Las notas verdes son de apoyo.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:580px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/21-un-documento.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1000" height="911" alt="Nodo Edit Fields Un documento con tres campos: documento Factura 9999, proveedor P-101 y monto_total 595000."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/21-un-documento.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Edit Fields Un documento con tres campos: documento Fac" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Nodo «Un documento». <strong>①</strong> Los tres campos del contrato: <code>documento</code> con el texto Factura 9999, <code>proveedor</code> con P-101 y <code>monto_total</code> como número, 595000.</figcaption></figure>

<figure class="lamina-apunte" style="position:relative;max-width:580px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/22-segundo-llamador-subworkflow.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1000" height="986" alt="Nodo Execute Workflow del segundo flujo con el subworkflow Normalizar documento elegido y sus tres campos mapeados."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/22-segundo-llamador-subworkflow.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Nodo Execute Workflow del segundo flujo con el subworkflow N" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Llamada del segundo flujo. <strong>①</strong> El subworkflow elegido desde la lista, el mismo del flujo principal. <strong>②</strong> El mapeo de los tres campos, con las mismas expresiones.</figcaption></figure>

**Paso 17. Predecir y ejecutar.** Antes de ejecutar, escribe qué neto y qué IVA esperas para un monto total de 595000. Después pulsa **Execute workflow** y abre «Normalizar documento». Debes ver `monto_neto` **500000** e `iva` **95000**: 595000 dividido por 1,19 da exactamente 500000, y 595000 menos 500000 da 95000.

<figure class="lamina-apunte" style="position:relative;max-width:1000px;margin:18px auto 24px"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/23-salida-500000-95000.webp" style="display:block;width:100%;height:auto;border:1px solid #d4d9e1" loading="lazy" width="1700" height="605" alt="Panel del nodo Normalizar documento del segundo flujo: entrada Factura 9999 y salida con monto_neto 500000 e iva 95000."><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-loops-subworkflows/23-salida-500000-95000.webp" target="_blank" rel="noopener noreferrer" aria-label="Ampliar Panel del nodo Normalizar documento del segundo flujo: entra" style="position:absolute;right:8px;top:8px;padding:4px 8px;background:var(--color-bg);border:1px solid var(--color-divider);font-size:13px">Ampliar ↗</a><figcaption>Resultado del segundo flujo. <strong>①</strong> INPUT: Factura 9999, P-101 y 595000. <strong>②</strong> OUTPUT: <code>monto_neto</code> 500000 e <code>iva</code> 95000. <strong>③</strong> El panel indica «1 sub-execution»: el cálculo lo hizo el subworkflow.</figcaption></figure>

El segundo flujo no copió ningún cálculo: llamó al mismo subworkflow que usa el flujo principal. Si mañana el IVA cambia, la fórmula se corrige una sola vez, en «Normalizar montos», y ambos flujos quedan al día. Antes de tocarla, prueba el cambio con los dos flujos.

## Si algo no resulta

| Qué ves | Qué revisar |
| --- | --- |
| «Normalizar documento» muestra una advertencia. | Falta elegir el subworkflow en el campo **Workflow** (Paso 7). |
| El subworkflow no aparece en la lista. | Quizás no está guardado o tiene otro nombre. Guárdalo y comprueba que se llame «Normalizar documento». |
| No aparecen los campos de **Workflow Inputs**. | Cierra el nodo y ábrelo otra vez. Si sigue igual, revisa que el subworkflow esté guardado. |
| El flujo se ejecuta una vez y se detiene. | Falta la conexión de regreso al loop, o está en la salida equivocada (Paso 10). |
| Salen diez ítems por `loop` y nada por `done`. | «Normalizar documento» no está conectado de vuelta al loop. |
| El subworkflow devuelve campos vacíos. | Los campos de **Workflow Inputs** deben ser expresiones y llamarse exactamente `documento`, `proveedor` y `monto_total`. |
| `monto_neto` sale en `null`. | El documento no trae monto. Es lo esperado: «Solo con monto» lo descarta. |
| El resultado no es 2, 2 y 4. | Compara las expresiones de `monto_neto` e `iva` con las de la sección 6.5: un carácter distinto cambia el monto. |
| El archivo `.json` no se importa. | Descárgalo de nuevo desde la carpeta de recursos y no lo abras ni lo guardes desde un procesador de texto. |

## Autoevaluación

```quiz
? Un loop con Batch Size = 5 recibe diez ítems. ¿Qué entrega en total?
+ Por loop, cinco ítems en dos pasadas, y por done, los diez al final.
- Por la salida done, cinco ítems en dos pasadas.
- Por loop, diez ítems en una sola pasada.
> Las dos primeras pasadas salen por loop. Cuando ya no quedan ítems, los diez que regresaron salen juntos por done.
? ¿Qué pasa si «Normalizar documento» no se conecta de vuelta a la entrada del loop?
- El loop entrega los diez ítems por done de todas formas.
- n8n reconecta el nodo automáticamente.
+ El loop entrega el primer lote y el flujo se detiene sin llegar a done.
> La conexión de regreso es lo que le avisa al loop que terminó con el lote. Sin ella no entrega el siguiente.
? El flujo principal procesó diez documentos en lotes de cinco. ¿Cuántas ejecuciones del subworkflow esperas ver?
- Diez, una por documento.
+ Dos, una por cada lote de cinco.
- Tres, una por cada pasada del loop.
> La tercera pasada no llama al subworkflow: solo entrega los diez ítems por done.
? Abres la lista del campo Workflow y ves dos entradas llamadas «Normalizar documento». ¿Cuál eliges?
- La primera, la resaltada en naranja.
+ La que no está resaltada: es el subworkflow que creaste en tu instancia.
- Cualquiera, porque las dos son iguales.
> La resaltada es el valor que traía el archivo importado. Después de elegir la otra, la lista queda con una sola entrada.
? Dos flujos distintos llaman al mismo subworkflow y el IVA cambia. ¿Dónde se corrige la fórmula?
+ Una sola vez, dentro del subworkflow.
- En cada flujo que llama al subworkflow.
- En el Filter del flujo principal.
> Esa es la ventaja de separar el cálculo. Antes de cambiarlo, conviene probarlo con los casos de cada flujo.
```

## Documentación de referencia

- [Nodo Loop Over Items (Split In Batches)](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.splitinbatches/)
- [Hacer loops en n8n](https://docs.n8n.io/flow-logic/looping/)
- [Nodo Execute Workflow](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executeworkflow/)
- [Nodo Execute Workflow Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executeworkflowtrigger/)
- [Subworkflows](https://docs.n8n.io/flow-logic/subworkflows/)
- [Nodo Edit Fields (Set)](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.set/)
- [Diccionario práctico de expresiones en n8n](Guias.dc.html#/c/construccion-agentes-ia-automatizacion/extra-diccionario-expresiones-n8n)
