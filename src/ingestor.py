"""Core LLM-based term sheet ingestion logic."""

from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None  # type: ignore[assignment]

# Fields the LLM is asked to extract from every term sheet.
TERM_SHEET_FIELDS = [
    "company_name",
    "investment_amount",
    "pre_money_valuation",
    "post_money_valuation",
    "valuation_cap",
    "discount_rate",
    "interest_rate",
    "security_type",
    "investors",
    "lead_investor",
    "closing_date",
    "liquidation_preference",
    "participation",
    "anti_dilution",
    "board_composition",
    "pro_rata_rights",
    "information_rights",
    "governing_law",
]

_SYSTEM_PROMPT = (
    "You are a financial analyst specialising in venture-capital term sheets. "
    "Extract structured information from the provided term sheet text and return "
    "it as a single valid JSON object. Use null for any field that cannot be found. "
    "Do not include markdown fences or any text outside the JSON object."
)

_USER_PROMPT_TEMPLATE = """Extract the following fields from the term sheet below.

Fields to extract:
{fields}

Term sheet text:
\"\"\"
{text}
\"\"\"

Return a JSON object with exactly the listed keys."""


def _build_user_prompt(text: str) -> str:
    fields_list = "\n".join(f"- {f}" for f in TERM_SHEET_FIELDS)
    return _USER_PROMPT_TEMPLATE.format(fields=fields_list, text=text)


def ingest(
    text: str,
    model: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Send *text* to the LLM and return extracted term sheet fields.

    Args:
        text:    Raw text content of the term sheet.
        model:   OpenAI model identifier (defaults to the ``OPENAI_MODEL``
                 environment variable, or ``gpt-4o``).
        api_key: OpenAI API key (defaults to the ``OPENAI_API_KEY``
                 environment variable).

    Returns:
        A dictionary containing the extracted term sheet fields.

    Raises:
        ImportError:  If the ``openai`` package is not installed.
        ValueError:   If the LLM response cannot be parsed as JSON.
        openai.OpenAIError: For API-level errors.
    """
    if openai is None:
        raise ImportError(
            "openai package is required. Install it with: pip install openai"
        )

    resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
    resolved_model = model or os.getenv("OPENAI_MODEL", "gpt-4o")

    client = openai.OpenAI(api_key=resolved_api_key)

    response = client.chat.completions.create(
        model=resolved_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(text)},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    raw = response.choices[0].message.content or ""
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned non-JSON content:\n{raw}"
        ) from exc


def ingest_file(
    file_path: str,
    model: str | None = None,
    api_key: str | None = None,
) -> dict[str, Any]:
    """Load a term sheet document from disk and ingest it.

    Convenience wrapper around :func:`ingest` and
    :func:`~src.parsers.load_document`.

    Args:
        file_path: Path to the term sheet file (.txt, .md, .pdf, or .docx).
        model:     OpenAI model identifier.
        api_key:   OpenAI API key.

    Returns:
        A dictionary containing the extracted term sheet fields.
    """
    from src.parsers import load_document

    text = load_document(file_path)
    return ingest(text, model=model, api_key=api_key)
