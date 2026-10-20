"""Simulador del Bus de Servicios y de los modulos contraparte de Desembolso.

Reproduce los contratos propuestos para CR-INT-04 (Evaluacion), CR-INT-05 (Cuentas),
CR-INT-06 (Cobranza), la validacion de identidad (Clientes) y Seguridad (OAuth2/JWKS,
antifraude y eventos). Permite inyectar fallas desde /_sim para probar el modulo.
Solo para Desarrollo y pruebas: guarda todo en memoria.
"""
from __future__ import annotations

import asyncio
import base64
import copy
import hashlib
import json
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from . import datos

LIMA = timezone(timedelta(hours=-5))
EMISOR, AUDIENCIA, KID = "bna-seguridad", "bna-api", "sim-bna-2026"

app = FastAPI(title="Simulador del Bus de Servicios BNA", version="1.0.0")
_lock = threading.Lock()
_clave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)

ESCENARIO_BASE: dict[str, Any] = {
    "cuentas_abono": "NORMAL",      # NORMAL | TIMEOUT_REGISTRADO | TIMEOUT_NO_REGISTRADO | RECHAZO | ERROR
    "demora_timeout_seg": 5.0,      # demora de las respuestas "perdidas"
    "cobranza_fallos": 0,           # proximas N entregas a Cobranza fallan con 503
    "evaluacion_caida": False,
    "clientes_caida": False,
    "cuentas_caida": False,
    "cobranza_caida": False,
    "antifraude_denegar": False,
}
estado: dict[str, Any] = {}


def _reiniciar() -> None:
    with _lock:
        estado.clear()
        estado.update({
            "escenario": dict(ESCENARIO_BASE),
            "aprobaciones": {a["aprobacion_id"]: copy.deepcopy(a) for a in datos.APROBACIONES},
            "cuentas": {c["cuenta_id"]: dict(c) for c in datos.CUENTAS},
            "abonos": {},          # clave -> registro
            "reversiones": {},     # clave -> registro
            "eventos_cobranza": {},  # evento_id -> acuse
            "activaciones": {},    # credito_id -> veces activado
            "eventos_seguridad": [],
            "intentos_abono": 0,
            "secuencia": 0,
            "ya_demorados": set(),  # creditos cuyo primer abono ya se "perdio"
        })


_reiniciar()


def _ahora_lima() -> datetime:
    return datetime.now(LIMA).replace(tzinfo=None, microsecond=0)


def _siguiente(prefijo: str) -> str:
    estado["secuencia"] += 1
    return f"{prefijo}-2026-{estado['secuencia']:06d}"


def _enmascarar(numero: str) -> str:
    return "****" + numero[-4:]


