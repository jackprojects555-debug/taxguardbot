# DEPLOYMENT.md

How to run TaxGuardBot locally and in production.

---

## Requirements

- Python 3.14.4 (local) or 3.12+ (server)
- `.env` file with `BOT_TOKEN` set
- `ADMIN_TOKEN` exported in shell before running admin server

See `.env.example` for full variable list.

---

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Run Bot

```bash
source .venv/bin/activate
python3 -m app.bot
```

Requires: `BOT_TOKEN` in `.env`
On startup prints: `Bot is running...`
Stops with: `Ctrl+C`

---

## Run Admin Server

```bash
export ADMIN_TOKEN='your-long-random-secret'
source .venv/bin/activate
python3 -m app.admin_server
```

Default URL: `http://127.0.0.1:8080`
Override bind address: `export ADMIN_HOST=0.0.0.0`
Override port: `export ADMIN_PORT=9000`

Note: `ADMIN_TOKEN` must be exported — the admin server does not call `load_dotenv()`.
See DECISIONS.md #007.

---

## Data Files

All data is stored in `data/` (gitignored — never committed).

| File | Contents |
|---|---|
| `data/transactions.json` | Per-user transaction history |
| `data/users.json` | User registry (Telegram IDs, block status, display names) |
| `data/messages.json` | Bot copy / message templates (editable via admin panel) |

Both processes load these files into memory at startup.
`data/messages.json` hot-reloads when changed — bot picks up admin edits without restart.
`data/users.json` and `data/transactions.json` do NOT hot-reload in the bot process.

---

## Deployment Status

Currently: local machine only. No hosted deployment.
No CI/CD pipeline yet (planned in ENG-002).
No automated backup (documented risk — see DECISIONS.md #002).

---

## Restart Notes

- Restarting the bot reloads all data from disk — no data loss from normal restarts.
- Admin edits to users or transactions require a bot restart to reflect in-memory state.
- Admin edits to messages do not require restart (hot-reload via file mtime).
