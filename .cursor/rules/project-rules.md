# Cursor Project Rules — TaxGuardBot

## General Philosophy

This project follows professional software engineering workflows.

Priorities:
1. Stability
2. Readability
3. Small safe iterations
4. Clear architecture
5. Maintainability

Avoid unnecessary complexity.

---

## Before Making Changes

Always:
- Read README.md
- Read relevant docs/
- Inspect existing architecture
- Understand affected files

Never start coding blindly.

---

## Change Rules

- Make small focused changes only.
- Do not modify unrelated files.
- Do not rewrite architecture without approval.
- Do not change storage behavior without approval.
- Do not change calculation logic without adding tests.
- Do not introduce new dependencies without approval.
- Prefer explicit readable code.

---

## File Boundaries

Safe to edit with care:
- `app/calculations.py` — pure logic, always add tests when changing
- `app/bot.py` — message handling, small changes only
- `docs/` — documentation updates

Require explicit approval before touching:
- `app/storage.py` / `app/user_storage.py` — storage behavior
- `app/admin_server.py` — auth and API surface
- `app/message_store.py` — hot-reload logic
- `requirements.txt` — dependency changes

Never touch:
- `data/` — live data files
- `.env` — secrets

---

## AI Workflow

ChatGPT: brainstorming, architecture, specifications
Claude Code: implementation, refactoring, testing
Cursor: inspection, editing, navigation, review
Human: final approval, architecture decisions, production decisions

---

## Testing Rules

When changing logic:
- update or add tests
- run tests before completion
- do not break existing functionality

---

## Documentation Rules

Meaningful changes should update:
- `docs/TASKS.md`
- `docs/PROJECT_STATE.md`
- relevant specs if architecture or product changes

Documentation is part of development.

---

## Never

- Never commit secrets or `data/` files.
- Never bypass validation intentionally.
- Never deploy directly to production.
- Never delete unrelated code.
- Never perform large rewrites without approval.
