# PLANTILLA I-04
Prácticas ITIL 4 aplicadas al servicio de TI
Actividad I-04 | Del 09/10 al 16/10/2026 | Versión para completar y validar
Objetivo: proponer cómo se atienden incidentes, solicitudes de servicio, cambios, disponibilidad y continuidad en el servicio SRV-CR correspondiente. Una propuesta no equivale a una política aprobada ni a una prueba ejecutada.
# 0. Identificación del servicio

| Campo | Completar por el módulo |
| Módulo y enlace del Comité | Desembolso \| Sebastián Conde (enlace del Comité; designación por ratificar) |
| Código y nombre del servicio | SRV-CR-04 \| Servicio de Gestión del Desembolso de Créditos |
| Líder / responsable funcional | Iván Edgardo Reaño Soto \| Líder del módulo; responsable funcional propuesto |
| Versión / fecha / estado | v1.0 \| 18/10/2026 \| En revisión |
| Fuentes revisadas | Ficha I-01 SRV-CR-04; TOGAF Fase I; Matriz CR-INT; Lineamiento Python/FastAPI/MySQL; Informe ITIL4 v0.1; DB_CONTROL_ACCESO (sin credenciales) |

# Instrucciones de llenado
Completar todos los apartados con base en I-01 y en las interfaces CR-INT vigentes. Si un valor no existe, escribir «Pendiente de validación» y señalar quién debe resolverlo. Prioridades, responsables y procedimientos son propuestas hasta su ratificación. No registrar credenciales ni contraseñas.
# 1. Gestión de incidentes
Un incidente es la interrupción o degradación no planificada del servicio. Proponer al menos dos escenarios relevantes para el módulo.

| ID / escenario | Impacto y detección | Atención y escalamiento | Recuperación y evidencia |
| INC-01
Abono sin resultado confirmado de Cuentas | Operación queda pendiente y existe riesgo de reintento duplicado. Detección: timeout, ausencia de confirmación CR-INT-05 o estado financiero no confirmado. | Desembolso registra el caso y consulta el estado; escala a Cuentas, Bus y Tecnología. Seguridad participa si el problema es de autorización/acceso. | Consultar por identificador/correlación antes de reintentar; cerrar con confirmación financiera y logs. No ejecutar un segundo abono sin comprobar el primero. |
| INC-02
Fallo de notificación a Cobranza tras abono confirmado | El cliente ya recibió fondos, pero la obligación no continúa hacia Cobranza. Detección: error o ausencia de confirmación en CR-INT-06. | Desembolso conserva el estado financiero confirmado y coordina reenvío con Cobranza, Bus y Tecnología; no revierte el abono por una falla de entrega. | Confirmar recepción en Cobranza, registrar reintentos controlados, resultado y correlación; cerrar cuando la entrega quede comprobada. |
| Ejemplo DES (propuesto): abono sin respuesta de Cuentas | No se confirma el resultado financiero; alerta por timeout / operación pendiente | Desembolso registra caso y coordina con Cuentas y Bus; Seguridad si corresponde | Consultar estado por identificador antes de reintentar; cerrar con confirmación y logs. No ejecutar doble abono. |

Prioridad propuesta por incidente: [INC-01: Alta / riesgo de duplicidad o estado financiero incierto]  [INC-02: Alta / interrumpe la continuidad del crédito después de un abono confirmado]. El Comité ratifica niveles y plazos de atención; no son SLA aprobados.
# 2. Gestión de solicitudes de servicio
Las solicitudes de servicio ITIL son peticiones de atención o acceso TI (no solicitudes de crédito del cliente). Incluir al menos una solicitud estándar.

| ID y solicitud TI | Solicitante y autorización | Atención / entrega / cierre |
| REQ-01: revisión/habilitación de permisos del rol LIDER_DESEMBOLSO para consumir servicios requeridos | Líder o usuario autorizado del módulo; validación del propietario funcional y autorización de Seguridad/Tecnología, por ratificar. | Registrar solicitud; verificar rol y necesidad mínima; revisar DESEMBOLSO_LEER/DESEMBOLSO_EJECUTAR y alcance de APIs; aplicar solo el cambio aprobado, probar acceso y cerrar con evidencia. |
| Ejemplo (propuesto): habilitar acceso de consulta a órdenes de desembolso | Usuario autorizado del BNA; aprobación del propietario funcional y Seguridad, por ratificar | Comprobar identidad/rol, tramitar permiso mínimo, validar acceso y registrar evidencia de cierre. |

# 3. Habilitación y gestión de cambios
Documentar una modificación prevista en servicio, API, base de datos o configuración; separar reversión técnica del software de reversión financiera de una transacción.

