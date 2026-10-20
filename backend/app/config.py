"""Configuracion por ambiente (variables de entorno o archivo .env)."""
from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ambiente: str = "desarrollo"
    database_url: str = "mysql+pymysql://root@127.0.0.1:3306/bna"
    bus_base_url: str = "http://127.0.0.1:9000"
    cors_origenes: str = "http://localhost:3000"

    # Seguridad (OAuth2 / JWT emitido por el modulo de Seguridad)
    jwt_emisor: str = "bna-seguridad"
    jwt_audiencia: str = "bna-api"
    servicio_cliente_id: str = "desembolso-svc"
    servicio_cliente_secreto: str = "desembolso-dev-secret"

    # Integracion (RT-04)
    timeout_dependencia_seg: float = 3.0
    timeout_abono_seg: float = 3.0
    reintentos_consulta: int = 2

    # Recuperacion de ordenes inciertas (RN-07, RT-06)
    recuperacion_intervalo_seg: float = 10.0
    recuperacion_espera_seg: float = 30.0
    recuperacion_gracia_seg: float = 120.0
    alerta_incierta_min: float = 15.0

    # Entrega a Cobranza (RN-08)
    entrega_intervalo_seg: float = 5.0
    entrega_max_intentos: int = 10
    entrega_backoff_base_seg: float = 5.0
    entrega_backoff_max_seg: float = 900.0

    # Reglas configurables
    validacion_vigencia_min: int = 30
    antifraude_habilitado: bool = True
    reversion_habilitada: bool = False
    reversion_plazo_horas: int = 24

    trabajos_habilitados: bool = True

    @cached_property
    def jwks_url(self) -> str:
        return f"{self.bus_base_url}/seguridad/v1/jwks.json"
