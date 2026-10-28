from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg2://soc_lite:soc_lite_local_only@postgres:5432/soc_lite'
    jwt_secret: str = 'cambia-esta-clave-local'
    jwt_algorithm: str = 'HS256'
    access_token_minutes: int = 120
    service_api_key: str = 'soc-lite-service-local'
    cors_origins: str = 'http://localhost:5173'
    triage_url: str = 'http://triage:8001'
    demo_mode: bool = True

    @property
    def cors_list(self): return [x.strip() for x in self.cors_origins.split(',') if x.strip()]

settings = Settings()
