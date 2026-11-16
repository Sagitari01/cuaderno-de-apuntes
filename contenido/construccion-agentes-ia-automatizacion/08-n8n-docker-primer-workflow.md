# n8n y Docker · Tu primer workflow de decisión

Un equipo recibe documentos con montos distintos y necesita decidir cuáles aprueba, cuáles deja pendientes y cuáles requieren revisión. En Make ya viste cómo separar datos incompletos de errores técnicos. Ahora vas a construir la decisión en **n8n** con cuatro documentos ficticios y a ejecutarla en tu equipo con **Docker**.

**Al terminar:** podrás levantar n8n, seguir los datos entre nodos, comprobar los tres resultados y exportar tu flujo como JSON.

**Antes de empezar:** necesitas Docker y Compose, una terminal, un navegador y permisos para iniciar contenedores. Puedes recorrer la explicación y predecir las rutas antes de instalar Docker.

## 1. Las piezas de n8n

Un **workflow** es un conjunto de nodos conectados. Un **trigger** lo inicia. Los nodos siguientes reciben datos, los transforman o deciden a qué salida enviarlos. Una **ejecución** es una corrida del workflow con datos concretos.

| En Make | En n8n | Ejemplo |
| --- | --- | --- |
| Escenario | Workflow | Clasificar documentos |
| Módulo | Nodo | Crear datos, evaluar un monto |
| Bundle | Ítem, aproximadamente | Un documento con sus campos |
| Router y filtros | Nodos de decisión como If o Switch | Salida verdadera o falsa de un If |
| Run once | Ejecución manual de prueba | Pulsar Execute Workflow con Manual Trigger |

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/01-workflow-items.svg" target="_blank" rel="noopener noreferrer"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/01-workflow-items.svg" style="display:block;width:100%;height:auto" loading="lazy" alt="Manual Trigger inicia el flujo; Documentos de prueba genera ítems que evalúa el primer If."></a><figcaption>Diagrama didáctico. El flujo empieza una vez y el If revisa cada documento que recibe.</figcaption></figure>

Un ítem normalmente tiene datos en `json` y puede tener archivos en `binary`. En esta práctica usamos datos JSON. Cuando un campo del nodo está en modo **Expression**, `{{ $json.monto_total }}` lee el monto del ítem actual. En modo **Fixed**, `500000` es el mismo umbral para todos los documentos.

Para comprobar un resultado, ejecuta el workflow desde **Manual Trigger**, abre un nodo y compara **Input** con **Output**. En un **If**, revisa ambas salidas. Para conexiones externas, utiliza las credenciales de n8n y revisa los archivos exportados antes de compartirlos. Esta práctica trabaja con datos ficticios y no requiere claves de API.

## 2. Docker para ejecutar n8n en tu equipo

| Concepto | Qué significa en la práctica |
| --- | --- |
| Imagen | Paquete de software que contiene n8n y su entorno. Una etiqueta fija ayuda a repetir la instalación. |
| Contenedor | Instancia de esa imagen que ejecutas en tu equipo. |
| Puerto | Punto de acceso. En el ejemplo, tu navegador entra por `5690` y Docker lo conecta con `5678` dentro del contenedor. |
| Volumen | Almacenamiento administrado por Docker que conserva los datos cuando se recrea el contenedor. |
| Compose | Lee un archivo YAML que declara los servicios y cómo se ejecutan. |

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/02-docker-local.svg" target="_blank" rel="noopener noreferrer"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/02-docker-local.svg" style="display:block;width:100%;height:auto" loading="lazy" alt="El navegador accede a n8n por el puerto local 5690 y el contenedor usa un volumen para los datos."></a><figcaption>Diagrama de la instalación local mínima. El puerto publicado y el puerto interno cumplen tareas distintas.</figcaption></figure>

### Alternativa mínima para la demostración

Si tienes el paquete de la actividad, sigue su `compose.yaml`. La práctica del curso describe tres servicios: n8n, PostgreSQL y la API de laboratorio. En esa configuración, n8n abre en `http://localhost:5690` y la API en el puerto `5691`.

La siguiente configuración complementaria levanta **solo n8n con SQLite**. Sirve para construir y probar el workflow de esta guía. Si el paquete del curso ya está usando el puerto 5690, utiliza esa instancia o cambia el puerto local de esta alternativa.

Guarda esto en una carpeta nueva con el nombre `compose.yaml`:

```yaml
services:
  n8n:
    image: n8nio/n8n:2.44.6
    ports:
      - "127.0.0.1:5690:5678"
    environment:
      TZ: America/Santiago
      GENERIC_TIMEZONE: America/Santiago
      N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS: "true"
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  n8n_data:
```

Desde esa carpeta, comprueba Docker, valida el YAML e inicia el servicio:

```bash
docker --version
docker compose version
docker compose config -q
docker compose up -d
docker compose ps
```

