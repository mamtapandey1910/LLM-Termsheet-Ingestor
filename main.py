from __future__ import annotations

import argparse

from src.database import (
    check_database_connection,
    create_database_if_not_exists,
    create_tables,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM Termsheet Ingestor")
    parser.add_argument("--db-create", action="store_true", help="create database if missing")
    parser.add_argument("--db-check", action="store_true", help="check PostgreSQL connectivity")
    parser.add_argument("--db-init", action="store_true", help="create database tables")
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

    print(
        "LLM Termsheet Ingestor is set up. "
        "Use: python main.py --db-create | --db-check | --db-init."
    )


if __name__ == "__main__":
    main()
