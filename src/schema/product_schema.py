from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class EventExtract(BaseModel):
    """Product event (coupon, autocall, strike, maturity)."""

    event_type: str = Field(description="Strike, Coupon, Autocall, or Maturity")
    event_date: date = Field(description="Observation date")
    event_level_pct: Decimal | None = Field(default=None, description="Barrier level %")
    event_strike_pct: Decimal | None = Field(default=None, description="Strike %")
    event_amount: Decimal | None = Field(default=None, description="Coupon or redemption amount %")
    event_payment_date: date | None = Field(default=None, description="Payment date")


class UnderlyingExtract(BaseModel):
    """Underlying index or asset."""

    bbg_code: str = Field(description="Bloomberg code")
    weight: Decimal | None = Field(default=None, description="Basket weight")
    initial_price: Decimal | None = Field(default=None, description="Initial price")


class TermsheetExtract(BaseModel):
    """Extracted termsheet data."""

    isin: str = Field(description="ISIN code")
    issuer: str = Field(description="Issuer name")
    currency: str = Field(default="GBP", description="Currency")
    issue_date: date = Field(description="Issue date")
    trade_date: date = Field(description="Trade date")
    maturity_date: date = Field(description="Maturity date")

    sedol: str | None = Field(default=None, description="SEDOL code")
    short_description: str | None = Field(default=None, description="Product description")
    product_type: str | None = Field(default=None, description="Product type")
    guarantor: str | None = Field(default=None, description="Guarantor")
    dealer: str | None = Field(default=None, description="Dealer")
    nominal_amount: Decimal | None = Field(default=None, description="Nominal amount")
    specified_denomination: Decimal | None = Field(default=None, description="Denomination")
    calculation_amount: Decimal | None = Field(default=None, description="Calculation amount")
    strike_date: date | None = Field(default=None, description="Strike date")
    coupon_barrier_level: Decimal | None = Field(default=None, description="Coupon barrier %")
    knock_in_barrier_level: Decimal | None = Field(default=None, description="Knock-in barrier %")

    events: list[EventExtract] = Field(default_factory=list, description="Events")
    underlyings: list[UnderlyingExtract] = Field(default_factory=list, description="Underlyings")
