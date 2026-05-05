# CHANGELOG

## v1.1 - 2026-05-05

### Added

- Reset command with multiple variations (reset, Reset, אפס, נקה, מחק)
- Test strategy document for consistent validation
- Improve message formatting (spacing and readability, no wording changes)

---

## v1.0 - 2026-05-05

### Added

- Telegram bot setup
- Environment configuration with .env
- Basic message handling
- Income input parsing
- Support for VAT-included and VAT-excluded ("נוכה") inputs
- Calculation engine:
  - VAT
  - Income tax
  - National insurance
  - Social savings
- Transaction model
- In-memory storage per user
- "מצב" command for summary
- Action-oriented UX response

### Improvements

- Support for comma-separated input (e.g., "11,700", "11,700 נוכה")
- Robust input parsing (spaces, currency symbol, flexible formats)
- Input validation and improved error handling (negative, zero, invalid formats)
- Monthly tracking: "מצב" now reflects current month only

### Fixes

- Remove debug print from bot parsing

### Technical

- Project structure initialized
- Git repository initialized
- GitHub repository connected
- Requirements file created