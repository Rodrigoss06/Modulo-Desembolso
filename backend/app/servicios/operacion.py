"""Recuperacion de ordenes inciertas, entrega a Cobranza (outbox), conciliacion y metricas."""
from __future__ import annotations

import logging
from datetime import date, timedelta

from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session, sessionmaker

from ..config import Config
from ..core.correlacion import correlacion_actual
from ..core.dinero import a_decimal, formatear
from ..core.errores import ErrorNegocio
from ..core.seguridad import Usuario
from ..integraciones.bus import ClienteBus
from ..integraciones.modulos import Modulos
from ..persistencia.modelos import EventoEntrega, Orden
from .auditoria import Auditor
from .ordenes import ServicioOrdenes, utc_ahora

log = logging.getLogger("desembolso.operacion")


class Recuperador:
    """RN-07: resuelve ordenes EN_PROCESO/POR_VERIFICAR consultando a Cuentas por la misma clave."""

    def __init__(self, config: Config, fabrica: sessionmaker[Session], ordenes: ServicioOrdenes, reversiones=None):
        self.config, self.Sesion, self.ordenes, self.reversiones = config, fabrica, ordenes, reversiones

    def ejecutar(self, actor: str = "svc:recuperador") -> dict:
        resumen = {"revisadas": 0, "confirmadas": 0, "rechazadas": 0, "pendientes": 0, "errores": 0, "alertas": 0}
        with self.Sesion() as s:
            filas = s.execute(text(
                "SELECT id, correlation_id, TIMESTAMPDIFF(SECOND, actualizado_en, CURRENT_TIMESTAMP(3)) AS segundos "
                "FROM des_orden WHERE estado = 'POR_VERIFICAR' OR (estado = 'EN_PROCESO' AND "
                "actualizado_en < CURRENT_TIMESTAMP(3) - INTERVAL :espera SECOND) ORDER BY actualizado_en LIMIT 50"),
                {"espera": int(self.config.recuperacion_espera_seg)}).all()
        for orden_id, correlacion, segundos in filas:
            resumen["revisadas"] += 1
            token = correlacion_actual.set(correlacion)
            try:
                final = self.ordenes.resolver_incierta(orden_id, actor=actor,
                                                       rechazar_no_encontrado=segundos >= self.config.recuperacion_gracia_seg)
                clave = {"CONFIRMADA": "confirmadas", "RECHAZADA": "rechazadas"}.get(final, "pendientes")
                resumen[clave] += 1
            except ErrorNegocio as exc:
                resumen["errores"] += 1
                log.warning("No se pudo resolver la orden %s: %s", orden_id, exc.mensaje)
            finally:
                correlacion_actual.reset(token)
            if segundos >= self.config.alerta_incierta_min * 60:
                resumen["alertas"] += 1
                log.error("ALERTA INC-01: orden %s incierta hace %s s", orden_id, segundos)
        if self.reversiones:
            resumen["reversiones"] = self.reversiones.recuperar(actor)
        return resumen


