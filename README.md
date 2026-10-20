# Módulo 13 · Desembolso — Banco Nacional de Arequipa (BNA)

Servicio **SRV-CR-04 · Gestión del Desembolso de Créditos** de la Línea de Créditos del proyecto
integrador BNA (UCSM · Gestión de Sistemas y Tecnologías de la Información, 2026).

Convierte un crédito aprobado por Evaluación en un abono confirmado en la cuenta de ahorros del
titular, previa validación de identidad, y entrega el resultado a Cobranza, con idempotencia,
tratamiento de resultados inciertos y trazabilidad completa.

📄 **Informe técnico:** [`docs/Informe_Tecnico_Modulo_Desembolso.docx`](docs/Informe_Tecnico_Modulo_Desembolso.docx)
([PDF](docs/Informe_Tecnico_Modulo_Desembolso.pdf))

## Estructura

| Carpeta | Contenido |
|---|---|
| `backend/` | API FastAPI del módulo (puerto 8000) y pruebas pytest |
| `simuladores/` | Simulador del Bus de Servicios: Evaluación, Clientes, Cuentas, Cobranza y Seguridad (puerto 9000) |
| `frontend/` | Pantallas de agencia en Next.js (puerto 3000) |
| `database/` | Base BNA unificada con el script `08_desembolso.sql` del módulo |
| `docs/` | Informe técnico, generador, diagramas, capturas y documentos fuente |

## Ejecución local (Windows · PowerShell)

Requisitos: Python 3.11+, Node.js 20+, MySQL 8.4.

```powershell
# 1. Base de datos (crea bna desde cero)
cd database; .\cargar_bna.ps1; cd ..

# 2. Simulador del Bus de Servicios
cd simuladores; python -m venv .venv; .venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn app.main:app --port 9000

# 3. API (otra terminal)
cd backend; python -m venv .venv; .venv\Scripts\pip install -r requirements-dev.txt
copy .env.example .env; .venv\Scripts\uvicorn app.main:app --port 8000

# 4. Frontend (otra terminal)
cd frontend; npm install; copy .env.example .env.local; npm run build; npm start
```

Abrir http://localhost:3000 con `operador1`, `supervisor1` o `auditor1` (contraseña `Demo2026!`,
solo desarrollo). Documentación de la API: http://localhost:8000/docs.

## Pruebas

```powershell
cd backend
$env:DES_TEST_MYSQL = "mysql+pymysql://root@127.0.0.1:3306"   # servidor MySQL 8.4 de pruebas
.venv\Scripts\python -m pytest
```

Las pruebas crean la base `bna_test_desembolso` con `08_desembolso.sql`, levantan el simulador y la
API en hilos y verifican los escenarios de la Fase I: duplicidad, concurrencia, respuesta perdida,
caída de Cobranza, permisos y triggers de integridad.

## Informe

```powershell
python docs/generar_informe.py                            # regenera el .docx sobre la plantilla del curso
powershell -File docs/herramientas/actualizar-informe.ps1 # índice y PDF con Word
cd docs/herramientas; npm install; npm run diagramas      # diagramas Mermaid
npm run capturas                                          # capturas (con el sistema levantado)
```
