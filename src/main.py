"""Entry point for the LLM Termsheet Ingestor.

Usage:
    python -m src.main <path-to-termsheet.txt>

The script reads the termsheet text, calls OpenAI to extract structured
fields, and persists the result to PostgreSQL.
"""

import sys

from dotenv import load_dotenv

from .database import ensure_table, get_connection, insert_termsheet
from .extractor import extract_termsheet_data


def ingest(text: str) -> int:
    """Extract data from *text* and insert it into the database.

    Args:
        text: Raw termsheet text.

    Returns:
        The database row id of the inserted record.
    """
    data = extract_termsheet_data(text)

    with get_connection() as conn:
        ensure_table(conn)
        row_id = insert_termsheet(conn, data)

    print(f"Termsheet ingested successfully (id={row_id}).")
    print(f"  Deal name   : {data.deal_name}")
    print(f"  Borrower    : {data.borrower}")
    print(f"  Amount      : {data.facility_amount}")
    print(f"  Interest    : {data.interest_rate}")
    print(f"  Maturity    : {data.maturity_date}")
    return row_id


def main() -> None:
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python -m src.main <path-to-termsheet.txt>")
        sys.exit(1)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()

    ingest(text)


if __name__ == "__main__":
    main()
