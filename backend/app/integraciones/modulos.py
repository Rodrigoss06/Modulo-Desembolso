"""Adaptadores de los modulos contraparte. Los contratos son la propuesta del equipo (seccion 11.3)."""
from __future__ import annotations

import contextvars
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from ..config import Config
from ..core.dinero import a_decimal
from ..core.errores import DependenciaNoDisponible, ErrorNegocio
from ..core.tiempo import ahora_lima, desde_iso
from .bus import ClienteBus, cuerpo_o_error

log = logging.getLogger("desembolso.integraciones")


@dataclass(frozen=True)
class Aprobacion:
    aprobacion_id: str
    version: int
    credito_id: str
    cliente_id: str
    cliente_nombre: str
    cliente_documento: str
    producto: str
    importe: Decimal
    moneda: str
    plazo_meses: int | None
    tasa_tea: str | None
    estado: str
    vigente_hasta: datetime | None

    @property
    def habilitada(self) -> bool:
        return self.estado == "HABILITADA" and (self.vigente_hasta is None or self.vigente_hasta >= ahora_lima())

    @classmethod
    def desde(cls, d: dict) -> Aprobacion:
        return cls(
            aprobacion_id=d["aprobacion_id"], version=int(d.get("version", 1)), credito_id=d["credito_id"],
            cliente_id=d["cliente_id"], cliente_nombre=d.get("cliente_nombre", ""),
            cliente_documento=d.get("cliente_documento", ""), producto=d.get("producto", ""),
            importe=a_decimal(d["importe"]), moneda=d["moneda"], plazo_meses=d.get("plazo_meses"),
            tasa_tea=d.get("tasa_tea"), estado=d["estado"], vigente_hasta=desde_iso(d.get("vigente_hasta")))


class Evaluacion:
    """CR-INT-04: aprobaciones habilitadas por Evaluacion."""

    def __init__(self, bus: ClienteBus, config: Config):
        self._bus, self._config = bus, config

    def buscar(self, documento: str | None = None, credito_id: str | None = None) -> list[Aprobacion]:
        params = {k: v for k, v in {"documento": documento, "credito_id": credito_id}.items() if v}
        r = self._bus.solicitar("Evaluacion", "GET", "/evaluacion/v1/aprobaciones", params=params,
                                reintentos=self._config.reintentos_consulta)
        return [Aprobacion.desde(a) for a in cuerpo_o_error(r, "Evaluación")["items"]]

    def obtener(self, aprobacion_id: str) -> Aprobacion | None:
        r = self._bus.solicitar("Evaluacion", "GET", f"/evaluacion/v1/aprobaciones/{aprobacion_id}",
                                reintentos=self._config.reintentos_consulta)
        if r.status_code == 404:
            return None
        return Aprobacion.desde(cuerpo_o_error(r, "Evaluación"))


class Clientes:
    """Validacion de identidad del titular (IF-02); no se intercambia biometria."""

    def __init__(self, bus: ClienteBus):
        self._bus = bus

    def validar_identidad(self, cliente_id: str, metodo: str, agencia_id: str | None) -> dict:
        r = self._bus.solicitar("Clientes", "POST", "/clientes/v1/validaciones-identidad",
                                json={"cliente_id": cliente_id, "metodo": metodo, "canal": "AGENCIA", "agencia_id": agencia_id})
        return cuerpo_o_error(r, "Clientes")


