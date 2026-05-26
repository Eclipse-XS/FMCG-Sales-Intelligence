from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FSI_", env_file=".env", extra="ignore")
    active_domain_pack: str = "coca_cola_demo"
    artifact_root: str = "artifacts/canonical"
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_required_for_readiness: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
