# TASKS.md

Active and backlog tasks. Update status when work starts or completes.

---

## In Progress

### [PROD-002] Transaction status tracking
Status: In review
Branch: feature/prod-002-transaction-status
PR: #7
Scope: Transaction model fields, storage layer, מצב gap reporting, admin API
Commits: A (model + storage + tests), B (bot + admin API)

---

## Done

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

## Backlog — Product

### [PROD-002] Transaction status tracking
Status: In progress — see In Progress section above

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
