import json
import os

from openai import OpenAI

from .models import TermsheetData

_EXTRACTION_PROMPT = """
You are a financial analyst expert. Extract structured information from the following termsheet text.
Return a JSON object with these fields (use null for any field not found):
- deal_name: Name or identifier of the deal
- borrower: Name of the borrower or issuer
- lender: Name of the lender or arranger
- facility_type: Type of facility (e.g., Term Loan, Revolving Credit Facility)
- currency: Currency of the facility (e.g., USD, EUR)
- facility_amount: Total size of the facility (e.g., "$500,000,000")
- interest_rate: Interest rate or pricing terms (e.g., "SOFR + 2.50%")
- maturity_date: Maturity or final repayment date
- closing_date: Expected or actual closing date
- purpose: Purpose or use of proceeds
- covenants: Key covenants (summarise briefly)
- fees: Fee terms (upfront, commitment, etc.)

Return only the JSON object with no additional explanation.

Termsheet text:
\"\"\"
{text}
\"\"\"
"""


def extract_termsheet_data(text: str, client: OpenAI | None = None) -> TermsheetData:
    """Use OpenAI to extract structured data from termsheet text.

    Args:
        text: The raw termsheet text to parse.
        client: Optional OpenAI client; a new one is created from the environment
                if not provided.

    Returns:
        A :class:`TermsheetData` instance populated with extracted values.
    """
    if client is None:
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": _EXTRACTION_PROMPT.format(text=text),
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    content = response.choices[0].message.content
    data = json.loads(content)
    data["raw_text"] = text
    return TermsheetData(**data)