Abre [n8n en tu equipo](http://localhost:5690). Si es la primera vez, configura una cuenta local de laboratorio. Abre también [la comprobación de salud](http://localhost:5690/healthz) y busca el estado `ok`. Si el editor no carga, revisa `docker compose logs n8n` y confirma que el puerto local esté disponible. Si al cambiar el puerto usas, por ejemplo, `5692`, usa ese mismo valor en el navegador.

**Al terminar:** `docker compose stop` detiene los servicios y `docker compose start` los vuelve a iniciar. En esta configuración, `docker compose down` retira los contenedores y conserva el volumen nombrado. La opción `-v` elimina los volúmenes de la práctica y sus datos. Al autoalojar, tú administras los respaldos, las actualizaciones y la disponibilidad.

## 3. Construye el workflow con cuatro documentos

Crea un workflow llamado **Lab Calbuco · Decisión documental**.

1. Agrega **Manual Trigger** y conéctalo a un nodo **Code** llamado **Documentos de prueba**. Selecciona **Run Once for All Items** con JavaScript. Pega el bloque completo. Úsalo como fuente de datos ficticios para poder concentrarte en los nodos de decisión.

```javascript
return [
  { json: { documento: 'OC-9102', monto_total: 320000 } },
  { json: { documento: 'Factura 4521', monto_total: 1250000 } },
  { json: { documento: 'Corrupto', monto_total: null } },
  { json: { documento: 'Borde', monto_total: 500000 } },
];
```

2. Agrega un nodo **If** llamado **Datos completos**. Evalúa `{{ $json.monto_total }}` como número y selecciona la operación de existencia (**exists**). Confirma con el caso `null` que tu configuración lo envía por **false**. Para esta práctica solo comprobamos la presencia del monto con los datos controlados del bloque.
3. Conecta **true** a un segundo **If**, **Supera umbral**. Evalúa el mismo campo con comparación numérica **is greater than** y escribe `500000` como valor fijo.
4. Agrega un **Edit Fields (Set)** al final de cada rama. En modo **Manual Mapping**, añade el campo de texto `estado` y conserva los campos de entrada. Usa estos estados:

| Nodo de origen | Salida | Texto fijo en `estado` |
| --- | --- | --- |
| Datos completos | false | `Contingencia` |
| Supera umbral | true | `Pendiente` |
| Supera umbral | false | `Aprobado` |

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/03-rutas-calbuco.svg" target="_blank" rel="noopener noreferrer"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/03-rutas-calbuco.svg" style="display:block;width:100%;height:auto" loading="lazy" alt="El primer If manda los datos sin monto a contingencia; el segundo separa valores superiores a 500.000 de los demás."></a><figcaption>Diagrama de decisión. El caso de 500.000 va por la salida falsa del segundo If y queda aprobado.</figcaption></figure>

**Para conversar:** ¿qué cambia si `monto_total` llega como texto? La actividad entrega números y un `null` deliberadamente. Al incorporar una API o un PDF real, comprueba y normaliza tipos antes de comparar. Un dato faltante requiere una ruta de negocio. Un nodo que falla requiere revisar la ejecución y la causa del error.

## 4. Ejecuta, verifica y exporta

1. Pulsa **Execute Workflow**. Verifica que **Documentos de prueba** entregue cuatro ítems.
2. Abre las salidas de los If y de cada **Edit Fields**. Comprueba cada documento en la tabla. Los resultados mostrados son los esperados para esta configuración.

| Documento | Monto (CLP) | Estado esperado |
| --- | ---: | --- |
| OC-9102 | 320.000 | Aprobado |
| Factura 4521 | 1.250.000 | Pendiente |
| Corrupto | Sin dato (`null`) | Contingencia |
| Borde | 500.000 | Aprobado |

3. Cambia temporalmente el caso **Borde** a `500001`, ejecuta y verifica que ahora quede **Pendiente**. Restáuralo a `500000` y guarda el workflow.
4. Abre el menú del workflow y elige **Download** para exportarlo como JSON. Comprueba que el archivo incluya los nodos y las conexiones del flujo. Guarda como evidencia dos salidas de nodo, el estado de `docker compose ps` y la respuesta de `/healthz`. Si lo guardas en GitHub, revisa el JSON y deja el archivo `.env` fuera del repositorio.

### Diagnóstico durante la práctica

| Si ocurre esto | Revisa primero |
| --- | --- |
| Docker no responde. | Comprueba que el motor de Docker esté iniciado y ejecuta `docker compose version`. |
| Compose no encuentra el archivo. | Abre la terminal en la carpeta que contiene `compose.yaml`. |
| El navegador no abre el editor. | Revisa `docker compose ps`, los logs y el puerto local del YAML. |
| El caso Borde queda pendiente en $500.000. | Comprueba que el segundo If use `>`, con un umbral de tipo numérico. |
| El estado aparece, pero se perdió el documento. | Activa en Edit Fields la salida de los campos de entrada. |

```quiz
? ¿Qué compruebas si abres Output de Documentos de prueba?
- Que existen cuatro workflows.
+ Que una ejecución generó cuatro ítems.
- Que Docker abrió cuatro puertos.
> Cada ítem representa un documento y se procesa en una misma ejecución.
? ¿A qué salida llega el caso con monto null?
- Aprobado.
- Pendiente.
+ Contingencia, por el primer If.
> Comprueba primero que exista un monto; solo después se evalúa el umbral.
? ¿Qué mantiene los datos de esta instalación cuando se recrea el contenedor?
- El puerto 5690.
+ El volumen n8n_data.
- El enlace del navegador.
> El volumen conserva el almacenamiento de la instancia.
```

[Manual Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.manualworkflowtrigger/) · [If](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.if/) · [Edit Fields](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.set/) · [Exportar workflows](https://docs.n8n.io/workflows/export-import/) · [Instalación con Docker](https://docs.n8n.io/hosting/installation/docker/)
