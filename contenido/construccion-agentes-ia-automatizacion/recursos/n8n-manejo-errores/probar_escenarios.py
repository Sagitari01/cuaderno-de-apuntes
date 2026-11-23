#!/usr/bin/env python3
"""Envía los cinco casos de prueba al webhook de producción y compara con lo esperado.

    python3 probar_escenarios.py [URL_WEBHOOK] [URL_SIMULADOR]

Valores por defecto: http://localhost:5678/webhook/consulta-disponibilidad y http://localhost:8081
Necesita el workflow principal publicado y el simulador en marcha. Solo usa la biblioteca estándar.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

WEBHOOK = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5678/webhook/consulta-disponibilidad"
SIMULADOR = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8081"
DATOS = Path(__file__).parent / "datos-prueba"

# archivo, código HTTP esperado, estado esperado, disponibles esperados, peticiones al simulador, respuestas del simulador
ESPERADO = [
    ("01-exito.json", 200, "confirmado", 3, [200]),
    ("02-temporal.json", 200, "confirmado", 6, [503, 200]),
    ("03-caida-opcional.json", 200, "degradado", None, [503, 503, 503]),
    ("04-caida-obligatoria.json", 503, "error", "-", [503, 503, 503]),
    ("05-sin-stock.json", 200, "confirmado", 0, [200]),
]


def pedir(url, cuerpo=None):
    datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
    peticion = urllib.request.Request(url, datos, {"Content-Type": "application/json"} if datos else {})
    try:
        with urllib.request.urlopen(peticion, timeout=30) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "null")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8") or "null")


def main():
    pedir(SIMULADOR + "/reiniciar")
    fallos = 0
    for archivo, codigo, estado, disponibles, respuestas in ESPERADO:
        caso = json.loads((DATOS / archivo).read_text(encoding="utf-8"))
        http, cuerpo = pedir(WEBHOOK, caso)
        _, intentos = pedir(f"{SIMULADOR}/intentos?solicitud_id={caso['solicitud_id']}")
        vistas = [d["respuesta"] for d in intentos["detalle"]]
        ok = (http == codigo and cuerpo.get("estado") == estado
              and (disponibles == "-" or cuerpo.get("disponibles") == disponibles) and vistas == respuestas)
        fallos += not ok
        print(f"{'OK   ' if ok else 'FALLA'} {caso['solicitud_id']} {caso['escenario']:<10} HTTP {http} estado={cuerpo.get('estado')} "
              f"disponibles={cuerpo.get('disponibles')} respuestas del simulador={vistas}")
        time.sleep(1)
    print("Todos los escenarios coinciden." if not fallos else f"{fallos} escenario(s) no coinciden con lo esperado.")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
