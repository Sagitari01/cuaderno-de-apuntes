# Cómo manejar errores y leer ejecuciones en n8n

Una biblioteca recibe solicitudes para consultar su catálogo. Si el servicio responde, la biblioteca muestra cuántos ejemplares están disponibles. Si el servicio falla, la respuesta depende de la consulta. Una ficha opcional puede quedar pendiente. Para confirmar disponibilidad hace falta un dato válido del catálogo.

Aquí verás cómo volver a intentar una consulta, continuar por una ruta de contingencia y registrar una falla que detiene el workflow.

## 1. Decide qué hacer cuando falla un paso

El nodo **HTTP Request** llama al catálogo. En este ejemplo, `200` indica que el catálogo respondió y `503` que el servicio está temporalmente indisponible. Una interrupción breve puede resolverse si la consulta se repite después de una pausa.

| Situación | Qué hace el flujo | Dato que entrega |
| --- | --- | --- |
| El servicio responde en el primer intento. | Sigue por la salida normal. | Disponibilidad confirmada. |
| El servicio falla una vez y después responde. | Repite la consulta y sigue por la salida normal. | Disponibilidad confirmada. |
| El servicio sigue fallando y la consulta era opcional. | Conserva la solicitud y marca el resultado como degradado. | Disponibilidad desconocida. |
| El servicio sigue fallando y la consulta era obligatoria. | Detiene el flujo y registra el incidente en otro workflow. | La solicitud queda sin confirmar. |

El valor `0` significa que se confirmó que no quedan ejemplares. La salida degradada usa `null` para expresar que la biblioteca desconoce esa cantidad.

## 2. Configura los intentos del nodo

En **HTTP Request → Settings**, activa **Retry On Fail** y define **Max. Tries = 3** y **Wait Between Tries (ms) = 1.000** para la demostración. Con tres intentos hay una llamada inicial y hasta dos repeticiones. Si el primer `503` va seguido de un `200`, el nodo termina después de dos llamadas.

<!-- captura: 03-http-settings.webp -->

El ajuste repite el nodo cuando la llamada se considera un error. Para que un `503` cuente como falla en este ejemplo, deja desactivado **Never Error**, que está en las opciones de respuesta de HTTP Request. Un error permanente, como una credencial incorrecta, requiere corregir su causa. La consulta de ejemplo usa **GET** y se limita a leer datos. Antes de reintentar un paso que crea una reserva o escribe un registro, comprueba si repetirlo podría duplicar esa operación.

## 3. Encauza el error dentro del workflow principal

**Continue On Fail** puede aparecer en materiales de versiones anteriores. En **Settings → On Error**, la interfaz actual ofrece estas acciones.

| Opción | Efecto |
| --- | --- |
| **Stop Workflow** | Detiene el flujo y la ejecución queda como fallida. |
| **Continue** | Permite avanzar por la salida normal tras el error. El resultado que recibe el nodo siguiente depende del nodo que falló. |
| **Continue (using error output)** | Envía la información del error por una salida separada para que el flujo pueda decidir qué hacer. |

En la biblioteca, el flujo comienza en **Webhook**. **Edit Fields** toma el identificador de la solicitud y el tipo de consulta del cuerpo JSON. **HTTP Request** consulta el catálogo. Cuando responde, la salida normal lleva a **Confirmar disponibilidad**, que devuelve el dato obtenido.

<!-- captura: 02-http-parametros.webp -->
<!-- captura: 06-exito-normal.webp -->

Si se agotan los intentos, la salida de error lleva a un **IF**. Su condición pregunta si la consulta era opcional. Si es verdadera, **Registrar contingencia** conserva el identificador y produce `estado: degradado`, `disponibles: null` y `motivo: catalogo_no_disponible`. Si es falsa, **Stop And Error** detiene el flujo con un mensaje que identifica la solicitud. El registro de contingencia se puede leer en la salida del nodo guardada en **Executions**.

<!-- captura: 01-flujo-principal.webp -->

La ruta degradada puede aparecer como **Success** en el historial, porque el flujo terminó después de manejar el error. El campo `estado` permite distinguir ese resultado de una consulta confirmada.

<!-- captura: 08-contingencia.webp -->

