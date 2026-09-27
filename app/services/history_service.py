"""SQLite síncrono: rotas executam estas funções em threads do FastAPI."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager

from app.core.config import settings
from app.core.exceptions import HistoryIOError
from app.core.logging import get_logger
from app.models.advice import AdviceResponse

logger = get_logger(__name__)


@contextmanager
def database() -> Iterator[sqlite3.Connection]:
    """Transação por operação, fechamento garantido e erros sem dados internos."""
    try:
        settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(settings.DATABASE_PATH, timeout=5)
        try:
            with connection:
                yield connection
        finally:
            connection.close()
    except (OSError, sqlite3.Error) as exc:
        logger.exception("Falha no armazenamento do histórico")
        raise HistoryIOError("Não foi possível acessar o histórico", status_code=500) from exc


def initialize_database() -> None:
    with database() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS advice (
                id INTEGER PRIMARY KEY,
                original TEXT NOT NULL,
                gritando TEXT NOT NULL,
                sussurrando TEXT NOT NULL,
                fetched_at TEXT
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS legacy_imports (
                source TEXT PRIMARY KEY,
                digest TEXT UNIQUE NOT NULL
            )
        """)


def save_to_history(entry: AdviceResponse) -> None:
    with database() as connection:
        connection.execute(
            "INSERT INTO advice (original, gritando, sussurrando, fetched_at) VALUES (?, ?, ?, ?)",
            (entry.original, entry.gritando, entry.sussurrando, entry.fetched_at.isoformat()),
        )


def read_history(last: int = 15) -> str:
    """Seleciona os últimos registros por ID e mantém a apresentação cronológica."""
    if not 1 <= last <= 100:
        raise ValueError("last deve estar entre 1 e 100")
    with database() as connection:
        rows = connection.execute(
            "SELECT original, gritando, sussurrando FROM advice ORDER BY id DESC LIMIT ?",
            (last,),
        ).fetchall()
    return (
        "".join(
            f"Original: {original}\nGritando: {gritando}\nSussurrando: {sussurrando}\n{'-' * 30}\n"
            for original, gritando, sussurrando in reversed(rows)
        )
        or "(sem histórico ainda)"
    )
