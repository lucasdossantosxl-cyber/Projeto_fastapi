"""Tests for the history endpoint and service."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_history_file(tmp_path: Path) -> None:
    """Use a temporary history file for every test."""
    original = settings.HISTORICO_PATH
    settings.HISTORICO_PATH = tmp_path / "test_historico.txt"
    yield
    settings.HISTORICO_PATH = original


def test_get_history_empty() -> None:
    response = client.get("/historico")
    assert response.status_code == 200
    assert response.json()["content"] == "(sem histórico ainda)"


def test_get_history_with_entries() -> None:
    # Seed the history file with 2 entries
    content = (
        "Original: First advice\n"
        "Gritando: FIRST ADVICE\n"
        "Sussurrando: first advice\n"
        "------------------------------\n"
        "Original: Second advice\n"
        "Gritando: SECOND ADVICE\n"
        "Sussurrando: second advice\n"
        "------------------------------\n"
    )
    settings.HISTORICO_PATH.write_text(content, encoding="utf-8")

    response = client.get("/historico?last=1")
    assert response.status_code == 200
    assert "Second advice" in response.json()["content"]
    assert "First advice" not in response.json()["content"]


def test_get_history_invalid_last() -> None:
    response = client.get("/historico?last=0")
    assert response.status_code == 422  # validation error

    response = client.get("/historico?last=101")
    assert response.status_code == 422
