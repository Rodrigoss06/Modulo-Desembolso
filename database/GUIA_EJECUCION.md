# Guía de ejecución — Base de datos BNA (MySQL 8.4)

Permite a cualquier integrante crear y cargar la base `bna` desde cero en Windows.

- **Contenido esperado:** 67 tablas, 9 vistas, 10 triggers, 3 routines, 1 evento, 4 agencias (seed).
- `sql/99_bna_unificado.sql` **elimina y recrea** la base en cada carga.
- Todos los comandos se ejecutan desde la carpeta `database/` del repositorio.

## 0. Requisitos

1. MySQL Server 8.4 (ruta por defecto `C:\Program Files\MySQL\MySQL Server 8.4`).
2. PowerShell.
3. Si MySQL no está registrado como servicio: datadir inicializado en
   `C:\ProgramData\MySQL\MySQL Server 8.4\Data` (o pásalo con `-DataDir`).

## 1. Arrancar MySQL

```powershell
.\iniciar_mysql.ps1                       # o: Start-Service MySQL84 si es servicio
Get-Process mysqld                        # comprobar
```

`--datadir` debe ir entre comillas porque la ruta tiene espacios; el script ya lo hace.

## 2. Cargar la base

```powershell
.\cargar_bna.ps1                          # root sin contraseña (desarrollo)
.\cargar_bna.ps1 -Password "miclave"      # root con contraseña
```

Comando manual equivalente (el `cmd /c` es necesario para que `<` funcione en PowerShell):

```powershell
cmd /c '"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root < "sql\99_bna_unificado.sql"'
```

> En MySQL Shell (`mysqlsh`), `\source` no ejecuta bien el `DROP DATABASE`.
> Usa `mysql.exe`, o borra la base a mano antes: `DROP DATABASE IF EXISTS bna;`.

## 3. Verificar

```powershell
.\verificar_bna.ps1
```

| Objeto | Cantidad |
|---|---|
| Tablas | 67 |
| Vistas | 9 |
| Triggers | 10 |
| Routines | 3 |
| Eventos | 1 |
| Agencias (seed) | 4 |

## 4. Detener

```powershell
.\detener_mysql.ps1
```

## 5. Carga por partes (depuración)

Orden de dependencias: `01 → 02 → … → 13`. Solo `01` crea la base; cada script hace `USE bna;`.
`08_desembolso.sql` no depende de ningún otro y puede cargarse solo sobre una base `bna` vacía.

## 6. Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `Can't connect to MySQL server ... (10061)` | El servidor está apagado: paso 1. |
| `Failed to set datadir` | Falta comillas en `--datadir`. Usa `iniciar_mysql.ps1`. |
| `ERROR 1007 ... database exists` | El `DROP` no corrió (típico en mysqlsh). Carga con `mysql.exe`. |
| `ERROR 1644 ... transicion de estado no permitida` | Un `UPDATE` intentó una transición inválida de `des_orden`; es el comportamiento esperado del trigger. |
| `ERROR 1644 ... des_auditoria es de solo insercion` | La bitácora no admite UPDATE/DELETE; es intencional. |
| `ERROR 1062 ... uk_orden_credito_en_ejecucion` | Ya hay una orden en ejecución o confirmada para ese crédito (RN-05). |

## 7. Seguridad

- Los usuarios del seed (`admin123`, etc.) son **de prueba**. No usarlos fuera de desarrollo.
- En Testing/Producción el módulo se conecta con el usuario de `usuario_app_desembolso.sql`
  (contraseña propia, fuera del repositorio).
