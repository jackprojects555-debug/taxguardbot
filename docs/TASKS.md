# TASKS.md

Active and backlog tasks. Update status when work starts or completes.

---

## In Progress

### [PROD-001] Per-user onboarding and tax rate configuration
Status: In review
Branch: feature/prod-001-onboarding
PR: #6
Scope: BotUser model fields, onboarding state machine, bot routing, admin API exposure
Commits: A (model), B (wire rates), C (onboarding flow + tests), D (admin API)

---

## Done

### [ENG-001] Engineering migration — Phase 1: Documentation
Status: Complete
Merged: feature/engineering-migration → main

### [ENG-002] Engineering migration — Phase 2: Tooling
Status: Complete
Merged: feature/engineering-migration → main

---

## Backlog — Product

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
