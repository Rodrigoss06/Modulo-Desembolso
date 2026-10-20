"""Entorno de pruebas: MySQL real con 08_desembolso.sql, simulador del Bus y API en hilos uvicorn.

Variable opcional DES_TEST_MYSQL (por defecto mysql+pymysql://root@127.0.0.1:3306).
"""
from __future__ import annotations

import importlib
import importlib.util
import os
import socket
import sys
import threading
import time
import uuid
from pathlib import Path

import httpx
import pytest
import uvicorn
from sqlalchemy import create_engine, text

from app.config import Config
from app.main import crear_app

RAIZ = Path(__file__).resolve().parents[2]
MYSQL = os.environ.get("DES_TEST_MYSQL", "mysql+pymysql://root@127.0.0.1:3306")
BD_PRUEBA = "bna_test_desembolso"
TABLAS = ["des_evento_entrega", "des_validacion", "des_solicitud_reversion", "des_auditoria", "des_orden", "des_correlativo"]


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _servir(aplicacion) -> tuple[str, uvicorn.Server]:
    puerto = _puerto_libre()
    servidor = uvicorn.Server(uvicorn.Config(aplicacion, host="127.0.0.1", port=puerto, log_level="warning"))
    threading.Thread(target=servidor.run, daemon=True).start()
    limite = time.time() + 15
    while not servidor.started:
        if time.time() > limite:
            raise RuntimeError("El servidor de pruebas no inició")
        time.sleep(0.05)
    return f"http://127.0.0.1:{puerto}", servidor


def ejecutar_script(conexion, sql: str) -> None:
    """Ejecuta un script con bloques DELIMITER como lo haria el cliente mysql."""
    delimitador, bloque = ";", []
    cursor = conexion.cursor()
    for linea in sql.splitlines():
        limpia = linea.strip()
        if not limpia or limpia.startswith("--"):
            continue
        if limpia.upper().startswith("DELIMITER "):
            delimitador = limpia.split()[1]
            continue
        bloque.append(linea)
        if limpia.endswith(delimitador):
            sentencia = "\n".join(bloque).strip()[: -len(delimitador)]
            if sentencia.strip():
                cursor.execute(sentencia)
            bloque = []


@pytest.fixture(scope="session")
def motor_prueba():
    admin = create_engine(MYSQL, isolation_level="AUTOCOMMIT")
    with admin.connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS {BD_PRUEBA}"))
        c.execute(text(f"CREATE DATABASE {BD_PRUEBA} CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"))
    script = (RAIZ / "database" / "sql" / "08_desembolso.sql").read_text(encoding="utf-8")
    script = script.replace("USE bna;", f"USE {BD_PRUEBA};")
    motor = create_engine(f"{MYSQL}/{BD_PRUEBA}", isolation_level="AUTOCOMMIT")
    crudo = motor.raw_connection()
    try:
        ejecutar_script(crudo, script)
    finally:
        crudo.close()
    yield motor
    motor.dispose()
    admin.dispose()


def _cargar_simulador():
    """Carga simuladores/app como paquete 'simulador_bna' (evita el choque con el paquete app del backend)."""
    carpeta = RAIZ / "simuladores" / "app"
    spec = importlib.util.spec_from_file_location("simulador_bna", carpeta / "__init__.py",
                                                  submodule_search_locations=[str(carpeta)])
    paquete = importlib.util.module_from_spec(spec)
    sys.modules["simulador_bna"] = paquete
    spec.loader.exec_module(paquete)
    return importlib.import_module("simulador_bna.main").app


@pytest.fixture(scope="session")
def simulador():
    url, servidor = _servir(_cargar_simulador())
    yield url
    servidor.should_exit = True


@pytest.fixture(scope="session")
def config(motor_prueba, simulador) -> Config:
    return Config(
        _env_file=None,
        database_url=f"{MYSQL}/{BD_PRUEBA}",
        bus_base_url=simulador,
        trabajos_habilitados=False,
        timeout_abono_seg=0.8,
        timeout_dependencia_seg=3,
        reintentos_consulta=0,
        recuperacion_espera_seg=0,
        recuperacion_gracia_seg=1,
        entrega_backoff_base_seg=0,
        entrega_max_intentos=3,
    )


