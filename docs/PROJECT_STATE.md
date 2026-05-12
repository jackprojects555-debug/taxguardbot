# PROJECT_STATE.md

Current state of the TaxGuardBot project. Update this file when state changes meaningfully.

---

## Status

Engineering migration in progress — documentation and tooling only.
No feature development in progress.

## Version

v1.1 (see docs/CHANGELOG.md)

## Active Branch

feature/engineering-migration

---

## What Works

- Income input → VAT/tax calculation → storage → Hebrew response
- VAT-included and VAT-excluded inputs (`נוכה` keyword)
- Input parsing: commas, spaces, ₪ symbol, empty/zero/negative/k-suffix validation
- Reset commands: `reset`, `אפס`, `נקה`, `מחק`
- Monthly status summary: `מצב`
- JSON file persistence — survives process restart
- User registry — upsert on first message, block support
- Admin server: user CRUD, transaction view, message template editing
- Admin dashboard — single-page HTML at `http://127.0.0.1:8080`
- Message hot-reload — admin edits to `data/messages.json` reflect in bot without restart

## Where It Runs

Local machine only. No hosted deployment currently.

---

## Known Technical Debt

- No automated tests (see TASKS.md ENG-002)
- No CI pipeline (see TASKS.md ENG-002)
- Two-process data consistency gap (see DECISIONS.md #003)
- No data backup strategy (see DECISIONS.md #002)
- Tax rates hardcoded for all users (see DECISIONS.md #004)
- `ADMIN_TOKEN` must be exported manually — not loaded from `.env` (see DECISIONS.md #007)

---

## What Is Not Yet Built

From MASTER_SPEC_V1.md:

- Onboarding flow / per-user tax rate configuration (PROD-001)
- Transaction statuses: open / partial / saved / canceled (PROD-002)
- Transfer confirmation commands: `העברתי` (PROD-003)
- Correction commands: `תקן`, `בטל` (PROD-004)
- Automated reminders: mid-month and end-of-month (PROD-005)
- Database migration (PROD-006)
- Website layer
