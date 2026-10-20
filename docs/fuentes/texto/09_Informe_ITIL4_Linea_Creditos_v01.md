UNIVERSIDAD CATÓLICA DE SANTA MARÍA
Escuela Profesional de Ingeniería de Sistemas
Gestión de Sistemas y Tecnologías de la Información
# INFORME CONSOLIDADO DE FASE II
ITIL 4
Línea de Créditos del Banco Nacional de Arequipa (BNA)

| Campo | Detalle |
| Responsable | Comité de Créditos (transversal) |
| Líder | Mathias Cabrera |
| Integrantes | Piero Ponce, Ángel Cruz, Yhosfer Quispe, Sebastián Conde y Álvaro Montoya |
| Cobertura de esta versión | I-01: servicios TI; I-02 e I-03: propuestas de flujos de valor |
| Por incorporar | I-04: prácticas; I-05: catálogo final / niveles; I-06: pruebas e integración |
| Versión / condición | v0.1 – Documento de trabajo para revisión, no informe final aprobado |
| Fecha | Octubre de 2026 |

Trabajo acumulativo: se ampliará con evidencia validada en las actividades restantes.
# Resumen ejecutivo
Este informe reúne el avance documental de la Fase II - ITIL 4 de la Línea de Créditos del BNA. A partir de las cinco fichas de identificación de servicios (I-01), se establece un catálogo preliminar de SRV-CR-01 a SRV-CR-05 y se modelan dos propuestas de flujo de valor: I-02 (Captación, Solicitud y Evaluación) e I-03 (Desembolso y Cobranza). Se mantiene la continuidad con la arquitectura TOGAF de Fase I y las interfaces CR-INT.
El informe distingue lo respaldado por fichas y plan de trabajo de los aspectos todavía no validados. El flujo financiero se representa por medio de Cuentas; el Bus es una capa técnica de integración. Se registra, asimismo, la necesidad de ampliar Captación con la verificación financiera interna/externa exigida por el alcance general del BNA. Las actividades I-04, I-05 e I-06 se reservan para completar prácticas ITIL, niveles de servicio y evidencias reales de Testing.

| Estado del documento:  Las cinco fichas existen, pero sus códigos y responsables funcionales aún pueden requerir ratificación. Los flujos I-02/I-03 son consolidaciones preliminares preparadas por el Comité; no se presentan como aprobaciones oficiales ni como pruebas ejecutadas. |

# Índice de contenido
1.  Introducción, objetivos y alcance
2.  Criterios de consolidación y fuentes
3.  I-01. Servicios TI y valor generado
4.  I-02. Flujo de valor Captación–Solicitud–Evaluación
5.  I-03. Flujo de valor Desembolso–Cobranza
6.  Interoperabilidad, tecnología y control de accesos
7.  Brechas y decisiones pendientes
8.  Plan de incorporación de I-04, I-05 e I-06
9.  Conclusiones y acciones inmediatas
10.  Referencias
# 1. Introducción, objetivos y alcance
La Fase I con TOGAF definió las vistas de arquitectura y la relación entre Captación, Solicitud, Evaluación, Desembolso y Cobranza. La Fase II aplica ITIL 4 para describir el valor de los servicios TI y las condiciones de gestión que permitirán prestarlos y soportarlos. El objetivo de este documento es consolidar lo disponible sin duplicar los informes de cada módulo.
Alcance de esta versión: identificación de cinco servicios, consumidores, entradas, salidas, valor y dependencias; propuesta de dos flujos de valor transversales; registro de decisiones no ratificadas; y preparación de las secciones de operación, niveles de servicio y Testing. No se declara que las APIs estén implementadas, que exista una infraestructura operativa ni que los SLA hayan sido aprobados.
# 2. Criterios de consolidación y fuentes
Una función técnica aislada (p. ej., registrar garantía) no se cuenta automáticamente como servicio independiente cuando contribuye al mismo resultado de negocio.
Los diagramas operativos de las fichas son insumos para los flujos de valor, pero no sustituyen el análisis de la Cadena de Valor del Servicio (SVC) de ITIL 4.
La trazabilidad funcional sigue el sentido de la matriz CR-INT del informe TOGAF; no se inventan integraciones ni propietarios de datos.
La propuesta de stack Python + FastAPI + MySQL se registra como base común, sujeta a las ratificaciones técnicas que correspondan.
Una regla pendiente se presenta como pendiente aun cuando aparezca en un borrador de otro equipo o en una matriz de permisos.
# 3. I-01. Identificación de servicios TI y valor generado
El objetivo de I-01 (28/09–04/10) es identificar los servicios que soportan la Línea de Créditos y el valor para el cliente y el BNA. Se recibieron cinco fichas: una por módulo. Los códigos se utilizan para facilitar la consolidación, con condición preliminar hasta su ratificación.
Tabla 1. Catálogo preliminar de servicios TI de Créditos

