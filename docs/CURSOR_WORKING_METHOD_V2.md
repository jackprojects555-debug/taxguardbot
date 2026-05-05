# CURSOR WORKING METHOD V2

## Goal

Minimize token usage and maximize precision and control when working with Cursor.

---

## Core Principle

Cursor executes code changes.
It does NOT think, plan, explore, or design.

All thinking happens outside Cursor.

---

## Fundamental Shift from V1

### V1 Approach
- Cursor reads docs
- Cursor gets full context
- Cursor “understands” the project

### V2 Approach
- Cursor receives a minimal, isolated task
- No docs, no exploration, no scanning
- Full control by the developer

---

## Golden Rules

### 1. Never reference docs

❌ Do NOT write:
"Open docs/PROMPT_V1.md"

✔ Instead:
Paste only the exact task into the chat

---

### 2. Always limit scope

Every prompt must begin with:

"Modify only [FILE]"

Example:
Modify only app/storage.py

---

### 3. Prevent project scanning

Always include:

"Do not inspect other files"

This avoids unnecessary token usage.

---

### 4. One task only

❌ Do NOT:
- combine features
- ask multiple changes

✔ DO:
- one change
- one purpose
- one file (if possible)

---

### 5. Keep prompts minimal

Remove:
- explanations
- background
- reasoning
- storytelling

Only include:
- task
- constraints
- output

---

### 6. Strict constraints

Always define boundaries:

- Do not change unrelated code
- Do not change APIs
- Do not add dependencies
- Do not refactor beyond scope

---

### 7. Define output format

Always include:

- "Return only diff"
OR
- "Return only updated function"
OR
- "Return full updated file"

---

## Standard Prompt Template


Modify only [FILE].

Do not inspect other files.

Task:
[ONE specific change]

Constraints:

Do not change unrelated code
Do not change APIs
Do not add dependencies
Keep change minimal

Output:
Return only diff.


---

## Ultra-Thin Prompt (Preferred)

When possible, use:


Modify only app/storage.py.

Do not inspect other files.

Task:
Add USER_TRANSACTIONS.clear() as first line in _load_from_file.

Do not change anything else.

Output:
Return only diff.


---

## When NOT to use Cursor

Do manually if:

- change is 1–3 lines
- editing text (CHANGELOG, README)
- editing prompts
- git operations
- obvious bug fix

---

## When TO use Cursor

- logic implementation
- parsing logic
- storage systems
- controlled refactoring
- repetitive code changes

---

## Workflow

1. Define task outside Cursor
2. Reduce to minimal prompt
3. Send to Cursor
4. Review diff
5. Test manually
6. Commit

---

## Red Flags (Stop Immediately)

If Cursor:

- modifies multiple files unexpectedly
- rewrites large code sections
- changes wording or labels
- ignores constraints
- produces long output

→ STOP

Rollback:


git restore [file]


---

## Token Efficiency Rules

### Target

- Small task: 2K–10K tokens
- Medium task: 10K–30K tokens

### Warning

- >50K tokens → inefficient
- >100K tokens → broken workflow

---

## Root Cause of High Token Usage

High usage is NOT caused by prompt length.

It is caused by:

- scanning multiple files
- loading docs
- excessive context

---

## Key Principle

Token usage = context size, not prompt size.

---

## Final Rule

Cursor is a tool, not a partner.

You define:
- what to do
- where to do it
- what not to touch

Cursor executes.

Nothing more.