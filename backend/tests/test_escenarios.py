"""Escenarios de verificacion de la Fase I (tabla 17 del Informe TOGAF) y reglas RN-01 a RN-10."""
from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timedelta, timezone

LIMA = timezone(timedelta(hours=-5))


def _hoy_lima() -> str:
    return datetime.now(LIMA).date().isoformat()


def test_flujo_completo_confirmado(cliente, sim, sql):
    op = cliente("operador1")
    r = op.get("/creditos-habilitados", params={"documento": "70000001"})
    assert r.status_code == 200
    credito = r.json()[0]
    assert credito["habilitada"] and credito["cliente_documento"] == "****0001"

    orden = op.preparar(credito["aprobacion_id"]).json()
    assert orden["estado"] == "PREPARADA" and orden["importe"] == "10000.00" and orden["moneda"] == "PEN"
    assert orden["codigo_orden"].startswith("DES-")

    orden = op.post(f"/ordenes/{orden['id']}/identidad", json={"metodo": "BIOMETRIA_DACTILAR"}).json()
    assert orden["identidad"]["resultado"] == "APROBADA" and orden["estado"] == "PREPARADA"

    cuentas = {c["cuenta_id"]: c for c in op.get(f"/ordenes/{orden['id']}/cuentas-elegibles").json()}
    assert cuentas["CTA-0001"]["elegible"]
    assert cuentas["CTA-0002"]["motivo"] == "MONEDA_DISTINTA"
    assert cuentas["CTA-0003"]["motivo"] == "CUENTA_BLOQUEADA"
    assert cuentas["CTA-0004"]["motivo"] == "CUENTA_MANCOMUNADA"

    orden = op.put(f"/ordenes/{orden['id']}/cuenta-destino",
                   json={"cuenta_id": "CTA-0001", "version": orden["version"]}).json()
    assert orden["estado"] == "VALIDADA" and "CONFIRMAR" in orden["acciones"]
    assert orden["cuenta_enmascarada"] == "****4521"

    r = op.confirmar(orden)
    assert r.status_code == 200, r.text
    orden = r.json()
    assert orden["estado"] == "CONFIRMADA"
    assert orden["operacion_financiera_id"] and orden["fecha_efectiva"]
    assert orden["eventos"][0]["tipo"] == "desembolso.confirmado" and orden["eventos"][0]["estado"] == "PENDIENTE"
    fases = {(v["tipo"], v["fase"]) for v in orden["validaciones"]}
    assert {("APROBACION", "EJECUCION"), ("CUENTA", "EJECUCION"), ("AUTORIZACION", "EJECUCION"),
            ("ANTIFRAUDE", "EJECUCION")} <= fases

    entrega = cliente("supervisor1").post("/operacion/entregas").json()
    assert entrega["confirmados"] == 1
    orden = op.get(f"/ordenes/{orden['id']}").json()
    assert orden["entrega_estado"] == "CONFIRMADA"

    constancia = op.get(f"/ordenes/{orden['id']}/constancia").json()
    assert constancia["operacion_financiera_id"] == orden["operacion_financiera_id"]
    assert constancia["cuenta_enmascarada"] == "****4521"
    assert sim.estado()["activaciones"] == {"CRE-2026-0001": 1}
    acciones = [f["accion"] for f in sql("SELECT accion FROM des_auditoria WHERE orden_id = :o", o=orden["id"])]
    assert {"PREPARAR", "VALIDAR", "CONFIRMAR", "ENTREGAR", "CONSULTAR"} <= set(acciones)


def test_preparacion_idempotente(cliente):
    op = cliente()
    clave = str(uuid.uuid4())
    primera = op.preparar("APR-2026-0001", clave)
    segunda = op.preparar("APR-2026-0001", clave)
    assert primera.status_code == 201 and segunda.status_code == 200
    assert segunda.headers["Idempotent-Replay"] == "true"
    assert primera.json()["id"] == segunda.json()["id"]


def test_misma_clave_contenido_distinto_conflicto(cliente):
    op = cliente()
    clave = str(uuid.uuid4())
    original = op.preparar("APR-2026-0001", clave).json()
    r = op.preparar("APR-2026-0008", clave)
    assert r.status_code == 409 and r.json()["codigo"] == "IDEMPOTENCIA_CONFLICTO"
    assert op.get(f"/ordenes/{original['id']}").json()["aprobacion_id"] == "APR-2026-0001"


