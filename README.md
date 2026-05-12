# TaxGuardBot

Telegram bot that helps freelancers manage cash flow by separating tax obligations from income in real-time.

## Features

- Income input via Telegram
- Automatic tax calculation:
  - VAT
  - Income tax
  - National insurance
  - Social savings
- Net available calculation
- Action-oriented response (how much to move aside)
- Monthly summary via מצב command
- Support for VAT-excluded inputs (נוכה)

## Tech Stack

- Python
- python-telegram-bot
- JSON file storage under `data/` (gitignored)
- FastAPI admin API + single-page dashboard

## Project Structure

```
app/
  __init__.py
  admin_server.py
  bot.py
  calculations.py
  message_store.py
  models.py
  static/
    admin.html
  storage.py
  user_storage.py
docs/
  CHANGELOG.md
  DECISIONS.md
  DEPLOYMENT.md
  MASTER_SPEC_V1.md
  PROJECT_STATE.md
  TASKS.md
  TEST_STRATEGY_V1.md
  (+ working method and prompt docs)
CLAUDE.md
requirements.txt
README.md
```

## Setup

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create `.env`:

- `BOT_TOKEN` — Telegram bot token (required for the bot process)
- `ADMIN_TOKEN` — long random secret for the admin API (required for `app.admin_server`)

Run the bot:

```bash
python3 -m app.bot
```

Run the admin panel (default `http://127.0.0.1:8080/`):

```bash
export ADMIN_TOKEN='replace-with-a-long-random-secret'
python3 -m app.admin_server
```

Optional: `ADMIN_HOST`, `ADMIN_PORT` override bind address and port.

Open the dashboard, paste the same `ADMIN_TOKEN` into the token field, then manage **users** (`data/users.json`) and **bot copy** (`data/messages.json`). The bot reloads message templates when `data/messages.json` changes (based on file modification time).

## Status

MVP working:
- Input → calculation → storage → summary

## Next Steps

- Persistent storage (DB)
- UX improvements
- Stronger admin auth (OAuth, VPN, etc.)

## AI Usage

**Cursor:** follows strict working method rules.
See: `docs/CURSOR_WORKING_METHOD_V2.md`

**Claude Code:** governed by `CLAUDE.md` at the project root.