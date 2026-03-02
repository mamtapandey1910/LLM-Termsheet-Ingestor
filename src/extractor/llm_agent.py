from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

from src.schema.product_schema import TermsheetExtract
from src.extractor.system_prompt import TERMSHEET_EXTRACTION_PROMPT

load_dotenv()

from src.extractor.errors import (
    MissingAPIKeyError,
    OpenAIInitializationError,
    OpenAICallError,
    LLMParseError,
    SchemaValidationError,
    call_with_backoff,
)


def extract_termsheet(parsed_text: str) -> TermsheetExtract:
    """Use LLM to extract structured termsheet data from PDF text."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise MissingAPIKeyError("OPENAI_API_KEY environment variable is required")

    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        raise OpenAIInitializationError(f"Failed to initialize OpenAI client: {e}")

    try:
        response = call_with_backoff(
            client.beta.chat.completions.parse,
            model="gpt-4o",
            messages=[
                {"role": "system", "content": TERMSHEET_EXTRACTION_PROMPT},
                {
                    "role": "user",
                    "content": f"Extract ALL data from this termsheet document. Return JSON matching TermsheetExtract schema:\n\n{parsed_text}",
                },
            ],
            temperature=0.0,
            response_format=TermsheetExtract,
        )
    except OpenAICallError:
        raise
    except Exception as e:
        # Wrap unexpected exceptions
        raise OpenAICallError(f"OpenAI API call failed: {e}")

    try:
        result = response.choices[0].message.parsed
    except Exception as e:
        raise LLMParseError(f"Failed to parse LLM response: {e}")

    if result is None:
        raise ValueError("LLM returned empty response")
    try:
        validated = TermsheetExtract.model_validate(result)
    except Exception as e:
        raise SchemaValidationError(f"Schema validation failed: {e}")
    return validated