@pytest.fixture(scope="session")
def aplicacion(config):
    return crear_app(config)


@pytest.fixture(scope="session")
def api_url(aplicacion):
    url, servidor = _servir(aplicacion)
    yield url
    servidor.should_exit = True


@pytest.fixture(autouse=True)
def limpiar(request, motor_prueba, simulador):
    with motor_prueba.connect() as c:
        c.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for tabla in TABLAS:
            c.execute(text(f"TRUNCATE TABLE {tabla}"))
        c.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    httpx.post(f"{simulador}/_sim/reiniciar")
    yield


class ClienteApi:
    """Cliente HTTP de la API autenticado como un usuario del simulador de Seguridad."""

    _tokens: dict[str, str] = {}

    def __init__(self, api_url: str, simulador: str, usuario: str | None):
        cabeceras = {}
        if usuario:
            if usuario not in self._tokens:
                r = httpx.post(f"{simulador}/seguridad/v1/token",
                               data={"grant_type": "password", "username": usuario, "password": "Demo2026!"})
                self._tokens[usuario] = r.json()["access_token"]
            cabeceras["Authorization"] = f"Bearer {self._tokens[usuario]}"
        self.http = httpx.Client(base_url=f"{api_url}/api/v1", headers=cabeceras, timeout=20)

    def get(self, ruta, **kw):
        return self.http.get(ruta, **kw)

    def post(self, ruta, clave: str | None = None, **kw):
        cabeceras = kw.pop("headers", {})
        if clave:
            cabeceras["X-Idempotency-Key"] = clave
        return self.http.post(ruta, headers=cabeceras, **kw)

    def put(self, ruta, **kw):
        return self.http.put(ruta, **kw)

    # ---- atajos del flujo
    def preparar(self, aprobacion_id: str, clave: str | None = None) -> httpx.Response:
        return self.post("/ordenes", clave=clave or str(uuid.uuid4()), json={"aprobacion_id": aprobacion_id})

    def hasta_validada(self, aprobacion_id: str, cuenta_id: str) -> dict:
        orden = self.preparar(aprobacion_id).json()
        r = self.post(f"/ordenes/{orden['id']}/identidad", json={"metodo": "BIOMETRIA_DACTILAR"})
        assert r.status_code == 200, r.text
        orden = r.json()
        r = self.put(f"/ordenes/{orden['id']}/cuenta-destino", json={"cuenta_id": cuenta_id, "version": orden["version"]})
        assert r.status_code == 200, r.text
        return r.json()

    def confirmar(self, orden: dict) -> httpx.Response:
        return self.post(f"/ordenes/{orden['id']}/confirmacion", clave=orden["idempotency_key"],
                         json={"version": orden["version"]})


@pytest.fixture
def cliente(api_url, simulador):
    def fabricar(usuario: str | None = "operador1") -> ClienteApi:
        return ClienteApi(api_url, simulador, usuario)
    return fabricar


@pytest.fixture
def sim(simulador):
    class Sim:
        def escenario(self, **cambios):
            httpx.post(f"{simulador}/_sim/escenarios", json=cambios).raise_for_status()

        def aprobacion(self, aprobacion_id, **cambios):
            httpx.post(f"{simulador}/_sim/aprobaciones/{aprobacion_id}", json=cambios).raise_for_status()

        def estado(self) -> dict:
            return httpx.get(f"{simulador}/_sim/estado").json()

        def abonos_de(self, credito_id) -> list[dict]:
            return [a for a in self.estado()["abonos"] if a["credito_id"] == credito_id]
    return Sim()


@pytest.fixture
def sql(motor_prueba):
    def ejecutar(sentencia: str, **parametros):
        with motor_prueba.connect() as c:
            resultado = c.execute(text(sentencia), parametros)
            return resultado.mappings().all() if resultado.returns_rows else resultado.rowcount
    return ejecutar
