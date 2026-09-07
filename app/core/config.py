"""Application configuration loaded from environment."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized app settings with env-var overrides."""

    # API
    APP_NAME: str = "Gerenciador de Conselhos API"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = False

    # External API
    ADVICE_API_URL: str = "https://api.adviceslip.com/advice"
    ADVICE_API_TIMEOUT: float = 5.0

    # Persistence
    HISTORICO_PATH: Path = Path(__file__).resolve().parent.parent.parent / "historico_conselhos.txt"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance – import this everywhere
settings = Settings()
