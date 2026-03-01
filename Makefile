.PHONY: setup run db-check test lint typecheck format clean help

PYTHON := .venv/bin/python
PIP := $(PYTHON) -m pip
PYTHONPATH := src

export PYTHONPATH

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) main.py

db-check:
	$(PYTHON) main.py --db-check

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy src

format:
	$(PYTHON) -m ruff check . --fix

clean:
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

help:
	@echo "Available targets:"
	@echo "  make setup     - create venv and install requirements"
	@echo "  make run       - run main.py"
	@echo "  make db-check  - verify PostgreSQL connection from main.py"
	@echo "  make test      - run tests"
	@echo "  make lint      - run lint checks"
	@echo "  make typecheck - run mypy"
	@echo "  make format    - auto-fix lint issues where possible"
	@echo "  make clean     - remove virtualenv and caches"
