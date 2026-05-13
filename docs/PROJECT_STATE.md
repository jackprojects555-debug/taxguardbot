# PROJECT_STATE.md

Current state of the TaxGuardBot project. Update this file when state changes meaningfully.

---

## Status

Active. V2-001 through V2-010 complete and merged to main. All V2 Core tasks done.

## Version

v2.0 (post V2-010)

## Active Branch

main

---

## What Works

### Bot commands (user-facing)

| Input (Hebrew) | Input (English) | Action |
|---|---|---|
| `11700` / `₪11,700` | same | Record income, calculate all allocations, reply with breakdown |
| `11700 נוכה` | `11700 vat excluded` | Same but treat amount as VAT-excluded |
| `העברתי` | `saved` | Mark full remaining balance as saved on latest open transaction |
| `העברתי 4000` | `saved 4000` | Mark partial amount as saved |
| `מצב` | `status` | Current-month summary: income, VAT, taxes, pension, to-save, saved, gap, available |
| `אחרון` | `last` | Details of last non-canceled transaction |
| `רשימה` | `list` | List transactions this month |
| `עזרה` | `help` | Full command list (language-aware) |
| `בטל אחרון` | `cancel last` | Cancel most recent non-canceled transaction |
| `בטל 3` | `cancel 3` | Cancel transaction #3 |
| `תקן אחרון 23400` | `fix last 23400` | Correct amount on last transaction, recalculate |
| `תקן 2 23400` | `fix 2 23400` | Correct amount on transaction #2, recalculate |
| `אפס` / `נקה` / `מחק` | `reset` / `clear` | Clear all transactions for this user |

### Onboarding flow

New users are walked through a 6-step state machine on first message:
1. Business type: עוסק מורשה (VAT-registered) or עוסק פטור (VAT-exempt)
2. VAT included default (skipped for VAT-exempt)
3. Income tax rate (e.g., 20 or 0.20)
4. National insurance — percentage (e.g., 8) or fixed monthly amount (e.g., 1200 חודשי)
5. Social savings — percentage or fixed monthly amount
6. Pension rate (e.g., 6 or 0.06) — send 0 to skip

Language is auto-detected from Telegram locale; each step responds in the user's language.

### Scheduled reports (automated, no user trigger)

- **15th of month at 09:00 Asia/Jerusalem** — mid-month report
- **Last day of month at 09:00 Asia/Jerusalem** — end-of-month report
- Users with no active transactions that month are skipped silently

### Admin server (operator-facing, port 8080)

- `GET /health`
- `GET /admin/users` — list all users
- `POST /admin/users` — create/replace user (supports `vat_period`)
- `PATCH /admin/users/{id}` — update user fields (rates, block status, modes, vat_period, etc.)
- `DELETE /admin/users/{id}` — delete user record
- `GET /admin/users/{id}/transactions` — list user's transactions
- `GET /admin/messages` — get all message templates
- `PUT /admin/messages` — replace message templates (hot-reload, no restart needed)
- `GET /admin/texts` — list all DB text overrides
- `GET /admin/texts/{key}` — get all language variants for a key (DB + defaults)
- `PUT /admin/texts/{key}/{lang}` — set a CMS override for a key/language
- `DELETE /admin/texts/{key}/{lang}` — remove a CMS override (falls back to default)
- `GET /admin/ui` — single-page HTML dashboard

---

## Data Models

### Transaction (app/models.py)

| Field | Type | Notes |
|---|---|---|
| `amount` | float | Total invoice amount |
| `vat_included` | bool | Whether VAT was included in input |
| `vat_amount` | float | Calculated VAT |
| `base_amount` | float | Pre-VAT amount |
| `income_tax_amount` | float | |
| `national_insurance_amount` | float | Computed from mode (percentage or fixed) |
| `social_savings_amount` | float | Computed from mode (percentage or fixed) |
| `pension_amount` | float | base_amount × pension_rate; 0 if no pension |
| `total_to_save` | float | Sum of all allocations |
| `remaining_amount` | float | total_to_save minus what's been saved |
| `available_amount` | float | base_amount minus total_to_save (spendable) |
| `month` | str | `"YYYY-MM"` |
| `created_at` | datetime | |
| `id` | int | Per-user, 1-indexed, assigned on insert |
| `status` | str | `open` / `partially_saved` / `fully_saved` / `canceled` |
| `saved_amount` | float | Cumulative amount confirmed transferred |
| `updated_at` | datetime? | Set on any mutation |
| `canceled_at` | datetime? | Set on cancel |

### BotUser (app/user_storage.py)

| Field | Type | Default | Notes |
|---|---|---|---|
| `telegram_user_id` | int | required | |
| `username` | str? | None | |
| `display_name` | str? | None | |
| `is_blocked` | bool | False | |
| `onboarding_completed` | bool | False | |
| `onboarding_step` | str? | None | Active step name during flow |
| `profile_notified` | bool | False | One-time notification flag |
| `business_type` | str | `vat_registered` | or `vat_exempt` |
| `vat_period` | str | `monthly` | or `bi_monthly` — groundwork for period-aware reports |
| `vat_included_default` | bool | True | False for vat_exempt |
| `income_tax_rate` | float | 0.20 | |
| `national_insurance_rate` | float | 0.08 | Used when mode=percentage |
| `national_insurance_mode` | str | `percentage` | or `fixed` |
| `national_insurance_fixed` | float | 0.0 | Used when mode=fixed |
| `social_savings_rate` | float | 0.05 | Used when mode=percentage |
| `social_savings_mode` | str | `percentage` | or `fixed` |
| `social_savings_fixed` | float | 0.0 | Used when mode=fixed |
| `pension_rate` | float | 0.0 | 0 = no pension allocation |
| `preferred_language` | str | `he` | `he` or `en` |

