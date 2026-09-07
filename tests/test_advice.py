"""Tests for the advice endpoint and service."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.main import app

client = TestClient(app)


@pytest.mark.anyio
async def test_get_advice_success(mocker: pytest.MockFixture) -> None:
    """Happy path: external API returns valid advice."""
    mock_resp = Response(200, json={"slip": {"advice": "Always be kind."}})
    mocker.patch("httpx.AsyncClient.get", return_value=mock_resp)

    response = client.get("/advice?save=false")
    assert response.status_code == 200

    data = response.json()
    assert data["original"] == "Always be kind."
    assert data["gritando"] == "ALWAYS BE KIND."
    assert data["sussurrando"] == "always be kind."
    assert "fetched_at" in data


@pytest.mark.anyio
async def test_get_advice_external_api_down(mocker: pytest.MockFixture) -> None:
    """External API returns 500."""
    mock_resp = Response(500, text="Internal Server Error")
    mocker.patch("httpx.AsyncClient.get", return_value=mock_resp)

    response = client.get("/advice?save=false")
    assert response.status_code == 500
    assert "API externa" in response.json()["detail"]


@pytest.mark.anyio
async def test_get_advice_malformed_json(mocker: pytest.MockFixture) -> None:
    """External API returns JSON without expected keys."""
    mock_resp = Response(200, json={"unexpected": "shape"})
    mocker.patch("httpx.AsyncClient.get", return_value=mock_resp)

    response = client.get("/advice?save=false")
    assert response.status_code == 502
    assert "Resposta inesperada" in response.json()["detail"]
