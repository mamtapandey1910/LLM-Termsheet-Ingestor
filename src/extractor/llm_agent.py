from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

from src.schema.product_schema import TermsheetExtract
from src.extractor.system_prompt import TERMSHEET_EXTRACTION_PROMPT

load_dotenv()


def extract_termsheet(parsed_text: str) -> TermsheetExtract:
    """Use LLM to extract structured termsheet data from PDF text."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    client = OpenAI(api_key=api_key)

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": TERMSHEET_EXTRACTION_PROMPT,
            },
            {
                "role": "user",
                "content": f"Extract ALL data from this termsheet document. Return JSON matching TermsheetExtract schema:\n\n{parsed_text}",
            },
        ],
        temperature=0.0,
        response_format=TermsheetExtract,
    )

    result = response.choices[0].message.parsed
    if result is None:
        raise ValueError("LLM returned empty response")
    
    return result
