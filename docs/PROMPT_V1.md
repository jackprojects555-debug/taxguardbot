# PROMPT V1 - TASK 1: Comma Parsing

## Context

We have an existing Telegram bot implemented in app/bot.py.

Current behavior:
- Accepts numeric input like "11700"
- Supports VAT-excluded input using the Hebrew keyword "נוכה"
- Uses calculate_income_split from app/calculations.py

The system is already working correctly and must not be broken.

---

## Task

Add support for comma-separated numbers.

The bot must correctly handle:
- "11,700"
- "11,700 נוכה"

---

## Scope

Modify only:
- app/bot.py

---

## Constraints

- Do NOT modify app/calculations.py
- Do NOT change calculation logic
- Do NOT change response format
- Do NOT remove or alter "נוכה" handling
- Do NOT add new dependencies
- Do NOT refactor unrelated code

---

## Expected Behavior

Before:
"11,700" → error

After:
"11,700" → treated as 11700

---

## Output

Return the full updated app/bot.py file only.