def test_aprobacion_no_habilitada_no_permite_preparar(cliente):
    op = cliente()
    for aprobacion in ("APR-2026-0003", "APR-2026-0004"):  # VENCIDA y REVOCADA
        r = op.preparar(aprobacion)
        assert r.status_code == 422 and r.json()["codigo"] == "APROBACION_NO_HABILITADA"
    habilitados = {c["credito_id"]: c for c in op.get("/creditos-habilitados", params={"documento": "70000003"}).json()}
    assert habilitados["CRE-2026-0003"]["habilitada"] is False


def test_identidad_rechazada_no_avanza(cliente, sim):
    op = cliente()
    orden = op.preparar("APR-2026-0007").json()
    r = op.post(f"/ordenes/{orden['id']}/identidad", json={"metodo": "BIOMETRIA_DACTILAR"})
    assert r.status_code == 422 and r.json()["codigo"] == "IDENTIDAD_RECHAZADA"
    orden = op.get(f"/ordenes/{orden['id']}").json()
    assert orden["estado"] == "PREPARADA" and orden["identidad"]["resultado"] == "RECHAZADA"
    r = op.confirmar(orden)
    assert r.status_code == 422 and r.json()["codigo"] == "VALIDACIONES_INCOMPLETAS"
    assert sim.estado()["intentos_abono"] == 0


def test_cuenta_no_elegible_no_habilita_confirmacion(cliente, sim):
    op = cliente()
    orden = op.preparar("APR-2026-0001").json()
    orden = op.post(f"/ordenes/{orden['id']}/identidad", json={"metodo": "DNI_Y_OTP"}).json()
    r = op.put(f"/ordenes/{orden['id']}/cuenta-destino", json={"cuenta_id": "CTA-0003", "version": orden["version"]})
    assert r.status_code == 422 and r.json()["codigo"] == "CUENTA_NO_ELEGIBLE"
    orden = op.get(f"/ordenes/{orden['id']}").json()
    assert orden["estado"] == "PREPARADA" and "CONFIRMAR" not in orden["acciones"] and orden["cuenta_id"] is None
    assert sim.estado()["intentos_abono"] == 0


def test_cuenta_moneda_distinta_bloqueada(cliente):
    op = cliente()
    orden = op.preparar("APR-2026-0001").json()
    orden = op.post(f"/ordenes/{orden['id']}/identidad", json={"metodo": "BIOMETRIA_FACIAL"}).json()
    r = op.put(f"/ordenes/{orden['id']}/cuenta-destino", json={"cuenta_id": "CTA-0002", "version": orden["version"]})
    assert r.status_code == 422 and r.json()["codigo"] == "MONEDA_DISTINTA"


def test_revalidacion_fallida_rechaza_sin_abono(cliente, sim):
    op = cliente()
    orden = op.hasta_validada("APR-2026-0008", "CTA-0012")
    sim.aprobacion("APR-2026-0008", estado="REVOCADA")
    r = op.confirmar(orden)
    assert r.status_code == 422 and r.json()["codigo"] == "REVALIDACION_FALLIDA"
    orden = op.get(f"/ordenes/{orden['id']}").json()
    assert orden["estado"] == "RECHAZADA" and "APROBACION" in orden["motivo_rechazo"]
    assert sim.estado()["intentos_abono"] == 0


def test_rechazo_de_cuentas(cliente, sim):
    op = cliente()
    orden = op.hasta_validada("APR-2026-0006", "CTA-0010")
    r = op.confirmar(orden)
    assert r.status_code == 200
    orden = r.json()
    assert orden["estado"] == "RECHAZADA" and "CUENTA_CON_RETENCION" in orden["motivo_rechazo"]
    assert orden["operacion_financiera_id"] is None and orden["eventos"] == []


def test_respuesta_perdida_se_recupera_sin_duplicar(cliente, sim):
    sim.escenario(demora_timeout_seg=1.5)  # mayor que timeout_abono_seg (0.8 s)
    op = cliente()
    orden = op.hasta_validada("APR-2026-0005", "CTA-0009")
    r = op.confirmar(orden)
    assert r.status_code == 202 and r.json()["estado"] == "POR_VERIFICAR"
    repetida = op.confirmar(orden)  # el operador reintenta: no debe enviarse otro abono
    assert repetida.status_code == 202
    assert sim.estado()["intentos_abono"] == 1
    verificada = op.post(f"/ordenes/{orden['id']}/verificacion")
    assert verificada.status_code == 200 and verificada.json()["estado"] == "CONFIRMADA"
    assert len(sim.abonos_de("CRE-2026-0005")) == 1
    assert verificada.json()["eventos"][0]["tipo"] == "desembolso.confirmado"


