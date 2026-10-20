"""Datos sinteticos del simulador. Ningun dato corresponde a personas reales."""
from decimal import Decimal

CLIENTES = {
    "CLI-0001": {"nombre": "Ana Lucía Quispe Mamani", "documento": "70000001"},
    "CLI-0002": {"nombre": "Luis Alberto Huamán Condori", "documento": "70000002"},
    "CLI-0003": {"nombre": "Rosa Elena Ccama Apaza", "documento": "70000003"},
    "CLI-0004": {"nombre": "Jorge Luis Puma Vilca", "documento": "70000004"},
    "CLI-0005": {"nombre": "María Fernanda Choque Torres", "documento": "70000005"},
    "CLI-0006": {"nombre": "Pedro Pablo Mamani Ríos", "documento": "70000006"},
    "CLI-0007": {"nombre": "Carmen Rosa Flores Sucasaire", "documento": "70000007"},
    "CLI-0008": {"nombre": "Víctor Hugo Zapana Larico", "documento": "70000008"},
}

# comportamiento: como responde Cuentas al abono de ese credito.
APROBACIONES = [
    {"aprobacion_id": "APR-2026-0001", "credito_id": "CRE-2026-0001", "cliente_id": "CLI-0001",
     "producto": "Crédito Personal", "importe": Decimal("10000.00"), "moneda": "PEN",
     "plazo_meses": 24, "tasa_tea": "22.00", "estado": "HABILITADA", "dias_vigencia": 25},
    {"aprobacion_id": "APR-2026-0002", "credito_id": "CRE-2026-0002", "cliente_id": "CLI-0002",
     "producto": "Crédito Vehicular", "importe": Decimal("5000.00"), "moneda": "USD",
     "plazo_meses": 36, "tasa_tea": "14.50", "estado": "HABILITADA", "dias_vigencia": 20},
    {"aprobacion_id": "APR-2026-0003", "credito_id": "CRE-2026-0003", "cliente_id": "CLI-0003",
     "producto": "Crédito Personal", "importe": Decimal("3500.00"), "moneda": "PEN",
     "plazo_meses": 12, "tasa_tea": "28.00", "estado": "VENCIDA", "dias_vigencia": -3},
    {"aprobacion_id": "APR-2026-0004", "credito_id": "CRE-2026-0004", "cliente_id": "CLI-0004",
     "producto": "Crédito MYPE", "importe": Decimal("15000.00"), "moneda": "PEN",
     "plazo_meses": 18, "tasa_tea": "24.50", "estado": "REVOCADA", "dias_vigencia": 10},
    {"aprobacion_id": "APR-2026-0005", "credito_id": "CRE-2026-0005", "cliente_id": "CLI-0005",
     "producto": "Crédito MYPE", "importe": Decimal("25000.00"), "moneda": "PEN",
     "plazo_meses": 36, "tasa_tea": "21.00", "estado": "HABILITADA", "dias_vigencia": 28,
     "comportamiento": "TIMEOUT_REGISTRADO"},
    {"aprobacion_id": "APR-2026-0006", "credito_id": "CRE-2026-0006", "cliente_id": "CLI-0006",
     "producto": "Crédito Personal", "importe": Decimal("8000.00"), "moneda": "PEN",
     "plazo_meses": 24, "tasa_tea": "23.00", "estado": "HABILITADA", "dias_vigencia": 15,
     "comportamiento": "RECHAZO"},
    {"aprobacion_id": "APR-2026-0007", "credito_id": "CRE-2026-0007", "cliente_id": "CLI-0007",
     "producto": "Crédito Personal", "importe": Decimal("6000.00"), "moneda": "PEN",
     "plazo_meses": 12, "tasa_tea": "26.00", "estado": "HABILITADA", "dias_vigencia": 18},
    {"aprobacion_id": "APR-2026-0008", "credito_id": "CRE-2026-0008", "cliente_id": "CLI-0008",
     "producto": "Crédito Personal", "importe": Decimal("12000.00"), "moneda": "PEN",
     "plazo_meses": 30, "tasa_tea": "21.50", "estado": "HABILITADA", "dias_vigencia": 22},
]

CUENTAS = [
    {"cuenta_id": "CTA-0001", "cliente_id": "CLI-0001", "numero": "21500012344521", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0002", "cliente_id": "CLI-0001", "numero": "21500087657730", "producto": "Ahorro Dólares", "moneda": "USD", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0003", "cliente_id": "CLI-0001", "numero": "21500011119812", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "BLOQUEADA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0004", "cliente_id": "CLI-0001", "numero": "21500033336019", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "MANCOMUNADA"},
    {"cuenta_id": "CTA-0005", "cliente_id": "CLI-0002", "numero": "21500055558841", "producto": "Ahorro Dólares", "moneda": "USD", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0006", "cliente_id": "CLI-0002", "numero": "21500066663307", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0007", "cliente_id": "CLI-0003", "numero": "21500077771145", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0008", "cliente_id": "CLI-0004", "numero": "21500088882290", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0009", "cliente_id": "CLI-0005", "numero": "21500099995563", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0010", "cliente_id": "CLI-0006", "numero": "21500010106678", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0011", "cliente_id": "CLI-0007", "numero": "21500011117734", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0012", "cliente_id": "CLI-0008", "numero": "21500012128856", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
    {"cuenta_id": "CTA-0013", "cliente_id": "CLI-0008", "numero": "21500013134402", "producto": "Ahorro Soles", "moneda": "PEN", "estado": "ACTIVA", "titularidad": "INDIVIDUAL"},
]

# Clientes cuya validacion de identidad se rechaza.
IDENTIDAD_RECHAZADA = {"CLI-0007"}

# Usuarios de desarrollo emitidos por el simulador de Seguridad (contrasena: Demo2026!).
LEER, EJECUTAR = "DESEMBOLSO_LEER", "DESEMBOLSO_EJECUTAR"
USUARIOS = {
    "operador1": {"nombre": "Carla Medina", "rol": "OPERADOR_AGENCIA", "permisos": [LEER, EJECUTAR]},
    "operador2": {"nombre": "Diego Paredes", "rol": "OPERADOR_AGENCIA", "permisos": [LEER, EJECUTAR]},
    "supervisor1": {"nombre": "Lucía Torres", "rol": "SUPERVISOR", "permisos": [LEER, EJECUTAR]},
    "supervisor2": {"nombre": "Martín Salas", "rol": "SUPERVISOR", "permisos": [LEER, EJECUTAR]},
    "auditor1": {"nombre": "Patricia Nina", "rol": "AUDITOR", "permisos": [LEER]},
}
CONTRASENA_DEMO = "Demo2026!"
AGENCIA = {"agencia_id": "0198b000-0000-7001-8000-000000000001", "agencia_nombre": "Agencia Arequipa Centro"}

CLIENTES_SERVICIO = {"desembolso-svc": "desembolso-dev-secret"}