| Código / módulo | Servicio y consumidor | Entrada → salida | Valor para cliente / BNA |
| SRV-CR-01
Captación | Captación de Clientes de Crédito.
Cliente / Solicitud | Interés y datos iniciales → prospecto y verificación preliminar para Solicitud | Evita reprocesos; favorece datos consistentes y trazables. La comprobación financiera interna/externa debe incorporarse al alcance. |
| SRV-CR-02
Solicitud | Gestión de Solicitud de Crédito.
Asesor / Evaluación | Cliente verificado + condiciones → expediente versionado; resultado de Evaluación | Trámite estructurado para el cliente; expediente uniforme y control de versiones para el BNA. |
| SRV-CR-03
Evaluación | Evaluación Crediticia.
Solicitud / analista / Desembolso | Expediente → APROBADO, OBSERVADO o RECHAZADO y observaciones | Respuesta trazable; evaluación del riesgo y evidencia de la decisión para el banco. |
| SRV-CR-04
Desembolso | Gestión del Desembolso.
Cliente / operador / Cobranza | Crédito aprobado + cuenta válida → abono confirmado y notificación | Fondos autorizados con control del destino; trazabilidad y prevención de duplicación. |
| SRV-CR-05
Cobranza | Cobro de Cuotas de Crédito.
Cliente / Home Banking | Crédito activo + pago → pago aplicado, saldo y comprobante | Pago flexible y consultable; recuperación y seguimiento de cartera para el BNA. |

## 3.1. Estado por módulo y observaciones de I-01
Tabla 2. Revisión documental y aspectos por conciliar

| Módulo | Estado del insumo | Observación prioritaria |
| Captación | Ficha recibida (I-01). | La ficha se concentra en prospectos/identidad; incorporar y trazar situación financiera interna/externa, central de riesgos y relación con Clientes (CR-INT-09). Su sección de dependencias dice «por confirmar» incluso para relaciones ya presentes en CR-INT. |
| Solicitud | Ficha recibida (I-01). | Mantener catálogo final de estados y autoridad del calendario vigente como pendientes. |
| Evaluación | Ficha recibida (I-01). | No presentar los umbrales de score/ratio propuestos como oficiales; precisar el tratamiento de OBSERVADO. |
| Desembolso | Ficha recibida (I-01). | Permisos, resultado incierto, idempotencia, activación de obligación, calendario y reversión por ratificar. |
| Cobranza | Ficha recibida (I-01). | Definir fórmula/responsable de mora y propiedad del calendario; Home Banking es el canal digital confirmado para el flujo modelado. |

Por ello, I-01 dispone de insumos suficientes para consolidación preliminar, pero el cierre formal requiere atender las observaciones de la Tabla 2 y validar la matriz con los enlaces responsables.
# 4. I-02. Flujo de valor: Captación, Solicitud y Evaluación
Responsables según plan: Ángel Cruz y Yhosfer Quispe. Periodo previsto: 01/10–08/10. La demanda surge cuando un cliente requiere un crédito; el servicio combinado convierte esa necesidad en una solicitud completa y una decisión trazable. Este apartado es una propuesta de consolidación del Comité derivada de las fichas I-01 y deberá validarse con los módulos.
Figura 1. Secuencia de prestación que fundamenta el flujo de valor I-02
## 4.1. Actividades y resultados de valor
Tabla 3. Actividades del flujo I-02 y resultados verificables

