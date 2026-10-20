UNIVERSIDAD CATÓLICA DE SANTA MARÍA
Escuela Profesional de Ingeniería de Sistemas
Gestión de Sistemas y Tecnologías de la Información
LINEAMIENTO TÉCNICO COMÚN - LÍNEA DE CRÉDITOS
Python + FastAPI + MySQL

| Proyecto | Plataforma Digital Banco Nacional de Arequipa (BNA) |
| Comité | Comité de Créditos |
| Líder | Mathias Cabrera |
| Fase | II - ITIL 4 |
| Inicio de fase | 28/09/2026 |

# 1. Propósito
Establecer una base técnica uniforme para los módulos de la Línea de Créditos durante la Fase II, sin reemplazar las decisiones específicas que posteriormente deban ser ratificadas por el Comité de Tecnología.
# 2. Stack de trabajo

| Componente | Tecnología / criterio |
| Lenguaje backend | Python |
| Framework API | FastAPI |
| Base de datos | MySQL |
| Integración entre módulos | Servicios/API |
| Documentación de API | OpenAPI / Swagger generado por FastAPI |
| Ambientes previstos | Desarrollo / Testing / Producción |

# 3. Reglas técnicas iniciales
Cada módulo mantiene su propia lógica de negocio y sus datos.
Un módulo no debe modificar directamente las tablas MySQL de otro módulo.
La comunicación entre módulos debe realizarse mediante servicios/API acordados.
Las dependencias deben respetar el TOGAF y la matriz CR-INT.
Las operaciones sensibles deberán poder identificarse y trazarse.
Los contratos finales de error, timeout, seguridad y despliegue se cerrarán cuando corresponda con Tecnología e Infraestructura.
# 4. Qué se exige en I-01
En I-01 solo se debe registrar la tecnología como habilitadora del servicio. No se requiere todavía definir todos los endpoints, modelos Pydantic, tablas físicas, scripts SQL ni configuraciones de despliegue.
# 5. Ejemplos futuros de endpoints (solo orientativos)

| No son contratos definitivos: Los siguientes nombres sirven únicamente para entender el tipo de integración que podría existir. No deben tratarse como endpoints oficiales hasta que cada módulo y el Comité de Tecnología los acuerden. |

POST /solicitudes
POST /evaluaciones
POST /desembolsos
POST /pagos
# 6. Testing
La guía general del proyecto exige evidencias de pruebas e integración en el ambiente de Testing durante la Fase II. La preparación técnica deberá permitir posteriormente registrar escenarios, resultados esperados, resultados obtenidos y evidencia de integración.