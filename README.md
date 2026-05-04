# TaxGuardBot

Telegram bot that helps freelancers manage cash flow by separating tax obligations from income in real-time.

## Features

- Income input via Telegram
- Automatic tax calculation:
  - VAT
  - Income tax
  - National insurance
  - Social savings
- Net available calculation
- Action-oriented response (how much to move aside)
- Monthly summary via מצב command
- Support for VAT-excluded inputs (נוכה)

## Tech Stack

- Python
- python-telegram-bot
- In-memory storage (MVP)

## Project Structure

app/
  bot.py
  calculations.py
  models.py
  storage.py
docs/
requirements.txt
README.md

## Setup

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create .env:

BOT_TOKEN=your_token_here

Run:

python3 -m app.bot

## Status

MVP working:
- Input → calculation → storage → summary

## Next Steps

- Persistent storage (DB)
- UX improvements
- Admin dashboard