def test_confirmaciones_concurrentes_un_solo_abono(cliente, sim):
    op1, op2 = cliente("operador1"), cliente("operador2")
    orden_a = op1.hasta_validada("APR-2026-0008", "CTA-0012")
    orden_b = op2.hasta_validada("APR-2026-0008", "CTA-0013")
    respuestas = {}

    def confirmar(nombre, op, orden):
        respuestas[nombre] = op.confirmar(orden)

    hilos = [threading.Thread(target=confirmar, args=("a", op1, orden_a)),
             threading.Thread(target=confirmar, args=("a2", op1, orden_a)),
             threading.Thread(target=confirmar, args=("b", op2, orden_b))]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    estados = sorted(r.json().get("estado") or r.json().get("codigo") for r in respuestas.values())
    assert len(sim.abonos_de("CRE-2026-0008")) == 1
    finales = {op1.get(f"/ordenes/{o['id']}").json()["estado"] for o in (orden_a, orden_b)}
    assert finales == {"CONFIRMADA", "RECHAZADA"}, estados


def test_cobranza_caida_mantiene_confirmado(cliente, sim):
    sim.escenario(cobranza_caida=True)
    op, sup = cliente(), cliente("supervisor1")
    orden = op.confirmar(op.hasta_validada("APR-2026-0001", "CTA-0001")).json()
    resumen = sup.post("/operacion/entregas").json()
    assert resumen["reprogramados"] == 1
    orden = op.get(f"/ordenes/{orden['id']}").json()
    assert orden["estado"] == "CONFIRMADA" and orden["entrega_estado"] == "PENDIENTE"
    assert orden["eventos"][0]["intentos"] == 1 and "DEPENDENCIA_NO_DISPONIBLE" in orden["eventos"][0]["ultimo_error"]
    sim.escenario(cobranza_caida=False)
    assert sup.post("/operacion/entregas").json()["confirmados"] == 1
    assert op.get(f"/ordenes/{orden['id']}").json()["entrega_estado"] == "CONFIRMADA"


def test_entrega_fallida_tras_reintentos_y_reintento_manual(cliente, sim, sql):
    sim.escenario(cobranza_caida=True)
    op, sup = cliente(), cliente("supervisor1")
    orden = op.confirmar(op.hasta_validada("APR-2026-0001", "CTA-0001")).json()
    for _ in range(3):  # entrega_max_intentos = 3 en pruebas
        sup.post("/operacion/entregas")
    evento = op.get(f"/ordenes/{orden['id']}").json()["eventos"][0]
    assert evento["estado"] == "FALLIDO"
    assert sup.get("/operacion/resumen").json()["entregas"][0]["estado"] == "FALLIDO"
    sim.escenario(cobranza_caida=False)
    assert sup.post(f"/operacion/entregas/{evento['id']}/reintento").status_code == 200
    assert sup.post("/operacion/entregas").json()["confirmados"] == 1


def test_reenvio_evento_no_duplica_activacion(cliente, sim, sql):
    op, sup = cliente(), cliente("supervisor1")
    orden = op.confirmar(op.hasta_validada("APR-2026-0001", "CTA-0001")).json()
    sup.post("/operacion/entregas")
    sql("UPDATE des_evento_entrega SET estado = 'PENDIENTE', siguiente_intento = NULL WHERE orden_id = :o", o=orden["id"])
    assert sup.post("/operacion/entregas").json()["confirmados"] == 1
    assert sim.estado()["activaciones"] == {"CRE-2026-0001": 1}
    ultimo = sql("SELECT detalle FROM des_auditoria WHERE accion = 'ENTREGAR' ORDER BY id")[-1]["detalle"]
    assert (json.loads(ultimo) if isinstance(ultimo, str) else ultimo)["duplicado"] is True


def test_acceso_sin_permiso_es_auditado(cliente, sql):
    sin_token = cliente(None).get("/ordenes")
    assert sin_token.status_code == 401 and sin_token.json()["codigo"] == "NO_AUTENTICADO"
    r = cliente("auditor1").preparar("APR-2026-0001")
    assert r.status_code == 403 and r.json()["codigo"] == "PERMISO_DENEGADO"
    filas = sql("SELECT actor_id, resultado FROM des_auditoria WHERE accion = 'ACCESO_DENEGADO'")
    assert filas and filas[0]["actor_id"] == "auditor1" and filas[0]["resultado"] == "403"
    assert cliente("operador1").get("/operacion/resumen").status_code == 403


