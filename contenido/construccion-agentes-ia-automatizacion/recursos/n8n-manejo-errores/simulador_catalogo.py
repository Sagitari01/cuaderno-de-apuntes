#!/usr/bin/env python3
"""Simulador del catálogo de una biblioteca ficticia.

Responde consultas de disponibilidad por HTTP y puede fallar a propósito para
practicar el manejo de errores en n8n. Usa solo la biblioteca estándar de Python.

    python3 simulador_catalogo.py            # escucha en el puerto 8080
    PUERTO=8081 python3 simulador_catalogo.py

Rutas:
    GET /disponibilidad?solicitud_id=LIB-201&titulo=El faro de papel&escenario=exito
    GET /intentos?solicitud_id=LIB-201   peticiones recibidas por solicitud
    GET /registro                        todas las peticiones recibidas
    GET /reiniciar                       borra contadores y registro
    GET /salud                           comprobación de que el servicio está activo
"""
import json
import os
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PUERTO = int(os.environ.get("PUERTO", "8080"))

# Libro: (ejemplares totales, préstamos activos). Todos los datos son ficticios.
CATALOGO = {
    "El faro de papel": (5, 2),
    "Jardines de tinta": (4, 4),
    "Atlas de las nubes verdes": (7, 1),
    "La casa de los mapas": (3, 0),
    "Viaje al bosque azul": (6, 4),
    "Historias del reloj": (8, 3),
}
ESCENARIOS = ("exito", "temporal", "caida", "sin_stock")

candado = threading.Lock()
contadores = {}   # solicitud_id -> peticiones recibidas
registro = []     # una entrada por petición


def ahora():
    return datetime.now().astimezone().isoformat(timespec="seconds")


class Manejador(BaseHTTPRequestHandler):
    server_version = "SimuladorCatalogo/1.0"

    def responder(self, codigo, cuerpo):
        datos = json.dumps(cuerpo, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        url = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        if url.path == "/disponibilidad":
            return self.disponibilidad(q)
        if url.path == "/intentos":
            sid = q.get("solicitud_id", "")
            with candado:
                detalle = [r for r in registro if r["solicitud_id"] == sid]
                return self.responder(200, {"solicitud_id": sid, "peticiones": contadores.get(sid, 0), "detalle": detalle})
        if url.path == "/registro":
            with candado:
                return self.responder(200, {"total": len(registro), "contadores": contadores, "peticiones": registro})
        if url.path == "/reiniciar":
            with candado:
                contadores.clear()
                registro.clear()
            return self.responder(200, {"estado": "reiniciado"})
        if url.path == "/salud":
            return self.responder(200, {"estado": "activo"})
        return self.responder(404, {"error": "ruta_desconocida"})

    def disponibilidad(self, q):
        sid = q.get("solicitud_id", "")
        titulo = q.get("titulo", "")
        escenario = q.get("escenario", "")
        if not sid or escenario not in ESCENARIOS:
            return self.responder(400, {"error": "parametros_invalidos", "escenarios": list(ESCENARIOS)})
        with candado:
            contadores[sid] = contadores.get(sid, 0) + 1
            n = contadores[sid]
            if escenario == "caida":
                codigo = 503
            elif escenario == "temporal":
                codigo = 503 if n % 2 == 1 else 200   # falla en las peticiones impares
            else:
                codigo = 200
            if codigo == 200 and titulo not in CATALOGO:
                codigo = 404
            registro.append({"n": n, "hora": ahora(), "solicitud_id": sid, "titulo": titulo,
                             "escenario": escenario, "respuesta": codigo})
        print(f"[{ahora()}] {sid} #{n} {escenario} -> {codigo}", flush=True)
        if codigo == 503:
            return self.responder(503, {"error": "servicio_no_disponible", "solicitud_id": sid, "peticion": n})
        if codigo == 404:
            return self.responder(404, {"error": "titulo_desconocido", "titulo": titulo})
        total, prestamos = CATALOGO[titulo]
        if escenario == "sin_stock":
            prestamos = total
        return self.responder(200, {"solicitud_id": sid, "titulo": titulo, "ejemplares_totales": total,
                                    "prestamos_activos": prestamos, "disponibles": total - prestamos})

    def log_message(self, *args):
        pass  # el registro propio de arriba reemplaza al de http.server


if __name__ == "__main__":
    print(f"Simulador del catálogo escuchando en el puerto {PUERTO}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PUERTO), Manejador).serve_forever()
