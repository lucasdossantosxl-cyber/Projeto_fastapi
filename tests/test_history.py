import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_application
from app.models.advice import AdviceResponse
from app.services.history_service import save_to_history


def test_history_empty(client: TestClient) -> None:
    assert client.get("/historico").json() == {"last": 15, "content": "(sem histórico ainda)"}


def test_history_limit_order_and_persistence(client: TestClient) -> None:
    for text in ["First", "Second", "Third"]:
        save_to_history(AdviceResponse.from_raw_text(text))
    with TestClient(create_application()) as restarted:
        response = restarted.get("/historico?last=2")
    assert response.status_code == 200
    content = response.json()["content"]
    assert "First" not in content
    assert content.index("Second") < content.index("Third")
    with sqlite3.connect(settings.DATABASE_PATH) as db:
        rows = db.execute("SELECT id, fetched_at FROM advice").fetchall()
    assert len(rows) == 3
    assert all(timestamp.endswith("+00:00") for _, timestamp in rows)


@pytest.mark.parametrize("last", ["0", "101", "-1", "abc", "1.5"])
def test_invalid_last(client: TestClient, last: str) -> None:
    assert client.get(f"/historico?last={last}").status_code == 422


@pytest.mark.parametrize("last", [1, 100])
def test_valid_boundaries(client: TestClient, last: int) -> None:
    assert client.get(f"/historico?last={last}").status_code == 200


def test_multiline_and_sql_text(client: TestClient) -> None:
    text = "Hello\nworld'); DROP TABLE advice;--"
    save_to_history(AdviceResponse.from_raw_text(text))
    assert text in client.get("/historico?last=1").json()["content"]
    assert client.get("/advice").status_code == 200


@pytest.mark.parametrize("route", ["/historico", "/advice"])
def test_storage_error(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, route: str
) -> None:
    blocker = tmp_path / "file_instead_of_directory"
    blocker.write_text("blocked")
    monkeypatch.setattr(settings, "DATABASE_PATH", blocker / "db.sqlite")
    response = client.get(route)
    assert response.status_code == 500
    assert response.json() == {"detail": "Não foi possível acessar o histórico"}
    assert str(blocker) not in response.text
