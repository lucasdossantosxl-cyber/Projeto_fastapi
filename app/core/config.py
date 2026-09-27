"""Configuração centralizada; valores podem vir do arquivo .env."""

from pathlib import Path

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Gerenciador de Conselhos API"
    APP_VERSION: str = "0.3.0"
    DEBUG: bool = False
    ADVICE_API_URL: HttpUrl = HttpUrl("https://api.adviceslip.com/advice")
    ADVICE_API_TIMEOUT: float = Field(default=5.0, gt=0)
    DATABASE_PATH: Path = Path("data/conselhos.db")
    # Compatibilidade com .env antigo; usado apenas pela migração explícita.
    HISTORICO_PATH: Path = Path("historico_conselhos.txt")
    LOG_LEVEL: str = "INFO"


settings = Settings()
