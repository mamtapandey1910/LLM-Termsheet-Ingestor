#!/usr/bin/env python3
"""Test validation layer with actual LLM extraction.

Tests the full flow:
1. Parse PDF
2. LLM extraction (schema validation at parse time)
3. Business validation (after LLM, before DB)
"""
from pathlib import Path

from pydantic import ValidationError

from src.extractor import extract_termsheet, parse_pdf_text
from src.helpers.validation import validate_termsheet

DEFAULT_PDF = "data/XS3184638594_Termsheet_Final.pdf"


def test_full_extraction_and_validation():
    """Test actual LLM extraction followed by validation."""
    pdf_path = Path(DEFAULT_PDF)
    
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        return None
    
    print("=" * 60)
    print("FULL LLM EXTRACTION + VALIDATION TEST")
    print("=" * 60)
    
    # Step 1: Parse PDF
    print(f"\n1. Parsing PDF: {pdf_path}")
    text = parse_pdf_text(str(pdf_path))
    print(f"   Extracted {len(text)} characters")
    
    # Step 2: LLM Extraction (ISIN validated at parse time by Pydantic)
    print("\n2. Calling LLM for extraction...")
    try:
        result = extract_termsheet(text)
        print("   ✓ Schema validation passed (ISIN format OK)")
    except ValidationError as e:
        print("   ✗ Schema validation failed:")
        for error in e.errors():
            print(f"     - {error['loc'][0]}: {error['msg']}")
        return None
    
    # Show extracted data
    print("\n   Extracted data:")
    print(f"     ISIN: {result.isin}")
    print(f"     Issuer: {result.issuer}")
    print(f"     Issue Date: {result.issue_date}")
    print(f"     Maturity Date: {result.maturity_date}")
    print(f"     Coupon Barrier: {result.coupon_barrier_level}%")
    print(f"     Knock-in Barrier: {result.knock_in_barrier_level}%")
    print(f"     Events: {len(result.events)}")
    print(f"     Underlyings: {len(result.underlyings)}")
    
    # Step 3: Business Validation
    print("\n3. Running business validation...")
    validation = validate_termsheet(result)
    validation.print_results()
    
    return validation


if __name__ == "__main__":
    result = test_full_extraction_and_validation()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if result is None:
        print("  Test failed during extraction")
    elif result.is_valid:
        print("  ✓ All validations PASSED - ready for DB insert")
    else:
        print("  ✗ Business validation FAILED - would NOT insert to DB")
        for error in result.errors:
            print(f"    - {error}")
