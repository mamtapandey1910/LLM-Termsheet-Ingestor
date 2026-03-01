from typing import Optional
from pydantic import BaseModel, Field


class TermsheetData(BaseModel):
    """Structured data extracted from a financial termsheet."""

    deal_name: Optional[str] = Field(None, description="Name or identifier of the deal")
    borrower: Optional[str] = Field(None, description="Name of the borrower or issuer")
    lender: Optional[str] = Field(None, description="Name of the lender or arranger")
    facility_type: Optional[str] = Field(
        None, description="Type of facility (e.g., Term Loan, Revolving Credit)"
    )
    currency: Optional[str] = Field(None, description="Currency of the facility")
    facility_amount: Optional[str] = Field(
        None, description="Total size of the facility"
    )
    interest_rate: Optional[str] = Field(
        None, description="Interest rate or pricing terms"
    )
    maturity_date: Optional[str] = Field(None, description="Maturity or repayment date")
    closing_date: Optional[str] = Field(
        None, description="Expected or actual closing date"
    )
    purpose: Optional[str] = Field(None, description="Purpose or use of proceeds")
    covenants: Optional[str] = Field(
        None, description="Key financial or non-financial covenants"
    )
    fees: Optional[str] = Field(None, description="Fees (upfront, commitment, etc.)")
    raw_text: Optional[str] = Field(None, description="Original termsheet text")
