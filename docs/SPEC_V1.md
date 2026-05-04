# SPEC V1 - TaxGuardBot

## Product Definition

User inputs income and gets how much to set aside per income.

---

## Core Flow

1. User sends income amount
2. System calculates:
   - VAT (if applicable)
   - Income tax
   - National insurance
   - Social savings
3. System returns:
   - total to set aside
   - net available
   - action instruction

---

## Supported Inputs

- Number only: 11700
- VAT excluded: "11700 נוכה"

---

## System Behavior

- Each input is treated as a transaction
- Each transaction is saved per user
- System maintains running totals

---

## Commands

### מצב

Returns:
- total income
- total to set aside
- total available

---

## Data Model

Transaction includes:
- amount
- vat_included
- vat_amount
- base_amount
- income_tax_amount
- national_insurance_amount
- social_savings_amount
- total_to_save
- available_amount
- created_at

---

## Constraints

- No bank integration
- No automation of payments
- No external APIs

---

## Architecture Rule

System must allow future:
- expense tracking
- automation
- integrations

Without breaking existing logic