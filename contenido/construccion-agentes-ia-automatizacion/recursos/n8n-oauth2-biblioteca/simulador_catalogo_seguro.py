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

  OAuth 2.0 (Authorization Code, con PKCE opcional). El navegador usa /oauth/autorizar; n8n usa /oauth/token:
    GET  /oauth/autorizar            pantalla de consentimiento (client_id, redirect_uri, scope, state)
    POST /oauth/decidir              la persona pulsa Autorizar o Rechazar; vuelve a n8n con un código o con un error
    POST /oauth/token                canjea el código por tokens (authorization_code) o renueva (refresh_token)
    POST /oauth/revocar              el cliente revoca una autorización (RFC 7009)
    GET  /oauth/autorizaciones       la persona ve y revoca las autorizaciones que dio
    GET  /catalogo/oauth             cabecera Authorization: Bearer <access token>; exige el scope catalogo.leer
    GET  /oauth/perfil               cabecera Authorization: Bearer <access token>; exige el scope perfil.leer
    POST /demo/oauth/vencer-tokens   ayuda solo para practicar: vence todos los access tokens sin esperar 5 minutos
    GET  /registro                   últimas peticiones recibidas (sin valores secretos)
    GET  /reiniciar                  borra el registro

Las rutas protegidas aceptan ?titulo=El faro de papel. Sin título devuelven todo el catálogo.
Cada petición se anota en la salida estándar sin mostrar claves, contraseñas, códigos ni tokens.

AVISO: la parte OAuth es un simulador EDUCATIVO. Guarda todo en memoria (al reiniciar se pierden las autorizaciones), no tiene
inicio de sesión real, límites de intentos ni HTTPS. No lo uses como servidor de autorización en un sistema real.
"""
import base64
import hashlib
import hmac
import html
import json
import os
import re
import secrets
import threading
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlparse

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

# OAuth 2.0: la aplicación registrada (n8n) y la persona que autoriza. Todo ficticio y de demostración.
OAUTH_CLIENTE = os.environ.get("OAUTH_CLIENT_ID", "biblioteca-n8n")
OAUTH_SECRETO = os.environ.get("OAUTH_CLIENT_SECRET", "demo-secreto-oauth-biblioteca")
# Lista exacta de direcciones de vuelta permitidas (separadas por coma). Cualquier otra se rechaza.
OAUTH_REDIRECTS = [u.strip() for u in os.environ.get(
    "OAUTH_REDIRECT_URIS", "http://localhost:5680/rest/oauth2-credential/callback").split(",") if u.strip()]
OAUTH_CODIGO_VIGENCIA = int(os.environ.get("OAUTH_CODIGO_VIGENCIA", "60"))        # segundos, un solo uso
OAUTH_ACCESO_VIGENCIA = int(os.environ.get("OAUTH_ACCESO_VIGENCIA", "300"))       # segundos
OAUTH_REFRESH_VIGENCIA = int(os.environ.get("OAUTH_REFRESH_VIGENCIA", "86400"))   # segundos
OAUTH_CUENTA = "lectora-demo@biblioteca.example"
SCOPES = {
    "catalogo.leer": "Consultar el catálogo: título, ejemplares totales, préstamos activos y disponibles (solo lectura)",
    "perfil.leer": "Ver el nombre de la cuenta (no da acceso al catálogo)",
}
SCOPE_MINIMO = "perfil.leer"  # lo que se concede si la aplicación no pide ningún permiso

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


# ---------- OAuth 2.0 (estado en memoria) ----------
solicitudes = {}    # id -> petición de autorización pendiente de consentimiento
codigos = {}        # código -> datos de la autorización y si ya se usó
concesiones = {}    # id -> autorización dada por la persona (scope, si está revocada)
accesos = {}        # access token -> {concesion, exp}
refrescos = {}      # refresh token -> {concesion, exp}
SOLICITUD_VIGENCIA = 600


def token_aleatorio(prefijo):
    return prefijo + secrets.token_urlsafe(32)


def limpiar_oauth():
    """Descarta lo vencido. Se llama con el candado tomado."""
    ahora = time.time()
    for tabla, campo in ((solicitudes, "exp"), (codigos, "exp")):
        for k in [k for k, v in tabla.items() if v[campo] <= ahora - 3600]:
            del tabla[k]


def desafio_s256(verificador):
    return b64u(hashlib.sha256(verificador.encode()).digest())


def revocar_concesion(concesion_id):
    """Revoca la autorización completa: sus access tokens y su refresh token dejan de servir."""
    c = concesiones.get(concesion_id)
    if c:
        c["revocada"] = True


def emitir_tokens(concesion_id, con_refresh):
    """Crea un access token (y, la primera vez, el refresh token) para una autorización. Candado tomado."""
    c = concesiones[concesion_id]
    ahora = time.time()
    acceso = token_aleatorio("at_")
    accesos[acceso] = {"concesion": concesion_id, "exp": ahora + OAUTH_ACCESO_VIGENCIA}
    if con_refresh:
        c["refresh"] = token_aleatorio("rt_")
        refrescos[c["refresh"]] = {"concesion": concesion_id, "exp": ahora + OAUTH_REFRESH_VIGENCIA}
    return {"access_token": acceso, "token_type": "Bearer", "expires_in": OAUTH_ACCESO_VIGENCIA,
            "refresh_token": c["refresh"], "scope": " ".join(c["scope"])}


ESTILO = ("body{font-family:system-ui,sans-serif;background:#f4efe3;margin:0;padding:24px;color:#222}"
          ".t{max-width:520px;margin:32px auto;background:#fff;border:1px solid #d9d0bb;border-radius:10px;padding:24px}"
          "h1{font-size:1.25rem;margin:0 0 12px}ul{padding-left:20px}code{background:#eee;padding:1px 5px;border-radius:4px}"
          ".b{display:flex;gap:12px;margin-top:20px}button{font-size:1rem;padding:10px 18px;border-radius:6px;border:1px solid #888;cursor:pointer}"
          ".ok{background:#2f6f4f;color:#fff;border-color:#2f6f4f}.no{background:#fff}"
          ".n{font-size:.85rem;color:#555;margin-top:16px}table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid #ddd;padding:6px;text-align:left}")


def pagina(titulo, cuerpo):
    return (f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{html.escape(titulo)}</title><style>{ESTILO}</style></head><body><div class=\"t\">{cuerpo}</div></body></html>")


def pantalla_consentimiento(solicitud_id, sol):
    permisos = "".join(f"<li><code>{html.escape(s)}</code>: {html.escape(SCOPES[s])}</li>" for s in sol["scope"])
    aviso = ""
    if sol["scope_omitido"]:
        aviso = f"<p class=\"n\">La aplicación no pidió permisos: solo se concede el mínimo (<code>{SCOPE_MINIMO}</code>).</p>"
    return pagina("Autorizar acceso", f"""<h1>Biblioteca (demostración): autorizar acceso</h1>