| Tramo | Actividad principal | Salida / valor |
| Captación | Recibir interés; identificar/verificar cliente; completar comprobación financiera interna y externa (ajuste pendiente). | Prospecto y perfil preliminar para Solicitud; menos duplicación de datos. |
| Solicitud | Registrar monto, plazo, moneda, pago doble, calendario preliminar y respaldos; versionar y remitir expediente. | Expediente completo y trazable para Evaluación. |
| Evaluación | Aplicar workflow según monto y reglas vigentes; analizar observaciones; emitir resultado y devolverlo a Solicitud. | Decisión APROBADO/OBSERVADO/RECHAZADO; habilitar Desembolso solo si APROBADO. |

## 4.2. Relación con la Cadena de Valor del Servicio de ITIL 4
Tabla 4. Interpretación de actividades SVC para I-02

| Actividad SVC | Contribución propuesta |
| Engage | Interacción inicial con el solicitante; consulta y comunicación del estado/resultado. |
| Design & Transition | Definir expediente, reglas vigentes, criterios de aceptación e interoperabilidad entre módulos. |
| Obtain/Build | Preparar los componentes y contratos de integración requeridos; no implica que estén ya construidos. |
| Deliver & Support | Prestar Captación, Solicitud y Evaluación; manejar observaciones y casos no concluidos. |
| Plan | Mantener objetivos, prioridades, responsables y lineamientos aprobados de Créditos. |
| Improve | Corregir causas de reproceso, revisar resultados de pruebas y optimizar el flujo. |

Criterio clave: no equivale a elaborar un segundo BPMN del crédito. La Figura 1 muestra la secuencia funcional que entrega valor; la Tabla 4 explica las actividades SVC que permiten diseñar, operar, dar soporte y mejorar ese servicio.
# 5. I-03. Flujo de valor: Desembolso y Cobranza
Responsables según plan: Sebastián Conde y Álvaro Montoya. Periodo previsto: 05/10–12/10. El valor comienza con un crédito aprobado y culmina con fondos correctamente abonados y una obligación gestionable, cuyos pagos quedan aplicados y trazados. Esta consolidación se basa en las fichas de Desembolso y Cobranza y requiere validación de sus enlaces.
Figura 2. Secuencia de prestación que fundamenta el flujo de valor I-03
## 5.1. Actividades y condiciones de continuidad
Tabla 5. Actividades del flujo I-03 y controles asociados

| Tramo | Actividad y control | Valor / salida |
| Desembolso | Recibir aprobación válida; validar cuenta, titularidad, monto y moneda; solicitar abono a Cuentas por CR-INT-05; confirmar antes de reintentar un resultado incierto. | Abono confirmado, referencia financiera y constancia; evita duplicación y destinos erróneos. |
| Activación | Tras abono confirmado, notificar obligación a Cobranza por CR-INT-06. Si falla la notificación, gestionar reenvío sin deshacer el abono. | Continuidad del ciclo crediticio sin doble desembolso. |
| Cobranza | Recibir pago desde Home Banking (CR-INT-08); verificar crédito/cuota; determinar monto exigible; solicitar cargo a Cuentas (CR-INT-07); aplicar sólo tras confirmación. | Cuotas y saldo actualizados, comprobante y trazabilidad. |
| Excepciones | Rechazos, pagos no confirmados, mora, reversión y conciliación quedan sujetos a políticas/contratos específicos por validar. | Prevención de movimientos inconsistentes y registro para seguimiento. |

## 5.2. Relación con la Cadena de Valor del Servicio de ITIL 4
Tabla 6. Interpretación de actividades SVC para I-03

| Actividad SVC | Contribución propuesta |
| Engage | Cliente/operador recibe constancia; Home Banking inicia pagos; interfaces mantienen información del estado. |
| Design & Transition | Definir condiciones de desembolso/pago, idempotencia, conciliación y recuperación ante fallos. |
| Obtain/Build | Preparar servicios API y persistencia con validación de Seguridad, Tecnología e Infraestructura. |
| Deliver & Support | Gestionar abonos, activación, cobros, incidencias y comprobantes. |
| Plan | Priorizar servicios críticos, dependencias operativas y políticas que faltan por ratificar. |
| Improve | Analizar fallos en abonos, pagos y notificaciones para reducir reprocesos. |

