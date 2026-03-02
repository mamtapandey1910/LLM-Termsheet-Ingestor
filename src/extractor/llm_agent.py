from __future__ import annotations

import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI

from src.schema.product_schema import TermsheetExtract

load_dotenv()


def _strip_markdown_json(text: str) -> str:
    """Strip markdown code blocks from JSON response."""
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text)
    return match.group(1) if match else text


def extract_termsheet(parsed_text: str) -> TermsheetExtract:
    """Use LLM to extract structured termsheet data from PDF text."""
    print("=== INPUT TEXT ===")
    print(parsed_text)
    print("=== END INPUT ===")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    client = OpenAI(api_key=api_key)

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert financial document extraction engine. "
                    "Given an article, produce a JSON object that exactly "
                    "matches the TermsheetExtract schema."
                ),
            },
            {
                "role": "user",
                "content": f"Produce the JSON now for the {parsed_text}",
            },
        ],
        temperature=0.1,
        response_format=TermsheetExtract,
    )

    print(response.choices[0].message.parsed)
    
    if response.choices[0].message.parsed is not None:
        return response.choices[0].message.parsed

    raw_text = response.choices[0].message.content
    if raw_text is None:
        raise ValueError("LLM returned empty response")

    clean_json = _strip_markdown_json(raw_text)
    data = json.loads(clean_json)
    return TermsheetExtract.model_validate(data)
