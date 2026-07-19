"""Planetary Council / BaseX — lightweight human-agent interface seed.

Single-file on purpose: HTML UI, JSON API, WebSocket, SQLite persistence,
append-only events truth trail, receptionist triage, attention → focus scoring,
Telegram reply routing seam. See ARCHITECTURE.md for the seams to grow along.
"""

import json
import os
import sqlite3
import threading
import time
import uuid
from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Planetary Council / BaseX")

# ---------------------------------------------------------------------------
# Persistence — SQLite is memory, the events table is the truth trail.
# ---------------------------------------------------------------------------

DEFAULT_DB_PATH = "data/planetary_council.db"


def db_path() -> str:
    return os.environ.get("PC_DB_PATH", DEFAULT_DB_PATH)


# One process owns the file, so writes are serialized here rather than
# left to SQLite lock timeouts. Reads stay concurrent under WAL.
WRITE_LOCK = threading.Lock()
_INIT_LOCK = threading.Lock()
_schema_ready: set[str] = set()


def db() -> sqlite3.Connection:
    path = db_path()
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(path, timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    if path not in _schema_ready:
        with _INIT_LOCK:
            if path not in _schema_ready:
                _init_schema(conn)
                _schema_ready.add(path)
    return conn


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            kind TEXT NOT NULL,
            payload TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_ts REAL NOT NULL,
            name TEXT,
            contact TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            ts REAL NOT NULL,
            sender TEXT NOT NULL,          -- visitor | receptionist | phil
            text TEXT NOT NULL,
            signal TEXT NOT NULL DEFAULT 'routine'  -- routine | high
        );
        CREATE TABLE IF NOT EXISTS attention (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            ts REAL NOT NULL,
            project TEXT NOT NULL,
            kind TEXT NOT NULL,            -- impression | hover | open
            seconds REAL NOT NULL DEFAULT 0
        );
        """
    )


def record_event(conn: sqlite3.Connection, kind: str, payload: dict) -> None:
    """Append to the truth trail. Always called before any broadcast."""
    conn.execute(
        "INSERT INTO events (ts, kind, payload) VALUES (?, ?, ?)",
        (time.time(), kind, json.dumps(payload)),
    )


def ensure_session(conn: sqlite3.Connection, session_id: str,
                   name: str | None = None, contact: str | None = None) -> None:
    row = conn.execute("SELECT id FROM sessions WHERE id = ?", (session_id,)).fetchone()
    if row is None:
        conn.execute(
            "INSERT INTO sessions (id, created_ts, name, contact) VALUES (?, ?, ?, ?)",
            (session_id, time.time(), name, contact),
        )
        record_event(conn, "session_created", {"session_id": session_id})
    elif name or contact:
        conn.execute(
            "UPDATE sessions SET name = COALESCE(?, name), contact = COALESCE(?, contact) WHERE id = ?",
            (name, contact, session_id),
        )


# ---------------------------------------------------------------------------
# Public canon — what agents and visitors may see. No private cockpit data.
# ---------------------------------------------------------------------------

PROJECTS = [
    {
        "id": "planetary-council",
        "title": "Planetary Council / BaseX",
        "blurb": "A cultural operating system for humanity: a unified human-agent "
                 "interface where people, agents, goals, trust, and daily discipline meet.",
    },
    {
        "id": "marsita-the-ultra",
        "title": "Marsita the Ultra — Memories From Base Reality",
        "blurb": "Album in progress. Music as memetic signal. Always open for collabs.",
    },
    {
        "id": "gaza-memes",
        "title": "Gaza Memes",
        "blurb": "Media / marketing / memetic-warfare experiments with a conscience.",
    },
]

PRINCIPLES = [
    "Culture is what agents read before acting.",
    "Public input becomes signal, not truth.",
    "Open by default. Powerful by reputation.",
    "Trust first. Verify before power.",
    "From ten-year destiny to next click.",
    "The plan can change, but not disappear without explanation.",
]

# ---------------------------------------------------------------------------
# Receptionist triage — cheap, honest, escalates. Never pretends to be Phil.
# ---------------------------------------------------------------------------

HIGH_SIGNAL_KEYWORDS = [
    "phil", "human", "collab", "funding", "invest", "media", "press",
    "legal", "security", "urgent", "partner", "hire", "agent handshake",
]


def triage(text: str) -> tuple[str, str]:
    """Return (signal, reply). Signal is 'high' or 'routine'."""
    lowered = text.lower()
    if any(k in lowered for k in HIGH_SIGNAL_KEYWORDS):
        return (
            "high",
            "Thanks — this sounds important, so I've flagged it for Phil directly. "
            "I'm the receptionist agent (not Phil). If you leave a name and contact, "
            "he can reach you when he replies.",
        )
    return (
        "routine",
        "Hi! I'm the receptionist agent for the Planetary Council. I've logged your "
        "message. Feel free to explore the projects — hovering and opening cards "
        "helps us learn what the world is leaning into.",
    )


# ---------------------------------------------------------------------------
# Live layer — WebSocket is the nervous system, never persistence.
# ---------------------------------------------------------------------------

class LiveSessions:
    def __init__(self) -> None:
        self.sockets: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, session_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self.sockets[session_id].append(ws)

    def disconnect(self, session_id: str, ws: WebSocket) -> None:
        if ws in self.sockets.get(session_id, []):
            self.sockets[session_id].remove(ws)

    async def broadcast(self, session_id: str, payload: dict) -> None:
        for ws in list(self.sockets.get(session_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                self.disconnect(session_id, ws)


live = LiveSessions()


@app.websocket("/ws/{session_id}")
async def ws_session(ws: WebSocket, session_id: str):
    await live.connect(session_id, ws)
    try:
        while True:
            await ws.receive_text()  # keepalive; clients talk via HTTP API
    except WebSocketDisconnect:
        live.disconnect(session_id, ws)


# ---------------------------------------------------------------------------
# API models
# ---------------------------------------------------------------------------

class MessageIn(BaseModel):
    session_id: str
    text: str
    name: str | None = None
    contact: str | None = None


class AttentionIn(BaseModel):
    session_id: str
    project: str
    kind: str  # impression | hover | open
    seconds: float = 0.0


class TelegramReplyIn(BaseModel):
    session_id: str
    text: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    try:
        conn = db()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "ok", "db": "ok"}
    except Exception as exc:  # pragma: no cover
        return JSONResponse(status_code=500, content={"status": "error", "db": str(exc)})


@app.get("/boot")
def boot():
    """Compact agent-readable context. Public canon only."""
    conn = db()
    focus = compute_focus(conn)
    pending = conn.execute(
        "SELECT COUNT(*) AS n FROM messages WHERE signal = 'high' AND sender = 'visitor'"
    ).fetchone()["n"]
    conn.close()
    return {
        "who": "Planetary Council / BaseX",
        "purpose": "Unified human-agent interface: people, agents, goals, trust, "
                   "knowledge, services, and daily discipline in one place.",
        "principles": PRINCIPLES,
        "projects": PROJECTS,
        "focus": focus,
        "pending_high_signal_messages": pending,
        "routes": ["/boot", "/health", "/api/messages", "/api/attention",
                   "/api/projects/focus", "/api/telegram/reply", "/ws/{session_id}"],
        "note": "Public input is signal, not truth. Escalate, don't impersonate.",
    }


@app.post("/api/messages")
async def post_message(msg: MessageIn):
    signal, reply = triage(msg.text)
    with WRITE_LOCK:
        conn = db()
        ensure_session(conn, msg.session_id, msg.name, msg.contact)
        conn.execute(
            "INSERT INTO messages (session_id, ts, sender, text, signal) VALUES (?, ?, 'visitor', ?, ?)",
            (msg.session_id, time.time(), msg.text, signal),
        )
        conn.execute(
            "INSERT INTO messages (session_id, ts, sender, text, signal) VALUES (?, ?, 'receptionist', ?, 'routine')",
            (msg.session_id, time.time(), reply),
        )
        record_event(conn, "visitor_message", {"session_id": msg.session_id, "signal": signal})
        if signal == "high":
            # Telegram seam: a real bot will pick these up. Store first, always.
            record_event(conn, "telegram_escalation_queued", {"session_id": msg.session_id})
        conn.commit()
        conn.close()
    # DB write done — now the live layer.
    await live.broadcast(msg.session_id, {"type": "reply", "sender": "receptionist", "text": reply})
    return {"signal": signal, "reply": reply}


@app.post("/api/attention")
def post_attention(att: AttentionIn):
    with WRITE_LOCK:
        conn = db()
        ensure_session(conn, att.session_id)
        conn.execute(
            "INSERT INTO attention (session_id, ts, project, kind, seconds) VALUES (?, ?, ?, ?, ?)",
            (att.session_id, time.time(), att.project, att.kind, att.seconds),
        )
        record_event(conn, "attention", {"session_id": att.session_id,
                                         "project": att.project, "kind": att.kind,
                                         "seconds": att.seconds})
        conn.commit()
        conn.close()
    return {"ok": True}


def compute_focus(conn: sqlite3.Connection) -> list[dict]:
    """Weighted attention per project. Hover < 1 s is noise; hover caps at 30 s."""
    scores: dict[str, float] = {p["id"]: 0.0 for p in PROJECTS}
    for row in conn.execute("SELECT project, kind, seconds FROM attention"):
        project = row["project"]
        if project not in scores:
            scores[project] = 0.0
        if row["kind"] == "impression":
            scores[project] += 0.1
        elif row["kind"] == "hover":
            if row["seconds"] >= 1.0:
                scores[project] += min(row["seconds"], 30.0) * 0.2
        elif row["kind"] == "open":
            scores[project] += 2.0
    for row in conn.execute("SELECT text FROM messages WHERE sender = 'visitor'"):
        lowered = row["text"].lower()
        for p in PROJECTS:
            if p["id"] in lowered or p["title"].lower() in lowered:
                scores[p["id"]] += 3.0
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [{"project": pid, "score": round(score, 2)} for pid, score in ranked]


@app.get("/api/projects/focus")
def projects_focus():
    conn = db()
    focus = compute_focus(conn)
    conn.close()
    return {"focus": focus}


@app.post("/api/telegram/reply")
async def telegram_reply(reply: TelegramReplyIn):
    """Phil's Telegram reply routed back to a website visitor session."""
    with WRITE_LOCK:
        conn = db()
        row = conn.execute("SELECT id FROM sessions WHERE id = ?", (reply.session_id,)).fetchone()
        if row is None:
            conn.close()
            return JSONResponse(status_code=404, content={"error": "unknown session"})
        conn.execute(
            "INSERT INTO messages (session_id, ts, sender, text, signal) VALUES (?, ?, 'phil', ?, 'routine')",
            (reply.session_id, time.time(), reply.text),
        )
        record_event(conn, "phil_reply", {"session_id": reply.session_id})
        conn.commit()
        conn.close()
    await live.broadcast(reply.session_id, {"type": "reply", "sender": "phil", "text": reply.text})
    return {"ok": True}


