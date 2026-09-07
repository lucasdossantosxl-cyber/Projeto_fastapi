"""Service layer: persist and retrieve advice history."""

from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.core.exceptions import HistoryIOError
from app.core.logging import get_logger
from app.models.advice import AdviceResponse, HistoryEntry

logger = get_logger(__name__)


def _ensure_history_file() -> Path:
    """Return the history file path, creating parent dirs if needed."""
    path = settings.HISTORICO_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def save_to_history(entry: AdviceResponse) -> None:
    """Append an advice entry to the history file.

    Raises:
        HistoryIOError: if the file cannot be written.
    """
    path = _ensure_history_file()
    history_entry = HistoryEntry(
        original=entry.original,
        gritando=entry.gritando,
        sussurrando=entry.sussurrando,
        fetched_at=entry.fetched_at,
    )

    try:
        with path.open("a", encoding="utf-8") as f:
            f.write(history_entry.to_file_format())
        logger.info("History saved", extra={"file": str(path)})
    except OSError as exc:
        logger.exception("Failed to write history file")
        raise HistoryIOError(f"Erro ao salvar histórico: {exc}") from exc


def read_history(last: int = 15) -> str:
    """Read the last *last* lines from the history file.

    Returns:
        The raw file content (or a friendly message if empty).
    """
    path = settings.HISTORICO_PATH

    if not path.exists():
        return "(sem histórico ainda)"

    try:
        with path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        logger.exception("Failed to read history file")
        raise HistoryIOError(f"Erro ao ler histórico: {exc}") from exc

    # Each entry is 4 lines (3 data + 1 separator)
    lines_per_entry = 4
    total_lines = last * lines_per_entry
    snippet = "".join(lines[-total_lines:]) if lines else "(sem histórico ainda)"
    return snippet
