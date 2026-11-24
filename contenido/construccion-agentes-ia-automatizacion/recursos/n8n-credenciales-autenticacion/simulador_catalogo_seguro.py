#!/usr/bin/env python3
"""API ficticia del catálogo de una biblioteca, con autenticación real.

Sirve para practicar credenciales en n8n. Usa solo la biblioteca estándar de Python.
TODOS los valores por defecto son de DEMOSTRACIÓN: no son seguros ni deben usarse en producción.

    python3 simulador_catalogo_seguro.py            # escucha en el puerto 8080
    PUERTO=8091 python3 simulador_catalogo_seguro.py

Rutas:
    GET  /salud                      comprueba que el servicio está activo
    GET  /catalogo/publico           sin autenticación (solo títulos y total de ejemplares)
    GET  /catalogo/api-key           cabecera X-API-Key
    GET  /catalogo/basic             cabecera Authorization: Basic usuario:clave (en Base64)
    POST /auth/token                 entrega un JWT si recibe usuario y clave correctos (JSON)
    GET  /catalogo/jwt               cabecera Authorization: Bearer <token>
    GET  /demo/token-vencido         ayuda solo para la clase: entrega un token ya vencido
    GET  /registro                   últimas peticiones recibidas (sin valores secretos)
    GET  /reiniciar                  borra el registro

Las rutas protegidas aceptan ?titulo=El faro de papel. Sin título devuelven todo el catálogo.
Cada petición se anota en la salida estándar sin mostrar claves, contraseñas ni tokens.
"""
import base64
import hashlib
import hmac
import json
import os
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PUERTO = int(os.environ.get("PUERTO", "8080"))

# Valores de DEMOSTRACIÓN. Se pueden cambiar con variables de entorno (ver .env.example).
API_KEY = os.environ.get("API_KEY", "demo-clave-api-biblioteca")
BASIC_USUARIO = os.environ.get("BASIC_USUARIO", "lector-demo")
BASIC_CLAVE = os.environ.get("BASIC_CLAVE", "demo-clave-basic")
JWT_USUARIO = os.environ.get("JWT_USUARIO", "lector-demo")
JWT_CLAVE = os.environ.get("JWT_CLAVE", "demo-clave-jwt")
# La clave de firma solo vive aquí, dentro del simulador. n8n nunca la conoce.
JWT_SECRETO = os.environ.get("JWT_SECRETO", "firma-solo-para-practica").encode()
JWT_VIGENCIA = int(os.environ.get("JWT_VIGENCIA", "300"))  # segundos
JWT_EMISOR = "catalogo-biblioteca-demo"

# Libro: (ejemplares totales, préstamos activos). Todos los datos son ficticios.
CATALOGO = {
    "El faro de papel": (5, 2),
    "Jardines de tinta": (4, 4),
    "Atlas de las nubes verdes": (7, 1),
    "La casa de los mapas": (3, 0),
    "Viaje al bosque azul": (6, 4),
    "Historias del reloj": (8, 3),
}

candado = threading.Lock()
registro = []


# ---------- JWT (HS256) ----------
def b64u(datos):
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


def b64u_decodificar(texto):
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def firmar(mensaje):
    return b64u(hmac.new(JWT_SECRETO, mensaje.encode(), hashlib.sha256).digest())


