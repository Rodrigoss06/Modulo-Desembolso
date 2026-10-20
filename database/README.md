# Base de datos — BNA unificada + módulo Desembolso

Copia de la base unificada del repositorio del proyecto
(`SantiagoCusirramos/Banco_Nacional_Arequipa`, carpeta `backend/Trabajo_hecho`,
commit `ab6a6ec` del 16/10/2026), con el **script 08 reemplazado** por el modelo
referencial del módulo de Desembolso y ajustes menores.

- **Motor:** MySQL 8.0 / 8.4 · InnoDB · utf8mb4 / utf8mb4_0900_ai_ci
- **Base:** `bna`
- **Claves:** UUID v7 en `CHAR(36)`, generados por la aplicación.

## Qué es propiedad del módulo

El módulo 13 **solo es dueño de las tablas `des_*`** (script `08_desembolso.sql`).
Las demás tablas (clientes, cuentas, evaluación, cobranza…) pertenecen a otros
módulos y se incluyen como contexto del BNA. **El código del módulo nunca las lee
ni las escribe** (principio PA-04, acuerdo AC-40): esos datos se obtienen por API
a través del Bus de Servicios (en desarrollo, mediante simuladores).

| Tabla | Responsabilidad |
|---|---|
| `des_orden` | Intención, ejecución y resultado del desembolso |
| `des_validacion` | Evidencia de aprobación, identidad, cuenta, autorización y antifraude |
| `des_evento_entrega` | Outbox hacia Cobranza con reintentos |
| `des_auditoria` | Bitácora de solo inserción |
| `des_solicitud_reversion` | Reversiones (política pendiente; deshabilitada por defecto) |
| `des_correlativo` | Correlativo anual del código `DES-AAAA-NNNNNN` |

Vistas: `des_v_ordenes_inciertas`, `des_v_entregas_pendientes`, `des_v_conciliacion_diaria`.
Triggers: `trg_des_orden_bu` (máquina de estados e inmutabilidad financiera),
`trg_des_auditoria_bu` y `trg_des_auditoria_bd` (bitácora inalterable).

## Cambios respecto de la base copiada

| # | Cambio | Motivo |
|---|---|---|
| 1 | `08_desembolso.sql` reescrito según el Modelo Referencial v1.0 del equipo | El script anterior no tenía idempotencia, outbox, estado incierto ni entrega independiente |
| 2 | Sin FK hacia tablas de otros módulos; ids externos como referencias lógicas | PA-04 y AC-40: no acceder a tablas ajenas |
| 3 | `credito_confirmado` → `credito_en_ejecucion` (UNIQUE) cubre EN_PROCESO, POR_VERIFICAR, CONFIRMADA y REVERTIDA | Con solo CONFIRMADA, dos órdenes podían llegar a Cuentas a la vez y duplicar el abono (RN-05) |
| 4 | `core_operacion_id` → `operacion_financiera_id`; `core_reversion_id` → `reversion_financiera_id` | Fase II: el abono se solicita a Cuentas por CR-INT-05; el ejecutor final (Cuentas o CORE) sigue pendiente |
| 5 | `cuenta_id` admite NULL mientras la orden está PREPARADA | La cuenta se elige y valida después de crear la orden (CU-02) |
| 6 | `des_validacion` agrega tipo `APROBACION` y columna `fase` | Evidencia de la revalidación en la frontera de ejecución (RN-06) |
| 7 | Reversión: estados `EN_PROCESO`/`POR_VERIFICAR`, `origen`, `autorizador_id` distinto del solicitante, una activa por orden | El resultado incierto aplica también al extorno (RN-07); AC-44; control de cuatro ojos |
| 8 | Nueva tabla `des_correlativo` | Generar `codigo_orden` sin carreras |
| 9 | Triggers de estados e inmutabilidad, y bitácora de solo inserción | Defensa en profundidad además del código |
| 10 | Vistas `des_v_*` movidas de `11_vistas.sql` a `08_desembolso.sql` | El script 08 queda autocontenido |
| 11 | Ejemplo de Desembolso en `13_consultas.sql` actualizado al nuevo modelo | Recorre PREPARADA → CONFIRMADA |
| 12 | `cargar_bna.ps1` apuntaba a una ruta inexistente; conteos de `verificar_bna.ps1` y rutas personales de la guía corregidos | Errores de la copia original |

## Cargar la base

Guía paso a paso y solución de problemas: [`GUIA_EJECUCION.md`](GUIA_EJECUCION.md).

```powershell
cd database
.\iniciar_mysql.ps1     # si MySQL no corre como servicio
.\cargar_bna.ps1        # borra y recrea bna con sql\99_bna_unificado.sql
.\verificar_bna.ps1     # esperado: 67 tablas, 9 vistas, 10 triggers, 3 routines, 1 evento
```

Solo el módulo (base vacía, sin el resto del BNA):

```powershell
mysql -u root -e "CREATE DATABASE IF NOT EXISTS bna CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
cmd /c 'mysql -u root < sql\08_desembolso.sql'
```

## Mantenimiento

- Tras modificar cualquier script 01–13: `python database/generar_unificado.py`
  regenera `sql/99_bna_unificado.sql` (no editarlo a mano).
- Usuario de aplicación de mínimo privilegio: `usuario_app_desembolso.sql`
  (sin DELETE; bitácora solo SELECT/INSERT). Cambiar la contraseña antes de usarlo.
- Diccionario: [`diccionario_datos.md`](diccionario_datos.md) · MER: [`mer_bna.mermaid`](mer_bna.mermaid).

Verificado el 19/10/2026 sobre MySQL 8.4.6: la carga completa termina sin errores
y las restricciones rechazan doble ejecución por crédito, transiciones inválidas,
cambios de importe tras la ejecución, modificación de la bitácora, claves de
idempotencia repetidas y reversiones autorizadas por el propio solicitante.