def _caido(bandera: str, modulo: str) -> None:
    if estado["escenario"][bandera]:
        raise HTTPException(503, {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": f"{modulo} no disponible (simulado)"})


def _hash(cuerpo: dict) -> str:
    return hashlib.sha256(json.dumps(cuerpo, sort_keys=True, default=str).encode()).hexdigest()


def _aprobacion_publica(a: dict) -> dict:
    cliente = datos.CLIENTES[a["cliente_id"]]
    vigente_hasta = (_ahora_lima() + timedelta(days=a["dias_vigencia"])).replace(hour=23, minute=59, second=59)
    return {
        "aprobacion_id": a["aprobacion_id"],
        "version": a.get("version", 1),
        "credito_id": a["credito_id"],
        "cliente_id": a["cliente_id"],
        "cliente_nombre": cliente["nombre"],
        "cliente_documento": cliente["documento"],
        "producto": a["producto"],
        "importe": f"{a['importe']:.2f}",
        "moneda": a["moneda"],
        "plazo_meses": a["plazo_meses"],
        "tasa_tea": a["tasa_tea"],
        "estado": a["estado"],
        "vigente_hasta": vigente_hasta.isoformat(),
    }


# ---------------------------------------------------------------------------
# Control del simulador
# ---------------------------------------------------------------------------
@app.get("/_sim/escenarios")
def ver_escenarios():
    return estado["escenario"]


@app.post("/_sim/escenarios")
def cambiar_escenarios(cambios: dict[str, Any]):
    with _lock:
        desconocidas = set(cambios) - set(ESCENARIO_BASE)
        if desconocidas:
            raise HTTPException(400, f"claves desconocidas: {sorted(desconocidas)}")
        estado["escenario"].update(cambios)
        return estado["escenario"]


@app.post("/_sim/reiniciar")
def reiniciar():
    _reiniciar()
    return {"ok": True}


@app.post("/_sim/aprobaciones/{aprobacion_id}")
def cambiar_aprobacion(aprobacion_id: str, cambios: dict[str, Any]):
    with _lock:
        a = estado["aprobaciones"].get(aprobacion_id)
        if not a:
            raise HTTPException(404)
        if "importe" in cambios:
            cambios["importe"] = Decimal(str(cambios["importe"]))
        a.update(cambios)
        return _aprobacion_publica(a)


@app.post("/_sim/cuentas/{cuenta_id}")
def cambiar_cuenta(cuenta_id: str, cambios: dict[str, Any]):
    with _lock:
        c = estado["cuentas"].get(cuenta_id)
        if not c:
            raise HTTPException(404)
        c.update(cambios)
        return c


@app.get("/_sim/estado")
def ver_estado():
    with _lock:
        return {
            "abonos": list(estado["abonos"].values()),
            "intentos_abono": estado["intentos_abono"],
            "reversiones": list(estado["reversiones"].values()),
            "eventos_cobranza": list(estado["eventos_cobranza"].values()),
            "activaciones": estado["activaciones"],
            "eventos_seguridad": len(estado["eventos_seguridad"]),
        }


@app.get("/health")
def salud():
    return {"estado": "ok"}


# ---------------------------------------------------------------------------
# Seguridad (OAuth2, JWKS, antifraude, eventos)
# ---------------------------------------------------------------------------
def _b64(n: int) -> str:
    return base64.urlsafe_b64encode(n.to_bytes((n.bit_length() + 7) // 8, "big")).rstrip(b"=").decode()


@app.get("/seguridad/v1/jwks.json")
def jwks():
    pub = _clave_privada.public_key().public_numbers()
    return {"keys": [{"kty": "RSA", "kid": KID, "use": "sig", "alg": "RS256", "n": _b64(pub.n), "e": _b64(pub.e)}]}


def _emitir(claims: dict, minutos: int = 30) -> dict:
    ahora = int(time.time())
    claims = {**claims, "iss": EMISOR, "aud": AUDIENCIA, "iat": ahora, "exp": ahora + minutos * 60, "jti": str(uuid.uuid4())}
    token = jwt.encode(claims, _clave_privada, algorithm="RS256", headers={"kid": KID})
    return {"access_token": token, "token_type": "bearer", "expires_in": minutos * 60}


@app.post("/seguridad/v1/token")
def token(grant_type: str = Form(...), username: str | None = Form(None), password: str | None = Form(None),
          client_id: str | None = Form(None), client_secret: str | None = Form(None)):
    if grant_type == "password":
        usuario = datos.USUARIOS.get(username or "")
        if not usuario or password != datos.CONTRASENA_DEMO:
            raise HTTPException(401, {"codigo": "CREDENCIALES_INVALIDAS", "mensaje": "Usuario o contraseña incorrectos"})
        return _emitir({"sub": username, "nombre": usuario["nombre"], "rol": usuario["rol"],
                        "permisos": usuario["permisos"], **datos.AGENCIA})
    if grant_type == "client_credentials":
        if datos.CLIENTES_SERVICIO.get(client_id or "") != client_secret:
            raise HTTPException(401, {"codigo": "CLIENTE_INVALIDO", "mensaje": "Cliente de servicio inválido"})
        return _emitir({"sub": f"svc:{client_id}", "nombre": client_id, "rol": "SERVICIO", "permisos": []})
    raise HTTPException(400, {"codigo": "GRANT_NO_SOPORTADO", "mensaje": grant_type})


@app.post("/seguridad/v1/antifraude/evaluaciones")
def antifraude(cuerpo: dict[str, Any]):
    denegar = estado["escenario"]["antifraude_denegar"] or Decimal(str(cuerpo.get("importe", "0"))) > Decimal("100000")
    return {"decision": "DENEGAR" if denegar else "PERMITIR", "referencia": f"AF-{uuid.uuid4().hex[:10].upper()}",
            "motivo": "Patrón de riesgo detectado (simulado)" if denegar else None}


@app.post("/seguridad/v1/eventos", status_code=202)
def eventos_seguridad(cuerpo: dict[str, Any]):
    with _lock:
        estado["eventos_seguridad"].append(cuerpo)
    return {"recibido": True}


# ---------------------------------------------------------------------------
# Evaluacion (CR-INT-04)
# ---------------------------------------------------------------------------
@app.get("/evaluacion/v1/aprobaciones")
def listar_aprobaciones(documento: str | None = None, credito_id: str | None = None):
    _caido("evaluacion_caida", "Evaluación")
    items = []
    for a in estado["aprobaciones"].values():
        doc = datos.CLIENTES[a["cliente_id"]]["documento"]
        if (documento and doc != documento) or (credito_id and a["credito_id"] != credito_id):
            continue
        items.append(_aprobacion_publica(a))
    return {"items": items}


@app.get("/evaluacion/v1/aprobaciones/{aprobacion_id}")
def obtener_aprobacion(aprobacion_id: str):
    _caido("evaluacion_caida", "Evaluación")
    a = estado["aprobaciones"].get(aprobacion_id)
    if not a:
        raise HTTPException(404, {"codigo": "APROBACION_NO_ENCONTRADA", "mensaje": "No existe la aprobación"})
    return _aprobacion_publica(a)


# ---------------------------------------------------------------------------
# Clientes (validacion de identidad)
# ---------------------------------------------------------------------------
@app.post("/clientes/v1/validaciones-identidad")
def validar_identidad(cuerpo: dict[str, Any]):
    _caido("clientes_caida", "Clientes")
    cliente_id = cuerpo.get("cliente_id")
    if cliente_id not in datos.CLIENTES:
        raise HTTPException(404, {"codigo": "CLIENTE_NO_ENCONTRADO", "mensaje": "Cliente inexistente"})
    rechazada = cliente_id in datos.IDENTIDAD_RECHAZADA
    return {
        "referencia": f"VID-{uuid.uuid4().hex[:12].upper()}",
        "resultado": "RECHAZADA" if rechazada else "APROBADA",
        "vence_en": (_ahora_lima() + timedelta(minutes=30)).isoformat(),
        "detalle": "La verificación biométrica no coincide con el titular" if rechazada else "Identidad del titular verificada",
    }


# ---------------------------------------------------------------------------
# Cuentas (CR-INT-05)
# ---------------------------------------------------------------------------
def _elegibilidad(c: dict | None, cliente_id: str, moneda: str | None) -> tuple[bool, str | None]:
    if c is None:
        return False, "CUENTA_INEXISTENTE"
    if c["cliente_id"] != cliente_id:
        return False, "TITULAR_DISTINTO"
    if c["estado"] != "ACTIVA":
        return False, "CUENTA_" + c["estado"]
    if c["titularidad"] != "INDIVIDUAL":
        return False, "CUENTA_MANCOMUNADA"
    if moneda and c["moneda"] != moneda:
        return False, "MONEDA_DISTINTA"
    return True, None


def _cuenta_publica(c: dict, cliente_id: str, moneda: str | None) -> dict:
    elegible, motivo = _elegibilidad(c, cliente_id, moneda)
    return {"cuenta_id": c["cuenta_id"], "numero_enmascarado": _enmascarar(c["numero"]), "producto": c["producto"],
            "moneda": c["moneda"], "estado": c["estado"], "titularidad": c["titularidad"],
            "elegible": elegible, "motivo": motivo}


@app.get("/cuentas/v1/cuentas-elegibles")
def cuentas_elegibles(cliente_id: str, moneda: str | None = None):
    _caido("cuentas_caida", "Cuentas")
    items = [_cuenta_publica(c, cliente_id, moneda) for c in estado["cuentas"].values() if c["cliente_id"] == cliente_id]
    return {"items": items}


@app.get("/cuentas/v1/cuentas/{cuenta_id}/elegibilidad")
def elegibilidad(cuenta_id: str, cliente_id: str, moneda: str | None = None):
    _caido("cuentas_caida", "Cuentas")
    c = estado["cuentas"].get(cuenta_id)
    elegible, motivo = _elegibilidad(c, cliente_id, moneda)
    return {"cuenta_id": cuenta_id, "elegible": elegible, "motivo": motivo,
            "numero_enmascarado": _enmascarar(c["numero"]) if c else None,
            "referencia": f"ELEG-{uuid.uuid4().hex[:10].upper()}"}


@app.post("/cuentas/v1/abonos", status_code=201)
async def abonar(cuerpo: dict[str, Any], x_idempotency_key: str = Header(...)):
    with _lock:
        estado["intentos_abono"] += 1
        escenario = dict(estado["escenario"])
        if escenario["cuentas_caida"]:
            raise HTTPException(503, {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Cuentas no disponible (simulado)"})
        previo = estado["abonos"].get(x_idempotency_key)
        if previo:
            if previo["hash"] != _hash(cuerpo):
                raise HTTPException(409, {"codigo": "IDEMPOTENCIA_CONFLICTO", "mensaje": "Clave usada con otro contenido"})
            return JSONResponse(status_code=200 if previo["estado"] == "CONFIRMADO" else 422, content=_abono_publico(previo))
        aprobacion = next((a for a in estado["aprobaciones"].values() if a["credito_id"] == cuerpo.get("credito_id")), {})
        comportamiento = escenario["cuentas_abono"]
        if comportamiento == "NORMAL":
            comportamiento = aprobacion.get("comportamiento", "NORMAL")
            if comportamiento == "TIMEOUT_REGISTRADO" and cuerpo.get("credito_id") in estado["ya_demorados"]:
                comportamiento = "NORMAL"
        cuenta = estado["cuentas"].get(cuerpo.get("cuenta_id"))
        elegible, motivo = _elegibilidad(cuenta, cuerpo.get("cliente_id", ""), cuerpo.get("moneda"))
        registro = {"clave": x_idempotency_key, "hash": _hash(cuerpo), "orden_id": cuerpo.get("orden_id"),
                    "credito_id": cuerpo.get("credito_id"), "cuenta_id": cuerpo.get("cuenta_id"),
                    "importe": str(cuerpo.get("importe")), "moneda": cuerpo.get("moneda")}
        if comportamiento == "RECHAZO" or not elegible:
            registro.update(estado="RECHAZADO", codigo=motivo or "CUENTA_CON_RETENCION",
                            motivo="La cuenta tiene una retención judicial vigente" if elegible else f"Cuenta no elegible: {motivo}")
            estado["abonos"][x_idempotency_key] = registro
            return JSONResponse(status_code=422, content=_abono_publico(registro))
        if comportamiento == "ERROR":
            raise HTTPException(500, {"codigo": "ERROR_INTERNO", "mensaje": "Falla interna simulada"})
        if comportamiento != "TIMEOUT_NO_REGISTRADO":
            registro.update(estado="CONFIRMADO", operacion_id=_siguiente("OPF"),
                            fecha_efectiva=_ahora_lima().isoformat())
            estado["abonos"][x_idempotency_key] = registro
        if comportamiento.startswith("TIMEOUT"):
            estado["ya_demorados"].add(cuerpo.get("credito_id"))
    if comportamiento.startswith("TIMEOUT"):
        await asyncio.sleep(escenario["demora_timeout_seg"])
        if comportamiento == "TIMEOUT_NO_REGISTRADO":
            raise HTTPException(504, {"codigo": "TIEMPO_AGOTADO", "mensaje": "Sin respuesta (simulado)"})
    return _abono_publico(registro)


def _abono_publico(r: dict) -> dict:
    return {k: r.get(k) for k in ("clave", "estado", "operacion_id", "fecha_efectiva", "codigo", "motivo", "importe", "moneda")}


@app.get("/cuentas/v1/abonos/{clave}")
def consultar_abono(clave: str):
    _caido("cuentas_caida", "Cuentas")
    r = estado["abonos"].get(clave)
    if not r:
        return JSONResponse(status_code=404, content={"clave": clave, "estado": "NO_ENCONTRADO"})
    return _abono_publico(r)


@app.get("/cuentas/v1/abonos")
def abonos_por_fecha(fecha: str):
    _caido("cuentas_caida", "Cuentas")
    items = [_abono_publico(r) | {"orden_id": r["orden_id"]} for r in estado["abonos"].values()
             if r.get("estado") in ("CONFIRMADO", "REVERTIDO") and r["fecha_efectiva"].startswith(fecha)]
    return {"items": items}


@app.post("/cuentas/v1/reversiones", status_code=201)
def revertir(cuerpo: dict[str, Any], x_idempotency_key: str = Header(...)):
    _caido("cuentas_caida", "Cuentas")
    with _lock:
        previo = estado["reversiones"].get(x_idempotency_key)
        if previo:
            return previo
        original = next((r for r in estado["abonos"].values() if r.get("operacion_id") == cuerpo.get("operacion_original_id")), None)
        if not original or original.get("estado") != "CONFIRMADO":
            r = {"clave": x_idempotency_key, "estado": "RECHAZADO", "motivo": "Operación original inexistente"}
            estado["reversiones"][x_idempotency_key] = r
            return JSONResponse(status_code=422, content=r)
        original["estado"] = "REVERTIDO"
        r = {"clave": x_idempotency_key, "estado": "CONFIRMADO", "operacion_id": _siguiente("REV"),
             "fecha_efectiva": _ahora_lima().isoformat()}
        estado["reversiones"][x_idempotency_key] = r
        return r


@app.get("/cuentas/v1/reversiones/{clave}")
def consultar_reversion(clave: str):
    r = estado["reversiones"].get(clave)
    if not r:
        return JSONResponse(status_code=404, content={"clave": clave, "estado": "NO_ENCONTRADO"})
    return r


# ---------------------------------------------------------------------------
# Cobranza (CR-INT-06)
# ---------------------------------------------------------------------------
@app.post("/cobranza/v1/eventos-desembolso")
def recibir_evento(cuerpo: dict[str, Any], x_idempotency_key: str = Header(...)):
    with _lock:
        if estado["escenario"]["cobranza_caida"]:
            raise HTTPException(503, {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Cobranza no disponible (simulado)"})
        if estado["escenario"]["cobranza_fallos"] > 0:
            estado["escenario"]["cobranza_fallos"] -= 1
            raise HTTPException(503, {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Falla transitoria (simulada)"})
        previo = estado["eventos_cobranza"].get(x_idempotency_key)
        if previo:
            return {**previo, "duplicado": True}
        acuse = {"evento_id": x_idempotency_key, "confirmacion_id": _siguiente("ACU"), "tipo": cuerpo.get("tipo"),
                 "orden_id": cuerpo.get("orden_id"), "credito_id": cuerpo.get("credito_id"),
                 "importe": cuerpo.get("importe"), "moneda": cuerpo.get("moneda"),
                 "recibido_en": _ahora_lima().isoformat(), "duplicado": False}
        estado["eventos_cobranza"][x_idempotency_key] = acuse
        if cuerpo.get("tipo") == "desembolso.confirmado":
            credito = cuerpo.get("credito_id")
            estado["activaciones"][credito] = estado["activaciones"].get(credito, 0) + 1
        return acuse


@app.get("/cobranza/v1/eventos-desembolso")
def eventos_por_fecha(fecha: str):
    if estado["escenario"]["cobranza_caida"]:
        raise HTTPException(503, {"codigo": "SERVICIO_NO_DISPONIBLE", "mensaje": "Cobranza no disponible (simulado)"})
    return {"items": [a for a in estado["eventos_cobranza"].values() if a["recibido_en"].startswith(fecha)]}


@app.exception_handler(HTTPException)
async def _errores(request: Request, exc: HTTPException):
    detalle = exc.detail if isinstance(exc.detail, dict) else {"codigo": "ERROR", "mensaje": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content=detalle)
