
|  |  |

UNIVERSIDAD CATÓLICA DE SANTA MARÍA
ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS
Gestión de Sistemas y Tecnologías de la Información – A
MODELO REFERENCIAL DE BASE DE DATOS
Módulo 13 – Desembolso · Línea de Créditos
Proyecto Integrador: Plataforma Digital Banco Nacional de Arequipa (BNA)

| CÓDIGO | APELLIDOS Y NOMBRES | ROL |
| 2023600951 | Centeno Lopez, Jose Alfredo | Integrante |
| 2023223181 | Lazo Franco, Mauricio Paolo | Integrante |
| 2023223991 | Nuñez Arista, Piero Bruker | Integrante |
| 2023224941 | Reaño Soto, Iván Edgardo | Líder de equipo |
| 2023225471 | Sucapuca Santamarina, Rodrigo Alonso | Integrante |


| Motor de base de datos | MySQL 8.0 · InnoDB · utf8mb4 |
| Capa de aplicación | Python 3.11 · FastAPI · SQLAlchemy 2.0 |
| Versión del modelo | 1.0 |
| Fecha | 25/09/2026 |
| Dirigido a | Comité de Tecnología, Core, Bus de Servicios e Infraestructura |

Docentes: Jorge Martínez / Mario Santillana
Arequipa – Perú
2026
ÍNDICE
1. Objeto del documento	3
2. Convenciones del modelo	3
3. Modelo físico del módulo	4
4. Diccionario de datos	5
4.1. Tabla des_orden	5
4.2. Tabla des_validacion	6
4.3. Tabla des_evento_entrega	6
4.4. Tabla des_auditoria	7
4.5. Tabla des_solicitud_reversion	8
5. Catálogos de valores	8
5.1. Ciclo de estados de la orden	9
6. Referencias hacia otros módulos	10
7. Restricciones e índices	10
8. Vistas de apoyo operativo	11
9. Reglas que el modelo impone	11
10. Solicitudes a los módulos de Core, Bus e Infraestructura	12
11. Archivos que acompañan a este documento	12
ÍNDICE DE FIGURAS
Figura 1. Modelo físico de las cinco tablas del módulo de Desembolso.	4
Figura 2. Transiciones válidas de la columna estado.	9
Figura 3. Identificadores externos que el módulo almacena como referencia lógica.	10
1. Objeto del documento
Este documento entrega el modelo referencial de base de datos del módulo de Desembolso, solicitado por el Comité PMI para que los equipos de Core, Bus de Servicios e Infraestructura dispongan de la estructura de datos del módulo. Contiene el modelo físico, el diccionario de datos, los catálogos de valores, las referencias hacia otros módulos y el script de creación listo para ejecutar.
El módulo registra la intención de desembolsar un crédito aprobado, la evidencia de las validaciones previas, el resultado financiero devuelto por el Core y la entrega del resultado hacia Cobranza. El modelo no almacena saldos ni asientos contables: esa información pertenece al Core.
2. Convenciones del modelo
•	Prefijo de tablas. Todas las tablas usan el prefijo des_. El esquema puede ser compartido entre módulos y el prefijo evita colisiones de nombres.
•	Identificadores propios. CHAR(36) con UUID versión 4 generado por la aplicación. No se usa AUTO_INCREMENT en entidades de negocio porque todavía no existe un generador central de secuencias acordado con el Core.
•	Importes. DECIMAL(15,2) en todos los casos. Queda prohibido FLOAT o DOUBLE para cálculos monetarios.
•	Moneda. CHAR(3) según ISO-4217, restringido por CHECK a PEN y USD.
•	Fechas. DATETIME para fechas de negocio y TIMESTAMP en UTC para marcas de auditoría. La conversión a hora de Arequipa se realiza en la capa de aplicación.
•	Integridad referencial. Se declaran llaves foráneas únicamente entre tablas del propio módulo. Los identificadores de otros módulos son referencias lógicas verificadas por interfaz a través del Bus de Servicios.
•	Nomenclatura. snake_case en tablas y columnas, prefijos uk_ para claves únicas, idx_ para índices, fk_ para llaves foráneas y ck_ para restricciones de verificación.
•	Juego de caracteres. utf8mb4 con colación utf8mb4_0900_ai_ci en todas las tablas.
3. Modelo físico del módulo
Figura 1. Modelo físico de las cinco tablas del módulo de Desembolso.

| Tabla | Responsabilidad | Volumen estimado |
| des_orden | Intención, ejecución y resultado del desembolso. | Una fila por orden |
| des_validacion | Evidencia de identidad, cuenta y autorización. | Dos a cuatro por orden |
| des_evento_entrega | Bandeja de salida hacia Cobranza con reintento. | Una a dos por orden |
| des_auditoria | Bitácora de solo inserción de todas las acciones. | Cinco a diez por orden |
| des_solicitud_reversion | Seguimiento de reversiones autorizadas. | Excepcional |