<p>La aplicación <strong>{html.escape(sol["cliente"])}</strong> (n8n) pide permiso para actuar con la cuenta
<strong>{html.escape(OAUTH_CUENTA)}</strong> (cuenta ficticia).</p>
<p>Permisos que pide:</p><ul>{permisos}</ul>{aviso}
<form method="post" action="/oauth/decidir">
<input type="hidden" name="solicitud" value="{html.escape(solicitud_id)}">
<div class="b"><button class="ok" name="decision" value="autorizar">Autorizar</button>
<button class="no" name="decision" value="rechazar">Rechazar</button></div></form>
<p class="n">Autorizar no entrega tu contraseña a la aplicación: solo le da un permiso limitado que puedes revocar cuando quieras.
Simulador educativo: no uses este servidor en un sistema real.</p>""")


# ---------- Datos ----------
def datos_libro(titulo, completo):
    total, prestamos = CATALOGO[titulo]
    libro = {"titulo": titulo, "ejemplares_totales": total}
    if completo:
        libro.update({"prestamos_activos": prestamos, "disponibles": total - prestamos})
    return libro


class Manejador(BaseHTTPRequestHandler):
    server_version = "CatalogoSeguro/2.0"

    def log_message(self, formato, *args):
        pass

    def _responder(self, codigo, cuerpo, motivo=None, mecanismo="-", cabeceras=None, credencial=None):
        if isinstance(cuerpo, str):
            datos, tipo = cuerpo.encode(), "text/html; charset=utf-8"
        else:
            datos, tipo = json.dumps(cuerpo, ensure_ascii=False, indent=2).encode(), "application/json; charset=utf-8"
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
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

    # ----- OAuth 2.0 -----
    def _formulario(self):
        try:
            largo = min(int(self.headers.get("Content-Length", "0") or 0), 65536)
        except ValueError:
            largo = 0
        texto = self.rfile.read(largo).decode(errors="replace")
        return {k: v[0] for k, v in parse_qs(texto, keep_blank_values=True).items()}

    def _volver(self, redirect, params, state, motivo):
        """Devuelve al navegador a la aplicación con un código o un error (siempre con el state recibido)."""
        if state:
            params = {**params, "state": state}
        destino = redirect + ("&" if "?" in redirect else "?") + urlencode(params)
        self._responder(302, "", motivo=motivo, mecanismo="oauth2", credencial="no",
                        cabeceras={"Location": destino, "Cache-Control": "no-store"})

    def _error_pagina(self, texto, motivo):
        """Errores que NO se pueden devolver a la aplicación (cliente o redirect_uri dudosos): se muestran en pantalla."""
        self._responder(400, pagina("No se puede continuar", f"<h1>No se puede continuar</h1><p>{html.escape(texto)}</p>"),
                        motivo=motivo, mecanismo="oauth2", credencial="no", cabeceras={"Cache-Control": "no-store"})

    def _error_oauth(self, codigo, error, detalle, motivo, cabeceras=None):
        self._responder(codigo, {"error": error, "error_description": detalle}, motivo=motivo, mecanismo="oauth2",
                        cabeceras={"Cache-Control": "no-store", "Pragma": "no-cache", **(cabeceras or {})}, credencial="sí")

    def _cliente_valido(self, datos):
        autorizacion = self.headers.get("Authorization", "")
        if autorizacion.startswith("Basic "):
            try:
                cliente, _, secreto = base64.b64decode(autorizacion[6:], validate=True).decode().partition(":")
            except Exception:
                return False
        else:
            cliente, secreto = datos.get("client_id", ""), datos.get("client_secret", "")
        return iguales(cliente, OAUTH_CLIENTE) and iguales(secreto, OAUTH_SECRETO)

    def _autorizar(self):
        q = {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}
        # 1) Si el cliente o la dirección de vuelta no son los registrados, NO se redirige a ningún lado.
        if q.get("client_id") != OAUTH_CLIENTE:
            return self._error_pagina("La aplicación no está registrada (client_id desconocido).", "cliente_desconocido")
        redirect = q.get("redirect_uri", "")
        if redirect not in OAUTH_REDIRECTS:
            return self._error_pagina("La dirección de vuelta (redirect_uri) no está registrada para esta aplicación.",
                                      "redirect_uri_no_registrada")
        # 2) Desde aquí los errores vuelven a la aplicación con el state.
        state = q.get("state", "")
        if q.get("response_type") != "code":
            return self._volver(redirect, {"error": "unsupported_response_type"}, state, "response_type_no_soportado")
        if not state:
            return self._volver(redirect, {"error": "invalid_request", "error_description": "Falta el parámetro state."},
                                state, "falta_state")
        pedidos = q.get("scope", "").split()
        if any(p not in SCOPES for p in pedidos):
            return self._volver(redirect, {"error": "invalid_scope", "error_description": "Permiso desconocido."},
                                state, "scope_desconocido")
        desafio = q.get("code_challenge", "")
        if desafio or q.get("code_challenge_method"):
            if q.get("code_challenge_method") != "S256" or not re.fullmatch(r"[A-Za-z0-9._~-]{43,128}", desafio):
                return self._volver(redirect, {"error": "invalid_request", "error_description": "PKCE: solo se acepta S256."},
                                    state, "pkce_invalido")
        solicitud = {"cliente": OAUTH_CLIENTE, "redirect": redirect, "state": state, "scope": pedidos or [SCOPE_MINIMO],
                     "scope_omitido": not pedidos, "desafio": desafio, "exp": time.time() + SOLICITUD_VIGENCIA}
        ident = secrets.token_urlsafe(24)
        with candado:
            limpiar_oauth()
            solicitudes[ident] = solicitud
        self._responder(200, pantalla_consentimiento(ident, solicitud), mecanismo="oauth2", credencial="no", cabeceras={
            "Cache-Control": "no-store", "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'"})

    def _decidir(self):
        datos = self._formulario()
        with candado:
            solicitud = solicitudes.pop(datos.get("solicitud", ""), None)
        if solicitud is None or solicitud["exp"] <= time.time():
            return self._error_pagina("La solicitud venció o ya se usó. Vuelve a empezar desde n8n.", "solicitud_vencida")
        if datos.get("decision") != "autorizar":
            return self._volver(solicitud["redirect"], {"error": "access_denied"}, solicitud["state"], "consentimiento_rechazado")
        codigo = token_aleatorio("cd_")
        with candado:
            codigos[codigo] = {**solicitud, "exp": time.time() + OAUTH_CODIGO_VIGENCIA, "usado": False, "concesion": None}
        self._volver(solicitud["redirect"], {"code": codigo}, solicitud["state"], "consentimiento_aceptado")

    def _token(self):
        datos = self._formulario()
        if not self._cliente_valido(datos):
            return self._error_oauth(401, "invalid_client", "Client ID o Client Secret incorrectos.", "cliente_invalido",
                                     {"WWW-Authenticate": 'Basic realm="oauth"'})
        grant = datos.get("grant_type")
        if grant == "authorization_code":
            return self._canjear_codigo(datos)
        if grant == "refresh_token":
            return self._renovar(datos)
        self._error_oauth(400, "unsupported_grant_type", "Usa authorization_code o refresh_token.", "grant_no_soportado")

    def _canjear_codigo(self, datos):
        codigo, motivo, respuesta = datos.get("code", ""), None, None
        with candado:
            r = codigos.get(codigo)
            if r is None:
                motivo = "codigo_desconocido"
            elif r["usado"]:
                # Reutilizar un código es señal de robo: se revoca lo que ya se había emitido con él.
                revocar_concesion(r["concesion"])
                motivo = "codigo_reutilizado"
            else:
                r["usado"] = True  # un solo uso, aunque el canje falle
                if r["exp"] <= time.time():
                    motivo = "codigo_vencido"
                elif r["redirect"] != datos.get("redirect_uri"):
                    motivo = "redirect_uri_distinta"
                elif r["desafio"] and not iguales(desafio_s256(datos.get("code_verifier", "")), r["desafio"]):
                    motivo = "pkce_invalido"
                else:
                    ident = secrets.token_urlsafe(8)
                    concesiones[ident] = {"cliente": r["cliente"], "scope": r["scope"], "revocada": False,
                                          "creada": datetime.now().astimezone().strftime("%H:%M:%S"), "refresh": None}
                    r["concesion"] = ident
                    respuesta = emitir_tokens(ident, True)
        if motivo:
            return self._error_oauth(400, "invalid_grant", "El código no es válido, venció, ya se usó o no coincide.", motivo)
        self._responder(200, respuesta, mecanismo="oauth2", credencial="sí",
                        cabeceras={"Cache-Control": "no-store", "Pragma": "no-cache"})

    def _renovar(self, datos):
        motivo, respuesta = None, None
        with candado:
            reg = refrescos.get(datos.get("refresh_token", ""))
            if reg is None:
                motivo = "refresh_token_desconocido"
            elif concesiones[reg["concesion"]]["revocada"]:
                motivo = "autorizacion_revocada"
            elif reg["exp"] <= time.time():
                motivo = "refresh_token_vencido"
            else:
                respuesta = emitir_tokens(reg["concesion"], False)
        if motivo:
            return self._error_oauth(400, "invalid_grant", "El refresh token no es válido, venció o fue revocado.", motivo)
        self._responder(200, respuesta, mecanismo="oauth2", credencial="sí",
                        cabeceras={"Cache-Control": "no-store", "Pragma": "no-cache"})

    def _revocar(self):
        datos = self._formulario()
        if not self._cliente_valido(datos):
            return self._error_oauth(401, "invalid_client", "Client ID o Client Secret incorrectos.", "cliente_invalido",
                                     {"WWW-Authenticate": 'Basic realm="oauth"'})
        token = datos.get("token", "")
        with candado:
            reg = refrescos.get(token) or accesos.get(token)
            if reg:
                revocar_concesion(reg["concesion"])  # revocar cualquiera de los dos tokens revoca toda la autorización
        # Siempre 200, exista o no el token (RFC 7009): no se revela qué tokens existen.
        self._responder(200, {"estado": "ok"}, motivo="revocacion", mecanismo="oauth2", credencial="sí")

    def _validar_oauth(self, scope_requerido):
        """Devuelve la autorización si el token sirve; si no, responde 401 o 403 y devuelve None."""
        autorizacion = self.headers.get("Authorization", "")
        if not autorizacion.startswith("Bearer "):
            self._rechazar("oauth2", "falta_credencial", "Falta la cabecera Authorization: Bearer <access token>.",
                           'Bearer realm="catalogo"', "no")
            return None
        with candado:
            reg = accesos.get(autorizacion[7:].strip())
            concesion = dict(concesiones[reg["concesion"]]) if reg else None
        motivo = None
        if reg is None:
            motivo, detalle = "token_desconocido", "El access token no existe. Autoriza la conexión de nuevo."
        elif concesion["revocada"]:
            motivo, detalle = "autorizacion_revocada", "La persona revocó la autorización. Hay que volver a autorizar."
        elif reg["exp"] <= time.time():
            motivo, detalle = "token_vencido", "El access token venció. Renuévalo con el refresh token."
        if motivo:
            self._rechazar("oauth2", motivo, detalle, f'Bearer error="invalid_token", error_description="{motivo}"', "sí")
            return None
        if scope_requerido not in concesion["scope"]:
            self._responder(403, {"error": "prohibido", "motivo": "insufficient_scope",
                                  "detalle": "El token es válido, pero no tiene el permiso que exige esta ruta.",
                                  "requerido": scope_requerido, "concedidos": concesion["scope"]},
                            motivo="insufficient_scope", mecanismo="oauth2", credencial="sí",
                            cabeceras={"WWW-Authenticate": f'Bearer error="insufficient_scope", scope="{scope_requerido}"'})
            return None
        return concesion

    def _autorizaciones(self):
        with candado:
            filas = list(concesiones.items())
        cuerpo = ""
        for ident, c in filas:
            estado = "revocada" if c["revocada"] else "vigente"
            boton = "" if c["revocada"] else (
                f'<form method="post" action="/oauth/autorizaciones/revocar"><input type="hidden" name="autorizacion" '
                f'value="{html.escape(ident)}"><button class="no">Revocar</button></form>')
            cuerpo += (f"<tr><td>{html.escape(c['cliente'])}</td><td>{html.escape(' '.join(c['scope']))}</td>"
                       f"<td>{html.escape(c['creada'])}</td><td>{estado}</td><td>{boton}</td></tr>")
        tabla = (f"<table><tr><th>Aplicación</th><th>Permisos</th><th>Hora</th><th>Estado</th><th></th></tr>{cuerpo}</table>"
                 if cuerpo else "<p>Todavía no has autorizado ninguna aplicación.</p>")
        self._responder(200, pagina("Autorizaciones", f"<h1>Aplicaciones que autorizaste</h1>{tabla}"
                                    "<p class=\"n\">Revocar quita el acceso a esa aplicación sin cambiar tu contraseña.</p>"),
                        mecanismo="oauth2", credencial="no", cabeceras={"Cache-Control": "no-store"})

    def _revocar_persona(self):
        datos = self._formulario()
        with candado:
            revocar_concesion(datos.get("autorizacion", ""))
        self._responder(303, "", motivo="revocada_por_la_persona", mecanismo="oauth2", credencial="no",
                        cabeceras={"Location": "/oauth/autorizaciones"})

    def _vencer_tokens(self):
        with candado:
            for reg in accesos.values():
                reg["exp"] = time.time() - 1
            cantidad = len(accesos)
        self._responder(200, {"estado": "access_tokens_vencidos", "cantidad": cantidad,
                              "nota": "Solo para practicar: los refresh tokens siguen vigentes."}, mecanismo="demo")

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
        if ruta == "/oauth/autorizar":
            return self._autorizar()
        if ruta == "/oauth/autorizaciones":
            return self._autorizaciones()
        if ruta == "/catalogo/oauth":
            if self._validar_oauth("catalogo.leer"):
                self._catalogo("oauth2", completo=True)
            return
        if ruta == "/oauth/perfil":
            concesion = self._validar_oauth("perfil.leer")
            if concesion:
                self._responder(200, {"acceso": "oauth2", "cuenta": OAUTH_CUENTA, "scope": concesion["scope"]},
                                mecanismo="oauth2", credencial="sí")
            return
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
        acciones = {"/auth/token": self._token_jwt, "/oauth/decidir": self._decidir, "/oauth/token": self._token,
                    "/oauth/revocar": self._revocar, "/oauth/autorizaciones/revocar": self._revocar_persona,
                    "/demo/oauth/vencer-tokens": self._vencer_tokens}
        accion = acciones.get(urlparse(self.path).path)
        if accion is None:
            return self._responder(404, {"error": "ruta_no_encontrada"}, "ruta_no_encontrada")
        accion()

    def _token_jwt(self):
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
