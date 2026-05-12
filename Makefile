setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -U pip
	. .venv/bin/activate && pip install -r requirements.txt
	. .venv/bin/activate && pip install ruff pytest

test:
	. .venv/bin/activate && pytest

lint:
	. .venv/bin/activate && ruff check .

format:
	. .venv/bin/activate && ruff format .

check: lint test
