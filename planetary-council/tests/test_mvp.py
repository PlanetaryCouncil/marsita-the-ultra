import sqlite3

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("PC_DB_PATH", str(tmp_path / "test.db"))
    from app.main import app
    with TestClient(app) as c:
        yield c


def rows(tmp_path, table):
    conn = sqlite3.connect(tmp_path / "test.db")
    conn.row_factory = sqlite3.Row
    return conn.execute(f"SELECT * FROM {table}").fetchall()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok", "db": "ok"}


def test_message_persistence_and_routine_triage(client, tmp_path):
    res = client.post("/api/messages", json={"session_id": "s1", "text": "hello there"})
    assert res.status_code == 200
    body = res.json()
    assert body["signal"] == "routine"
    assert "receptionist" in body["reply"].lower()

    messages = rows(tmp_path, "messages")
    senders = [m["sender"] for m in messages]
    assert senders == ["visitor", "receptionist"]

    events = [e["kind"] for e in rows(tmp_path, "events")]
    assert "session_created" in events
    assert "visitor_message" in events


def test_high_signal_triage_queues_escalation(client, tmp_path):
    res = client.post(
        "/api/messages",
        json={"session_id": "s2", "text": "I want to collaborate with Phil on funding",
              "name": "Ada", "contact": "ada@example.org"},
    )
    assert res.json()["signal"] == "high"
    events = [e["kind"] for e in rows(tmp_path, "events")]
    assert "telegram_escalation_queued" in events
    session = rows(tmp_path, "sessions")[0]
    assert session["name"] == "Ada"
    assert session["contact"] == "ada@example.org"


def test_attention_and_focus_scoring(client):
    sid = "s3"
    # Accidental sub-second hover must be ignored.
    client.post("/api/attention", json={"session_id": sid, "project": "gaza-memes",
                                        "kind": "hover", "seconds": 0.4})
    # Real interest in planetary-council.
    client.post("/api/attention", json={"session_id": sid, "project": "planetary-council",
                                        "kind": "hover", "seconds": 12})
    client.post("/api/attention", json={"session_id": sid, "project": "planetary-council",
                                        "kind": "open"})
    focus = client.get("/api/projects/focus").json()["focus"]
    ranked = {f["project"]: f["score"] for f in focus}
    assert focus[0]["project"] == "planetary-council"
    assert ranked["gaza-memes"] == 0.0
    # Hover seconds are capped at 30.
    client.post("/api/attention", json={"session_id": sid, "project": "marsita-the-ultra",
                                        "kind": "hover", "seconds": 500})
    focus = client.get("/api/projects/focus").json()["focus"]
    ranked = {f["project"]: f["score"] for f in focus}
    assert ranked["marsita-the-ultra"] == pytest.approx(6.0)


def test_telegram_reply_routes_to_live_session(client, tmp_path):
    client.post("/api/messages", json={"session_id": "s4", "text": "hi"})
    with client.websocket_connect("/ws/s4") as ws:
        res = client.post("/api/telegram/reply",
                          json={"session_id": "s4", "text": "Phil here — let's talk."})
        assert res.status_code == 200
        pushed = ws.receive_json()
    assert pushed == {"type": "reply", "sender": "phil", "text": "Phil here — let's talk."}
    senders = [m["sender"] for m in rows(tmp_path, "messages")]
    assert senders[-1] == "phil"


def test_telegram_reply_unknown_session(client):
    res = client.post("/api/telegram/reply", json={"session_id": "nope", "text": "x"})
    assert res.status_code == 404


def test_boot_exposes_public_canon_only(client):
    boot = client.get("/boot").json()
    assert boot["who"] == "Planetary Council / BaseX"
    assert "Culture is what agents read before acting." in boot["principles"]
    assert {p["id"] for p in boot["projects"]} == {"planetary-council", "marsita-the-ultra", "gaza-memes"}
    assert "/api/telegram/reply" in boot["routes"]
    assert "pending_high_signal_messages" in boot
