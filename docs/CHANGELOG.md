# CHANGELOG

## v2.0 — 2026-05-13

### V2 Core complete (V2-001 through V2-010)

#### Added
- **Help command** (V2-003) — `עזרה` / `help` returns full bilingual command list; language follows user profile
- **Command alias registry** (V2-002) — central parser maps Hebrew + English inputs to actions; income parser handles `₪`, commas, `נוכה`, `vat excluded`
- **Bilingual onboarding** (V2-004) — language auto-detected from Telegram locale; all onboarding messages in user's language
- **CMS foundation** (V2-005) — `bot_texts` DB table for runtime text overrides; `t(key, lang)` with message_store fallback; no restart needed
- **Pension allocation** (V2-006) — `pension_rate` field on user profile; pension calculated per transaction; shown in income confirmation and status if > 0
- **NI / social savings fixed-monthly mode** (V2-007) — national insurance and social savings can be set as a flat monthly amount instead of a percentage; onboarding accepts `1200 חודשי` / `1200 monthly` format
- **Admin CMS text endpoints** (V2-008) — `GET/PUT/DELETE /admin/texts` and `/admin/texts/{key}/{lang}` for runtime message editing
- **VAT period flag** (V2-009) — `vat_period` field on user profile (`monthly` / `bi_monthly`); groundwork for period-aware VAT reports
- **Status command enhancements** (V2-010) — pension line shown if pension > 0; NI and social savings lines show `(קבוע)` label when in fixed mode

#### Fixed
- `preferred_language` column migration (V2-001) — existing databases upgraded without data loss
- `create_or_update_admin` NOT NULL bug — `is_blocked` defaulted to NULL on upsert when not specified; now falls back to existing value

---

## v1.7 — 2026-05 (PROD-007)

### Added
- PostgreSQL backend via psycopg2-binary; `DATABASE_URL` env var selects Neon in production
- SQLite retained for local dev (no `DATABASE_URL` needed)
- `_Conn` wrapper normalises `?` vs `%s` placeholders across both backends
- Render deployment config

---

## v1.6 — 2026-05 (PROD-006)

### Added
- Full database migration: JSON file storage replaced with SQLite/PostgreSQL
- Idempotent `_MIGRATIONS` list — `ALTER TABLE ADD COLUMN` with try/except per column
- `data/taxguard.db` for local persistence

---

## v1.5 — 2026-05 (PROD-005)

### Added
- Automated mid-month report (15th at 09:00 Asia/Jerusalem)
- Automated end-of-month report (last day at 09:00)
- Users with no active transactions skipped silently

---

## v1.4 — 2026-05 (PROD-004)

### Added
- Correction commands: `תקן אחרון`, `תקן N`, `fix last`, `fix N`
- Show last transaction: `אחרון` / `last`
- Show list: `רשימה` / `list`
- Cancel by ID: `בטל N` / `cancel N`

---

## v1.3 — 2026-05 (PROD-003)

### Added
- Transfer confirmation: `העברתי` / `saved` marks full transfer
- Partial transfer: `העברתי 4000` / `saved 4000`
- Transaction status tracking: `open` → `partially_saved` → `fully_saved`

---

## v1.2 — 2026-05 (PROD-001 / PROD-002)

### Added
- Per-user onboarding: business type, VAT included default, income tax rate, NI rate, social savings rate
- User profile persistence (`BotUser` dataclass, CRUD)
- Transaction status model (`open`, `canceled`, etc.)
- Admin server (FastAPI, port 8080) with Bearer token auth
- Admin endpoints: users CRUD, transactions list, messages get/put, health check, HTML dashboard
- Block/unblock users via admin API

---

## v1.1 — 2026-05-05

### Added
- Reset command: `reset`, `אפס`, `נקה`, `מחק`
- JSON-based persistence (data survives restarts)
- Detailed monthly breakdown in status summary (VAT, income tax, NI, social savings)
- Test strategy document

---

## v1.0 — 2026-05-05

### Added
- Telegram bot setup with environment configuration
- Income input parsing (VAT-included and `נוכה` VAT-excluded)
- Calculation engine: VAT, income tax, national insurance, social savings
- `מצב` status command (current month only)
- Support for comma-separated and `₪`-prefixed inputs
- Input validation and error handling
