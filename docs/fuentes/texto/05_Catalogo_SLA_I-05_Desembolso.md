# PLANTILLA I-05
Catálogo y niveles de servicio - propuesta del módulo
Actividad I-05 | Del 13/10 al 20/10/2026 | Consolidación y validación de servicios
Objetivo: complementar la ficha I-01, sin redefinir el servicio, con responsable, horario, criticidad, indicadores y objetivos medibles propuestos. Un SLA solo es oficial cuando las partes competentes lo aprueban.
# 0. Identificación y trazabilidad

| Campo | Completar por el módulo |
| Módulo y enlace del Comité | Desembolso \| Sebastián Conde (enlace del Comité; designación por ratificar) |
| Código y nombre del servicio | SRV-CR-04 \| Servicio de Gestión del Desembolso de Créditos |
| Líder / responsable funcional | Iván Edgardo Reaño Soto \| Líder del módulo; responsable funcional propuesto |
| Versión / fecha / estado | v1.0 \| 18/10/2026 \| En revisión |
| Fuentes revisadas | Ficha I-01 SRV-CR-04; TOGAF Fase I; Matriz CR-INT; Lineamiento Python/FastAPI/MySQL; Informe ITIL4 v0.1; DB_CONTROL_ACCESO (sin credenciales) |

# 1. Ficha de catálogo del servicio

| Campo | Completar con base en I-01 y acuerdos vigentes |
| Código / nombre | SRV-CR-04 \| Servicio de Gestión del Desembolso de Créditos |
| Propósito y valor | Convertir un crédito aprobado en un abono confirmado y consultable / asegurar control, trazabilidad y continuidad hacia Cobranza. |
| Consumidores | Cliente con crédito aprobado; personal autorizado del BNA en agencia; módulo de Cobranza. |
| Propietario funcional / soporte técnico | Iván Edgardo Reaño Soto, líder del módulo \| Equipo de Desembolso; soporte transversal según incidencia \| Responsabilidad funcional por ratificar |
| Dependencias e interfaces | Evaluación \| CR-INT-04; Cuentas \| CR-INT-05; Cobranza \| CR-INT-06; Seguridad/Auditoría \| CR-INT-10. Responsables: módulos propietarios; contratos por ratificar. |
| Horario / ventana de servicio | Horario y zona horaria: Pendiente de validación con Comité/Infraestructura \| Soporte fuera de horario: por definir |
| Criticidad y sustento | Alta (propuesta) \| Entrega fondos autorizados; un fallo puede dejar abonos inciertos, duplicidad o impedir continuidad hacia Cobranza. |
| Canal para incidencias y solicitudes TI | Pendiente de validación: no se evidencia mesa de ayuda, correo o sistema de tickets oficial en las fuentes revisadas. |
| Tecnología habilitadora | Python + FastAPI \| MySQL \| Servicios/API; Bus como mecanismo técnico de integración, sujeto a ratificación técnica. |

# 2. Indicadores y objetivos de servicio (SLO propuestos)
Seleccionar métricas pertinentes y medibles. Los valores entre corchetes deben justificarse, no completarse con números inventados. Diferenciar indicador, objetivo propuesto y SLA formal.

| Indicador / definición | Cómo se calcula o mide | Objetivo y evidencia | Estado |
| Disponibilidad del servicio | (Minutos dentro de horario acordado - minutos de indisponibilidad) / minutos acordados × 100 | Meta numérica: Pendiente de validación \| Evidencia propuesta: health checks, logs de API/MySQL y registros de integración | Pendiente de validación |
| Tiempo de respuesta | p95 de la API del SRV-CR-04; registrar por separado la espera de dependencias CR-INT-04/05/06 hasta que se acuerde el SLA extremo a extremo. | Meta numérica: Pendiente de validación \| Logs/métricas del módulo | Pendiente de validación |
| Tasa de fallas de operación | Operaciones de desembolso no confirmadas/fallidas ÷ intentos válidos × 100; exclusiones y estados definitivos por ratificar. | Meta numérica: Pendiente de validación \| Registros de órdenes, correlación y trazas | Pendiente de validación |
| Tiempo de restauración | Desde detección confirmada de incidente hasta servicio restaurado | Meta numérica: Pendiente de validación \| Tickets y monitoreo, cuando exista canal operativo | Pendiente de validación |
| Abonos sin confirmar | Órdenes con resultado financiero pendiente en CR-INT-05 ÷ solicitudes de abono válidas × 100. | Meta numérica: Pendiente de validación \| Estados de orden, referencia financiera y logs correlacionados | Pendiente de validación |

