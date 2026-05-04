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

---

# PROMPT V1 - TASK 2: Robust Input Parsing

## Context

We have a working Telegram bot in app/bot.py.

Current behavior:
- Supports numeric input like "11700"
- Supports comma-separated numbers like "11,700"
- Supports VAT-excluded input using "נוכה"

---

## Task

Improve input parsing to support real-world user inputs.

The bot must correctly handle:

- " 11,700 "
- "11 700"
- "₪11,700"
- "11700₪"
- "11,700 נוכה"
- combinations of the above

---

## Scope

Modify only:
- app/bot.py

---

## Constraints

- Do NOT modify app/calculations.py
- Do NOT change calculation logic
- Do NOT change response format
- Do NOT remove support for "נוכה"
- Do NOT add new dependencies
- Keep changes minimal and focused

---

## Expected Behavior

All valid numeric inputs with spaces, commas or currency symbols
must be correctly parsed into a float.

---

## Output

Return the full updated app/bot.py file only.

---

# PROMPT V1 - TASK 3: Input Validation & Error Handling

## Context

We have a Telegram bot that parses numeric income input.

Current behavior:
- Accepts numbers and formatted numbers
- Returns a generic error message on invalid input

---

## Task

Improve validation and error handling.

The bot must:

1. Reject non-numeric input with clear message
2. Reject negative values
3. Accept decimal values (e.g. "11700.50")
4. Reject shorthand formats (e.g. "11k")
5. Provide specific error messages

---

## Scope

Modify only:
- app/bot.py

---

## Constraints

- Do NOT modify app/calculations.py
- Do NOT change calculation logic
- Do NOT change valid input behavior
- Do NOT add new dependencies

---

## Expected Behavior

Examples:

"abc" → "Invalid input. Please enter a number."
"-500" → "Amount must be positive."
"11k" → "Unsupported format. Please enter full number."
"11700.50" → accepted

---

## Output

Return the full updated app/bot.py file only.