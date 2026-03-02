"""Validation layer for termsheet extraction.

This module provides business logic validation that runs:
1. After LLM extraction creates the response
2. Before inserting data into the database

Note: ISIN format validation is handled by Pydantic @field_validator
in the schema at parse time.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schema.product_schema import TermsheetExtract


@dataclass
class ValidationCheck:
    """Single validation check result."""

    name: str
    passed: bool
    message: str
    is_error: bool = True  # False = warning


@dataclass
class ValidationResult:
    """Result of validation with all checks tracked."""

    is_valid: bool = True
    checks: list[ValidationCheck] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_check(self, name: str, passed: bool, message: str, is_error: bool = True) -> None:
        """Add a validation check result."""
        self.checks.append(ValidationCheck(name=name, passed=passed, message=message, is_error=is_error))
        if not passed:
            if is_error:
                self.errors.append(message)
                self.is_valid = False
            else:
                self.warnings.append(message)

    def print_results(self) -> None:
        """Print comprehensive validation report."""
        # ANSI color codes
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        RESET = "\033[0m"

        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)

        # Group checks by type
        error_checks = [c for c in self.checks if c.is_error]
        warning_checks = [c for c in self.checks if not c.is_error]

        # Print required checks (errors)
        print("\n[Required Checks]")
        for check in error_checks:
            if check.passed:
                status = f"{GREEN}✓ PASS{RESET}"
            else:
                status = f"{RED}✗ FAIL{RESET}"
            print(f"  {status}: {check.name}")
            if not check.passed:
                print(f"         → {check.message}")

        # Print optional checks (warnings)
        if warning_checks:
            print("\n[Optional Checks]")
            for check in warning_checks:
                if check.passed:
                    status = f"{GREEN}✓ PASS{RESET}"
                else:
                    status = f"{YELLOW}⚠ WARN{RESET}"
                print(f"  {status}: {check.name}")
                if not check.passed:
                    print(f"         → {check.message}")

        # Summary
        passed_required = sum(1 for c in error_checks if c.passed)
        total_required = len(error_checks)
        passed_optional = sum(1 for c in warning_checks if c.passed)
        total_optional = len(warning_checks)

        print("\n" + "-" * 60)
        print(f"Required: {passed_required}/{total_required} passed")
        print(f"Optional: {passed_optional}/{total_optional} passed")
        print("-" * 60)

        if self.is_valid:
            print(f"Result: {GREEN}✓ VALIDATION PASSED{RESET}")
        else:
            print(f"Result: {RED}✗ VALIDATION FAILED{RESET}")
        print("=" * 60 + "\n")


def validate_termsheet(data: TermsheetExtract) -> ValidationResult:
    """
    Validate extracted termsheet data before database insertion.

    Required Checks (Errors - will block insertion):
    - ISIN format (validated at schema level)
    - Issue Date < Maturity Date
    - At least one underlying present
    - Barriers within logical range (0-100%)

    Optional Checks (Warnings - informational only):
    - Trade date vs issue date
    - Strike date vs maturity date
    - Events present
    - Event dates within product lifetime
    """
    result = ValidationResult()

    # === REQUIRED CHECKS (block insertion if failed) ===

    # 1. ISIN format (already validated by Pydantic, but report it)
    result.add_check(
        name="ISIN format",
        passed=True,  # If we got here, Pydantic already validated it
        message=f"ISIN {data.isin} format is valid",
        is_error=True,
    )

    # 2. Issue Date < Maturity Date
    dates_valid = data.issue_date < data.maturity_date
    result.add_check(
        name="Issue date before maturity",
        passed=dates_valid,
        message=f"Issue date ({data.issue_date}) must be before maturity date ({data.maturity_date})",
        is_error=True,
    )

    # 3. At least one underlying present
    has_underlyings = len(data.underlyings) > 0
    result.add_check(
        name="Underlyings present",
        passed=has_underlyings,
        message=f"At least one underlying required (found {len(data.underlyings)})",
        is_error=True,
    )

    # 4. Coupon barrier in valid range (0-100%)
    if data.coupon_barrier_level is not None:
        coupon_valid = 0 <= data.coupon_barrier_level <= 100
        result.add_check(
            name="Coupon barrier range (0-100%)",
            passed=coupon_valid,
            message=f"Coupon barrier {data.coupon_barrier_level}% must be between 0-100",
            is_error=True,
        )
    else:
        result.add_check(
            name="Coupon barrier range (0-100%)",
            passed=True,
            message="Coupon barrier not specified",
            is_error=True,
        )

    # 5. Knock-in barrier in valid range (0-100%)
    if data.knock_in_barrier_level is not None:
        knockin_valid = 0 <= data.knock_in_barrier_level <= 100
        result.add_check(
            name="Knock-in barrier range (0-100%)",
            passed=knockin_valid,
            message=f"Knock-in barrier {data.knock_in_barrier_level}% must be between 0-100",
            is_error=True,
        )
    else:
        result.add_check(
            name="Knock-in barrier range (0-100%)",
            passed=True,
            message="Knock-in barrier not specified",
            is_error=True,
        )

    # === OPTIONAL CHECKS (warnings only) ===

    # 6. Trade date should be before or equal to issue date
    if data.trade_date and data.issue_date:
        trade_valid = data.trade_date <= data.issue_date
        result.add_check(
            name="Trade date <= issue date",
            passed=trade_valid,
            message=f"Trade date ({data.trade_date}) is after issue date ({data.issue_date})",
            is_error=False,
        )

    # 7. Strike date should be before maturity
    if data.strike_date and data.maturity_date:
        strike_valid = data.strike_date < data.maturity_date
        result.add_check(
            name="Strike date before maturity",
            passed=strike_valid,
            message=f"Strike date ({data.strike_date}) should be before maturity ({data.maturity_date})",
            is_error=False,
        )

    # 8. Events present
    has_events = len(data.events) > 0
    result.add_check(
        name="Events extracted",
        passed=has_events,
        message=f"No events extracted (expected at least 1)",
        is_error=False,
    )

    # 9. Event dates within product lifetime
    events_in_range = True
    for event in data.events:
        if event.event_date > data.maturity_date:
            events_in_range = False
            break
    if data.events:
        result.add_check(
            name="Event dates within lifetime",
            passed=events_in_range,
            message="Some event dates are after maturity date",
            is_error=False,
        )

    return result


def check_duplicate_isin(isin: str) -> bool:
    """Check if ISIN already exists in database."""
    from src.database.connection import SessionLocal
    from src.database.models import Product

    session = SessionLocal()
    try:
        existing = session.query(Product).filter(Product.isin == isin).first()
        return existing is not None
    finally:
        session.close()
