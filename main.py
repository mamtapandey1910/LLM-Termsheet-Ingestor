from __future__ import annotations

import argparse

from src.database import check_database_connection, get_database_url
from src.extractor import extract_termsheet
from src.validator import validate_termsheet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM Termsheet Ingestor")
    parser.add_argument("--db-check", action="store_true", help="check PostgreSQL connectivity")
    parser.add_argument("--file", type=str, help="path to PDF/Excel input file")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.db_check:
        check_database_connection()
        print(f"PostgreSQL connection successful: {get_database_url()}")
        return

    if args.file:
        extracted = extract_termsheet(args.file)
        validated = validate_termsheet(extracted)
        print(validated.model_dump())
        return

    print("LLM Termsheet Ingestor is set up. Use --db-check or --file <path>.")


if __name__ == "__main__":
    main()
