from __future__ import annotations

import argparse
from pathlib import Path

from src.cli import run


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM Termsheet Ingestor")
    parser.add_argument("pdf", help="path to termsheet PDF")
    parser.add_argument("-y", "--yes", action="store_true", help="skip confirmation prompt")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    return run(pdf_path, yes=args.yes)


if __name__ == "__main__":
    raise SystemExit(main())
