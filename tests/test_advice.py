from collections.abc import AsyncIterator

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_http_client


def test_advice_success_and_optional_save(client: TestClient) -> None:
    response = client.get("/advice?save=false")
    assert response.status_code == 200
    data = response.json()
    assert data["original"] == "Always be kind."
    assert data["gritando"] == "ALWAYS BE KIND."
    assert data["sussurrando"] == "always be kind."
    assert data["fetched_at"].endswith(("Z", "+00:00"))
    assert client.get("/historico").json()["content"] == "(sem histórico ainda)"
    assert client.get("/advice").status_code == 200
    assert "Always be kind." in client.get("/historico").json()["content"]


@pytest.mark.parametrize(
    ("external_response", "status"),
    [
        (httpx.Response(500), 502),
        (httpx.Response(404), 502),
        (httpx.Response(302), 502),
        (httpx.Response(200, content="not json"), 502),
        (httpx.Response(200, json={}), 502),
        (httpx.Response(200, json={"slip": None}), 502),
        (httpx.Response(200, json={"slip": {"advice": None}}), 502),
        (httpx.Response(200, json={"slip": {"advice": 123}}), 502),
        (httpx.Response(200, json={"slip": {"advice": []}}), 502),
        (httpx.Response(200, json={"slip": {"advice": "   "}}), 502),
        (httpx.ReadTimeout("private details"), 504),
        (httpx.ConnectError("private details"), 502),
    ],
)
def test_external_failures(
    client: TestClient, external_response: httpx.Response | Exception, status: int
) -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        if isinstance(external_response, Exception):
            raise external_response
        return external_response

    async def dependency() -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as external:
            yield external

    assert isinstance(client.app, FastAPI)
    client.app.dependency_overrides[get_http_client] = dependency
    response = client.get("/advice")
    assert response.status_code == status
    assert "detail" in response.json()
    assert "private details" not in response.text
    assert client.get("/historico").json()["content"] == "(sem histórico ainda)"


def test_invalid_save(client: TestClient) -> None:
    assert client.get("/advice?save=invalid").status_code == 422
