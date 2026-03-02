from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import get_origin, get_args

from pydantic import BaseModel, Field


def _get_type_str(annotation) -> str:
    """Convert Python type annotation to human-readable string."""
    origin = get_origin(annotation)
    
    if origin is list:
        inner = get_args(annotation)[0]
        return f"array of {inner.__name__}"
    
    # Handle Union types (X | None)
    if origin is type(None) or annotation is type(None):
        return "null"
    
    args = get_args(annotation)
    if args and type(None) in args:
        # It's Optional[X] or X | None
        non_none = [a for a in args if a is not type(None)]
        if non_none:
            inner = non_none[0]
            if inner is str:
                return "string or null"
            elif inner is date:
                return "string or null"
            elif inner is Decimal:
                return "number or null"
            else:
                return f"{inner.__name__} or null"
    
    # Simple types
    if annotation is str:
        return "string"
    elif annotation is date:
        return "string"
    elif annotation is Decimal:
        return "number"
    elif annotation is int:
        return "integer"
    elif annotation is float:
        return "number"
    elif annotation is bool:
        return "boolean"
    
    return str(annotation)


def _is_required(field_info) -> bool:
    """Check if a field is required (no default value)."""
    return field_info.default is ... or (field_info.default is None and field_info.default_factory is None and "None" not in str(field_info.annotation))


class EventExtract(BaseModel):
    """Extracted event data (coupon, autocall, strike, knock-in)."""

    # Required fields
    event_type: str = Field(description="Event type: Strike, Coupon, Autocall, Knock-in")
    event_date: date = Field(description="Event observation date (YYYY-MM-DD)")

    # Optional fields
    event_level_pct: Decimal | None = Field(default=None, description="Barrier level as percentage (e.g., 75 for 75%)")
    event_strike_pct: Decimal | None = Field(default=None, description="Strike percentage (e.g., 100 for 100%)")
    event_amount: Decimal | None = Field(default=None, description="Event amount (e.g., coupon rate 2.0375)")
    event_payment_date: date | None = Field(default=None, description="Payment date for the event (YYYY-MM-DD)")

    @classmethod
    def to_text_schema(cls) -> str:
        """Generate text schema for LLM prompt."""
        lines = ["Each event object has:"]
        for name, field in cls.model_fields.items():
            type_str = _get_type_str(field.annotation)
            required = "REQUIRED" if field.default is ... else ""
            desc = field.description or ""
            lines.append(f"- {name}: {type_str} {required} ({desc})")
        return "\n".join(lines)


class UnderlyingExtract(BaseModel):
    """Extracted underlying index/asset data."""

    # Required fields
    bbg_code: str = Field(description="Bloomberg code (e.g., 'UKX Index', 'SX5E Index')")

    # Optional fields
    weight: Decimal | None = Field(default=None, description="Weight in basket")
    initial_price: Decimal | None = Field(default=None, description="Initial/strike price")

    @classmethod
    def to_text_schema(cls) -> str:
        """Generate text schema for LLM prompt."""
        lines = ["Each underlying object has:"]
        for name, field in cls.model_fields.items():
            type_str = _get_type_str(field.annotation)
            required = "REQUIRED" if field.default is ... else ""
            desc = field.description or ""
            lines.append(f"- {name}: {type_str} {required} ({desc})")
        return "\n".join(lines)


class TermsheetExtract(BaseModel):
    """Structured data extracted from a termsheet PDF. Matches Product model in database."""

    # Required fields
    isin: str = Field(description="ISIN code (12 characters)")
    issuer: str = Field(description="Issuer name")
    currency: str = Field(default="GBP", description="Currency code (3 letters)")
    issue_date: date = Field(description="Issue date (YYYY-MM-DD)")
    trade_date: date = Field(description="Trade date (YYYY-MM-DD)")
    maturity_date: date = Field(description="Maturity date (YYYY-MM-DD)")

    # Optional fields
    sedol: str | None = Field(default=None, description="SEDOL code (7 characters)")
    short_description: str | None = Field(default=None, description="Short product description")
    product_type: str | None = Field(default=None, description="Product type (e.g., Phoenix Autocall)")
    guarantor: str | None = Field(default=None, description="Guarantor name")
    dealer: str | None = Field(default=None, description="Dealer name")
    nominal_amount: Decimal | None = Field(default=None, description="Aggregate nominal amount")
    specified_denomination: Decimal | None = Field(default=None, description="Specified denomination")
    calculation_amount: Decimal | None = Field(default=None, description="Calculation amount")
    strike_date: date | None = Field(default=None, description="Strike date (YYYY-MM-DD)")
    coupon_barrier_level: Decimal | None = Field(default=None, description="Coupon barrier level as decimal (e.g., 0.75 for 75%)")
    knock_in_barrier_level: Decimal | None = Field(default=None, description="Knock-in barrier level as decimal (e.g., 0.65 for 65%)")

    # Nested arrays
    events: list[EventExtract] = Field(default_factory=list, description="List of product events")
    underlyings: list[UnderlyingExtract] = Field(default_factory=list, description="List of underlying assets")

    @classmethod
    def to_text_schema(cls) -> str:
        """Generate complete text schema for LLM prompt."""
        lines = [
            "## REQUIRED FIELDS (must always be provided):"
        ]
        
        # Required fields (no default or default is ...)
        for name, field in cls.model_fields.items():
            if name in ("events", "underlyings"):
                continue
            if field.default is ... or (field.default is not None and field.default_factory is None and "None" not in str(field.annotation)):
                type_str = _get_type_str(field.annotation)
                desc = field.description or ""
                lines.append(f"- {name}: {type_str} ({desc})")
        
        lines.append("")
        lines.append("## OPTIONAL FIELDS (use null if not found):")
        
        # Optional fields
        for name, field in cls.model_fields.items():
            if name in ("events", "underlyings"):
                continue
            if field.default is None or "None" in str(field.annotation):
                type_str = _get_type_str(field.annotation)
                desc = field.description or ""
                lines.append(f"- {name}: {type_str} ({desc})")
        
        lines.append("")
        lines.append("## EVENTS ARRAY (extract all coupon, autocall, strike events):")
        lines.append(EventExtract.to_text_schema())
        
        lines.append("")
        lines.append("## UNDERLYINGS ARRAY (extract all underlying indices/assets):")
        lines.append(UnderlyingExtract.to_text_schema())
        
        lines.append("")
        lines.append("Extract ALL events and underlyings from the document.")
        
        return "\n".join(lines)


def get_extraction_prompt() -> str:
    """Get the full extraction prompt with schema for LLM."""
    return f"""You are a financial document extraction assistant.
Extract structured data from termsheet documents and return valid JSON.
Be precise with dates (YYYY-MM-DD format), numbers, and identifiers.

{TermsheetExtract.to_text_schema()}
"""
