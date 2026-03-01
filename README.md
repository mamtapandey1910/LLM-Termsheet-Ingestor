# LLM-Termsheet-Ingestor

A Python tool that uses OpenAI's LLMs to extract structured data from venture-capital term sheet documents. Supports plain text, Markdown, PDF, and DOCX inputs and outputs clean JSON.

## Features

- Parses **.txt**, **.md**, **.pdf**, and **.docx** term sheet files
- Sends the text to an OpenAI chat model (`gpt-4o` by default)
- Returns a structured JSON object with 18 standard term-sheet fields
- Simple CLI for one-off extraction or automation pipelines

## Extracted Fields

| Field | Description |
|---|---|
| `company_name` | Name of the company raising funds |
| `investment_amount` | Total round size |
| `pre_money_valuation` | Pre-money valuation |
| `post_money_valuation` | Post-money valuation |
| `valuation_cap` | Valuation cap (convertible instruments) |
| `discount_rate` | Conversion discount |
| `interest_rate` | Accruing interest rate |
| `security_type` | Type of security (e.g. Series A Preferred) |
| `investors` | List of investors |
| `lead_investor` | Lead investor name |
| `closing_date` | Expected closing date |
| `liquidation_preference` | Liquidation preference terms |
| `participation` | Participation rights |
| `anti_dilution` | Anti-dilution protection type |
| `board_composition` | Board seat allocation |
| `pro_rata_rights` | Pro-rata participation rights |
| `information_rights` | Information rights threshold |
| `governing_law` | Governing jurisdiction |

## Installation

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your OpenAI API key:

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

## Usage

### Command-line

```bash
python -m src.cli samples/sample_termsheet.txt
```

Optional flags:

| Flag | Description |
|---|---|
| `--model gpt-4o` | OpenAI model (default: `gpt-4o`) |
| `--api-key KEY` | API key (overrides `OPENAI_API_KEY` env var) |
| `-o result.json` | Write output to a file instead of stdout |
| `--indent N` | JSON indentation level (default: `2`) |

### Python API

```python
from src.ingestor import ingest, ingest_file

# From a file path
result = ingest_file("samples/sample_termsheet.txt")

# From raw text
with open("sheet.txt") as f:
    text = f.read()
result = ingest(text)

print(result["company_name"])
print(result["investment_amount"])
```

### Example Output

```json
{
  "company_name": "Acme Technologies, Inc.",
  "investment_amount": "$5,000,000",
  "pre_money_valuation": "$20,000,000",
  "post_money_valuation": "$25,000,000",
  "security_type": "Series A Preferred Stock",
  "investors": ["Sequoia Capital", "Andreessen Horowitz"],
  "lead_investor": "Sequoia Capital",
  "closing_date": "March 31, 2026",
  "governing_law": "State of Delaware"
}
```

## Project Structure

```
LLM-Termsheet-Ingestor/
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── samples/
│   └── sample_termsheet.txt  # Example term sheet
├── src/
│   ├── __init__.py
│   ├── parsers.py          # Document loading (.txt, .md, .pdf, .docx)
│   ├── ingestor.py         # LLM extraction logic
│   └── cli.py              # Command-line interface
└── tests/
    ├── test_parsers.py
    ├── test_ingestor.py
    └── test_cli.py
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```
