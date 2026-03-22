from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Config
    PROJECT_NAME: str = "SRE-Observability-Incident-Readiness"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # DB Config
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/sre_db"
    
    # Security Config
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_CHANGE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Observability Config
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://tempo:4317"
    
    # Failure Injection
    FAILURE_LATENCY_PROBABILITY: float = 0.0
    FAILURE_ERROR_PROBABILITY: float = 0.0

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
