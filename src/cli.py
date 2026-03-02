from __future__ import annotations

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
from src.extractor.errors import (
    MissingAPIKeyError,
    OpenAIInitializationError,
    OpenAICallError,
    LLMParseError,
    SchemaValidationError,
    ExtractorError,
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
        if response in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'")


def run(pdf: str | Path, yes: bool = False) -> int:
    """Run the ingest flow for a single PDF path.

    Args:
        pdf: path to the PDF file (string or Path)
        yes: if True, skip confirmation prompt
    """
    RED = "\033[91m"
    RESET = "\033[0m"

    if not pdf:
        print(f"{RED}ERROR: No PDF file specified. Please provide a PDF file path as an argument.{RESET}")
        return 1

    pdf_path = Path(pdf)
    if not pdf_path.exists():
        print(f"{RED}ERROR: PDF not found: {pdf_path}{RESET}")
        return 1

    # Setup database
    create_database_if_not_exists()
    create_tables()

    # Extract data from PDF
    print(f"Parsing PDF: {pdf_path}")
    text = parse_pdf_text(str(pdf_path))
    print(f"Extracted {len(text)} characters")

    # LLM Extraction
    print("Calling LLM for extraction...")
    run_id = generate_run_id()

    try:
        result = extract_termsheet(text)
    except SchemaValidationError as e:
        print("\n" + "=" * 50)
        print("SCHEMA VALIDATION FAILED")
        print("=" * 50)
        print(f"  ✗ {e}")
        print("=" * 50)
        print("\nERROR: Schema validation failed. Not inserting.")
        return 1
    except ExtractorError as e:
        print(f"ERROR: {e}")
        return 1
    except ValidationError as e:
        print("\n" + "=" * 50)
        print("SCHEMA VALIDATION FAILED")
        print("=" * 50)
        for error in e.errors():
            print(f"  ✗ {error['loc'][0]}: {error['msg']}")
        print("=" * 50)
        print("\nERROR: Schema validation failed. Not inserting.")
        return 1
    except Exception as e:
        print(f"ERROR: Unexpected extraction error: {e}")
        return 1

    # Save and display JSON output
    output_file = save_extraction_json(result, run_id)
    print(f"\nJSON saved to: {output_file}")

    # Business validation
    validation = validate_termsheet(result)
    validation.print_results()
    if not validation.is_valid:
        print("ERROR: Business validation failed. Not inserting to database.")
        return 1

    # Check duplicates
    is_duplicate = check_duplicate_isin(result.isin)
    if is_duplicate:
        print(f"{RED}ERROR: Duplicate ISIN detected: {result.isin}. Insertion aborted.{RESET}")
        return 1

    # Confirm
    if not yes and not confirm_insert(output_file, is_duplicate):
        print("\nInsert cancelled by user.")
        return 0

    # Save to database
    print("\nSaving to database...")
    product = save_termsheet(result)
    print(f"Saved product: {product.isin} (id: {product.id})")
    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LLM Termsheet Ingestor")
    parser.add_argument("pdf", help="path to termsheet PDF")
    parser.add_argument("-y", "--yes", action="store_true", help="skip confirmation prompt")
    args = parser.parse_args()

    raise SystemExit(run(args.pdf, yes=args.yes))
