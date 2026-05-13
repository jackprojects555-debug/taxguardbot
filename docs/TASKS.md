# TASKS.md

Active and backlog tasks. Update status when work starts or completes.

---

## In Progress

_(none)_

---

## Done

### [V2-005] CMS foundation
Status: Complete
Merged: feature/v2-005-cms-foundation → main (PR #18)

### [V2-004] Onboarding: language detection and bilingual flow
Status: Complete
Merged: feature/v2-004-onboarding-language → main (PR #17)

### [V2-003] Help command (both languages)
Status: Complete
Merged: feature/v2-003-help-command → main (PR #16)

### [V2-002] Command alias registry
Status: Complete
Merged: feature/v2-002-command-registry → main (PR #15)

### [V2-001] Schema migration: preferred_language column
Status: Complete
Merged: feature/v2-001-preferred-language → main (PR #14)

### [PROD-007] PostgreSQL backend + Render deployment config
Status: Complete
Merged: feature/prod-007-postgres → main (PR #13)
Note: Neon DB is provisioned and schema/data migrated. Local dev continues on SQLite (no DATABASE_URL in .env). Switch to Neon when bot is deployed to a remote server.

### [PROD-006] Database migration
Status: Complete
Merged: feature/prod-006-database → main (PR #12)

### [PROD-005] Automated reminders
Status: Complete
Merged: feature/prod-005-reminders → main (PR #11)

### [PROD-004] Correction commands
Status: Complete
Merged: feature/prod-004-correction-commands → main (PR #10)

### [PROD-003] Transfer confirmation commands
Status: Complete
Merged: feature/prod-003-transfer-commands → main (PR #8)

### [PROD-002] Transaction status tracking
Status: Complete
Merged: feature/prod-002-transaction-status → main (PR #7)

### [PROD-001] Per-user onboarding and tax rate configuration
Status: Complete
Merged: feature/prod-001-onboarding → main (PR #6)

### [ENG-001] Engineering migration — Phase 1: Documentation
Status: Complete
Merged: feature/engineering-migration → main

### [ENG-002] Engineering migration — Phase 2: Tooling
Status: Complete
Merged: feature/engineering-migration → main

---

## Backlog — V2 Core

### [V2-001] Schema migration: preferred_language column
Add `preferred_language TEXT NOT NULL DEFAULT 'he'` to users table.
Update BotUser dataclass, _row_to_user, user_summary_dict.
Add _apply_migrations() to handle existing databases without column.

### [V2-002] Command alias registry
New module: app/command_registry.py
Alias table mapping Hebrew + English inputs to action names.
Income parser: handles ₪, commas, נוכה, vat excluded.
Dispatcher replaces scattered regex in bot.py message handler.

### [V2-003] Help command (both languages)
/help and free-text "help" / "עזרה" → full command list.
Response language determined by user's preferred_language.
First real end-to-end test of the registry + language output.

### [V2-004] Onboarding: language selection step
Add language selection as step 0 of onboarding.
Auto-detect from Telegram language_code as default.
Save to preferred_language. All subsequent onboarding messages use user's language.

### [V2-005] CMS foundation
New DB table: bot_texts (key, language, content, updated_at).
New function: t(key, lang, **kwargs) with hard-coded fallback.
Migrate welcome and help strings first.

### [V2-006] Pension allocation field
Add pension_rate to user profile (default 0.0).
Update calculations.py, models.py, onboarding advanced settings.
Status command shows pension line if pension_rate > 0.

### [V2-007] NI / social savings fixed-monthly mode
Add national_insurance_mode + national_insurance_fixed columns.
Same for social_savings.
Add calculation branch. Update onboarding advanced settings.

### [V2-008] Admin: CMS text editor endpoints
GET /admin/texts, GET /admin/texts/{key}, PUT /admin/texts/{key}/{lang}.
Returns hard-coded fallback if key not in DB.
Validates non-empty content before saving.

### [V2-009] VAT period flag
Add vat_period column to users (monthly / bi-monthly, default monthly).
No calculation change yet — groundwork for period-aware reports.

### [V2-010] Status command enhancement
Show pension line if pension_rate > 0.
Show NI and social savings in correct mode (percentage vs fixed).
