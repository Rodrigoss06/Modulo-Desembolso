"""Validacion del JWT emitido por Seguridad (RS256 + JWKS) y usuario autenticado."""
from __future__ import annotations

from dataclasses import dataclass

import jwt

from .errores import ErrorNegocio

LEER = "DESEMBOLSO_LEER"
EJECUTAR = "DESEMBOLSO_EJECUTAR"
SUPERVISOR = "SUPERVISOR"
AUDITOR = "AUDITOR"


@dataclass(frozen=True)
class Usuario:
    id: str
    nombre: str
    rol: str
    permisos: frozenset[str]
    agencia_id: str | None
    agencia_nombre: str | None
    jti: str

    def tiene(self, permiso: str) -> bool:
        return permiso in self.permisos


class VerificadorJWT:
    def __init__(self, jwks_url: str, emisor: str, audiencia: str, timeout: float = 3.0):
        self._jwks = jwt.PyJWKClient(jwks_url, cache_keys=True, lifespan=600, timeout=int(max(timeout, 1)))
        self._emisor = emisor
        self._audiencia = audiencia

    def verificar(self, token: str) -> Usuario:
        try:
            clave = self._jwks.get_signing_key_from_jwt(token)
            datos = jwt.decode(token, clave.key, algorithms=["RS256"], audience=self._audiencia,
                               issuer=self._emisor, options={"require": ["exp", "iat", "sub"]})
        except jwt.PyJWKClientConnectionError as exc:
            raise ErrorNegocio(503, "DEPENDENCIA_NO_DISPONIBLE", "No se pudo validar el token con Seguridad",
                               {"modulo": "Seguridad"}) from exc
        except jwt.PyJWTError as exc:
            raise ErrorNegocio(401, "NO_AUTENTICADO", "Token inválido o vencido") from exc
        return Usuario(
            id=str(datos["sub"])[:40],
            nombre=datos.get("nombre", datos["sub"]),
            rol=datos.get("rol", ""),
            permisos=frozenset(datos.get("permisos", [])),
            agencia_id=datos.get("agencia_id"),
            agencia_nombre=datos.get("agencia_nombre"),
            jti=datos.get("jti", ""),
        )
