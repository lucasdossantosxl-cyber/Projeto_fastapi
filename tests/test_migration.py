import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from app.core.config import settings
from app.migrate_history import migrate_history
from app.services.history_service import initialize_database, read_history

ENTRY = "Original: Kind\nGritando: KIND\nSussurrando: kind\n" + "-" * 30 + "\n"


def test_migration_preserves_duplicates_and_source(tmp_path: Path) -> None:
    source = tmp_path / "legacy.txt"
    source.write_text(ENTRY * 2, encoding="utf-8")
    assert migrate_history(source) == 2
    assert migrate_history(source) == 0
    copy = tmp_path / "copy.txt"
    copy.write_bytes(source.read_bytes())
    assert migrate_history(copy) == 0
    assert source.read_text() == ENTRY * 2
    assert read_history(2) == ENTRY * 2
    with sqlite3.connect(settings.DATABASE_PATH) as db:
        assert db.execute("SELECT fetched_at FROM advice").fetchall() == [(None,), (None,)]


def test_changed_import_rejected(tmp_path: Path) -> None:
    source = tmp_path / "legacy.txt"
    source.write_text(ENTRY)
    migrate_history(source)
    source.write_text(ENTRY * 2)
    with pytest.raises(ValueError, match="mudou"):
        migrate_history(source)
    assert read_history(10) == ENTRY


@pytest.mark.parametrize("content", [ENTRY + "broken", "wrong\n" * 4, ENTRY + "wrong\n" * 4])
def test_invalid_file_is_not_partially_imported(tmp_path: Path, content: str) -> None:
    initialize_database()
    source = tmp_path / "bad.txt"
    source.write_text(content)
    with pytest.raises(ValueError):
        migrate_history(source)
    assert read_history() == "(sem histórico ainda)"


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="ler"):
        migrate_history(tmp_path / "missing.txt")


def test_concurrent_migration(tmp_path: Path) -> None:
    source = tmp_path / "legacy.txt"
    source.write_text(ENTRY)
    initialize_database()
    with ThreadPoolExecutor(max_workers=2) as pool:
        counts = list(pool.map(migrate_history, [source, source]))
    assert sorted(counts) == [0, 1]
    assert read_history(10) == ENTRY
