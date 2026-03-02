from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from src.schema.product_schema import TermsheetExtract

load_dotenv()

SYSTEM_PROMPT = """
You are a financial document extraction assistant.
Extract structured data from termsheet documents and return valid JSON.
Be precise with dates (YYYY-MM-DD format), numbers, and identifiers.
If a field is not found, use null.

Return JSON with these fields:
- isin: string (12 characters)
- sedol: string or null (7 characters)
- short_description: string or null (brief product description)
- issuer: string (issuer name)
- guarantor: string or null (guarantor name)
- currency: string (3 letters, default "GBP")
- notional_amount: number or null (aggregate nominal amount)
- product_type: string or null (e.g., "Phoenix Autocall")
- strike_date: string or null (YYYY-MM-DD, trade/strike date)
- issue_date: string (YYYY-MM-DD)
- maturity_date: string (YYYY-MM-DD)
- events: array of event objects with:
  - event_type: string ("Strike", "Coupon", "Autocall", "Knock-in")
  - event_level_pct: number or null (barrier level as percentage, e.g., 75)
  - event_strike_pct: number or null (strike percentage, e.g., 100)
  - event_date: string (YYYY-MM-DD)
  - event_amount: number or null (coupon rate or redemption amount)
  - event_payment_date: string or null (YYYY-MM-DD)
- underlyings: array of underlying objects with:
  - bbg_code: string (Bloomberg code, e.g., "SX5E Index", "UKX Index")
  - weight: number or null
  - initial_price: number or null (initial/strike price)

Extract ALL coupon events, autocall events, and underlyings from the document.
"""


def extract_termsheet(parsed_text: str) -> TermsheetExtract:
    """Use LLM to extract structured termsheet data from PDF text."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract termsheet data from:\n\n{parsed_text}"},
        ],
    )

    raw_json = response.choices[0].message.content
    if raw_json is None:
        raise ValueError("LLM returned empty response")

    data = json.loads(raw_json)

    return TermsheetExtract.model_validate(data)
