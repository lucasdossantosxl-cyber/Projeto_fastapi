from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_http_client
from app.core.config import settings
from app.main import create_application


@pytest.fixture(autouse=True)
def isolated_database(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "DATABASE_PATH", tmp_path / "history.db")
    # Os testes não fazem chamadas de rede e não dependem de proxies da máquina.
    for name in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_application()

    def respond(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"slip": {"advice": "Always be kind."}})

    async def mocked_client() -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as external:
            yield external

    app.dependency_overrides[get_http_client] = mocked_client
    with TestClient(app) as test_client:
        yield test_client
