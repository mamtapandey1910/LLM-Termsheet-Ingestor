from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from src.database import create_database_if_not_exists, create_tables, save_termsheet
from src.extractor import extract_termsheet, parse_pdf_text
from src.helpers import (
    check_duplicate_isin,
    generate_run_id,
    save_extraction_json,
    validate_termsheet,
)



def confirm_insert(output_file: Path, is_duplicate: bool) -> bool:
    """Prompt user to confirm before inserting to database."""
    print("\n" + "=" * 50)
    print("REVIEW DATA BEFORE INSERT")
    print("=" * 50)
    print(f"\nPlease review the extracted data:")
    print(f"  • JSON file: {output_file}")
    print(f"  • Console output above shows the full JSON")
    print(f"\nAction: {'UPDATE existing record' if is_duplicate else 'INSERT new record'}")
    print("=" * 50)
    
    while True:
        response = input("\nProceed with database insert? [y/n]: ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no"):
            return False
        else:
            print("Please enter 'y' or 'n'")


def main() -> None:
    parser = argparse.ArgumentParser(description="LLM Termsheet Ingestor")
    parser.add_argument("pdf", help="path to termsheet PDF")
    parser.add_argument("-y", "--yes", action="store_true", help="skip confirmation prompt")
    args = parser.parse_args()
    
    RED = "\033[91m"
    RESET = "\033[0m"
    if not args.pdf:
        print(f"{RED}ERROR: No PDF file specified. Please provide a PDF file path as an argument.{RESET}")
        sys.exit(1)

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"{RED}ERROR: PDF not found: {pdf_path}{RESET}")
        sys.exit(1)

    # Setup database
    create_database_if_not_exists()
    create_tables()

    # Extract data from PDF
    print(f"Parsing PDF: {pdf_path}")
    text = parse_pdf_text(str(pdf_path))
    print(f"Extracted {len(text)} characters")

    # Step 1: LLM Extraction (ISIN format validated at parse time by Pydantic)
    print("Calling LLM for extraction...")
    run_id = generate_run_id()
    
    try:
        result = extract_termsheet(text)
    except ValidationError as e:
        print("\n" + "=" * 50)
        print("SCHEMA VALIDATION FAILED")
        print("=" * 50)
        for error in e.errors():
            print(f"  ✗ {error['loc'][0]}: {error['msg']}")
        print("=" * 50)
        print("\nERROR: Schema validation failed. Not inserting.")
        sys.exit(1)

    # Save and display JSON output
    output_file = save_extraction_json(result, run_id)
    print(f"\nJSON saved to: {output_file}")

    # Step 2: Business Logic Validation (after LLM, before DB)
    validation = validate_termsheet(result)
    validation.print_results()

    if not validation.is_valid:
        print("ERROR: Business validation failed. Not inserting to database.")
        sys.exit(1)

    # Step 3: Check for duplicates
    is_duplicate = check_duplicate_isin(result.isin)
    if is_duplicate:
        RED = "\033[91m"
        RESET = "\033[0m"
        print(f"{RED}ERROR: Duplicate ISIN detected: {result.isin}. Insertion aborted.{RESET}")
        sys.exit(1)

    # Step 4: Confirm before inserting
    if not args.yes:
        if not confirm_insert(output_file, is_duplicate):
            print("\nInsert cancelled by user.")
            sys.exit(0)

    # Step 5: Save to database
    print("\nSaving to database...")
    product = save_termsheet(result)
    print(f"Saved product: {product.isin} (id: {product.id})")


if __name__ == "__main__":
    main()
