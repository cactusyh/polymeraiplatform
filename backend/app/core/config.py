"""Environment-based application settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and a local .env file."""

    app_name: str = "Polymer AI Platform"
    app_env: str = "development"
    app_version: str = "0.1.0"
    backend_host: str = "127.0.0.1"
    backend_port: int = 8000
    frontend_origin: str = "http://localhost:3000"
    database_url: str = (
        "postgresql+psycopg://polymer_ai:polymer_ai@localhost:5432/polymer_ai"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
