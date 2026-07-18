# Planetary Council / BaseX — Architecture

> The website is the body. WebSocket is the nervous system. Hermes is the brain.

This document is the answer to "figure a seamless architecture, lightweight and easy to
maintain." The description of the product is generic and subject to change — so the
architecture optimizes for **changeability**, not completeness. Start somewhere, then
increase / progress.

## Design principles

1. **One process, one file of truth.** A single FastAPI app serves HTML, JSON API, and
   WebSocket. SQLite is the only state. No queue, no cache, no second service until a
   real bottleneck demands one.
2. **Durable layer ≠ live layer.** SQLite (memory) and the append-only `events` table
   (truth trail) are durable. WebSocket is transport only — never persistence. The rule
   is mechanical: *write the database record first, broadcast second.*
3. **Public input becomes signal, not truth.** Visitor messages and attention data are
   raw signal stored for triage and scoring; nothing a visitor does is canon.
4. **Progressive layering.** Every future capability (Telegram bot, dashboard, Postgres,
   real Hermes) attaches to an existing seam instead of requiring a rewrite:
   - Telegram → already has its seam: `POST /api/telegram/reply` maps a reply to a
     visitor session. Wiring a real bot is adding a webhook caller, not new architecture.
   - Postgres → the DB is behind one `db()` function and an env var (`PC_DB_PATH`).
   - Smarter receptionist → `triage()` is one pure function; swap keyword rules for a
     cheap model call without touching routes.
   - Dashboard → a new route reading the same tables.

## System shape

```text
visitor / agent / Phil
  → HTTP + WebSocket
  → FastAPI app (app/main.py — single file on purpose)
  → SQLite (data/planetary_council.db, path via PC_DB_PATH)
  → append-only events table (truth trail)
  → WebSocket broadcast of live updates (after DB write)
  → Telegram routing seam for high-signal human replies
```

## Data model (4 tables, all created on startup)

| table      | role                                                        |
|------------|-------------------------------------------------------------|
| `events`   | append-only truth trail: every meaningful thing that happens |
| `sessions` | visitor sessions (id, name, contact, created)                |
| `messages` | visitor/receptionist/phil messages per session, with signal level |
| `attention`| impression / hover / open signals per project                |

## Machine-readable routes

| route                  | purpose                                            |
|------------------------|----------------------------------------------------|
| `/boot`                | compact agent-readable context (culture layer)     |
| `/health`              | server + DB health                                 |
| `/api/messages`        | visitor message ingestion → triage → reply/escalate |
| `/api/attention`       | hover/open/impression tracking                     |
| `/api/projects/focus`  | ranked project focus scores                        |
| `/api/telegram/reply`  | Phil's Telegram reply → website visitor session     |
| `/ws/{session_id}`     | live session updates                               |

## Focus scoring

Attention is weighted, not counted: hovers under 1 s are ignored (accidental), hover
seconds are capped at 30 (confusion ≠ 10× interest), opening a project detail outweighs
hovering, and a visitor message mentioning a project outweighs both.

> Public attention shows where the world is leaning in. Strategic priority decides
> whether we lean back.

## Receptionist boundaries

The triage layer greets, answers public-canon questions, collects intent, and escalates
high-signal messages (asks for Phil/human, collaboration, funding, media, legal,
security, urgent). It never pretends to be Phil, never commits, never grants
permissions. Escalation currently means: flagged `high` in the DB, surfaced in `/boot`,
and queued for the Telegram seam.

## Growth path (in order, each step optional until needed)

1. **Now:** this seed — full visitor loop minus real Telegram delivery.
2. Wire real Telegram bot (token via env, never committed) → full roundtrip:
   visitor → triage → Telegram → Phil → visitor, live over WebSocket.
3. Private dashboard route (sessions, focus scores, pending escalations) behind a
   simple admin token.
4. Deploy: any host that runs one Python process with a persistent disk (Fly.io volume
   or small VPS). Not static hosting — we need WebSockets + DB writes + webhook.
5. Postgres only when concurrent writes or managed backups become real needs.

## Guardrails (unchanged from the seed brief)

- Never commit secrets. `.env.example` documents, `.env` stays local.
- Private cockpit data stays out of public routes, including `/boot`.
- Visitor comments are never canon.
- Cheap triage + human escalation — no expensive agent loop per message.
- Ask before external side effects (public deploy, sending messages).