def test_constancia_solo_confirmada(cliente):
    op = cliente()
    orden = op.preparar("APR-2026-0001").json()
    r = op.get(f"/ordenes/{orden['id']}/constancia")
    assert r.status_code == 409 and r.json()["codigo"] == "ESTADO_INVALIDO"


def test_conciliacion(cliente, sim):
    op, sup = cliente(), cliente("supervisor1")
    op.confirmar(op.hasta_validada("APR-2026-0001", "CTA-0001"))
    sup.post("/operacion/entregas")
    reporte = sup.post("/conciliaciones", json={"fecha": _hoy_lima()}).json()
    assert reporte["estado"] == "CONCILIADO", reporte["diferencias"]
    assert reporte["totales"]["ordenes"] == 1 and reporte["totales"]["importe_cuentas"] == "10000.00"
    sim.escenario(cobranza_caida=True)
    r = sup.post("/conciliaciones", json={"fecha": _hoy_lima()})
    assert r.status_code == 503 and r.json()["codigo"] == "CONCILIACION_INCOMPLETA"


def test_reversion(cliente, aplicacion, sim):
    op, sup1, sup2 = cliente(), cliente("supervisor1"), cliente("supervisor2")
    orden = op.confirmar(op.hasta_validada("APR-2026-0001", "CTA-0001")).json()
    r = sup1.post(f"/ordenes/{orden['id']}/reversiones", clave=str(uuid.uuid4()), json={"motivo": "Error de digitación"})
    assert r.status_code == 409 and r.json()["codigo"] == "REVERSION_DESHABILITADA"
    aplicacion.state.config.reversion_habilitada = True
    try:
        solicitud = sup1.post(f"/ordenes/{orden['id']}/reversiones", clave=str(uuid.uuid4()),
                              json={"motivo": "Desistimiento del cliente dentro del plazo"}).json()
        assert solicitud["estado"] == "SOLICITADA"
        mismo = sup1.post(f"/reversiones/{solicitud['id']}/decision", json={"aprobar": True})
        assert mismo.status_code == 409 and mismo.json()["codigo"] == "AUTORIZADOR_INVALIDO"
        decidida = sup2.post(f"/reversiones/{solicitud['id']}/decision", json={"aprobar": True}).json()
        assert decidida["estado"] == "CONFIRMADA" and decidida["reversion_financiera_id"]
        orden = op.get(f"/ordenes/{orden['id']}").json()
        assert orden["estado"] == "REVERTIDA" and orden["operacion_financiera_id"]
        assert {e["tipo"] for e in orden["eventos"]} == {"desembolso.confirmado", "desembolso.revertido"}
    finally:
        aplicacion.state.config.reversion_habilitada = False


def test_bd_integridad(sql):
    import pytest
    from sqlalchemy.exc import IntegrityError, OperationalError

    base = ("INSERT INTO des_orden (id, codigo_orden, aprobacion_id, credito_id, cliente_id, cuenta_id, importe, moneda, "
            "estado, idempotency_key, request_hash, usuario_preparacion, correlation_id, operacion_financiera_id, "
            "fecha_efectiva) VALUES (:id, :codigo, 'APR', 'CRE-X', 'CLI', 'CTA', 100.00, 'PEN', :estado, :clave, "
            "REPEAT('a', 64), 'op', 'c', :op, :fecha)")
    sql(base, id="o1", codigo="DES-T-1", estado="CONFIRMADA", clave="k1", op="OPF-1", fecha="2026-10-19 10:00:00")
    sql(base, id="o2", codigo="DES-T-2", estado="VALIDADA", clave="k2", op=None, fecha=None)
    with pytest.raises(IntegrityError):  # RN-05: segundo desembolso del mismo credito
        sql("UPDATE des_orden SET estado = 'EN_PROCESO' WHERE id = 'o2'")
    with pytest.raises(OperationalError, match="transicion de estado no permitida"):
        sql("UPDATE des_orden SET estado = 'PREPARADA' WHERE id = 'o1'")
    with pytest.raises(OperationalError, match="inmutables"):
        sql("UPDATE des_orden SET importe = 1.00 WHERE id = 'o1'")
    sql("INSERT INTO des_auditoria (actor_id, accion, resultado, correlation_id) VALUES ('x', 'PRUEBA', 'OK', 'c')")
    with pytest.raises(OperationalError, match="solo insercion"):
        sql("DELETE FROM des_auditoria")
    with pytest.raises((IntegrityError, OperationalError)):  # CHECK: confirmada sin operacion financiera
        sql(base, id="o3", codigo="DES-T-3", estado="CONFIRMADA", clave="k3", op=None, fecha=None)
