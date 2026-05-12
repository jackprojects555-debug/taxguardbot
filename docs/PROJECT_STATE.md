# PROJECT_STATE.md

Current state of the TaxGuardBot project. Update this file when state changes meaningfully.

---

## Status

Active. PROD-001 through PROD-005 complete and merged to main.
Next: PROD-006 (database migration).

## Version

v1.5 (post PROD-005)

## Active Branch

main

---

## What Works

### Bot commands (user-facing)

| Input | Action |
|---|---|
| `11700` / `11,700` / `₪11700` | Record income, calculate VAT + taxes, reply with breakdown |
| `11700 נוכה` | Same but treat amount as VAT-excluded |
| `העברתי` | Mark full remaining balance as saved on latest open transaction |
| `העברתי 4000` | Mark partial amount as saved on latest open transaction |
| `מצב` | Current-month summary: income, VAT, taxes, to-save, saved, gap, available |
| `אחרון` | Show details of last non-canceled transaction |
| `רשימה` | List last 5 transactions this month, most recent first |
| `בטל אחרון` | Cancel the most recent non-canceled transaction |
| `בטל 3` | Cancel transaction #3 |
| `תקן אחרון 23400` | Correct amount on last non-canceled transaction, recalculate |
| `תקן 2 23400` | Correct amount on transaction #2, recalculate |
| `reset` / `אפס` / `נקה` / `מחק` | Clear all transactions for this user |

### Onboarding flow

New users are walked through a 4-5 step state machine on first message:
1. Business type: עוסק מורשה (VAT-registered) or עוסק פטור (VAT-exempt)
2. VAT included default (skipped for exempt)
3. Income tax rate (e.g., 20 or 0.20)
4. National insurance rate
5. Social savings rate

Existing users with pre-onboarding records get a one-time profile notification and skip the flow.

### Scheduled reports (automated, no user trigger)

- **15th of month at 09:00 Asia/Jerusalem** — mid-month report: income, to-save, saved, open gap
- **Last day of month at 09:00 Asia/Jerusalem** — end-of-month report: full breakdown including VAT, income tax, national insurance, social savings
- Users with no active transactions that month are skipped silently

### Admin server (operator-facing, port 8080)

- `GET /health`
- `GET /admin/users` — list all users
- `POST /admin/users` — create/replace user
- `PATCH /admin/users/{id}` — update user fields (rates, block status, onboarding, etc.)
- `DELETE /admin/users/{id}` — delete user record
- `GET /admin/users/{id}/transactions` — list user's transactions
- `GET /admin/messages` — get all message templates
- `PUT /admin/messages` — replace message templates (hot-reload, no restart needed)
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
| `national_insurance_amount` | float | |
| `social_savings_amount` | float | |
| `total_to_save` | float | Sum of all tax allocations |
| `remaining_amount` | float | total_to_save minus what's been saved |
| `available_amount` | float | base_amount minus taxes (spendable) |
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
| `onboarding_completed` | bool | False | True for pre-onboarding records |
| `onboarding_step` | str? | None | Active step name during flow |
| `profile_notified` | bool | False | One-time notification flag |
| `business_type` | str | `vat_registered` | or `vat_exempt` |
| `vat_included_default` | bool | True | False for vat_exempt |
| `income_tax_rate` | float | 0.20 | |
| `national_insurance_rate` | float | 0.08 | |
| `social_savings_rate` | float | 0.05 | |

---

## Module Map

| Module | Responsibility |
|---|---|
| `app/bot.py` | Telegram handler, command routing, JobQueue wiring |
| `app/calculations.py` | `calculate_income_split()` — pure math |
| `app/models.py` | `Transaction` dataclass |
| `app/storage.py` | Transaction CRUD + JSON persistence |
| `app/user_storage.py` | `BotUser` CRUD + JSON persistence |
| `app/onboarding.py` | Onboarding state machine |
| `app/transfers.py` | `process_transfer()` — full/partial transfer logic |
| `app/corrections.py` | show_last, show_list, cancel, correct |
| `app/reminders.py` | Report builders + async send callbacks |
| `app/message_store.py` | Hebrew message templates, hot-reload from disk |
| `app/admin_server.py` | FastAPI admin API + HTML dashboard |

---

## Message Keys (app/message_store.py)

### Core
- `transaction_success_he` — income recorded confirmation
- `status_summary_he` — מצב output
- `status_no_data_he` — no data this month
- `invalid_input_empty_en`, `invalid_number_en`, `unsupported_format_en`, `amount_must_be_positive_en`
- `reset_success_en`
- `user_blocked_he`

### Onboarding
- `onboarding_welcome_he`, `onboarding_ask_vat_included_he`, `onboarding_ask_income_tax_he`
- `onboarding_ask_national_insurance_he`, `onboarding_ask_social_savings_he`, `onboarding_complete_he`
- `onboarding_invalid_business_type_he`, `onboarding_invalid_yes_no_he`, `onboarding_invalid_rate_he`
- `profile_notified_he`

### Transfers
- `transfer_full_success_he`, `transfer_partial_success_he`, `transfer_no_open_he`, `transfer_invalid_amount_he`

### Corrections
- `no_transactions_he`, `transaction_not_found_he`, `transaction_already_canceled_he`
- `transaction_canceled_cannot_correct_he`, `cancel_success_he`
- `correction_invalid_amount_he`, `correction_success_he`
- `transaction_detail_he` — אחרון output
- `list_header_he`, `transaction_list_row_he` — רשימה output

### Reports
- `midmonth_report_he` — 15th automated report
- `endmonth_report_he` — end-of-month automated report

---

## Storage

- `data/transactions.json` — per-user transaction lists, keyed by user ID string
- `data/users.json` — all registered users
- `data/messages.json` — editable message templates (hot-reload)
- All files gitignored. Never commit.

---

## Tests

163 tests across 6 files, all passing:

| File | Count | Covers |
|---|---|---|
| `tests/test_user_storage.py` | 28 | BotUser defaults, backward compat, CRUD |
| `tests/test_onboarding.py` | 31 | Full flows, invalid input, VAT-exempt path |
| `tests/test_storage.py` | 28 | Transaction CRUD, backward compat, ID assignment |
| `tests/test_transfers.py` | 21 | Full/partial transfer, capping, error cases |
| `tests/test_corrections.py` | 24 | show_last, show_list, cancel, correct — all edge cases |
| `tests/test_reminders.py` | 14 | Report builders: empty, canceled, aggregation, gap |

Run with: `make test` or `pytest`

---

## Known Technical Debt

- Two-process data consistency gap: bot and admin server share JSON files with no locking (see DECISIONS.md #003)
- No data backup strategy (see DECISIONS.md #002)
- `ADMIN_TOKEN` must be exported manually — not loaded from `.env` (see DECISIONS.md #007)
- JSON file storage — PROD-006 will replace with a real database

---

## What Is Not Yet Built

- Database migration (PROD-006)
- Website layer
- Accountant export reports (spec section 12.4 — post-MVP)