4. Diccionario de datos
4.1. Tabla des_orden
Tabla principal del módulo. Conserva la intención del desembolso antes de invocar al Core y el resultado financiero una vez confirmado.

| Columna | Tipo y restricciones | Descripción |
| id | CHAR(36), PK | UUID v4 generado por la aplicación. |
| codigo_orden | VARCHAR(24), UK | Correlativo legible, formato DES-2026-000001. |
| aprobacion_id | VARCHAR(36), NOT NULL | Referencia lógica al módulo Evaluación (12). |
| aprobacion_version | INT UNSIGNED, DEF 1 | Versión de la aprobación consumida. |
| credito_id | VARCHAR(36), NOT NULL | Referencia lógica a Solicitud de Crédito (11). |
| cliente_id | VARCHAR(36), NOT NULL | Referencia lógica a Clientes (2). |
| cuenta_id | VARCHAR(36), NOT NULL | Cuenta destino, referencia a Cuentas (3). |
| importe | DECIMAL(15,2), CHECK > 0 | Monto bruto a desembolsar. |
| moneda | CHAR(3), CHECK PEN/USD | Código de moneda ISO-4217. |
| estado | ENUM, DEF PREPARADA | Estado financiero de la orden. Ver sección 5. |
| motivo_rechazo | VARCHAR(255), NULL | Motivo cuando el estado es RECHAZADA. |
| entrega_estado | ENUM, DEF PENDIENTE | Entrega a Cobranza, independiente del estado. |
| core_operacion_id | VARCHAR(40), NULL | Identificador de la operación en el Core (1). |
| fecha_efectiva | DATETIME, NULL | Fecha valor del desembolso según el Core. |
| idempotency_key | CHAR(36), UK | Clave de idempotencia enviada por el canal. |
| request_hash | CHAR(64), NOT NULL | SHA-256 del contenido de la solicitud. |
| canal | ENUM, DEF AGENCIA | Canal de origen de la operación. |
| agencia_id | VARCHAR(20), NULL | Agencia donde se prepara la orden. |
| usuario_preparacion | VARCHAR(40), NOT NULL | Operador que prepara la orden. |
| usuario_confirmacion | VARCHAR(40), NULL | Operador que confirma la ejecución. |
| correlation_id | CHAR(36), NOT NULL | Identificador de correlación propagado por el Bus. |
| version | INT UNSIGNED, DEF 0 | Control de concurrencia optimista. |
| credito_confirmado | VARCHAR(36), generada | Columna generada. Impone una sola orden confirmada por crédito. |
| creado_en | TIMESTAMP, DEF NOW | Marca de creación en UTC. |
| actualizado_en | TIMESTAMP, ON UPDATE | Marca de última modificación en UTC. |

4.2. Tabla des_validacion
Registra el resultado de cada validación previa a la ejecución. No almacena biometría: solo la referencia de evidencia devuelta por el módulo proveedor.

| Columna | Tipo y restricciones | Descripción |
| id | CHAR(36), PK | Identificador de la validación. |
| orden_id | CHAR(36), FK des_orden | Orden a la que pertenece la validación. |
| tipo | ENUM, NOT NULL | IDENTIDAD, CUENTA, AUTORIZACION o ANTIFRAUDE. |
| proveedor | VARCHAR(40), NOT NULL | Módulo que emitió la validación. |
| referencia_evidencia | VARCHAR(100), NOT NULL | Referencia opaca devuelta por el proveedor. |
| resultado | ENUM, NOT NULL | APROBADA o RECHAZADA. |
| detalle | VARCHAR(255), NULL | Observación funcional, sin datos sensibles. |
| vence_en | DATETIME, NULL | Vigencia de la validación si el proveedor la informa. |
| creado_en | TIMESTAMP, DEF NOW | Momento de la validación. |

4.3. Tabla des_evento_entrega
Implementa el patrón de bandeja de salida. Garantiza que el resultado llegue a Cobranza al menos una vez, aunque el módulo destino esté indisponible al momento de la confirmación.

| Columna | Tipo y restricciones | Descripción |
| id | CHAR(36), PK | Identificador del evento. |
| orden_id | CHAR(36), FK des_orden | Orden que originó el evento. |
| tipo | VARCHAR(60), NOT NULL | desembolso.confirmado o desembolso.revertido. |
| version_esquema | VARCHAR(10), DEF v1 | Versión del contrato del mensaje. |
| payload | JSON, NOT NULL | Mensaje publicado hacia Cobranza (14). |
| estado | ENUM, DEF PENDIENTE | PENDIENTE, ENVIADO, CONFIRMADO o FALLIDO. |
| intentos | SMALLINT UNSIGNED | Número de intentos de entrega realizados. |
| siguiente_intento | DATETIME, NULL | Momento del próximo reintento. |
| confirmacion_id | VARCHAR(60), NULL | Acuse de recibo devuelto por Cobranza. |
| ultimo_error | VARCHAR(255), NULL | Último error de entrega registrado. |
| creado_en | TIMESTAMP, DEF NOW | Creación del evento. |
| actualizado_en | TIMESTAMP, ON UPDATE | Último cambio de estado. |