def crear_jwt(usuario, vigencia):
    ahora = int(time.time())
    cabecera = b64u(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    cuerpo = b64u(json.dumps({"iss": JWT_EMISOR, "sub": usuario, "iat": ahora, "exp": ahora + vigencia},
                             separators=(",", ":")).encode())
    mensaje = cabecera + "." + cuerpo
    return mensaje + "." + firmar(mensaje)


def validar_jwt(token):
    """Devuelve (usuario, None) si el token es válido o (None, motivo) si no lo es."""
    partes = token.split(".")
    if len(partes) != 3:
        return None, "token_malformado"
    try:
        cabecera = json.loads(b64u_decodificar(partes[0]))
        datos = json.loads(b64u_decodificar(partes[1]))
    except Exception:
        return None, "token_malformado"
    if not isinstance(cabecera, dict) or not isinstance(datos, dict):
        return None, "token_malformado"
    if cabecera.get("alg") != "HS256":  # rechaza "none" y cualquier otro algoritmo
        return None, "algoritmo_no_permitido"
    if not hmac.compare_digest(firmar(partes[0] + "." + partes[1]), partes[2]):
        return None, "firma_invalida"
    if datos.get("iss") != JWT_EMISOR:
        return None, "emisor_invalido"
    exp = datos.get("exp")
    if not isinstance(exp, int) or exp <= int(time.time()):
        return None, "token_vencido"
    return datos.get("sub"), None


def iguales(a, b):
    return hmac.compare_digest(a.encode(), b.encode())


# ---------- Datos ----------
def datos_libro(titulo, completo):
    total, prestamos = CATALOGO[titulo]
    libro = {"titulo": titulo, "ejemplares_totales": total}
    if completo:
        libro.update({"prestamos_activos": prestamos, "disponibles": total - prestamos})
    return libro


class Manejador(BaseHTTPRequestHandler):
    server_version = "CatalogoSeguro/1.0"

    def log_message(self, formato, *args):
        pass

    def _responder(self, codigo, cuerpo, motivo=None, mecanismo="-", cabeceras=None, credencial=None):
        datos = json.dumps(cuerpo, ensure_ascii=False, indent=2).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        for k, v in (cabeceras or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(datos)
        entrada = {"hora": datetime.now().astimezone().strftime("%H:%M:%S"), "metodo": self.command,
                   "ruta": urlparse(self.path).path, "mecanismo": mecanismo,
                   "credencial_enviada": credencial, "estado": codigo, "motivo": motivo}
        with candado:
            registro.append(entrada)
            del registro[:-50]
        print(f"[{entrada['hora']}] {entrada['metodo']} {entrada['ruta']} -> {codigo}"
              f" ({mecanismo}{', ' + motivo if motivo else ''})", flush=True)

    def _rechazar(self, mecanismo, motivo, detalle, desafio, credencial):
        self._responder(401, {"error": "no_autorizado", "motivo": motivo, "detalle": detalle},
                        motivo=motivo, mecanismo=mecanismo, cabeceras={"WWW-Authenticate": desafio},
                        credencial=credencial)

    def _catalogo(self, mecanismo, completo):
        consulta = parse_qs(urlparse(self.path).query)
        titulo = (consulta.get("titulo") or [""])[0]
        if titulo:
            if titulo not in CATALOGO:
                return self._responder(404, {"error": "libro_no_encontrado", "titulo": titulo}, "libro_no_encontrado", mecanismo)
            cuerpo = {"acceso": mecanismo, **datos_libro(titulo, completo)}
        else:
            cuerpo = {"acceso": mecanismo, "libros": [datos_libro(t, completo) for t in CATALOGO]}
        self._responder(200, cuerpo, mecanismo=mecanismo, credencial="sí" if completo else "no")

    # ----- GET -----
    def do_GET(self):
        ruta = urlparse(self.path).path
        if ruta == "/salud":
            return self._responder(200, {"estado": "activo", "servicio": "catalogo-seguro"})
        if ruta == "/catalogo/publico":
            return self._catalogo("publico", completo=False)
        if ruta == "/catalogo/api-key":
            clave = self.headers.get("X-API-Key")
            if clave is None:
                return self._rechazar("api_key", "falta_credencial", "Falta la cabecera X-API-Key.", 'ApiKey header="X-API-Key"', "no")
            if not iguales(clave, API_KEY):
                return self._rechazar("api_key", "credencial_incorrecta", "La clave enviada no es válida.", 'ApiKey header="X-API-Key"', "sí")
            return self._catalogo("api_key", completo=True)
        if ruta == "/catalogo/basic":
            autorizacion = self.headers.get("Authorization", "")
            if not autorizacion.startswith("Basic "):
                return self._rechazar("basic", "falta_credencial", "Falta la cabecera Authorization: Basic.", 'Basic realm="catalogo"', "no")
            try:
                usuario, _, clave = base64.b64decode(autorizacion[6:], validate=True).decode().partition(":")
            except Exception:
                return self._rechazar("basic", "credencial_malformada", "El valor Base64 no es válido.", 'Basic realm="catalogo"', "sí")
            if not (iguales(usuario, BASIC_USUARIO) and iguales(clave, BASIC_CLAVE)):
                return self._rechazar("basic", "credencial_incorrecta", "Usuario o contraseña incorrectos.", 'Basic realm="catalogo"', "sí")
            return self._catalogo("basic", completo=True)
        if ruta == "/catalogo/jwt":
            autorizacion = self.headers.get("Authorization", "")
            if not autorizacion.startswith("Bearer "):
                return self._rechazar("jwt", "falta_credencial", "Falta la cabecera Authorization: Bearer <token>.", "Bearer", "no")
            _, motivo = validar_jwt(autorizacion[7:].strip())
            if motivo:
                textos = {"token_vencido": "El token venció. Solicita uno nuevo en /auth/token."}
                return self._rechazar("jwt", motivo, textos.get(motivo, "El token no es válido."),
                                      f'Bearer error="invalid_token", error_description="{motivo}"', "sí")
            return self._catalogo("jwt", completo=True)
        if ruta == "/demo/token-vencido":
            return self._responder(200, {"access_token": crear_jwt(JWT_USUARIO, -60), "token_type": "Bearer",
                                         "nota": "Solo para la clase: este token ya está vencido."}, mecanismo="demo")
        if ruta == "/registro":
            with candado:
                copia = list(registro)
            return self._responder(200, {"peticiones": len(copia), "detalle": copia})
        if ruta == "/reiniciar":
            with candado:
                registro.clear()
            print("registro reiniciado", flush=True)
            return self._responder(200, {"estado": "reiniciado"})
        self._responder(404, {"error": "ruta_no_encontrada"}, "ruta_no_encontrada")

    # ----- POST -----
    def do_POST(self):
        if urlparse(self.path).path != "/auth/token":
            return self._responder(404, {"error": "ruta_no_encontrada"}, "ruta_no_encontrada")
        try:
            largo = int(self.headers.get("Content-Length", "0"))
            cuerpo = json.loads(self.rfile.read(largo) or b"{}")
            usuario, clave = cuerpo["usuario"], cuerpo["clave"]
            if not isinstance(usuario, str) or not isinstance(clave, str):
                raise ValueError
        except Exception:
            return self._responder(400, {"error": "solicitud_invalida", "detalle": 'Envía un JSON con "usuario" y "clave".'},
                                   "solicitud_invalida", "jwt")
        if not (iguales(usuario, JWT_USUARIO) and iguales(clave, JWT_CLAVE)):
            return self._rechazar("jwt", "credencial_incorrecta", "Usuario o clave incorrectos.", 'Bearer realm="catalogo"', "sí")
        self._responder(200, {"access_token": crear_jwt(usuario, JWT_VIGENCIA), "token_type": "Bearer",
                              "expires_in": JWT_VIGENCIA}, mecanismo="jwt", credencial="sí")


if __name__ == "__main__":
    servidor = ThreadingHTTPServer(("0.0.0.0", PUERTO), Manejador)
    print(f"Catálogo seguro escuchando en el puerto {PUERTO}", flush=True)
    servidor.serve_forever()
