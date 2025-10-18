from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    project_name: str = "GeoRag LCT2025"
    api_prefix: str = "/api"
    secret_key: str = Field(
        default="change-me", description="Secret key used for signing JWT tokens."
    )
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    database_url: str = Field(
        default="sqlite:///./georag.db",
        description="SQLAlchemy database URL.",
    )
    storage_dir: Path = Field(
        default=Path("storage"),
        description="Directory on local filesystem where uploaded images are stored.",
    )
    sync_max_images: int = Field(
        default=5,
        description="Maximum number of images processed synchronously before delegating to a background task.",
    )
    default_admin_username: str = "admin"
    default_admin_password: str = "admin123"
    metrics_namespace: str = "georag"
    offline_geocoder_prefix: str = "Mocked address"
    offline_geocoder_city: Optional[str] = "GeoRag City"

    class Config:
        env_prefix = "GEORAG_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
