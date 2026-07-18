# Planetary Council / BaseX

A living human-agent website: public portal, personal dashboard, agent boot
context, and visitor interaction system in one lightweight FastAPI app.

> The website is the body. WebSocket is the nervous system. Hermes is the brain.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the design and growth path.

## Run

```bash
cd planetary-council
uv run uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Open <http://127.0.0.1:8765/>.

## Test

```bash
cd planetary-council
uv run pytest -q
```

## Endpoints

| route                  | purpose                                             |
|------------------------|-----------------------------------------------------|
| `/`                    | website UI: project cards + receptionist chat       |
| `/boot`                | compact agent-readable context                      |
| `/health`              | server + DB health                                  |
| `/api/messages`        | visitor message → triage → reply / escalation       |
| `/api/attention`       | impression / hover / open tracking                  |
| `/api/projects/focus`  | ranked project focus scores                         |
| `/api/telegram/reply`  | Phil's Telegram reply → visitor session (live push) |
| `/ws/{session_id}`     | live session updates over WebSocket                 |

## Configuration

Copy `.env.example` to `.env`. `PC_DB_PATH` moves the SQLite file (point it at a
persistent volume in production). Telegram variables stay empty until the real
bot is wired — tokens are never committed.
