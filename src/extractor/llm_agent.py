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
- issuer: string
- guarantor: string or null
- currency: string (3 letters, default "GBP")
- notional_amount: number or null
- strike_date: string (YYYY-MM-DD)
- issue_date: string (YYYY-MM-DD)
- maturity_date: string (YYYY-MM-DD)
- coupon_barrier_level: number or null (decimal, e.g., 0.65 for 65%)
- knock_in_barrier_level: number or null (decimal, e.g., 0.50 for 50%)
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
