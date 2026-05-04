# CURSOR WORKING METHOD V1 (EXECUTION GRADE)

## Core Principle

Cursor executes.
It does not decide.

All intelligence must exist in the prompt.

---

## Single Source of Truth

SPEC defines:
- what to build

PROMPT defines:
- how to build it

Cursor:
- executes only

---

## Absolute Rules

1. One task per prompt
2. One responsibility per change
3. One scope per execution
4. No vague language
5. No open-ended requests

If a prompt violates ANY of these → do not send

---

## Token Efficiency System

### Hard Limits

- Max files referenced: 2
- Max functions touched: 2
- No full project context
- No unnecessary code blocks

---

### Context Decision Matrix

Use EXACTLY this:

| Task Type | What to Send |
|----------|-------------|
| Small fix | description only |
| Function change | function only |
| File logic change | file |
| Structural change | file + short description |
| Multi-file | file names only |

---

## Prompt Structure (MANDATORY)

Every prompt MUST be:

### Context
Current system state in 1–2 lines

### Task
Single explicit instruction

### Scope
Exact files/functions allowed

### Constraints
What must NOT change

### Output
Exact expected format

---

## Prompt Quality Test (BEFORE SENDING)

A prompt is valid ONLY if:

- Can a junior dev execute it?
- Is the task measurable?
- Is output format defined?
- Is scope limited?

If ANY answer is NO → rewrite

---

## Execution Flow (STRICT)

1. Define SPEC
2. Break into micro tasks
3. For each task:
   - write prompt
   - validate prompt
   - run in Cursor
   - test locally
   - commit immediately

NO batching

---

## Commit Discipline

Every Cursor run = commit

Format:

git add .
git commit -m "atomic change: <exact description>"

---

## Cursor Usage Rules

### Use Cursor for:

- implementation
- targeted refactor
- repetitive code

### Do NOT use Cursor for:

- architecture
- product decisions
- debugging unknown issues

---

## File Handling Rules

### Never send full file if:

- change < 20 lines
- function is isolated

### Always send full file if:

- structure changes
- multiple internal dependencies
- unclear boundaries

---

## Anti-Waste Rules

NEVER:

- "improve code"
- "optimize"
- "make it cleaner"
- "refactor everything"

ALWAYS:

- define exact change
- define limits
- define output

---

## Prompt Templates

### 1. Fix

Context:
We have a function handling X.

Task:
Fix Y.

Scope:
Modify only function Z in file A.

Constraints:
Do not change logic outside Z.

Output:
Return updated function only.

---

### 2. Feature

Context:
System currently does X.

Task:
Add Y.

Scope:
Modify file A only.

Constraints:
Do not change existing behavior.

Output:
Return full updated file.

---

### 3. Refactor

Context:
Code has duplication in X.

Task:
Refactor X.

Scope:
Modify only X.

Constraints:
Behavior must remain identical.

Output:
Return updated code only.

---

## Pre-Send Checklist (MANDATORY)

Before EVERY prompt:

- Is task atomic?
- Is scope minimal?
- Is output defined?
- Is change measurable?

If ANY answer = NO → STOP

---

## Failure Protocol

If Cursor output is wrong:

1. DO NOT re-run blindly
2. Identify failure:
   - bad context?
   - bad scope?
   - vague task?
3. Fix prompt
4. Re-run

---

## Role System

Jack:
- decides WHAT

Assistant:
- defines PROMPT

Cursor:
- executes

---

## Final Rule

Efficiency is not about fewer prompts.
It is about correct prompts.

Bad prompt = exponential waste
Good prompt = linear progress