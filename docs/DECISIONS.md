# DECISIONS.md

Architectural and product decisions made during development.
Each entry records what was decided, why, and current status.

---

## 001 — Telegram-first delivery

Decision: Build as a Telegram bot, not a web app or mobile app.
Reason: Zero friction for the target user. Freelancers already use Telegram daily. No install required.
Status: Locked for MVP.

---

## 002 — JSON file storage

Decision: Store all data in JSON files under `data/`.
Reason: MVP speed. No database setup, no schema migrations, no infrastructure dependency.
Risk: No concurrent-write safety. No automated backup. Data loss on server failure or disk issue.
Status: Documented technical debt. Migration to a real database is a post-MVP task (see TASKS.md PROD-006).

---

## 003 — Two separate processes (bot + admin)

Decision: Run the Telegram bot and admin server as separate Python processes.
Reason: Isolates admin API failures from bot availability. Each can be started and stopped independently.
Risk: Processes do not share memory. Each loads `data/*.json` into its own in-memory dict at startup.
  - `message_store.py` hot-reloads via file mtime — admin message edits reach the bot without restart.
  - `storage.py` and `user_storage.py` do NOT hot-reload — admin edits to users or transactions
    require a bot restart to take effect in the bot process.
Status: Documented technical debt. Not a fix target during engineering migration phase.

---

## 004 — Hardcoded tax rates

Decision: Fixed rates for all users in MVP (VAT 17/117, income tax 20%, NI 8%, social savings 5%).
Reason: Per-user configurable rates are defined in MASTER_SPEC_V1.md but not needed to validate core behavior.
Status: Technical debt. Per-user rates are a planned product feature (see TASKS.md PROD-001).

---

## 005 — requirements.txt as install source

Decision: Keep `requirements.txt` as the install mechanism. Add `pyproject.toml` for tooling config only.
Reason: Minimal disruption during engineering migration. `requirements.txt` is already working in production.
Status: Acceptable for now. Revisit after tooling phase (ENG-002) is complete.

---

## 006 — Python 3.14.4 locally, 3.12 for CI

Decision: Local development runs Python 3.14.4 (pinned in `.python-version`). CI will target Python 3.12.
Reason: 3.14.4 was the installed version when development started. Python 3.12 has full ecosystem
  support and is available on standard CI runners without custom build steps.
Status: Acceptable split. No known incompatibilities between 3.12 and 3.14 in the current codebase.

---

## 007 — ADMIN_TOKEN via export, not .env

Decision: `ADMIN_TOKEN` must be set as an environment variable via `export`, not loaded from `.env`.
Reason: `app/admin_server.py` does not call `load_dotenv()` — unlike the bot, the admin server
  reads env vars directly via `os.getenv()`. The README documents the export pattern.
Status: Works as designed. Could be unified with `load_dotenv()` in a future cleanup pass.