# 6. Interoperabilidad, tecnología y control de accesos
Los módulos se relacionan mediante interfaces documentadas conceptualmente en TOGAF. El Bus de Servicios actúa como mecanismo técnico de enrutamiento/integración. Los movimientos financieros corresponden al servicio propietario Cuentas; una flecha hacia el CORE en un esquema tecnológico no habilita por sí misma un acceso funcional directo ni modifica esa responsabilidad.
Tabla 7. Trazabilidad de las interfaces de Créditos

| Interfaz | Relación funcional | Propósito |
| CR-INT-01 | Captación → Solicitud | Verificación/prospecto habilitante. |
| CR-INT-02 | Solicitud → Evaluación | Expediente versionado. |
| CR-INT-03 | Evaluación → Solicitud | Resultado y observaciones. |
| CR-INT-04 | Evaluación → Desembolso | Autorización del crédito aprobado. |
| CR-INT-05 | Desembolso → Cuentas | Solicitud y confirmación del abono. |
| CR-INT-06 | Desembolso → Cobranza | Desembolso confirmado y continuidad de obligación. |
| CR-INT-07 | Cobranza → Cuentas | Solicitud/confirmación de cargo del pago. |
| CR-INT-08 | Home Banking → Cobranza | Inicio de pago digital. |
| CR-INT-09 | Captación → Clientes | Consulta/referencia de identidad. |
| CR-INT-10 | Créditos → Seguridad/Auditoría | Registro de eventos críticos. |

Tecnología de referencia: Python y FastAPI en los servicios backend, MySQL como persistencia y APIs para la interoperabilidad. Cada módulo mantiene autoridad sobre su dominio y no modifica directamente tablas ajenas. La definición concreta de versiones, autenticación, contratos, timeouts y manejo de errores está sujeta al acuerdo con Tecnología y Seguridad.
El archivo DB_CONTROL_ACCESO identifica roles y permisos propuestos —entre otros LIDER_CREDITOS, LIDER_EVALUACION, LIDER_DESEMBOLSO y LIDER_COBRANZA—. Se utiliza como insumo de coordinación, no como prueba de que las APIs o controles estén implementados. Se excluyen de este informe credenciales y contraseñas contenidas en dicho archivo; no deben redistribuirse.
# 7. Brechas y decisiones pendientes
Tabla 8. Registro de asuntos que requieren validación o acuerdo

| ID | Asunto | Tratamiento requerido / instancia |
| P-01 | Captación: situación financiera y central de riesgos | Piero / Captación: corregir alcance de ficha SRV-CR-01 e interfaces con Clientes/Solicitud. |
| P-02 | Umbrales y estados de Evaluación | Yhosfer / Evaluación / Comité: ratificar workflow, catálogo de estados y tratamiento OBSERVADO. |
| P-03 | Autoridad sobre calendario vigente | Ángel, Sebastián y Álvaro: definir propiedad y difusión a Cobranza; no atribuir creación automática a Desembolso. |
| P-04 | Mora y pago fraccionado | Álvaro / Cobranza: determinar fórmula, responsable, aplicación y evidencias. |
| P-05 | Reversión e idempotencia | Sebastián / Tecnología / Cuentas: precisar política ante incertidumbre y autorización de operaciones. |
| P-06 | Contratos API y controles de acceso | Tecnología / Seguridad / Bus / módulos: autenticación, mensajes, estados, errores, timeouts y permisos. |
| P-07 | Canales adicionales de pago/captación | Confirmar interfaces antes de declarar ATM o Billetera Digital como vías activas de Cobranza. |
| P-08 | Validación del modelo I-02 e I-03 | Ángel/Yhosfer y Sebastián/Álvaro: ratificar tablas y diagramas en reunión del Comité. |

# 8. Incorporación progresiva de I-04, I-05 e I-06
Las siguientes secciones son la estructura prevista para actualizar este mismo informe. El estado indica actividades programadas o en elaboración, no resultados ejecutados o aprobados.
Tabla 9. Cronograma de integración al informe consolidado