| ID / cambio | Riesgo e impacto | Aprobación y pruebas | Reversión técnica y evidencia |
| CHG-01: ajustar el contrato CR-INT-05 para confirmación de abono e idempotencia | Impacta Desembolso, Cuentas y Bus; un contrato incompatible puede dejar operaciones inciertas o favorecer reintentos duplicados. | Desembolso propone; análisis de impacto con Cuentas/Bus; aprobación de Tecnología; prueba de compatibilidad en Testing antes de desplegar. | Conservar la versión anterior del contrato/configuración y restaurarla si falla la prueba; registrar versión, resultados y evidencia. No confundir rollback técnico con reversión financiera. |
| Ejemplo (propuesto): cambiar estructura de respuesta de API Desembolso→Cobranza | Riesgo de incompatibilidad en CR-INT-06 y de no activar obligación | Evaluación de impacto con ambos módulos/Bus; aprobación de Tecnología; prueba de compatibilidad en Testing | Mantener versión anterior y restaurarla si falla; registrar resultados y versión aplicada. |

# 4. Gestión de disponibilidad
Indicar componentes esenciales, método de medición, responsables y acciones de respuesta. No fijar porcentajes sin sustento y coordinación con I-05.

| Componente / dependencia | Monitoreo y evidencia | Objetivo / responsable |
| API del SRV-CR-04 y MySQL del módulo | Health check de API, errores HTTP/aplicación, conectividad a persistencia, operaciones pendientes y logs con correlación; frecuencia por definir con Infraestructura. | Meta numérica y horario: Pendiente de validación. Desembolso monitorea su servicio; Infraestructura/ Tecnología validan plataforma y métricas. |
| Ejemplo DES: API de Desembolso y respuesta de Cuentas | Health check, errores de integración, operaciones sin confirmación, logs con correlación | Objetivos numéricos pendientes; Desembolso monitorea su API y escala a Cuentas/Bus según causa. |

# 5. Gestión de continuidad del servicio
Definir qué se hace ante interrupción grave y cómo se vuelve a la operación normal. RTO y RPO no deben inventarse: consignarlos como propuestas justificadas o pendientes.

| Escenario crítico | Contingencia y recuperación | RTO / RPO / retorno / responsables |
| Indisponibilidad prolongada de la API o MySQL de Desembolso | Detener nuevas ejecuciones, preservar los estados ya registrados y recuperar aplicación/persistencia con Infraestructura. Antes de reabrir, validar integridad y revisar operaciones pendientes. | RTO/RPO: Pendiente de validación. Responsables propuestos: Desembolso, Infraestructura y Tecnología; retorno normal solo tras verificación. |
| Ejemplo DES: caída sostenida de Cuentas | Mantener órdenes en estado controlado y consultar estado cuando se recupere dependencia. No reintentar automáticamente un abono incierto. | RTO/RPO pendientes. Coordinar Desembolso, Cuentas, Bus e Infraestructura; verificar abonos antes de liberar flujo normal. |

# 6. Validación, evidencias y decisiones pendientes

| Elemento | Resultado / referencia | Estado y revisor |
| Compatibilidad con I-01 y CR-INT | SRV-CR-04; CR-INT-04 (Evaluación→Desembolso), CR-INT-05 (Desembolso→Cuentas), CR-INT-06 (Desembolso→Cobranza) y CR-INT-10 (Créditos→Seguridad/Auditoría). | Propuesta para revisión \| Sebastián Conde / Comité de Créditos |
| Roles y permisos | LIDER_DESEMBOLSO: DESEMBOLSO_LEER y DESEMBOLSO_EJECUTAR. La matriz no confirma por sí sola autorización para consumir APIs externas ni ejecutar el asiento financiero. | Pendiente \| Seguridad, Tecnología y Bus/Cuentas |
| Evidencias que existen | Evidencia documental disponible: I-01, TOGAF, matriz CR-INT, lineamiento técnico, informe ITIL4 y control de accesos. No se aportaron logs/tickets reales de Testing. | Documental disponible / evidencia operativa no disponible |
| Decisiones por ratificar | Permisos y ejecución financiera; idempotencia; activación/calendario; entrega CR-INT-06; política de reversión; contratos API, errores/timeouts y SLA. | Pendiente \| Comité de Créditos, Tecnología, Seguridad, Cuentas, Cobranza e Infraestructura según tema |

Entrega al enlace: plantilla completada; indicar fuentes utilizadas y dudas abiertas. La revisión del Comité es necesaria antes de incorporar la ficha al informe ITIL 4 consolidado.