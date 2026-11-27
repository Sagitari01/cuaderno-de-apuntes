# Biblioteca: webhook protegido y túneles

**Propósito:** recibir un evento externo de devolución de un libro, proteger el receptor mediante Header Auth, limitar las rutas expuestas mediante Nginx y utilizar un túnel HTTPS temporal. El workflow confirma la recepción, no modifica inventarios reales.

**Entorno:** n8n 2.44.6, editor local 5682, proxy 8092. Elige Postman o PowerShell como cliente HTTP. Los dos caminos están desarrollados paso a paso en la Guía 18.

1. Guarda compose.yaml y nginx.conf juntos. Ejecuta `docker compose config --quiet` y `docker compose up -d`.
2. Abre http://localhost:5682, configura el propietario e importa el workflow semicompletado.
3. Prueba la Test URL local con la escucha activada. En Postman importa `biblioteca-webhooks.postman_collection.json`, entra a Variables y deja baseUrl en http://localhost:5682. Abre la primera solicitud de carpeta 1. En PowerShell carga evento-biblioteca.json y ejecuta el POST de la sección 4 de la guía.
4. Configura Header Auth con `X-Biblioteca-Token`, guarda y publica. Configura el token local de Postman o la variable $token de PowerShell. Comprueba los tres casos: sin token (403), incorrecto (403) y correcto (200).
5. Cambia la base a http://localhost:8092. Repite los tres casos y comprueba los bloqueos de raíz, ruta de prueba, otro webhook y GET (carpeta 3 en Postman o comandos de la sección 6). No abras el túnel si falla un control.
6. Ejecuta `docker compose run --rm --no-deps tunnel` en otra terminal. Cloudflare Quick Tunnel no requiere cuenta; ngrok es opcional. El agente apunta a http://proxy:8080, no al editor.
7. Cambia baseUrl o $base por la URL HTTPS. Repite carpetas 2 y 3 en Postman o los bloques equivalentes en PowerShell. En Postman no ejecutes la colección completa: carpeta 1 solo se usa en local antes de proteger.
8. Pulsa Ctrl+C para cerrar el túnel y confirma `docker compose ps -a`. Si sigue Up, ejecuta `docker stop NOMBRE_DEL_CONTENEDOR` con el nombre del listado. Comprueba el fallo del acceso público y la continuidad local mediante una solicitud válida por 8092. Despublica el workflow y limpia los datos de prueba. `docker compose down` detiene el laboratorio sin borrar sus volúmenes.

**Seguridad:** nunca abras el túnel antes de configurar y probar Header Auth. Usa datos ficticios, no secretos reales, y respeta los permisos de red. No compartas el token en exports. La guía incluye resultados del recorrido de referencia del 27/11/2026 con PowerShell y curl.exe; la colección describe las mismas pruebas.

**Documentación:** consulta la Guía 18 para los dos caminos, explicaciones, pruebas, comparación y diagnóstico.