4.4. Tabla des_auditoria
Bitácora de solo inserción. El usuario de aplicación recibe permisos INSERT y SELECT, nunca UPDATE ni DELETE, de modo que el registro no pueda alterarse desde el servicio.

| Columna | Tipo y restricciones | Descripción |
| id | BIGINT UNSIGNED, PK AI | Correlativo interno de la bitácora. |
| orden_id | CHAR(36), NULL | Orden afectada, si la acción corresponde a una. |
| actor_id | VARCHAR(40), NOT NULL | Usuario o servicio que ejecuta la acción. |
| accion | VARCHAR(60), NOT NULL | PREPARAR, VALIDAR, CONFIRMAR, CONSULTAR o REVERTIR. |
| resultado | VARCHAR(40), NOT NULL | Resultado de la acción registrada. |
| correlation_id | CHAR(36), NOT NULL | Correlación con la traza del Bus. |
| ip | VARCHAR(45), NULL | Dirección de origen, admite IPv6. |
| detalle | JSON, NULL | Datos enmascarados, sin secretos ni cuentas completas. |
| creado_en | TIMESTAMP(3), DEF NOW | Marca con precisión de milisegundos. |

4.5. Tabla des_solicitud_reversion
Registra las solicitudes de reversión. La política que las autoriza permanece pendiente de aprobación del Comité de Créditos, por lo que la tabla queda preparada pero sin uso en la Fase I.

| Columna | Tipo y restricciones | Descripción |
| id | CHAR(36), PK | Identificador de la solicitud. |
| orden_id | CHAR(36), FK des_orden | Orden cuyo desembolso se desea revertir. |
| motivo | VARCHAR(255), NOT NULL | Motivo declarado por el solicitante. |
| solicitante_id | VARCHAR(40), NOT NULL | Usuario que solicita la reversión. |
| autorizacion_id | VARCHAR(60), NULL | Referencia de autorización de Seguridad (9). |
| estado | ENUM, DEF SOLICITADA | SOLICITADA, AUTORIZADA, CONFIRMADA o RECHAZADA. |
| idempotency_key | CHAR(36), UK | Clave propia de la reversión. |
| core_reversion_id | VARCHAR(40), NULL | Operación de reversión registrada por el Core. |
| creado_en | TIMESTAMP, DEF NOW | Creación de la solicitud. |
| actualizado_en | TIMESTAMP, ON UPDATE | Último cambio de estado. |

5. Catálogos de valores

| Columna | Valores admitidos |
| des_orden.estado | PREPARADA, VALIDADA, EN_PROCESO, POR_VERIFICAR, CONFIRMADA, RECHAZADA, REVERTIDA |
| des_orden.entrega_estado | PENDIENTE, CONFIRMADA |
| des_orden.canal | AGENCIA, HOME_BANKING |
| des_orden.moneda | PEN, USD |
| des_validacion.tipo | IDENTIDAD, CUENTA, AUTORIZACION, ANTIFRAUDE |
| des_validacion.resultado | APROBADA, RECHAZADA |
| des_evento_entrega.estado | PENDIENTE, ENVIADO, CONFIRMADO, FALLIDO |
| des_solicitud_reversion.estado | SOLICITADA, AUTORIZADA, CONFIRMADA, RECHAZADA |

5.1. Ciclo de estados de la orden
Figura 2. Transiciones válidas de la columna estado.
El estado POR_VERIFICAR es el punto clave del modelo. Cuando el módulo pierde la respuesta del Core no asume que la operación falló: la orden queda en ese estado y un proceso de recuperación consulta el resultado por la misma referencia. La columna entrega_estado es independiente, porque una falla de entrega a Cobranza no convierte un desembolso confirmado en rechazado.
6. Referencias hacia otros módulos
Figura 3. Identificadores externos que el módulo almacena como referencia lógica.

| Columna | Módulo propietario | Dato que se espera recibir |
| aprobacion_id | Evaluación (12) | Identificador y versión de la aprobación del crédito. |
| credito_id | Solicitud de Crédito (11) | Identificador del crédito y sus condiciones. |
| cliente_id | Clientes (2) | Identificador del titular validado. |
| cuenta_id | Cuentas (3) | Identificador de la cuenta destino elegible. |
| core_operacion_id | Core (1) | Identificador de la operación financiera confirmada. |
| autorizacion_id | Seguridad (9) | Referencia de autorización y control antifraude. |