class Cuentas:
    """CR-INT-05: elegibilidad de la cuenta destino y abono del credito."""

    def __init__(self, bus: ClienteBus, config: Config):
        self._bus, self._config = bus, config

    def elegibles(self, cliente_id: str, moneda: str) -> list[dict]:
        r = self._bus.solicitar("Cuentas", "GET", "/cuentas/v1/cuentas-elegibles",
                                params={"cliente_id": cliente_id, "moneda": moneda}, reintentos=self._config.reintentos_consulta)
        return cuerpo_o_error(r, "Cuentas")["items"]

    def elegibilidad(self, cuenta_id: str, cliente_id: str, moneda: str) -> dict:
        r = self._bus.solicitar("Cuentas", "GET", f"/cuentas/v1/cuentas/{cuenta_id}/elegibilidad",
                                params={"cliente_id": cliente_id, "moneda": moneda}, reintentos=self._config.reintentos_consulta)
        return cuerpo_o_error(r, "Cuentas")

    def abonar(self, cuerpo: dict, clave: str) -> dict:
        """Un solo intento. Timeout, error 5xx o conflicto de clave se tratan como resultado incierto."""
        r = self._bus.solicitar("Cuentas", "POST", "/cuentas/v1/abonos", json=cuerpo, clave=clave,
                                timeout=self._config.timeout_abono_seg)
        if r.status_code in (200, 201, 422):
            return r.json()
        raise DependenciaNoDisponible("Cuentas", incierto=True, causa=f"HTTP_{r.status_code}")

    def consultar_abono(self, clave: str) -> dict:
        r = self._bus.solicitar("Cuentas", "GET", f"/cuentas/v1/abonos/{clave}", reintentos=self._config.reintentos_consulta)
        if r.status_code == 404:
            return {"clave": clave, "estado": "NO_ENCONTRADO"}
        return cuerpo_o_error(r, "Cuentas")

    def abonos_por_fecha(self, fecha: str) -> list[dict]:
        r = self._bus.solicitar("Cuentas", "GET", "/cuentas/v1/abonos", params={"fecha": fecha},
                                reintentos=self._config.reintentos_consulta)
        return cuerpo_o_error(r, "Cuentas")["items"]

    def revertir(self, cuerpo: dict, clave: str) -> dict:
        r = self._bus.solicitar("Cuentas", "POST", "/cuentas/v1/reversiones", json=cuerpo, clave=clave,
                                timeout=self._config.timeout_abono_seg)
        if r.status_code in (200, 201, 422):
            return r.json()
        raise DependenciaNoDisponible("Cuentas", incierto=True, causa=f"HTTP_{r.status_code}")

    def consultar_reversion(self, clave: str) -> dict:
        r = self._bus.solicitar("Cuentas", "GET", f"/cuentas/v1/reversiones/{clave}", reintentos=self._config.reintentos_consulta)
        if r.status_code == 404:
            return {"clave": clave, "estado": "NO_ENCONTRADO"}
        return cuerpo_o_error(r, "Cuentas")


class Cobranza:
    """CR-INT-06: entrega del desembolso confirmado; Cobranza deduplica por evento_id."""

    def __init__(self, bus: ClienteBus, config: Config):
        self._bus, self._config = bus, config

    def enviar_evento(self, evento: dict, evento_id: str) -> dict:
        r = self._bus.solicitar("Cobranza", "POST", "/cobranza/v1/eventos-desembolso", json=evento, clave=evento_id)
        return cuerpo_o_error(r, "Cobranza")

    def acuses_por_fecha(self, fecha: str) -> list[dict]:
        r = self._bus.solicitar("Cobranza", "GET", "/cobranza/v1/eventos-desembolso", params={"fecha": fecha},
                                reintentos=self._config.reintentos_consulta)
        return cuerpo_o_error(r, "Cobranza")["items"]


class Seguridad:
    """Antifraude (IF-05) y eventos criticos hacia Seguridad/Auditoria (CR-INT-10)."""

    def __init__(self, bus: ClienteBus):
        self._bus = bus
        self._ejecutor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="eventos-seguridad")

    def antifraude(self, datos: dict) -> dict:
        r = self._bus.solicitar("Seguridad", "POST", "/seguridad/v1/antifraude/evaluaciones", json=datos)
        return cuerpo_o_error(r, "Seguridad")

    def publicar_evento(self, evento: dict) -> None:
        """Mejor esfuerzo: la bitacora local es la fuente de verdad; una falla solo se registra."""
        def _enviar():
            try:
                self._bus.solicitar("Seguridad", "POST", "/seguridad/v1/eventos", json=evento)
            except ErrorNegocio as exc:
                log.warning("No se pudo publicar el evento critico en Seguridad: %s", exc.mensaje)
        self._ejecutor.submit(contextvars.copy_context().run, _enviar)


class Modulos:
    def __init__(self, bus: ClienteBus, config: Config):
        self.bus = bus
        self.evaluacion = Evaluacion(bus, config)
        self.clientes = Clientes(bus)
        self.cuentas = Cuentas(bus, config)
        self.cobranza = Cobranza(bus, config)
        self.seguridad = Seguridad(bus)
