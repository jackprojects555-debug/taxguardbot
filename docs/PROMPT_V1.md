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

---

# PROMPT V1 - TASK 4: Monthly Tracking

## Context

We store transactions per user in memory.
Each transaction includes a created_at timestamp.

---

## Task

Update the "מצב" command to return only transactions from the current month.

---

## Scope

Modify only:
- app/bot.py

---

## Constraints

- Do NOT modify storage structure
- Do NOT modify calculations
- Do NOT change how transactions are saved
- Use existing created_at field

---

## Expected Behavior

If user has transactions across months:
"מצב" should show only current month totals.

---

## Output

Return updated parts of app/bot.py only.

---

# PROMPT V1.1 - TASK 1: Reset Command

## Context

We store transactions per user in memory.

Users currently cannot reset or clear their data.

---

## Task

Add a new command:

"reset"

When user sends "reset":
- all their stored transactions must be deleted

---

## Scope

Modify only:
- app/bot.py
- app/storage.py

---

## Constraints

- Do NOT modify calculations
- Do NOT change transaction structure
- Do NOT affect other users' data

---

## Expected Behavior

User sends:
"reset"

System:
- clears their data
- responds: "All data has been reset."

---

## Output

Return updated parts of files only.

---

# PROMPT V1.1 - TASK 2: Reset Command Variations

## Context

We already support "reset" command to clear user data.

---

## Task

Extend reset command to support multiple variations:

- "reset"
- "Reset"
- "אפס"
- "נקה"
- "מחק"

All must trigger the same behavior.

---

## Scope

Modify only:
- app/bot.py

---

## Constraints

- Do NOT modify storage
- Do NOT change reset logic
- Only extend input matching
- Keep implementation simple

---

## Expected Behavior

Any of the above inputs:
→ clears data
→ returns: "All data has been reset."

---

## Output

Return updated parts of app/bot.py only.

---

# PROMPT V1.1 - TASK 3: UX Improvement (STRICT)

## Context

We have a working Telegram bot in app/bot.py.
Messages must remain EXACTLY the same in wording.

---

## Task

Improve visual formatting ONLY.

---

## Scope

Modify only:
- response strings inside handle_message

---

## Constraints (CRITICAL)

- Do NOT change ANY existing words
- Do NOT rename ANY labels
- Do NOT translate or rephrase anything
- Do NOT remove any lines
- Do NOT add new sentences
- Only add spacing (newlines) if needed

---

## Required Changes

1. Improve spacing between sections
2. Add consistent blank lines where helpful
3. Keep original text EXACTLY as is

---

## Output

Return updated handle_message function only.

---

# PROMPT V1.1 - TASK 4: Better Summary (STRICT)

## Context

We have a "מצב" command that returns summary totals.

---

## Task

Extend the summary to include additional aggregated fields.

---

## Scope

Modify only:
- summary response inside handle_message in app/bot.py

---

## Constraints

- Do NOT change existing wording
- Do NOT rename existing labels
- Do NOT remove existing lines
- Do NOT change order of existing fields
- Only ADD new lines for additional totals

---

## Required Additions

Add totals for:

- VAT (מע״מ)
- Income tax (מס הכנסה)
- National insurance (ביטוח לאומי)
- Social savings (סוציאליות)

Each must be summed from transactions.

---

## Placement

Insert new totals in the "מצב" response,
between existing breakdown and totals sections.

---

## Output

Return updated handle_message function only.

---

# PROMPT V1.1 - TASK 5: Basic Persistence (STRICT)

## Context

Transactions are currently stored in memory in USER_TRANSACTIONS.

---

## Task

Add simple JSON file persistence.

---

## Scope

Modify only:
- app/storage.py

---

## Constraints (CRITICAL)

- Do NOT change existing function names
- Do NOT change transaction structure
- Do NOT modify bot logic
- Do NOT add external dependencies
- Keep storage API identical

---

## File Requirements

- Use a single JSON file:
  data/transactions.json

- Structure:

{
  "user_id": [
    {transaction},
    ...
  ]
}

---

## Required Behavior

1. On add_transaction:
   - update memory
   - write full data to file

2. On get_transactions:
   - read from memory (NOT file)

3. On startup:
   - load file into memory once

4. On clear_transactions:
   - update memory
   - update file

---

## Implementation Notes

- Use built-in json module
- Ensure file is created if not exists
- Handle empty file safely

---

## Output

Return updated storage.py only.

---

# PROMPT V1.1 - TASK 5.1: Persistence Fix (Reload Safety)

## Context

Persistence was implemented in storage.py.

---

## Task

Ensure safe reload behavior.

---

## Scope

Modify only:
- app/storage.py

---

## Constraints

- Do NOT change existing APIs
- Do NOT change JSON structure
- Do NOT change persistence logic

---

## Required Changes

1. Add USER_TRANSACTIONS.clear() at the start of _load_from_file
2. Ensure file ends with newline

---

## Output

Return updated storage.py only.
