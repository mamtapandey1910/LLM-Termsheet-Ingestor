from __future__ import annotations

import argparse
import json

from src.database import (
    check_database_connection,
    create_database_if_not_exists,
    create_tables,
)
from src.extractor import extract_termsheet, parse_pdf_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM Termsheet Ingestor")
    parser.add_argument("--db-create", action="store_true", help="create database if missing")
    parser.add_argument("--db-check", action="store_true", help="check PostgreSQL connectivity")
    parser.add_argument("--db-init", action="store_true", help="create database tables")
    parser.add_argument("--extract", type=str, metavar="FILE", help="extract data from termsheet PDF")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.db_create:
        create_database_if_not_exists()
        print("Database ready")
        return

    if args.db_check:
        check_database_connection()
        print("PostgreSQL connection successful")
        return

    if args.db_init:
        create_tables()
        print("Schema created")
        return

    if args.extract:
        print(f"Parsing PDF: {args.extract}")
        text = parse_pdf_text(args.extract)
        print(f"Extracted {len(text)} characters of text")
        print("Calling LLM for structured extraction...")
        result = extract_termsheet(text)
        print("\n--- Extracted Termsheet Data ---")
        print(json.dumps(result.model_dump(mode="json"), indent=2, default=str))
        return

    print(
        "LLM Termsheet Ingestor is set up. "
        "Use: python main.py --db-create | --db-check | --db-init | --extract <file>."
    )


if __name__ == "__main__":
    main()
