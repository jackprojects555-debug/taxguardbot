# TASKS.md

Active and backlog tasks. Update status when work starts or completes.

---

## In Progress

### [ENG-001] Engineering migration — Phase 1: Documentation
Status: In progress
Branch: feature/engineering-migration
Scope: .env.example, PROJECT_SETUP.md, CLAUDE.md, .cursor/rules/, DECISIONS.md,
       PROJECT_STATE.md, TASKS.md, DEPLOYMENT.md

---

## Backlog — Engineering

### [ENG-002] Engineering migration — Phase 2: Tooling
Status: Not started
Scope:
- pyproject.toml (tooling config only — ruff, pytest settings)
- Makefile (setup, test, lint, format, check targets)
- .pre-commit-config.yaml (ruff hook)
- tests/test_calculations.py (unit tests for calculations.py)
- .github/workflows/tests.yml (CI pipeline, Python 3.12)
Prerequisite: ENG-001 merged

---

## Backlog — Product

### [PROD-001] Per-user onboarding and tax rate configuration
Status: Not started
Spec: MASTER_SPEC_V1.md sections 9, 10
Notes: Requires per-user fields on BotUser model. Tax rates currently hardcoded.
Prerequisite: ENG-002 complete (tests must exist before logic changes)

### [PROD-002] Transaction status tracking
Status: Not started
Spec: MASTER_SPEC_V1.md section 10.5
Notes: Add fields: status, saved_amount, remaining_amount, updated_at, canceled_at

### [PROD-003] Transfer confirmation commands
Status: Not started
Spec: MASTER_SPEC_V1.md section 10.4
Notes: `העברתי` (full), `העברתי {amount}` (partial)

### [PROD-004] Correction commands
Status: Not started
Spec: MASTER_SPEC_V1.md section 11
Notes: `תקן אחרון`, `בטל אחרון`, `תקן {id}`, `בטל {id}`

### [PROD-005] Automated reminders
Status: Not started
Spec: MASTER_SPEC_V1.md sections 12.2, 12.3
Notes: Mid-month (15th) and end-of-month reports. Requires scheduler.

### [PROD-006] Database migration
Status: Not started
Notes: Replace JSON file storage with a real database.
Prerequisite: PROD-001 or PROD-002 (schema clearer once user model is extended)
