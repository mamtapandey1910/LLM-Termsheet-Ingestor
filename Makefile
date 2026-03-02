.PHONY: setup run dev db-create db-check db-init extract test lint typecheck format clean help

PYTHON := .venv/bin/python
PIP := $(PYTHON) -m pip
PYTHONPATH := src
FILE := data/XS3184638594_Termsheet_Final.pdf

export PYTHONPATH

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) main.py

dev:
	$(PYTHON) main.py --db-create
	$(PYTHON) main.py --db-check
	$(PYTHON) main.py --db-init
	$(PYTHON) main.py

db-create:
	$(PYTHON) main.py --db-create

db-check:
	$(PYTHON) main.py --db-check

db-init:
	$(PYTHON) main.py --db-init

extract:
	$(PYTHON) main.py --extract $(FILE)

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
	@echo "  make dev       - db-create + db-check + db-init + run"
	@echo "  make db-create - create database if missing"
	@echo "  make db-check  - verify PostgreSQL connection from main.py"
	@echo "  make db-init   - create schema tables"
	@echo "  make extract   - extract data from termsheet (FILE=path/to/file.pdf)"
	@echo "  make test      - run tests"
	@echo "  make lint      - run lint checks"
	@echo "  make typecheck - run mypy"
	@echo "  make format    - auto-fix lint issues where possible"
	@echo "  make clean     - remove virtualenv and caches"