Ninguna de estas columnas lleva FOREIGN KEY. El módulo no consulta tablas ajenas: obtiene y verifica estos identificadores llamando a los servicios correspondientes a través del Bus. Por esa razón los tipos se declaran como VARCHAR(36) y no como CHAR(36): el formato definitivo de cada identificador depende de la convención que fije el Comité de Tecnología.
7. Restricciones e índices

| Nombre | Tipo | Propósito |
| uk_orden_idempotency | UNIQUE | Una misma clave de idempotencia no crea dos órdenes. |
| uk_orden_credito_confirmado | UNIQUE | Sobre columna generada: un solo desembolso confirmado por crédito. |
| uk_orden_codigo | UNIQUE | Correlativo legible irrepetible. |
| ck_orden_importe | CHECK | El importe debe ser mayor que cero. |
| ck_orden_moneda | CHECK | Solo se admiten PEN y USD. |
| idx_orden_estado | ÍNDICE | Recuperación de órdenes inciertas por estado y fecha. |
| idx_orden_entrega | ÍNDICE | Búsqueda de entregas pendientes hacia Cobranza. |
| idx_evento_pendientes | ÍNDICE | Selección de eventos a reintentar por el proceso de entrega. |
| idx_auditoria_correlation | ÍNDICE | Reconstrucción de una operación completa desde la traza. |

La restricción uk_orden_credito_confirmado merece atención: se apoya en una columna generada que solo toma el valor de credito_id cuando el estado es CONFIRMADA y es NULL en cualquier otro caso. Como MySQL permite múltiples NULL en un índice único, el efecto neto es que pueden existir varias órdenes preparadas o rechazadas para el mismo crédito, pero solo una confirmada. Este es el control de duplicidad del lado del módulo; el control definitivo permanece en el Core.
8. Vistas de apoyo operativo

| Vista | Uso previsto |
| des_v_ordenes_inciertas | Alimenta el proceso de recuperación que consulta el resultado al Core. |
| des_v_entregas_pendientes | Monitoreo de entregas a Cobranza que superan la política de reintentos. |
| des_v_conciliacion_diaria | Base para cuadrar operaciones e importes por fecha y moneda contra el Core. |

9. Reglas que el modelo impone
•	Una solicitud repetida con la misma clave de idempotencia no genera una segunda orden; la restricción única la rechaza en la base de datos, no solo en el código.
•	Un crédito no puede tener dos desembolsos confirmados de forma simultánea, ni siquiera bajo escritura concurrente.
•	El resultado financiero nunca se deduce de un tiempo de espera agotado. El estado POR_VERIFICAR obliga a consultar al Core antes de tomar otra acción.
•	La entrega a Cobranza se modela como bandeja de salida con reintento, de modo que la indisponibilidad del módulo destino no afecta la consistencia del desembolso.
•	La bitácora es de solo inserción. El servicio no recibe permisos para modificarla ni borrarla.
•	El módulo no guarda huellas ni imágenes faciales, únicamente la referencia de evidencia que devuelve el módulo de Clientes.
10. Solicitudes a los módulos de Core, Bus e Infraestructura

| Destinatario | Solicitud |
| Core (1) | Confirmar si el abono y el asiento se registran en una sola transacción y entregar el formato definitivo de core_operacion_id y de la fecha efectiva. |
| Core (1) | Definir el plan de cuentas contables aplicable al desembolso de créditos. |
| Bus de Servicios (8) | Fijar el nombre de las cabeceras de correlación e idempotencia y el formato del sobre de eventos y de los errores. |
| Bus de Servicios (8) | Indicar si ofrece mensajería con acuse; de lo contrario la entrega a Cobranza se realiza por llamada idempotente con reintento. |
| Infraestructura | Confirmar versión de MySQL, juego de caracteres del servidor, zona horaria y si cada módulo tendrá esquema propio o uno compartido. |
| Infraestructura | Crear el usuario de aplicación con permisos INSERT y SELECT sobre des_auditoria, sin UPDATE ni DELETE. |
| Clientes (2) y Cuentas (3) | Entregar el formato de cliente_id y cuenta_id para fijar longitud y tipo definitivos de esas columnas. |

11. Archivos que acompañan a este documento

| Archivo | Contenido |
| desembolso_modelo_bd.sql | Script DDL completo para MySQL 8: cinco tablas, tres vistas y una fila de ejemplo para el ambiente de Desarrollo. |
| desembolso_models.py | Modelos SQLAlchemy 2.0 y esquemas Pydantic v2 equivalentes, para el servicio FastAPI del módulo. |

El script se ejecuta sobre una base vacía sin dependencias de otros módulos. Las tablas no referencian objetos externos, de modo que puede cargarse en cualquier orden respecto de los demás módulos.

