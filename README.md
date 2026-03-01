# LLM Termsheet Ingestor

A Python application that reads financial termsheets, uses **OpenAI** to extract
structured fields from the raw text, and persists the results to **PostgreSQL**.

---

## Features

- **OpenAI extraction** – sends termsheet text to an OpenAI chat model (default `gpt-4o-mini`) and receives a structured JSON response containing deal name, borrower, lender, facility type, currency, amount, interest rate, maturity date, closing date, purpose, covenants, and fees.
- **PostgreSQL persistence** – stores every extracted termsheet in a `termsheets` table (auto-created on first run).
- **Pydantic models** – strongly-typed data model for the extracted fields.
- **Environment-driven configuration** – all secrets and connection details are read from a `.env` file or environment variables.

---

## Project Structure

```
LLM-Termsheet-Ingestor/
├── requirements.txt          # Python dependencies
├── .env.example              # Template for environment variables
├── sample_termsheet.txt      # Example termsheet for a quick demo
├── src/
│   ├── models.py             # Pydantic TermsheetData model
│   ├── extractor.py          # OpenAI-based extraction logic
│   ├── database.py           # PostgreSQL helpers (connect, create table, insert)
│   └── main.py               # CLI entry point
└── tests/
    ├── test_extractor.py     # Unit tests for the extractor
    └── test_database.py      # Unit tests for the database layer
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your OPENAI_API_KEY and Postgres credentials
```

### 3. Run the ingestor

```bash
python -m src.main sample_termsheet.txt
```

Example output:

```
Termsheet ingested successfully (id=1).
  Deal name   : Project Apollo
  Borrower    : Apollo Industries Ltd.
  Amount      : $250,000,000
  Interest    : Term SOFR + 2.75%
  Maturity    : March 31, 2030
```

---

## Environment Variables

| Variable           | Default         | Description                        |
|--------------------|-----------------|------------------------------------|
| `OPENAI_API_KEY`   | *(required)*    | Your OpenAI API key                |
| `OPENAI_MODEL`     | `gpt-4o-mini`   | OpenAI chat model to use           |
| `POSTGRES_HOST`    | `localhost`     | PostgreSQL host                    |
| `POSTGRES_PORT`    | `5432`          | PostgreSQL port                    |
| `POSTGRES_DB`      | `termsheet_db`  | Database name                      |
| `POSTGRES_USER`    | `postgres`      | Database user                      |
| `POSTGRES_PASSWORD`| *(required)*    | Database password                  |

---

## Running Tests

```bash
python -m pytest tests/ -v
```

All tests use mocks — no live OpenAI or PostgreSQL connection is required.