---

## Module Map

| Module | Responsibility |
|---|---|
| `app/bot.py` | Telegram handler, command routing, JobQueue wiring |
| `app/calculations.py` | `calculate_income_split()` — pure math, supports all modes |
| `app/models.py` | `Transaction` dataclass |
| `app/storage.py` | Transaction CRUD (SQLite/PostgreSQL) |
| `app/user_storage.py` | `BotUser` CRUD (SQLite/PostgreSQL) |
| `app/database.py` | DB connection, schema init, idempotent migrations |
| `app/onboarding.py` | 6-step onboarding state machine, bilingual |
| `app/command_registry.py` | Command parsing — Hebrew + English aliases, income parser |
| `app/cms.py` | `t(key, lang)` — DB override layer with message_store fallback |
| `app/transfers.py` | `process_transfer()` — full/partial transfer logic |
| `app/corrections.py` | show_last, show_list, cancel, correct |
| `app/reminders.py` | Report builders + async send callbacks |
| `app/message_store.py` | Default message templates (Hebrew + English), hot-reload |
| `app/admin_server.py` | FastAPI admin API (users, messages, CMS texts) |

---

## Database

- **Local dev**: SQLite at `data/taxguard.db` (no `DATABASE_URL` in `.env`)
- **Production**: PostgreSQL via psycopg2-binary (set `DATABASE_URL` to Neon connection string)
- Schema managed by idempotent `_MIGRATIONS` list in `app/database.py` (try/except per column)
- `data/` directory is gitignored — never commit

---

## Message Keys (app/message_store.py)

### Core
- `transaction_success_he` — income recorded confirmation (includes pension_line if set)
- `status_summary_he` — מצב/status output (includes NI/SS mode labels, pension line)
- `status_no_data_he` — no data this month
- `invalid_number_en`, `unsupported_format_en`, `amount_must_be_positive_en`
- `reset_success_en`, `user_blocked_he`

### Help
- `help_he`, `help_en` — full bilingual command lists

### Onboarding
- `onboarding_welcome_he/en`, `onboarding_ask_vat_included_he/en`
- `onboarding_ask_income_tax_he/en`, `onboarding_ask_national_insurance_he/en`
- `onboarding_ask_social_savings_he/en`, `onboarding_ask_pension_he/en`
- `onboarding_complete_he/en`
- `onboarding_invalid_business_type_he/en`, `onboarding_invalid_yes_no_he/en`
- `onboarding_invalid_rate_he/en`, `onboarding_invalid_rate_or_fixed_he/en`
- `profile_notified_he`

### Transfers
- `transfer_full_success_he`, `transfer_partial_success_he`
- `transfer_no_open_he`, `transfer_invalid_amount_he`

### Corrections
- `no_transactions_he`, `transaction_not_found_he`
- `transaction_already_canceled_he`, `transaction_canceled_cannot_correct_he`
- `cancel_success_he`, `correction_invalid_amount_he`, `correction_success_he`
- `transaction_detail_he` — אחרון output
- `list_header_he`, `transaction_list_row_he` — רשימה output

### Reports
- `midmonth_report_he` — 15th automated report
- `endmonth_report_he` — end-of-month automated report

---

## Tests

325 tests across 13 files, all passing:

| File | Count | Covers |
|---|---|---|
| `tests/test_calculations.py` | 29 | Income split, all modes, pension, edge cases |
| `tests/test_cms.py` | 16 | `t()`, `get_text`, `set_text`, `delete_text`, `list_texts` |
| `tests/test_command_registry.py` | 56 | Hebrew + English parsing, income formats, edge cases |
| `tests/test_corrections.py` | 24 | show_last, show_list, cancel, correct |
| `tests/test_help.py` | 5 | Help command bilingual output |
| `tests/test_onboarding.py` | 59 | Full flows (both paths), fixed mode, pension, invalid inputs |
| `tests/test_reminders.py` | 14 | Report builders: empty, canceled, aggregation, gap |
| `tests/test_status.py` | 13 | Status formatting: pension line, NI/SS mode labels |
| `tests/test_storage.py` | 21 | Transaction CRUD, backward compat, ID assignment |
| `tests/test_transfers.py` | 21 | Full/partial transfer, capping, error cases |
| `tests/test_user_storage.py` | 35 | BotUser defaults, backward compat, CRUD, vat_period |
| `tests/test_admin_texts.py` | 26 | CMS text CRUD endpoints |
| `tests/test_admin_users.py` | 6 | Admin user API, vat_period field |

Run with: `make test` or `pytest`

---

## Known Issues (found during first real-user test)

- **Onboarding welcome is abrupt** — jumps straight to business type question without explaining what the bot does
- **No "ערוך" / settings command** — no way to edit profile (tax rates, modes) after onboarding completes
- **No escape commands during onboarding** — typing "help" mid-flow is treated as an invalid onboarding answer
- **Responses not fully bilingual** — English commands work but most replies are hardcoded Hebrew (`_he` keys)

---

## What Is Not Yet Built

- Settings/edit command (`ערוך`) to update profile after onboarding
- Improved onboarding intro message
- Full bilingual responses (English users get Hebrew replies)
- Escape commands during onboarding
- Website layer
- Accountant export reports (spec section 12.4 — post-MVP)