# 3. Atención, escalamiento y dependencias

| Nivel / evento | Responsable y función | Escala a / disparador |
| Nivel 1: registro y clasificación | Encargado inicial / soporte del módulo; canal formal pendiente de validación. | Escala si no se resuelve, el servicio se degrada o existe impacto alto/operación incierta. |
| Nivel 2: diagnóstico de módulo | Equipo de Desembolso SRV-CR-04; líder Iván Edgardo Reaño Soto. Revisa orden, validaciones, estados y logs. | Escala ante error CR-INT, problema de dependencia, autorización o infraestructura. |
| Nivel 3: integración/infraestructura/seguridad | Cuentas/Bus/Tecnología para CR-INT-05; Cobranza/Bus para CR-INT-06; Seguridad para permisos; Infraestructura para disponibilidad. | Disparador: dependencia externa, timeout/contrato no resuelto, falla de plataforma o control de acceso. Acuerdos aún pendientes. |

# 4. Condiciones para convertir propuesta en SLA formal

| Tema | Definición requerida | Responsable de ratificación |
| Compromiso de servicio | Horario, exclusiones, consumidores incluidos, metas, procedimiento de medición | Comité de Créditos, propietario funcional, Tecnología e Infraestructura; módulos afectados cuando corresponda. |
| Incidentes y tiempos | Prioridades, escalamiento, atención y recuperación consistente con I-04 | Comité de Créditos; Desembolso; soporte/Infraestructura. Prioridades y tiempos por ratificar. |
| Dependencias y contingencia | Acuerdos con otros módulos; RTO/RPO y evidencia técnica si corresponde | Dueños de Evaluación, Cuentas y Cobranza; Bus, Seguridad e Infraestructura según dependencia. |
| Aceptación y fecha | Versión, fecha de vigencia, aprobadores y mecanismo de revisión | Por definir por el Comité de Créditos y las instancias técnicas competentes. |

# 5. Ejemplo breve de referencia - Evaluación (NO aprobado)

| Elemento | Ejemplo para SRV-CR-03 |
| Servicio | Evaluación Crediticia: transforma expediente de Solicitud en resultado y observaciones. |
| Consumo y dependencia | Solicitud CR-INT-02/03; Desembolso CR-INT-04 solo si aprobado; Seguridad/Auditoría CR-INT-10. |
| Indicador medible | Latencia de la API de evaluación; tiempo de resolución de casos OBSERVADOS por analista; disponibilidad del servicio. |
| Meta / horario | Por definir con dueños de servicio, Tecnología e Infraestructura; no inventar cifras. |
| Estado | Ejemplo ilustrativo, pendiente de validación; no prueba de funcionamiento ni SLA aprobado. |

# 6. Control de revisión y envío al Comité

| Verificación | Resultado para completar |
| Coherencia con servicio y fichas I-01 | Sí, con observaciones abiertas: permisos, ejecución financiera, idempotencia, activación/calendario, entrega y reversión. |
| Códigos y interfaces CR-INT verificados | CR-INT-04, CR-INT-05, CR-INT-06 y CR-INT-10 \| Matriz CR-INT de referencia del Comité de Créditos (28/09/2026; versión no indicada). |
| Objetivos propuestos justificados | Métodos de medición definidos; metas numéricas y evidencia operativa aún no disponibles. Validación prevista con I-06/Testing. |
| Propietarios y aprobadores identificados | Iván Edgardo Reaño Soto (propietario funcional propuesto); Comité de Créditos y responsables de dependencias/instancias técnicas, por ratificar. |
| Estado de la propuesta | Para revisión del enlace y consolidación \| No constituye SLA aprobado. |

Entrega al enlace: ficha actualizada, indicadores con fórmulas verificables y pendientes explícitos. El Comité integra I-05 y solicita aprobaciones antes de presentar SLA como definitivos.