## 4. Registra una falla del workflow completo

Crea otro workflow con **Error Trigger** como primer nodo. Conecta un **Edit Fields** para preparar un registro con el nombre del workflow, el identificador de la ejecución, el último nodo ejecutado y el mensaje de error. Guarda el manejador y publícalo o actívalo según tu versión de n8n. En **Settings → Error workflow** del flujo principal, elige ese manejador. Guarda y publica o activa el principal para realizar la prueba automática.

<!-- captura: 04-flujo-de-error.webp -->
<!-- captura: 05-vinculo-error-workflow.webp -->

La ejecución que se detiene en **Stop And Error** pasa al manejador si se disparó automáticamente. En un webhook, usa su **Production URL** en la instancia de práctica. **Execute workflow** en el editor o una llamada a **Test URL** sirven para depurar el flujo, pero el disparador de errores se comprueba con una ejecución automática. El término *Production URL* corresponde al modo del disparador dentro de n8n. Puedes usarlo en una instancia local.

El manejador registra el incidente en otra ejecución. Para correlacionarla, compara el `execution.id` recibido por **Error Trigger** con el ID de la ejecución fallida del flujo principal. Si la falla ocurre en el disparador o n8n no guarda la ejecución original, algunos campos, como el ID o la URL, pueden faltar.

<!-- captura: 10-registro-incidente.webp -->

## 5. Lee el historial de ejecuciones

1. Abre **Executions** del flujo principal y localiza la ejecución por su hora e identificador. En una prueba, conserva los datos de ejecuciones fallidas y exitosas para comparar las ramas.
2. Abre la ejecución y selecciona **HTTP Request**. Revisa su entrada, el código o mensaje de error disponible y la salida por la que siguió. Para comprobar los intentos intermedios, usa el registro del servicio consultado.
3. En la ruta degradada, abre **Registrar contingencia** y comprueba el estado. En la crítica, abre **Stop And Error** y lee su mensaje.
4. Abre **Executions** del manejador. Busca el registro que referencia el ID del flujo principal y compara workflow, nodo y mensaje.

<!-- captura: 07-reintento-recuperado.webp -->
<!-- captura: 09-ejecucion-fallida.webp -->

**Retry On Fail** repite un nodo durante la ejecución en curso. **Retry execution** en el historial vuelve a procesar una ejecución fallida con sus datos anteriores. Según la opción elegida, se utiliza el workflow original o la versión guardada actualmente.

<!-- captura: 12-reintentar-ejecucion.webp -->

## Comprueba lo que entendiste

```quiz
? El catálogo responde 503 en la primera llamada y 200 en la segunda. ¿Cuántas llamadas realizó el nodo?
+ Dos. La segunda recuperó la consulta.
- Tres. Siempre se alcanza el máximo configurado.
- Una. El reintento se ejecuta en otro workflow.
> Max. Tries fija un límite. El nodo deja de reintentar cuando la llamada tiene éxito.
```

```quiz
? Una consulta opcional sigue fallando después de los reintentos. ¿Qué debería mostrar la salida degradada?
- Un valor de cero y una disponibilidad confirmada.
+ Un estado degradado y la disponibilidad como null.
- Una cantidad estimada a partir del catálogo anterior.
> El estado degradado indica que se pudo manejar la falla. null conserva la diferencia entre falta de información y cero ejemplares.
```

```quiz
? ¿Qué prueba permite comprobar que Error Trigger recibe un fallo real del flujo principal?
- Ejecutar solo el nodo Edit Fields del manejador.
- Disparar el flujo desde la Test URL en el editor.
+ Provocar una falla en una ejecución automática de un workflow con su Error workflow configurado.
> Error Trigger se activa ante fallas de ejecuciones automáticas. El manejador corre en una ejecución propia.
```

## Documentación de n8n

- [Manejo de errores](https://docs.n8n.io/flow-logic/error-handling/)
- [Configuración de nodos](https://docs.n8n.io/workflows/components/nodes/)
- [Error Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.errortrigger/)
- [Stop And Error](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.stopanderror/)
- [Historial y reintento de ejecuciones](https://docs.n8n.io/workflows/executions/all-executions/)
