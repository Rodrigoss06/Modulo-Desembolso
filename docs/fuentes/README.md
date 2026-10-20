# Documentos fuente del módulo Desembolso

Originales entregados por el equipo y el Comité de Créditos. La carpeta `texto/`
contiene su texto extraído para búsqueda rápida (las tablas de los PDF pueden
aparecer desalineadas: ante una duda, el original manda).

**Precedencia ante contradicciones:** lo más reciente prevalece. Orden de
vigencia: acta ACT-2026-007 (18/10) > I-04 / I-05 (18/10) > Ficha I-01 (11/10) >
Informe ITIL4 de la línea (10/2026) > Modelo Referencial BD (25/09) > Informe
TOGAF Fase I (09/09, versión final). La síntesis vigente está en
[`../DOCUMENTO_TECNICO.md`](../DOCUMENTO_TECNICO.md).

| # | Documento | Qué aporta | Texto |
|---|---|---|---|
| 01 | [Informe TOGAF Fase I — Desembolso](01_Informe_TOGAF_FaseI_Desembolso.pdf) | Alcance, reglas RN-01..10, RF-01..10, RNF-01..07, CU-01..07, entidades, estados, interfaces IF-01..09, pantallas, riesgos, escenarios de verificación | [txt](texto/01_Informe_TOGAF_FaseI_Desembolso.txt) |
| 02 | [Modelo Referencial BD](02_Modelo_Referencial_BD_Desembolso.docx) | Tablas `des_*`, diccionario, catálogos, índices, vistas, solicitudes a Core/Bus/Infra | [md](texto/02_Modelo_Referencial_BD_Desembolso.md) |
| 03 | [Ficha de servicio SRV-CR-04 (I-01)](03_Ficha_Servicio_SRV-CR-04_I-01.pdf) | Servicio ITIL, consumidores, entradas/salidas, dependencias CR-INT, observaciones OBS-DES-01..09 | [txt](texto/03_Ficha_Servicio_SRV-CR-04_I-01.txt) |
| 04 | [Prácticas ITIL 4 (I-04)](04_Practicas_ITIL4_I-04_Desembolso.pdf) | Incidentes INC-01/02, solicitud REQ-01, cambio CHG-01, disponibilidad y continuidad | [md](texto/04_Practicas_ITIL4_I-04_Desembolso.md) |
| 05 | [Catálogo y SLA (I-05)](05_Catalogo_SLA_I-05_Desembolso.pdf) | Criticidad, indicadores (disponibilidad, p95, fallas, abonos sin confirmar), escalamiento | [md](texto/05_Catalogo_SLA_I-05_Desembolso.md) |
| 06 | [Acta ACT-2026-007](06_Acta_ACT-2026-007_Desembolso.pdf) | Acuerdos AC-40..AC-47 y consultas abiertas al docente | [txt](texto/06_Acta_ACT-2026-007_Desembolso.txt) |
| 07 | [Lineamiento técnico Créditos](07_Lineamiento_Tecnico_FastAPI_MySQL_Creditos.docx) | Stack común Python + FastAPI + MySQL y reglas técnicas | [md](texto/07_Lineamiento_Tecnico_FastAPI_MySQL_Creditos.md) |
| 08 | [Referencia TOGAF y matriz CR-INT](08_Referencia_TOGAF_Matriz_CR-INT.docx) | Flujo de la línea y matriz CR-INT-01..10; pendientes que no deben volverse regla | [md](texto/08_Referencia_TOGAF_Matriz_CR-INT.md) |
| 09 | [Informe ITIL 4 de la Línea de Créditos v0.1](09_Informe_ITIL4_Linea_Creditos_v01.docx) | Catálogo SRV-CR-01..05; Cuentas es dueño de los movimientos; brechas P-01..P-08 | [md](texto/09_Informe_ITIL4_Linea_Creditos_v01.md) |
| 10 | [Stack tecnológico BNA](10_Stack_Tecnologico_BNA.md) | Stack oficial del banco, reglas de datos, estándares de integración (headers, timeouts) | — |

Excluidos a propósito: entregables GSTI-LAB04 (tratan sobre SEDAPAR, no del BNA),
plantillas vacías de I-04/I-05 y la base `BNA_CONTROL_ACCESO` (contiene datos de
usuarios y hashes; el Informe ITIL4 pide no redistribuirlos). De esta última solo
se usan los nombres de rol y permiso, citados en el documento técnico.
