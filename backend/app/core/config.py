from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+psycopg://continuum@localhost:5434/continuum"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    BUSINESS_TIMEZONE: str = "America/New_York"
    BUSINESS_HOURS_START: str = "09:00"
    BUSINESS_HOURS_END: str = "17:00"
    INACTIVITY_THRESHOLD_DAYS: int = 90
    AS_OF_DATE: str = "2026-10-31"

    DATA_SEED: int = 20270101
    DATASET_SCALE: str = "full"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
