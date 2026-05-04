# MASTER_SPEC_V1.md

# TaxGuard Bot — Master Product Specification V1

## 1. Document Purpose

This document defines the first professional specification for the TaxGuard Bot MVP.

The purpose of this document is to create one clear source of truth for the product, including the problem, target users, user experience, operational model, data structure, MVP scope, and future expansion.

This document should be used by the founder, product manager, developer, AI builder, or any future team member working on the product.

---

## 2. Product Name

Working name: **TaxGuard Bot**

The name is temporary and may change later.

---

## 3. Product Definition

TaxGuard Bot is a Telegram bot for independent workers and small business owners.

The bot helps users separate money that is not truly available for personal or business use, such as VAT, income tax, national insurance, and social savings allocations.

The bot does not hold money, does not transfer money, does not connect to bank accounts, and does not provide formal tax advice in the MVP stage.

Its first purpose is behavioral: when income enters the user’s account, the bot immediately calculates how much should be set aside and pushes the user to perform the separation manually.

---

## 4. Core Problem

Independent workers often receive income into their bank account as one amount.

That amount may include VAT and may also create future obligations for income tax, national insurance, and other savings or social allocations.

Because the money enters as one visible balance, users may mistakenly treat the entire amount as available.

The real problem is not only lack of income. The real problem is lack of immediate separation at the moment the income is received.

The product solves this by creating a simple real-time trigger: income received → calculation → instruction to separate → confirmation of action.

---

## 5. Target User

The first target user is an independent worker or small business owner who receives income during the month and needs help separating money for future obligations.

Primary target users:

* Licensed independent workers / VAT-registered businesses
* Exempt independent workers
* Freelancers
* Consultants
* Service providers
* Small business owners with irregular income

The product is not initially intended for complex companies, accountants, or users who need full accounting software.

---

## 6. MVP Philosophy

The MVP must be very narrow.

The product should not start as a fintech infrastructure company.

The MVP should test one core behavioral question:

**When a user receives income and immediately sees how much is not truly available, will the user separate the money?**

The MVP must avoid unnecessary complexity:

* No open banking
* No bank integration
* No money custody
* No payment execution
* No trust account
* No automatic tax filing
* No full accounting system

The MVP should focus on speed, clarity, and behavioral validation.

---

## 7. Core Product Loop

The core loop is the heart of the product.

1. The user receives income.
2. The user sends the income amount to the Telegram bot.
3. The bot calculates the required allocations.
4. The bot shows the user how much should be saved and how much is actually available.
5. The user transfers the required amount manually to a separate savings account or designated place.
6. The user confirms whether the transfer was made fully, partially, or not yet.
7. The bot stores the transaction and updates the monthly status.

If this loop works, the product has potential.

If users do not report income or do not act after receiving the calculation, the product must be reconsidered.

---

## 8. Product Stages

The product has three main user-facing stages:

1. Registration / onboarding
2. Ongoing operation
3. Reports

There is also a horizontal correction layer that must apply across the product.

The correction layer allows the user to change profile settings and correct individual income entries.

All information must be organized by calendar month.

---

## 9. Registration / Onboarding

### 9.1 Goal

The goal of registration is to create a basic user profile that allows the bot to calculate allocations.

The onboarding must be short and clear.

The user should not feel like they are filling out a tax form.

### 9.2 Required Questions

The bot should ask the following questions:

1. What type of business are you?

   * VAT-registered / licensed business
   * VAT-exempt business

2. Do the amounts you usually send include VAT?

   * Yes
   * No / VAT already deducted

3. What amount should be allocated for income tax?

   * Percentage-based allocation
   * Default option: 20%
   * Other common options: 10%, 30%, custom

4. What amount should be allocated for national insurance?

   * Percentage-based allocation, or
   * Fixed monthly target, e.g., ₪500 per month

5. What amount should be allocated for social savings?

   * Percentage-based allocation, or
   * Fixed monthly target

6. Do you have a separate account or destination for saving tax money?

   * Yes
   * No

### 9.3 Pre-Use Step

After onboarding, the bot must explain that the product only works if the user has a place to move the money.

If the user has no separate account or destination, the bot should recommend creating one.

The bot does not need to store the actual bank account details in the MVP.

Example message:

“Before you start, choose a separate place where you will move money for tax and future obligations. This can be a separate bank account, savings account, or any account you do not use for daily spending.”

### 9.4 Editing Registration Data

The user must be able to edit registration data later.

Changes to settings should apply forward only.

Past transactions should not change automatically unless the user explicitly requests recalculation.

---

## 10. Ongoing Operation

### 10.1 Income Reporting

The user reports income by sending an amount to the bot.

Examples:

* `11700`
* `11700 נוכה`

If the user sends only a number, the bot uses the user’s default VAT setting.

If the user adds a keyword (e.g., “נוכה”), the bot treats the income as VAT-excluded or VAT already deducted.

ADMIN REQUIREMENT:

The keyword used for VAT exclusion must be configurable via system settings and support multi-language mapping.

### 10.2 Calculation Logic

If the amount includes VAT:

* VAT = amount × 17 / 117
* Base amount = amount − VAT

If the amount does not include VAT or VAT was already deducted:

* VAT = 0
* Base amount = amount

All other allocations are calculated from the base amount after VAT reduction.

Allocations may be of two types:

1. Percentage-based allocation
2. Fixed monthly target allocation

Percentage-based allocations:

* Income tax = base amount × user income tax rate
* National insurance, if percentage-based = base amount × user national insurance rate
* Social savings, if percentage-based = base amount × user social savings rate

Fixed monthly target allocations:

Some allocations may be configured as a fixed monthly target rather than a percentage from each income.

Example: National insurance = ₪500 per month.

For fixed monthly targets, the system tracks:

* Monthly target amount
* Amount already saved this month
* Remaining amount for the month

When a new income is reported, the bot should allocate only the remaining amount needed to complete the monthly target.

MVP rule:

* Fixed monthly target is completed as early as possible during the month.
* The bot does not try to predict how many future income events the user will have.
* If the remaining target is ₪300, the bot asks the user to save ₪300 from the current income.
* Once the monthly target is completed, future income events in that month do not allocate more for that fixed target.

Total to save:

VAT + all percentage-based allocations + remaining fixed monthly target allocations

Available amount:

Original amount − total to save

### 10.3 Bot Response

After calculation, the bot should display:

* Income amount
* VAT allocation
* Income tax allocation
* National insurance allocation
* Social savings allocation
* Total amount to save
* Available amount
* Action prompt

Example:

“Income received: ₪11,700

To save:
VAT: ₪1,700
Income tax: ₪2,000
National insurance: ₪800
Social savings: ₪500

Total to transfer: ₪5,000
Available: ₪6,700

Did you transfer the money?”

### 10.4 User Actions After Calculation

The user must be able to choose:

* I transferred the full amount
* I transferred a partial amount
* Remind me later
* Not now

The user should also be able to write:

* `העברתי`
* `העברתי 4000`

If the user writes `העברתי`, the full required amount is marked as saved.

If the user writes `העברתי 4000`, only ₪4,000 is marked as saved.

The system then calculates the remaining gap.

### 10.5 Transaction Statuses

Each income transaction must have a status:

* Open
* Partially saved
* Fully saved
* Canceled

### 10.6 Monthly Organization

Every transaction must be assigned to a month in `YYYY-MM` format.

The month should normally be based on the transaction creation date.

Reports and summaries should be calculated by month.

---

## 11. Corrections

Corrections are essential because users will make mistakes.

The system must support corrections both for user settings and individual income entries.

### 11.1 Correction Commands

Initial commands:

* `אחרון` — show last transaction
* `תקן אחרון 12500` — update last transaction amount
* `בטל אחרון` — cancel last transaction
* `רשימה` — show recent transactions
* `תקן 2 9000` — update transaction ID 2
* `בטל 2` — cancel transaction ID 2

### 11.2 Recalculation Rule

When a transaction is corrected, the system recalculates only that transaction.

When user settings are changed, previous transactions should not change automatically.

---

## 12. Reports

Reports are behavioral, not accounting reports.

The purpose of reports is to help the user understand whether they separated enough money.

### 12.1 Current Status Command

The user can write:

`מצב`

The bot returns current monthly status:

* Total income this month
* Total amount that should have been saved
* Total actually marked as saved
* Remaining gap

### 12.2 Mid-Month Report

On the 15th of each month, the bot sends a mid-month report.

The report should include:

* Monthly income so far
* Amount that should have been saved
* Amount marked as saved
* Open gap

### 12.3 End-Month Report

At the end of each month, the bot sends a monthly report.

The report should include:

* Total monthly income
* Total VAT allocation
* Total income tax allocation
* Total national insurance allocation
* Total social savings allocation
* Total amount that should have been saved
* Amount actually marked as saved
* Gap

### 12.4 Future Accountant Report

In the future, reports may be expanded so they can be exported and sent to an accountant.

This is not part of the MVP.

---

## 13. Admin / Operator Perspective

The operator is the person who manages the product.

At first, the operator may be the founder.

The product should be designed so the operator can eventually manage:

* Onboarding questions
* Default rates
* Message wording
* Help text
* User activity
* Monthly reports
* Reminders
* Support issues

### 13.1 CMS Direction

The bot should not be built as a fully hard-coded flow.

The onboarding flow and messages should be structured as data where possible.

For MVP, this may be done using JSON files.

However, the system must be designed in a way that allows:

* Future CMS (Content Management System)
* Admin Panel for live updates

Admin Panel (V1 or early V2) should include:

* Editing onboarding questions
* Editing keywords (multi-language support)
* Editing default rates
* Viewing users and activity
* Viewing success metrics dashboard

The bot should not be built as a fully hard-coded flow.

The onboarding flow and messages should be structured as data where possible.

