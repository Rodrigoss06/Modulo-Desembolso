UNIVERSIDAD CATÓLICA DE SANTA MARÍA
Escuela Profesional de Ingeniería de Sistemas
Gestión de Sistemas y Tecnologías de la Información
REFERENCIA DE DEPENDENCIAS TOGAF Y MATRIZ CR-INT
Uso obligatorio para I-01 - Fase II ITIL 4

| Proyecto | Plataforma Digital Banco Nacional de Arequipa (BNA) |
| Comité | Comité de Créditos |
| Líder | Mathias Cabrera |
| Fase | II - ITIL 4 |
| Inicio de fase | 28/09/2026 |

# 1. Regla de uso

| Regla: Los módulos deben identificar sus servicios ITIL respetando las dependencias y límites ya definidos en Fase I. No se deben crear nuevas conexiones entre módulos sin coordinación previa con el Comité de Créditos. |

# 2. Flujo macro de Créditos
CAPTACIÓN  →  SOLICITUD  →  EVALUACIÓN  →  DESEMBOLSO  →  COBRANZA
# 3. Matriz CR-INT de referencia

| ID | Origen | Destino | Finalidad principal |
| CR-INT-01 | Captación | Solicitud | Entregar cliente verificado / perfil preliminar. |
| CR-INT-02 | Solicitud | Evaluación | Enviar expediente completo de solicitud. |
| CR-INT-03 | Evaluación | Solicitud | Retornar resultado y observaciones. |
| CR-INT-04 | Evaluación | Desembolso | Habilitar un crédito aprobado para desembolso. |
| CR-INT-05 | Desembolso | Cuentas | Solicitar/confirmar abono del crédito. |
| CR-INT-06 | Desembolso | Cobranza | Activar obligación luego del desembolso confirmado. |
| CR-INT-07 | Cobranza | Cuentas | Solicitar cargo/aplicación del pago. |
| CR-INT-08 | Home Banking | Cobranza | Iniciar pago de crédito desde canal digital. |
| CR-INT-09 | Captación | Clientes | Validar o referenciar identidad del solicitante. |
| CR-INT-10 | Créditos | Seguridad / Auditoría | Registrar eventos críticos y trazabilidad. |

# 4. Criterios para llenar la ficha ITIL
En Dependencias, colocar solamente módulos realmente necesarios para prestar el servicio.
No declarar Tarjetas como dependencia directa de Créditos si la relación ocurre a través de Home Banking.
No declarar acceso directo de Evaluación al CORE si no está respaldado por la matriz acordada.
Cuando el servicio use datos de otro módulo, debe referenciar al módulo propietario y no asumir propiedad del dato.
Las decisiones pendientes de Fase I deben permanecer como pendientes en la ficha ITIL.
# 5. Pendientes que NO deben convertirse en regla oficial
Umbrales exactos del workflow de Evaluación.
Catálogo final de estados entre Solicitud y Evaluación.
Propietario definitivo del calendario de pagos durante todo el ciclo.
Fórmula/tasa definitiva de mora.
Política completa de reversión de desembolsos.
Estándar final de errores, timeouts y detalles técnicos aún sujetos a Tecnología.