| Actividad / periodo | Responsables | Contenido que se incorporará | Estado actual |
| I-04
09–16/10 | Mathias Cabrera / Yhosfer Quispe | Procedimientos de incidentes, solicitudes de servicio, cambios, disponibilidad y continuidad; priorización y escalamiento. | Pendiente de desarrollo/validación |
| I-05
13–20/10 | Piero Ponce / Ángel Cruz | Catálogo definitivo, propietarios, criterios y objetivos propuestos de niveles de servicio, sujetos a aprobación. | Programado |
| I-06
18–25/10 | Sebastián Conde / Álvaro Montoya | Casos de prueba de integración en Testing, evidencias reales, resultados, incidencias y ajustes de arquitectura. | Programado |

## 8.1. Información mínima que se deberá recibir para I-04
Incidentes: escenario, impacto, prioridad, detección, responsable, escalamiento, recuperación y evidencia (p. ej., consulta a buró, evaluación, abono incierto, pago no confirmado).
Solicitudes de servicio: tipo de solicitud, canal, quién la autoriza, tratamiento y cierre.
Cambios: origen, análisis de impacto, aprobación, despliegue controlado y plan de reversión técnica.
Disponibilidad: componentes críticos, dependencias externas, objetivos propuestos y metodología de medición.
Continuidad: fallas previsibles, contingencia propuesta, responsables y RTO/RPO solo si son validados.
## 8.2. Información mínima para I-05 e I-06
I-05: ratificar nombre/código de los servicios, propietario funcional, horarios de atención, consumidores, métricas y objetivos propuestos de niveles de servicio. I-06: documentar entorno, versiones, datos de prueba, operación/API, resultado esperado y real, evidencia fechada, incidencias y validación con Calidad e Infraestructura. Ningún resultado de Testing se consigna sin ejecución comprobable.
# 9. Conclusiones y acciones inmediatas
La Línea de Créditos cuenta con cinco fichas I-01 que permiten estructurar un catálogo preliminar uniforme, pero aún no constituyen un catálogo definitivo aprobado.
I-02 integra identificación/verificación, expediente y decisión; I-03 integra desembolso confirmado y cobro. Ambos flujos se expresan como propuestas de valor bajo ITIL 4, distintas del BPMN operacional.
Las interfaces CR-INT permiten controlar las dependencias; Cuentas es propietario de los movimientos financieros y el Bus es infraestructura de integración.
Las principales brechas recaen en Captación, calendario, criterios de Evaluación, mora, reversión, contratos técnicos y permisos de acceso. Deben resolverse antes de fijar niveles de servicio y ejecutar pruebas concluyentes.
Se recomienda validar las tablas I-02/I-03 con sus enlaces, corregir SRV-CR-01, iniciar la matriz I-04 y continuar con I-05 e I-06 dentro del mismo informe acumulativo.
# 10. Referencias y documentos de trabajo
Universidad Católica de Santa María. (2026). Trabajo grupal integrador: Arquitectura del Banco Nacional de Arequipa (BNA), fases TOGAF, ITIL 4 y COBIT 2019 [Guía del proyecto].
Comité de Créditos BNA. (2026). Informe consolidado de arquitectura empresarial de la Línea de Créditos: Fase I TOGAF 10 [Documento de referencia].
Comité de Créditos BNA. (2026). Guía y plan de trabajo del Comité de Créditos [Cronograma I-01 a I-06].
Módulo Captación de Clientes. (2026). Ficha de identificación de servicio TI SRV-CR-01 [Propuesta I-01].
Módulo Solicitud de Crédito. (2026). Servicios TI y valor generado: SRV-CR-02 [Propuesta I-01].
Módulo Evaluación. (2026). Servicios de TI y valor generado: SRV-CR-03 [Propuesta I-01].
Módulo Desembolso. (2026). Servicios de TI y valor generado: SRV-CR-04 [Propuesta I-01].
Módulo Cobranza. (2026). Ficha de identificación de servicio TI SRV-CR-05 [Propuesta I-01].
Equipo de Control de Accesos BNA. (2026). DB_CONTROL_ACCESO [Matriz técnica de roles y permisos; referencia pendiente de validación].
AXELOS. (2019). ITIL Foundation: ITIL 4 edition. The Stationery Office.

