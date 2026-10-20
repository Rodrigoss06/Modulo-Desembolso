"""Cliente HTTP del Bus de Servicios: token de servicio, correlacion, tiempos de espera y metricas."""
from __future__ import annotations

import threading
import time
from collections import defaultdict

import httpx

from ..config import Config
from ..core.correlacion import correlation_id
from ..core.errores import DependenciaNoDisponible, ErrorNegocio


class ClienteBus:
    def __init__(self, config: Config, http: httpx.Client | None = None):
        self._config = config
        self._http = http or httpx.Client(base_url=config.bus_base_url, timeout=config.timeout_dependencia_seg)
        self._token: str | None = None
        self._token_vence = 0.0
        self._candado = threading.Lock()
        self.latencias: dict[str, list[float]] = defaultdict(lambda: [0, 0.0])

    def cerrar(self) -> None:
        self._http.close()

    def disponible(self) -> bool:
        try:
            return self._http.get("/health", timeout=2).status_code == 200
        except httpx.HTTPError:
            return False

    def _token_servicio(self) -> str:
        with self._candado:
            if self._token and time.time() < self._token_vence - 60:
                return self._token
            try:
                r = self._http.post("/seguridad/v1/token", data={
                    "grant_type": "client_credentials",
                    "client_id": self._config.servicio_cliente_id,
                    "client_secret": self._config.servicio_cliente_secreto,
                })
            except httpx.HTTPError as exc:
                raise DependenciaNoDisponible("Seguridad", causa=type(exc).__name__) from exc
            if r.status_code != 200:
                raise DependenciaNoDisponible("Seguridad", causa=f"HTTP_{r.status_code}")
            datos = r.json()
            self._token, self._token_vence = datos["access_token"], time.time() + datos["expires_in"]
            return self._token

    def solicitar(self, modulo: str, metodo: str, ruta: str, *, json: dict | None = None,
                  params: dict | None = None, clave: str | None = None, timeout: float | None = None,
                  reintentos: int = 0) -> httpx.Response:
        """Envia la peticion. Solo reintenta si `reintentos` > 0 (consultas); nunca en el abono (RT-04)."""
        cabeceras = {"X-Correlation-ID": correlation_id(), "Authorization": f"Bearer {self._token_servicio()}"}
        if clave:
            cabeceras["X-Idempotency-Key"] = clave
        intento = 0
        while True:
            inicio = time.perf_counter()
            try:
                respuesta = self._http.request(metodo, ruta, json=json, params=params, headers=cabeceras,
                                               timeout=timeout or self._config.timeout_dependencia_seg)
                error = None
                if respuesta.status_code >= 500:
                    error = DependenciaNoDisponible(modulo, incierto=True, causa=f"HTTP_{respuesta.status_code}")
            except httpx.TimeoutException:
                error = DependenciaNoDisponible(modulo, incierto=True, causa="TIEMPO_AGOTADO")
            except httpx.TransportError as exc:
                error = DependenciaNoDisponible(modulo, incierto=True, causa=type(exc).__name__)
            finally:
                acumulado = self.latencias[modulo.lower()]
                acumulado[0] += 1
                acumulado[1] += time.perf_counter() - inicio
            if error is None:
                return respuesta
            if intento >= reintentos:
                raise error
            intento += 1
            time.sleep(min(0.2 * 2 ** intento, 2.0))


def cuerpo_o_error(respuesta: httpx.Response, modulo: str, *, aceptados: tuple[int, ...] = (200, 201)) -> dict:
    if respuesta.status_code in aceptados:
        return respuesta.json()
    try:
        detalle = respuesta.json()
    except ValueError:
        detalle = {"texto": respuesta.text[:200]}
    raise ErrorNegocio(502, "RESPUESTA_INESPERADA", f"{modulo} respondió con estado {respuesta.status_code}", detalle)
