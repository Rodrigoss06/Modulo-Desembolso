"""Regenera sql/99_bna_unificado.sql concatenando los scripts 01 a 13 en orden.

Uso:  python database/generar_unificado.py
Ejecutar cada vez que se modifique cualquiera de los scripts 01-13.
"""
from datetime import date
from pathlib import Path

SQL_DIR = Path(__file__).resolve().parent / "sql"
SALIDA = SQL_DIR / "99_bna_unificado.sql"

ENCABEZADO = f"""-- =====================================================================
-- BNA - BASE DE DATOS UNIFICADA (TODO EN UNO)
-- Generado: {date.today().isoformat()}  |  MySQL 8.0/8.4  |  InnoDB  |  utf8mb4
-- Generado por database/generar_unificado.py: NO editar a mano.
-- NOTA: elimina y recrea la base bna para una carga limpia.
-- IDs: UUID v7 (CHAR(36)) en todas las claves primarias y foraneas.
-- =====================================================================
"""


def main() -> None:
    scripts = sorted(p for p in SQL_DIR.glob("[0-9][0-9]_*.sql") if not p.name.startswith("99_"))
    partes = [ENCABEZADO]
    for script in scripts:
        contenido = script.read_text(encoding="utf-8").replace("\r\n", "\n").rstrip("\n")
        partes.append(f"-- >>> INICIO {script.name}\n{contenido}\n\n-- <<< FIN {script.name}\n\n")
    SALIDA.write_text("".join(partes), encoding="utf-8", newline="\n")
    print(f"{SALIDA.name} regenerado con {len(scripts)} scripts")


if __name__ == "__main__":
    main()
