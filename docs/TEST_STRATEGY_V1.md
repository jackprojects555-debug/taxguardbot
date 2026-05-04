# TEST STRATEGY V1 - TaxGuardBot

## Goal

Ensure the bot behaves correctly across core flows:
- input parsing
- validation
- calculation
- storage
- monthly summary

---

## Testing Types

### 1. Manual Testing (Primary)

Used for:
- user flows
- UX validation
- edge cases

---

### 2. Automated Testing (Future)

Not implemented yet.

Will include:
- calculation tests
- parsing tests
- validation tests

---

## Core Test Scenarios

### Valid Inputs

- 11700
- 11,700
- ₪11,700
- 11 700
- 11700.50
- 11700 נוכה
- 11,700 נוכה

Expected:
- correct calculation
- correct response format

---

### Invalid Inputs

- abc
- ""
- 11k
- -500
- 0

Expected:
- clear error message
- no crash

---

### Edge Cases

- " 11,700 "
- "₪ 11,700"
- "11,700₪"
- multiple spaces

Expected:
- correctly parsed

---

### Monthly Behavior

1. Add multiple transactions
2. Ensure "מצב" shows totals
3. (future) test across months

---

## Regression Rule

After every change:

1. Run bot
2. Test:
   - one valid input
   - one invalid input
   - "מצב"

If any fail → do not commit

---

## Failure Handling

If bug found:

1. Reproduce
2. Define case
3. Fix with Cursor
4. Re-test
5. Commit

---

## Principle

Testing is not optional.

Every feature must be verified before commit.