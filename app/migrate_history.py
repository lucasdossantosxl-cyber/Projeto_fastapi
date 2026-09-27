"""Importação explícita: python -m app.migrate_history [arquivo.txt]."""

import argparse
import hashlib
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import HistoryIOError
from app.services.history_service import database, initialize_database


def migrate_history(source: Path) -> int:
    """Importa um snapshot uma vez, preservando duplicatas legítimas e o TXT."""
    try:
        raw = source.read_bytes()
        lines = raw.decode("utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValueError("Não foi possível ler o TXT em UTF-8") from exc
    if len(lines) % 4:
        raise ValueError("TXT inválido: cada registro precisa de quatro linhas")
    rows: list[tuple[str, str, str]] = []
    prefixes = ("Original: ", "Gritando: ", "Sussurrando: ")
    for offset in range(0, len(lines), 4):
        block = lines[offset : offset + 4]
        if block[3] != "-" * 30 or any(
            not line.startswith(prefix) for line, prefix in zip(block[:3], prefixes, strict=True)
        ):
            raise ValueError(f"TXT inválido no registro {offset // 4 + 1}")
        rows.append(
            (
                block[0][len(prefixes[0]) :],
                block[1][len(prefixes[1]) :],
                block[2][len(prefixes[2]) :],
            )
        )

    digest = hashlib.sha256(raw).hexdigest()
    identity = str(source.resolve())
    initialize_database()
    with database() as connection:
        # Serializa a verificação e a inserção, inclusive entre dois processos.
        connection.execute("BEGIN IMMEDIATE")
        previous = connection.execute(
            "SELECT digest FROM legacy_imports WHERE source = ?", (identity,)
        ).fetchone()
        if previous and previous[0] != digest:
            raise ValueError("Este TXT mudou após a importação; use o snapshot original")
        if connection.execute(
            "SELECT 1 FROM legacy_imports WHERE digest = ?", (digest,)
        ).fetchone():
            return 0
        connection.executemany(
            "INSERT INTO advice (original, gritando, sussurrando, fetched_at) "
            "VALUES (?, ?, ?, NULL)",
            rows,
        )
        connection.execute("INSERT INTO legacy_imports VALUES (?, ?)", (identity, digest))
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Importa o histórico TXT para SQLite sem apagá-lo")
    parser.add_argument("source", nargs="?", type=Path, default=settings.HISTORICO_PATH)
    args = parser.parse_args()
    try:
        count = migrate_history(args.source)
    except (ValueError, HistoryIOError) as exc:
        parser.exit(1, f"Erro: {exc}\n")
    print(f"{count} registro(s) importado(s). O arquivo original foi preservado.")


if __name__ == "__main__":
    main()