For MVP, this may be done using JSON files.

Future versions may include a real CMS or admin dashboard.
UPDATE: are we sure not CMS AND ADMIN PANEL even for V1?

### 13.2 Dynamic Flow Principle

Questions, texts, and options should ideally be stored separately from the core business logic.

The calculation logic should initially remain in code but must be modular to allow future migration into configurable logic.

The flow should support:

* Multi-language content
* Dynamic command keywords
* Flexible onboarding structure

Questions, texts, and options should ideally be stored separately from the core business logic.

The calculation logic may remain in code.
UPDATE: Also the calculation logic sgould be in a CMS so we can upadate when needed 

The flow should be flexible enough to add or remove onboarding questions later.

---

## 14. Data Model

### 14.1 User

Fields:

* id
* telegram_id
* first_name
* username
* business_type
* vat_included_default
* tax_rate
* national_insurance_allocation_type: percentage / monthly_target
* national_insurance_rate
* national_insurance_monthly_target
* social_savings_allocation_type: percentage / monthly_target
* social_savings_rate
* social_savings_monthly_target
* has_savings_destination
* onboarding_completed
* current_onboarding_step
* created_at
* updated_at

### 14.2 Transaction

Fields:

* id
* user_id
* amount_input
* vat_mode
* vat_amount
* base_amount
* income_tax_amount
* national_insurance_amount
* social_savings_amount
* total_to_save
* saved_amount
* remaining_amount
* available_amount
* status
* month
* created_at
* updated_at
* canceled_at

### 14.3 Reminder

Fields:

* id
* user_id
* transaction_id
* reminder_time
* reminder_type
* status
* created_at

### 14.4 Allocation Categories

The system should be designed around allocation categories rather than hard-coded tax fields only.

Each allocation category should support:

* Name
* Type: percentage / monthly_target
* Rate, if percentage-based
* Monthly target amount, if fixed monthly target
* Active / inactive status
* Display order

Initial allocation categories:

* VAT
* Income tax
* National insurance
* Social savings

Future allocation categories may include:

* Pension
* Education fund
* Emergency fund
* Expected expenses
* Personal goals
* Debt repayment

This means the product should avoid assuming that only VAT, tax, national insurance, and social savings will exist forever.

---

## 15. Commands

Initial supported commands:

* `/start`
* `מצב`
* `רשימה`
* `אחרון`
* `תקן אחרון {amount}`
* `בטל אחרון`
* `תקן {id} {amount}`
* `בטל {id}`
* `הגדרות`
* `עזרה`

Natural language inputs may be supported later.

---

## 16. Success Metrics

Primary metric:

* Percentage of required savings that users mark as saved

Secondary metrics:

* Number of income reports per user
* Weekly active users
* Number of users who complete onboarding
* Number of users who return after first use
* Average monthly gap per user
* Percentage of transactions marked fully saved
* Percentage of transactions marked partially saved

---

## 17. Monetization Direction

The MVP may start free.

A future freemium model can include:

Free tier:

* Basic income calculation
* Basic monthly status
* Manual confirmation

Paid tier:

* Advanced reports
* Monthly trend analysis
* Custom allocation categories
* Stronger reminders
* Exportable reports
* Accountant-ready summaries
* Premium support

Payment through Telegram may be explored later, but it is not necessary for the first MVP.

---

## 18. Non-Goals for MVP

The MVP must not include:

* Bank connection
* Open banking integration
* Automatic transfer
* Custody of funds
* Trust accounts
* Legal fiduciary service
* Formal tax filing
* Accountant dashboard

However:

* Multi-language support must be prepared at the architecture level
* Commands and texts must support localization

The MVP must not include:

* Bank connection
* Open banking integration
* Automatic transfer
* Custody of funds
* Trust accounts
* Legal fiduciary service
* Formal tax filing
* Accountant dashboard
* Full CMS
* Multi-language support unless necessary

---

## 19. Website (Required)

The product must include a website layer.

Initial website goals:

* Explain the product
* Drive users to Telegram bot
* Build trust

Future capabilities:

* User login
* Dashboard
* Billing

---

## 20. Admin Dashboard (Required)

Admin must be able to see:

* Users
* Activity
* Transactions
* Savings vs actual saved
* Gaps

---

## 21. Future Roadmap

Possible future directions:

1. More allocation categories
2. Custom user-defined savings rules
3. Open banking read-only integration
4. Automatic income detection
5. Accountant export
6. Premium subscription
7. Admin dashboard
8. Full CMS for bot flow management
9. Real account separation through financial partners
10. Payment automation

---

## 20. Final MVP Definition

TaxGuard Bot MVP is a Telegram bot that helps independent workers act at the moment income is received.

It calculates what portion of the income should be separated, pushes the user to make a manual transfer, records whether the transfer happened, and summarizes the user’s monthly behavior.

The MVP validates whether behavioral financial separation can become a real habit before building any heavy fintech infrastructure.
