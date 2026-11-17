# Primer vistazo a n8n y Docker

Imagina que a un equipo le llegan presupuestos todo el día. Alguien tiene que mirar cada monto y decidir si se aprueba, se deja pendiente o se revisa porque falta información. **n8n** permite automatizar ese recorrido conectando pasos en una pantalla.

## 1. Qué es n8n

Un **workflow** es el recorrido completo de la automatización. Cada paso es un **nodo**. El primer nodo suele ser un **disparador** (*trigger*). Le dice a n8n cuándo empezar. Por ejemplo, un disparador manual inicia el flujo cuando alguien pulsa el botón de ejecutar.

| Si ya conoces Make | En n8n lo verás como |
| --- | --- |
| Escenario | Workflow o flujo |
| Módulo | Nodo |
| Bundle o paquete de datos | Ítem o registro, aproximadamente |
| Filtro que decide por dónde sigue un dato | Nodo If con una salida para cada respuesta |

## 2. Cómo pasan los datos de un nodo a otro

Cada presupuesto es un **ítem**. Puede tener campos como el nombre del documento y el monto. Una sola **ejecución** puede procesar varios ítems. Si entran cuatro presupuestos, el mismo flujo puede revisar los cuatro y darles resultados distintos.

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/01-workflow-items.svg" target="_blank" rel="noopener noreferrer"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/01-workflow-items.svg" style="display:block;width:100%;height:auto" loading="lazy" alt="Manual Trigger inicia el flujo; Documentos de prueba genera ítems que evalúa el primer If."></a><figcaption>El disparador inicia una ejecución. El nodo de decisión revisa el monto de cada documento.</figcaption></figure>

Al abrir un nodo, **Input** muestra lo que recibió y **Output** lo que devolvió. Por ejemplo, si el nodo recibe un presupuesto por $320.000 y agrega el estado «Aprobado», el monto sigue ahí y el estado aparece como un campo nuevo.

## 3. Cómo se toma una decisión

Un nodo **If** hace una pregunta sobre los datos y tiene dos salidas: **true** si la condición se cumple y **false** si no se cumple. En el ejemplo de Calbuco se usan dos preguntas en orden. Primero, ¿tenemos el monto? Si lo tenemos, ¿supera los $500.000?

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/03-rutas-calbuco.svg" target="_blank" rel="noopener noreferrer"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/03-rutas-calbuco.svg" style="display:block;width:100%;height:auto" loading="lazy" alt="El primer If manda los datos sin monto a contingencia; el segundo separa valores superiores a 500.000 de los demás."></a><figcaption>El primer If comprueba si hay monto. El segundo aplica la regla de aprobación.</figcaption></figure>

| Lo que llega | Qué pasa |
| --- | --- |
| Presupuesto por $320.000 | **Aprobado**. El monto queda por debajo del límite. |
| Presupuesto por $500.000 | **Aprobado**. La condición pregunta si el monto es estrictamente mayor. |
| Presupuesto por $1.250.000 | **Pendiente**. El monto supera el límite. |
| Presupuesto sin monto | **Contingencia**. Hace falta revisar el documento. |

Un presupuesto sin monto puede recorrer una ruta prevista. Si un nodo falla al leer o guardar datos, miramos el historial de la ejecución para ubicar el error técnico.

## 4. Para qué sirve Docker

Puedes usar n8n como servicio en la nube o ejecutarlo en tu propio equipo. **Docker** permite hacer lo segundo usando una configuración repetible.

<figure class="lamina-apunte" style="max-width:1000px;margin:18px auto 24px"><a href="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/02-docker-local.svg" target="_blank" rel="noopener noreferrer"><img src="contenido/construccion-agentes-ia-automatizacion/imagenes/n8n-docker/02-docker-local.svg" style="display:block;width:100%;height:auto" loading="lazy" alt="El navegador accede a n8n por el puerto local 5690 y el contenedor usa un volumen para los datos."></a><figcaption>El navegador abre n8n en tu equipo. Docker ejecuta la aplicación y el volumen conserva sus datos.</figcaption></figure>

| Palabra | Explicación |
| --- | --- |
| **Imagen** | Paquete de software que contiene n8n y lo que necesita para arrancar. |
| **Contenedor** | Una instancia de ese paquete que Docker pone en marcha. |
| **Puerto** | Número que usa el navegador para conectarse con la aplicación. |
| **Volumen** | Espacio donde Docker guarda datos para que sigan disponibles al recrear el contenedor. |
| **Compose** | Herramienta que lee un archivo con la configuración y pone en marcha los servicios. |

Cuando n8n corre en tu equipo, necesita que el equipo y el servicio sigan encendidos para ejecutar automatizaciones. También puedes exportar un workflow como archivo **JSON**, que guarda la estructura de los nodos y sus conexiones.

## 5. Instalar n8n con Docker

Estos pasos quedan como referencia si quieres abrir n8n en tu equipo. Si en la sesión te entregan una carpeta con su propio `compose.yaml`, usa ese archivo. El siguiente ejemplo levanta una instancia local de n8n con SQLite.

1. Instala **Docker Desktop** en Windows o macOS y ábrelo. En Linux también puedes usar **Docker Engine** con el complemento **Compose**. Para comprobar que tu terminal reconoce ambos comandos, ejecuta:

```bash
docker --version
docker compose version
```

[Instalación de Docker por sistema operativo](https://docs.docker.com/get-docker/)

2. Crea una carpeta y guarda en ella un archivo llamado `compose.yaml` con este contenido:

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

El navegador entra por el puerto **5690** de tu equipo. Dentro del contenedor, n8n escucha en el **5678**. El volumen `n8n_data` conserva los datos de la instancia.

3. Abre una terminal **en esa carpeta**. Inicia n8n en segundo plano con el primer comando y comprueba que esté en ejecución con el segundo:

```bash
docker compose up -d
docker compose ps
```

4. Abre **`http://localhost:5690`** en el navegador. La primera vez, n8n te pedirá crear una cuenta de propietario para esta instalación.

| Si necesitas… | Comando |
| --- | --- |
| Ver qué pasó durante el arranque | `docker compose logs n8n` |
| Detener n8n y conservar sus datos | `docker compose stop` |
| Volver a iniciar el contenedor detenido | `docker compose start` |

Si el puerto 5690 está ocupado, cambia ese número en el archivo y abre la dirección con el nuevo puerto. Si cambiaste la configuración, vuelve a ejecutar `docker compose up -d`. Evita agregar `-v` a `docker compose down` si quieres conservar los datos: esa opción elimina el volumen de este ejemplo.

## Autoevaluación

```quiz
? Entran cuatro presupuestos en una sola ejecución. ¿Qué representa cada ítem?
- Un workflow completo.
+ Un documento con sus datos.
- Un contenedor de Docker.
> La misma ejecución puede llevar cuatro registros, uno por documento.
? Con la regla «mayor que $500.000», ¿qué pasa con un presupuesto de exactamente $500.000?
- Queda pendiente.
- Va a contingencia.
+ Queda aprobado.
> La condición solo se cumple si el monto supera los $500.000.
? ¿Qué elemento de Docker permite conservar los datos cuando se recrea el contenedor?
+ El volumen.
- El puerto.
- La pestaña del navegador.
> El volumen mantiene los datos fuera del contenedor.
```
