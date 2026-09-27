from fastapi.testclient import TestClient

from app.main import create_application


def test_shared_client_is_closed() -> None:
    app = create_application()
    with TestClient(app) as client:
        external = app.state.http_client
        assert not external.is_closed
        assert client.get("/historico").status_code == 200
        assert app.state.http_client is external
    assert external.is_closed
