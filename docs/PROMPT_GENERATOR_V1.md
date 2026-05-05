# PROMPT GENERATOR V1

## Goal

Generate minimal, precise, low-token prompts for Cursor.

---

## Instructions

Fill the fields below, then copy the generated prompt to Cursor.

---

## INPUT

FILE:
[example: app/storage.py]

TASK:
[one exact action]

FUNCTION (optional):
[specific function name]

CONSTRAINTS:
- Do not change unrelated code
- Do not change APIs
- Do not add dependencies
- Keep change minimal

OUTPUT TYPE:
[diff / function / full file]

---

## GENERATED PROMPT

Modify only [FILE].

Do not inspect other files.

Task:
[TASK]

[IF FUNCTION EXISTS]
Apply only inside function: [FUNCTION]

Constraints:
- Do not change unrelated code
- Do not change APIs
- Do not add dependencies
- Keep change minimal

Output:
Return only [OUTPUT TYPE].