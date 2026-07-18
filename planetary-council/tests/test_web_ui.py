import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PC_DB_PATH", str(tmp_path / "test.db"))
    from app.main import app
    with TestClient(app) as c:
        yield c


def test_ui_is_instrumented(client):
    html = client.get("/").text
    # Project cards carry attention instrumentation hooks.
    assert 'data-project="planetary-council"' in html
    assert 'data-project="marsita-the-ultra"' in html
    assert "/api/attention" in html
    # Chat wired to message API and live WebSocket.
    assert "/api/messages" in html
    assert "/ws/" in html
    # Privacy note for hover/attention analytics.
    assert "Privacy" in html
