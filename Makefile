.PHONY: setup run test lint typecheck format clean help

PYTHON := .venv/bin/python
PIP := $(PYTHON) -m pip
PYTHONPATH := src
PDF ?= data/XS3184638594_Termsheet_Final.pdf

export PYTHONPATH

setup:
	python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) main.py $(PDF)

test:
	# Run unit tests using unittest discovery (tests/ contains unittest files)
	$(PYTHON) -m unittest discover -v tests

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
	@echo "  make setup  - create venv and install requirements"
	@echo "  make run    - extract termsheet and output JSON (FILE=path/to/file.pdf)"
	@echo "  make test   - run tests"
	@echo "  make lint   - lint with ruff"
	@echo "  make format - auto-format with ruff"
	@echo "  make clean  - remove venv and caches"
	@echo "  make test      - run tests"
	@echo "  make lint      - run lint checks"
	@echo "  make typecheck - run mypy"
	@echo "  make format    - auto-fix lint issues where possible"
	@echo "  make clean     - remove virtualenv and caches"
