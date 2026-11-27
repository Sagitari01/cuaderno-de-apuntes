# Biblioteca: webhook protegido y túneles

**Versión de referencia:** n8n 2.44.6. Instancia nueva, puerto local 5682; proxy local 8092. No hay credenciales reales.

1. Guarda compose.yaml y nginx.conf juntos. Ejecuta `docker compose config --quiet` y `docker compose up -d`.
2. Abre http://localhost:5682, configura el propietario e importa el workflow semicompletado.
3. Usa carpeta 1 de la colección solo en localhost. Configura Header Auth con `X-Biblioteca-Token`, guarda y publica.
4. Prueba carpeta 2 en 5682 y luego 8092. Ejecuta carpeta 3 en 8092: solo el POST al receptor de producción debe pasar a n8n.
5. Solo entonces ejecuta **`docker compose run --rm --no-deps tunnel`** en otra terminal. No necesitas instalar cloudflared en el equipo ni crear una cuenta. El agente apunta al proxy `http://proxy:8080` dentro de Docker; el servicio es opcional y no arranca con `docker compose up -d`. Si ya tienes cloudflared instalado, la alternativa es `cloudflared tunnel --url http://localhost:8092`. ngrok queda como referencia opcional.
6. Cambia baseUrl en Postman por la URL HTTPS y repite carpetas 2 y 3. Configura el valor local de tokenBiblioteca, no exportes el secreto.
7. Opcional: copia env.example a .env con URL_PUBLICA y recrea n8n y proxy juntos. Repite todas las verificaciones.
8. Al cerrar: Ctrl+C en el túnel y comprueba `docker compose ps -a`. Si el contenedor del túnel sigue Up, usa `docker stop NOMBRE_DEL_CONTENEDOR` con el nombre que muestra el listado. Verifica el fallo del acceso público y la continuidad local antes de despublicar el workflow, limpiar datos de prueba y detener con `docker compose down`. No uses -v si necesitas el volumen.

**Advertencia:** el workflow inicialmente no tiene autenticación. Nunca abras el túnel antes de protegerlo y comprobar el proxy local. El flujo no persiste préstamos, no deduplica eventos y no valida firmas. El editor queda fuera de la ruta del túnel por diseño. No publiques datos reales.

**Estado:** recorrido principal probado el 27/11/2026 en Windows, con PowerShell y curl.exe, n8n 2.44.6 y cloudflared 2026.11.2 (imagen latest). Se verificaron confirmaciones válidas, rechazos 403, bloqueo 404/405 y cierre del túnel con continuidad local. Consulta la guía para los comandos alternativos y el registro completo. Pendientes: Postman, capturas anonimizadas, visor y fijación de la imagen del agente. No se probaron ngrok ni la configuración opcional URL_PUBLICA.
