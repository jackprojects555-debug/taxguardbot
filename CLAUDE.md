# Claude Code Rules — TaxGuardBot

## Before Every Task

Read:
- README.md
- relevant docs/ files
- docs/TASKS.md
- docs/PROJECT_STATE.md

---

## Project Context

- Telegram bot (`app/bot.py`) + separate FastAPI admin server (`app/admin_server.py`)
- JSON file storage in `data/` — gitignored, never commit
- Two processes share data only via files — documented risk in `docs/DECISIONS.md`
- See `docs/DEPLOYMENT.md` for how to run locally

---

## Rules

- Work incrementally. One focused change at a time.
- Do not modify unrelated files.
- Do not rewrite architecture without approval.
- Do not touch `data/` files.
- Do not modify `.env` or any secrets.
- Do not change storage behavior (`storage.py`, `user_storage.py`) without approval.
- Do not change calculation logic (`calculations.py`) without adding or updating tests.
- Do not introduce new dependencies without approval.
- Do not modify `app/admin_server.py` auth logic without approval.
- Prefer readability over cleverness.

---

## Required Workflow

1. Understand the task.
2. Identify affected files.
3. Implement minimal safe changes.
4. Run tests if available.
5. Summarize what changed and what was not touched.

---

## Never

- Never deploy directly to production.
- Never bypass tests intentionally.
- Never remove working functionality without approval.
- Never introduce unnecessary complexity.
- Never run the bot or admin server as part of a code change.
- Never commit `data/` files or `.env`.

---

## After Completing Work

Always report:
- files changed
- files explicitly not touched
- tests executed or skipped (and why)
- remaining risks
- suggested next steps