class Despachador:
    """RN-08 / CU-05: entrega al menos una vez de des_evento_entrega hacia Cobranza."""

    def __init__(self, config: Config, fabrica: sessionmaker[Session], modulos: Modulos, auditor: Auditor):
        self.config, self.Sesion, self.m, self.auditor = config, fabrica, modulos, auditor

    def ejecutar(self, limite: int = 20) -> dict:
        resumen = {"enviados": 0, "confirmados": 0, "reprogramados": 0, "fallidos": 0}
        with self.Sesion() as s, s.begin():
            eventos = s.execute(
                select(EventoEntrega.id, EventoEntrega.orden_id, EventoEntrega.payload, EventoEntrega.intentos,
                       Orden.correlation_id)
                .join(Orden, Orden.id == EventoEntrega.orden_id)
                .where(text("(des_evento_entrega.estado = 'PENDIENTE' AND (des_evento_entrega.siguiente_intento IS NULL "
                            "OR des_evento_entrega.siguiente_intento <= UTC_TIMESTAMP())) OR "
                            "(des_evento_entrega.estado = 'ENVIADO' AND des_evento_entrega.actualizado_en < "
                            "CURRENT_TIMESTAMP(3) - INTERVAL 120 SECOND)"))
                .order_by(EventoEntrega.creado_en).limit(limite)
                .with_for_update(skip_locked=True, of=EventoEntrega)).all()
            if eventos:
                s.execute(update(EventoEntrega).where(EventoEntrega.id.in_([e.id for e in eventos]))
                          .values(estado="ENVIADO").execution_options(synchronize_session=False))
        for evento_id, orden_id, payload, intentos, correlacion in eventos:
            resumen["enviados"] += 1
            token = correlacion_actual.set(correlacion)
            try:
                acuse = self.m.cobranza.enviar_evento(payload, evento_id)
                error = None
            except ErrorNegocio as exc:
                acuse, error = None, f"{exc.codigo}: {exc.mensaje}"
            try:
                with self.Sesion() as s, s.begin():
                    intentos += 1
                    if acuse:
                        s.execute(update(EventoEntrega).where(EventoEntrega.id == evento_id).values(
                            estado="CONFIRMADO", intentos=intentos, confirmacion_id=str(acuse.get("confirmacion_id"))[:60],
                            ultimo_error=None, siguiente_intento=None))
                        s.execute(update(Orden).where(Orden.id == orden_id).values(entrega_estado="CONFIRMADA")
                                  .execution_options(synchronize_session=False))
                        self.auditor.registrar(s, "ENTREGAR", "CONFIRMADO", actor="svc:despachador", orden_id=orden_id,
                                               detalle={"evento": evento_id, "acuse": acuse.get("confirmacion_id"),
                                                        "duplicado": acuse.get("duplicado", False)})
                        resumen["confirmados"] += 1
                    elif intentos >= self.config.entrega_max_intentos:
                        s.execute(update(EventoEntrega).where(EventoEntrega.id == evento_id).values(
                            estado="FALLIDO", intentos=intentos, ultimo_error=error[:255], siguiente_intento=None))
                        self.auditor.registrar(s, "ENTREGAR", "FALLIDO", actor="svc:despachador", orden_id=orden_id,
                                               detalle={"evento": evento_id, "error": error})
                        log.error("ALERTA INC-02: evento %s FALLIDO tras %s intentos", evento_id, intentos)
                        resumen["fallidos"] += 1
                    else:
                        espera = min(self.config.entrega_backoff_base_seg * 2 ** (intentos - 1),
                                     self.config.entrega_backoff_max_seg)
                        s.execute(update(EventoEntrega).where(EventoEntrega.id == evento_id).values(
                            estado="PENDIENTE", intentos=intentos, ultimo_error=error[:255],
                            siguiente_intento=utc_ahora() + timedelta(seconds=espera)))
                        resumen["reprogramados"] += 1
            finally:
                correlacion_actual.reset(token)
        return resumen

    def reintentar(self, usuario: Usuario, evento_id: str) -> dict:
        with self.Sesion() as s, s.begin():
            evento = s.get(EventoEntrega, evento_id)
            if evento is None:
                raise ErrorNegocio(404, "EVENTO_NO_ENCONTRADO", "No existe el evento de entrega")
            if evento.estado not in ("FALLIDO", "PENDIENTE"):
                raise ErrorNegocio(409, "ESTADO_INVALIDO", f"El evento está {evento.estado}")
            evento.estado, evento.siguiente_intento = "PENDIENTE", utc_ahora()
            self.auditor.registrar(s, "ENTREGAR", "REINTENTO_MANUAL", actor=usuario.id, orden_id=evento.orden_id,
                                   detalle={"evento": evento_id})
        return {"evento_id": evento_id, "estado": "PENDIENTE"}


class Conciliador:
    """RF-09 / CU-06: compara ordenes propias, abonos de Cuentas y acuses de Cobranza."""

    def __init__(self, fabrica: sessionmaker[Session], modulos: Modulos, auditor: Auditor):
        self.Sesion, self.m, self.auditor = fabrica, modulos, auditor

    def conciliar(self, usuario: Usuario, fecha: date, moneda: str | None) -> dict:
        texto_fecha = fecha.isoformat()
        try:
            abonos = self.m.cuentas.abonos_por_fecha(texto_fecha)
            acuses = self.m.cobranza.acuses_por_fecha(texto_fecha)
        except ErrorNegocio as exc:
            raise ErrorNegocio(503, "CONCILIACION_INCOMPLETA",
                               "Un origen no respondió; no se emite una conciliación parcial como definitiva",
                               exc.detalle) from exc
        with self.Sesion() as s:
            filtros = [func.date(Orden.fecha_efectiva) == texto_fecha, Orden.estado.in_(["CONFIRMADA", "REVERTIDA"])]
            if moneda:
                filtros.append(Orden.moneda == moneda)
            ordenes = s.scalars(select(Orden).where(*filtros).order_by(Orden.fecha_efectiva)).all()
        abonos_por_clave = {a["clave"]: a for a in abonos if not moneda or a.get("moneda") == moneda}
        acuses_por_orden = {a["orden_id"]: a for a in acuses if a.get("tipo") == "desembolso.confirmado"}
        diferencias, claves = [], set()
        for o in ordenes:
            claves.add(o.idempotency_key)
            abono = abonos_por_clave.get(o.idempotency_key)
            if abono is None:
                diferencias.append(_dif("FALTA_EN_CUENTAS", o, "Cuentas no registra el abono de la orden"))
            elif a_decimal(abono["importe"]) != o.importe:
                diferencias.append(_dif("IMPORTE_DIFERENTE", o, f"Cuentas registra {abono['importe']} {abono['moneda']}"))
            if o.id not in acuses_por_orden:
                diferencias.append(_dif("SIN_ACUSE_COBRANZA", o, f"Entrega a Cobranza {o.entrega_estado}"))
        for clave, abono in abonos_por_clave.items():
            if clave not in claves:
                diferencias.append({"tipo": "ABONO_SIN_ORDEN", "codigo_orden": None, "orden_id": abono.get("orden_id"),
                                    "detalle": f"Abono {abono.get('operacion_id')} sin orden confirmada en Desembolso"})
        total_propio = sum((o.importe for o in ordenes), a_decimal(0))
        total_cuentas = sum((a_decimal(a["importe"]) for a in abonos_por_clave.values()), a_decimal(0))
        reporte = {
            "fecha": texto_fecha, "moneda": moneda,
            "estado": "CONCILIADO" if not diferencias else "CON_DIFERENCIAS",
            "totales": {"ordenes": len(ordenes), "importe_ordenes": formatear(total_propio),
                        "abonos_cuentas": len(abonos_por_clave), "importe_cuentas": formatear(total_cuentas),
                        "acuses_cobranza": len(acuses_por_orden)},
            "ordenes": [{"codigo_orden": o.codigo_orden, "credito_id": o.credito_id, "importe": formatear(o.importe),
                         "moneda": o.moneda, "estado": o.estado, "entrega_estado": o.entrega_estado,
                         "operacion_financiera_id": o.operacion_financiera_id} for o in ordenes],
            "diferencias": diferencias,
        }
        with self.Sesion() as s, s.begin():
            self.auditor.registrar(s, "CONCILIAR", reporte["estado"], actor=usuario.id,
                                   detalle={"fecha": texto_fecha, "moneda": moneda, "diferencias": len(diferencias)})
        return reporte