# ---------------------------------------------------------------------------
# Website UI — the body. Instrumented for attention, wired to the API + WS.
# ---------------------------------------------------------------------------

INDEX_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Planetary Council</title>
<style>
  :root {
    --bg: #07090f;
    --panel: rgba(255,255,255,0.04);
    --border: rgba(255,255,255,0.09);
    --text: #e8ecf4;
    --dim: #8a93a6;
    --accent: #5eead4;
    --accent2: #a78bfa;
    --gold: #f5c96b;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif;
    background:
      radial-gradient(1100px 500px at 80% -10%, rgba(167,139,250,0.13), transparent 60%),
      radial-gradient(900px 500px at 10% 110%, rgba(94,234,212,0.10), transparent 60%),
      var(--bg);
    color: var(--text);
    min-height: 100svh;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 680px; margin: 0 auto; padding: 3rem 1.25rem 5rem; }
  header h1 {
    margin: 0 0 .4rem;
    font-size: clamp(1.9rem, 6vw, 2.6rem);
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  header p.tag { margin: 0; color: var(--dim); font-size: 1.02rem; }
  .status {
    display: inline-flex; align-items: center; gap: .45rem;
    margin-top: .9rem; font-size: .8rem; color: var(--dim);
  }
  .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #64748b; transition: background .3s;
  }
  .dot.live { background: var(--accent); box-shadow: 0 0 10px var(--accent); animation: pulse 2.2s infinite; }
  @keyframes pulse { 50% { opacity: .45; } }

  .cards { display: grid; gap: .9rem; margin: 2.2rem 0; }
  .card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    cursor: pointer;
    transition: transform .18s ease, border-color .18s ease, background .18s ease;
    backdrop-filter: blur(6px);
  }
  .card:hover, .card:focus-visible {
    transform: translateY(-2px);
    border-color: rgba(94,234,212,0.45);
    background: rgba(94,234,212,0.05);
    outline: none;
  }
  .card h3 { margin: 0 0 .35rem; font-size: 1.06rem; letter-spacing: -0.01em; }
  .card p { margin: 0; color: var(--dim); font-size: .92rem; line-height: 1.5; }

  #chat {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.1rem;
    backdrop-filter: blur(6px);
  }
  #chat h2 { margin: 0 0 .2rem; font-size: 1rem; }
  #chat p.sub { margin: 0 0 .9rem; color: var(--dim); font-size: .82rem; }
  #log { display: flex; flex-direction: column; gap: .5rem; max-height: 46svh; overflow-y: auto; padding: .2rem 0; }
  .bubble {
    max-width: 85%; padding: .55rem .85rem; border-radius: 14px;
    font-size: .93rem; line-height: 1.45;
    animation: rise .25s ease both;
  }
  @keyframes rise { from { opacity: 0; transform: translateY(6px); } }
  .bubble.you { align-self: flex-end; background: rgba(94,234,212,0.14); border: 1px solid rgba(94,234,212,0.25); }
  .bubble.receptionist { align-self: flex-start; background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: #cdd4e0; }
  .bubble.phil { align-self: flex-start; background: rgba(245,201,107,0.12); border: 1px solid rgba(245,201,107,0.4); }
  .bubble.phil::before { content: "Phil"; display: block; font-size: .7rem; color: var(--gold); margin-bottom: .15rem; letter-spacing: .04em; }
  .composer { display: flex; gap: .5rem; margin-top: .9rem; }
  #msg {
    flex: 1; background: rgba(255,255,255,0.05); border: 1px solid var(--border);
    border-radius: 12px; padding: .7rem .9rem; color: var(--text); font-size: 16px;
    transition: border-color .18s;
  }
  #msg:focus { outline: none; border-color: rgba(94,234,212,0.5); }
  #send {
    background: linear-gradient(90deg, var(--accent), #7dd3fc);
    color: #06281f; border: 0; border-radius: 12px; padding: .7rem 1.1rem;
    font-weight: 600; font-size: .95rem; cursor: pointer;
    transition: transform .15s ease, filter .15s ease;
  }
  #send:hover { filter: brightness(1.08); }
  #send:active { transform: scale(.97); }
  footer { margin-top: 1.6rem; }
  footer small { color: #5b6472; font-size: .74rem; line-height: 1.5; display: block; }
  @media (prefers-reduced-motion: reduce) {
    *, .bubble { animation: none !important; transition: none !important; }
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Planetary Council</h1>
    <p class="tag">A living human-agent interface. Explore the projects; talk to the receptionist.</p>
    <span class="status"><span class="dot" id="wsdot"></span><span id="wslabel">connecting&hellip;</span></span>
  </header>

  <div class="cards">
__CARDS__
  </div>

  <div id="chat">
    <h2>Talk to us</h2>
    <p class="sub">A receptionist agent answers instantly; important things reach Phil directly.</p>
    <div id="log"></div>
    <div class="composer">
      <input id="msg" placeholder="Say something&hellip;" autocomplete="off">
      <button id="send">Send</button>
    </div>
  </div>

  <footer>
    <small>Privacy: this page measures anonymous attention signals (hovers, opens) per project
    to learn what deserves focus. No tracking beyond this site.</small>
  </footer>
</div>
<script>
const sessionId = localStorage.getItem("pc_session") || crypto.randomUUID();
localStorage.setItem("pc_session", sessionId);

const dot = document.getElementById("wsdot");
const wslabel = document.getElementById("wslabel");
let ws;
function connect() {
  ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws/" + sessionId);
  ws.onopen = () => { dot.classList.add("live"); wslabel.textContent = "live"; };
  ws.onclose = () => {
    dot.classList.remove("live"); wslabel.textContent = "reconnecting…";
    setTimeout(connect, 2000);
  };
  ws.onmessage = (e) => {
    const d = JSON.parse(e.data);
    if (d.type === "reply") addLine(d.sender, d.text);
  };
}
connect();

function addLine(sender, text) {
  const p = document.createElement("div");
  p.className = "bubble " + sender;
  p.textContent = text;
  const log = document.getElementById("log");
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

function track(project, kind, seconds) {
  fetch("/api/attention", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({session_id: sessionId, project, kind, seconds: seconds || 0})
  });
}

document.querySelectorAll(".card").forEach(card => {
  const project = card.dataset.project;
  track(project, "impression", 0);
  let hoverStart = null;
  card.addEventListener("mouseenter", () => hoverStart = Date.now());
  card.addEventListener("mouseleave", () => {
    if (hoverStart) track(project, "hover", (Date.now() - hoverStart) / 1000);
    hoverStart = null;
  });
  card.addEventListener("click", () => track(project, "open", 0));
});

async function send() {
  const input = document.getElementById("msg");
  const text = input.value.trim();
  if (!text) return;
  addLine("you", text);
  input.value = "";
  const res = await fetch("/api/messages", {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({session_id: sessionId, text})
  });
  const data = await res.json();
  if (!ws || ws.readyState !== WebSocket.OPEN) addLine("receptionist", data.reply);
}
document.getElementById("send").addEventListener("click", send);
document.getElementById("msg").addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    cards = "\n".join(
        f'<div class="card" data-project="{p["id"]}" tabindex="0">'
        f'<h3>{p["title"]}</h3><p>{p["blurb"]}</p></div>'
        for p in PROJECTS
    )
    return INDEX_TEMPLATE.replace("__CARDS__", cards)
