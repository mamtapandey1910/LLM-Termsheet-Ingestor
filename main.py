from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.database import create_database_if_not_exists, create_tables, save_termsheet
from src.extractor import extract_termsheet, parse_pdf_text

DEFAULT_PDF = "data/XS3184638594_Termsheet_Final.pdf"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM Termsheet Ingestor")
    parser.add_argument("pdf", nargs="?", default=DEFAULT_PDF, help="path to termsheet PDF")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    pdf_path = Path(args.pdf)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Ensure database and tables exist
    # create_database_if_not_exists()
    # create_tables()

    print(f"Parsing PDF: {pdf_path}")
    text = parse_pdf_text(str(pdf_path))
    print(f"Extracted {len(text)} characters of text")

    print("Calling LLM for structured extraction...")
    result = extract_termsheet(text)

    print("\n--- Extracted Termsheet Data ---")
    print(json.dumps(result.model_dump(mode="json"), indent=2, default=str))

    # print("\nSaving to database...")
    # product = save_termsheet(result)
    # print(f"Saved product: {product.isin} (id: {product.id})")


if __name__ == "__main__":
    main()