def _dif(tipo: str, o: Orden, detalle: str) -> dict:
    return {"tipo": tipo, "codigo_orden": o.codigo_orden, "orden_id": o.id, "detalle": detalle}


class Operacion:
    """Monitor operativo y metricas para los indicadores de I-05."""

    def __init__(self, config: Config, fabrica: sessionmaker[Session], bus: ClienteBus):
        self.config, self.Sesion, self.bus = config, fabrica, bus

    def resumen(self) -> dict:
        with self.Sesion() as s:
            por_estado = dict(s.execute(select(Orden.estado, func.count()).group_by(Orden.estado)).all())
            inciertas = [dict(f._mapping) for f in s.execute(text(
                "SELECT id, codigo_orden, credito_id, importe, moneda, estado, segundos_en_estado, actualizado_en "
                "FROM des_v_ordenes_inciertas ORDER BY actualizado_en")).all()]
            entregas = [dict(f._mapping) for f in s.execute(text(
                "SELECT evento_id, orden_id, codigo_orden, credito_id, tipo, estado, intentos, siguiente_intento, "
                "ultimo_error, antiguedad_min FROM des_v_entregas_pendientes ORDER BY creado_en")).all()]
        for fila in inciertas:
            fila["importe"] = formatear(fila["importe"])
            fila["actualizado_en"] = fila["actualizado_en"].isoformat()
            fila["alerta"] = fila["segundos_en_estado"] >= self.config.alerta_incierta_min * 60
        for fila in entregas:
            fila["siguiente_intento"] = fila["siguiente_intento"].isoformat() if fila["siguiente_intento"] else None
        return {"ordenes_por_estado": por_estado, "inciertas": inciertas, "entregas": entregas,
                "reversion_habilitada": self.config.reversion_habilitada}

    def metricas(self) -> str:
        r = self.resumen()
        lineas = ["# HELP des_ordenes_por_estado Ordenes de desembolso por estado",
                  "# TYPE des_ordenes_por_estado gauge"]
        for estado in ("PREPARADA", "VALIDADA", "EN_PROCESO", "POR_VERIFICAR", "CONFIRMADA", "RECHAZADA", "REVERTIDA"):
            lineas.append(f'des_ordenes_por_estado{{estado="{estado}"}} {r["ordenes_por_estado"].get(estado, 0)}')
        pendientes = [e for e in r["entregas"] if e["estado"] != "FALLIDO"]
        lineas += [
            "# TYPE des_ordenes_inciertas gauge", f"des_ordenes_inciertas {len(r['inciertas'])}",
            "# TYPE des_entregas_pendientes gauge", f"des_entregas_pendientes {len(pendientes)}",
            "# TYPE des_entregas_fallidas gauge", f"des_entregas_fallidas {len(r['entregas']) - len(pendientes)}",
            "# TYPE des_entrega_antiguedad_max_minutos gauge",
            f"des_entrega_antiguedad_max_minutos {max((e['antiguedad_min'] for e in r['entregas']), default=0)}",
            "# HELP des_latencia_dependencia_segundos Latencia de llamadas a modulos contraparte",
            "# TYPE des_latencia_dependencia_segundos summary",
        ]
        for dependencia, (cantidad, suma) in sorted(self.bus.latencias.items()):
            lineas.append(f'des_latencia_dependencia_segundos_count{{dependencia="{dependencia}"}} {int(cantidad)}')
            lineas.append(f'des_latencia_dependencia_segundos_sum{{dependencia="{dependencia}"}} {suma:.4f}')
        return "\n".join(lineas) + "\n"
