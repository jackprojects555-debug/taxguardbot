# TASKS.md

Active and backlog tasks. Update status when work starts or completes.

---

## In Progress

### [PROD-005] Automated reminders
Status: In review
Branch: feature/prod-005-reminders
Scope: mid-month (15th) and end-of-month reports via PTB JobQueue
Commits: A (report builders + message keys + tests), B (bot wiring)

---

## Done

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

## Backlog — Product

### [PROD-005] Automated reminders
Status: In review — see In Progress section above

### [PROD-006] Database migration
Status: Not started
Notes: Replace JSON file storage with a real database.
Prerequisite: PROD-001 or PROD-002 (schema clearer once user model is extended)
