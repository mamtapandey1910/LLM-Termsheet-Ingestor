# LLM Termsheet Ingestor

Extracts termsheet data from PDF using LLM, validates, and saves to PostgreSQL.

## Quick Start

# LLM-Termsheet-Ingestor

prerequisites:- Python 3.8 or higher

- Make installed on your system
- A PDF file containing the termsheet data you want to ingest

steps to run this project:

1. Clone the repository
2. Copy the `.env.example` file to `.env` and fill in the required environment variables
3. Copy termsheet PDF files to the `data/<your_termsheet_file_in_pdf>` directory
4. Install the required dependencies using `make setup`
5. Run the ingestion process using `make run` or python main.py

if you to run custom pdf file, you can use the following command:

`make run PDF=data/<your_file_name>`
default pdf file is `data/XS3184638594_Termsheet_Final.pdf`

## Main Files

- `main.py` — Entry point
- `src/extractor/` — PDF parsing & LLM extraction
- `src/schema/` — Data models
- `src/helpers/validation.py` — Business validation
- `src/database/` — DB connection & models

## Validation

Validates ISIN format and business rules before DB insert. Shows validation report in terminal.

## Environment

Copy `.env.example` to `.env` and fill in required values.

## Usage

### Basic Usage

```bash
# Extract from default PDF
python main.py

# Extract from specific PDF
python main.py path/to/termsheet.pdf

# Skip confirmation prompt
python main.py -y
```

## Project Structure

```
LLM-Termsheet-Ingestor/
├── main.py                     # CLI entry point
├── docker-compose.yml          # PostgreSQL container
├── requirements.txt            # Python dependencies
├── data/                       # Sample termsheet PDFs
├── output/                     # JSON extraction results
└── src/
    ├── database/
    │   ├── connection.py       # DB connection & save logic
    │   └── models.py           # SQLAlchemy models
    ├── extractor/
    │   ├── pdf_parser.py       # PyMuPDF text extraction
    │   ├── llm_agent.py        # OpenAI GPT-4o extraction
    │   └── system_prompt.py    # LLM instructions
    ├── helpers/
    │   ├── validation.py       # Business logic validation
    │   └── output.py           # JSON output handling
    └── schema/
        └── product_schema.py   # Pydantic models
```

## Validation

Two-layer validation:

### 1. Schema Validation (Pydantic)

- ISIN format: 2 letters + 9 alphanumeric + 1 check digit
- Runs at parse time when LLM response is received

### 2. Business Validation

- Issue date must be before maturity date
- At least one underlying required
- Barrier levels must be 0-100%
- Runs after extraction, before database insert

## Database Schema

Three tables:

- `products` - Main product details (ISIN, issuer, dates, barriers)
- `product_events` - Events (coupon, autocall, strike, maturity)
- `product_underlyings` - Underlying assets (Bloomberg codes)

## Output

Extracted data is saved to:

- `output/extraction_<timestamp>_<uuid>.json` - Full JSON
- Console output with validation report
- PostgreSQL database (after user confirmation)

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# Type checking
mypy src

# Lint
ruff check .
```

## License

MIT
