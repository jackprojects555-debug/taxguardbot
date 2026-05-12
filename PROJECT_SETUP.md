# taxguardbot Setup

## Python
3.14.4

## Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## Run Bot
python3 -m app.bot

## Run Admin Server
export ADMIN_TOKEN='your-token-here'
python3 -m app.admin_server
# Default: http://127.0.0.1:8080
