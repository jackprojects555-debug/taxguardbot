# TASKS.md

Active and backlog tasks. Update status when work starts or completes.

---

## In Progress

### [PROD-004] Correction commands
Status: In review
Branch: feature/prod-004-correction-commands
PR: #10
Scope: show_last, show_list, cancel, correct — bot commands + tests
Commits: A (corrections module + tests), B (bot wiring)

---

## Done

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

## Backlog — Product

### [PROD-004] Correction commands
Status: In review — see In Progress section above

### [PROD-005] Automated reminders
Status: Not started
Spec: MASTER_SPEC_V1.md sections 12.2, 12.3
Notes: Mid-month (15th) and end-of-month reports. Requires scheduler.

### [PROD-006] Database migration
Status: Not started
Notes: Replace JSON file storage with a real database.
Prerequisite: PROD-001 or PROD-002 (schema clearer once user model is extended)
