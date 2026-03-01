"""Unit tests for the OpenAI-based termsheet extractor."""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.extractor import extract_termsheet_data
from src.models import TermsheetData

SAMPLE_TEXT = """
Deal Name: Project Apollo
Borrower: Apollo Industries Ltd.
Lender: Global Capital Bank N.A.
Facility Type: Senior Secured Term Loan A
Currency: USD
Facility Amount: $250,000,000
Interest Rate: Term SOFR + 2.75%
Maturity Date: March 31, 2030
Closing Date: March 31, 2025
Purpose: Refinancing and general corporate purposes
Covenants: Total Net Leverage <= 4.0x, ICR >= 3.0x
Fees: 1.00% upfront, 0.50% commitment
"""

EXPECTED_FIELDS = {
    "deal_name": "Project Apollo",
    "borrower": "Apollo Industries Ltd.",
    "lender": "Global Capital Bank N.A.",
    "facility_type": "Senior Secured Term Loan A",
    "currency": "USD",
    "facility_amount": "$250,000,000",
    "interest_rate": "Term SOFR + 2.75%",
    "maturity_date": "March 31, 2030",
    "closing_date": "March 31, 2025",
    "purpose": "Refinancing and general corporate purposes",
    "covenants": "Total Net Leverage <= 4.0x, ICR >= 3.0x",
    "fees": "1.00% upfront, 0.50% commitment",
}


def _make_mock_client(response_payload: dict) -> MagicMock:
    """Build a minimal OpenAI client mock that returns *response_payload*."""
    mock_message = MagicMock()
    mock_message.content = json.dumps(response_payload)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


def test_extract_returns_termsheet_data_instance():
    client = _make_mock_client(EXPECTED_FIELDS)
    result = extract_termsheet_data(SAMPLE_TEXT, client=client)
    assert isinstance(result, TermsheetData)


def test_extract_populates_all_fields():
    client = _make_mock_client(EXPECTED_FIELDS)
    result = extract_termsheet_data(SAMPLE_TEXT, client=client)

    assert result.deal_name == "Project Apollo"
    assert result.borrower == "Apollo Industries Ltd."
    assert result.lender == "Global Capital Bank N.A."
    assert result.facility_type == "Senior Secured Term Loan A"
    assert result.currency == "USD"
    assert result.facility_amount == "$250,000,000"
    assert result.interest_rate == "Term SOFR + 2.75%"
    assert result.maturity_date == "March 31, 2030"
    assert result.closing_date == "March 31, 2025"


def test_extract_stores_raw_text():
    client = _make_mock_client(EXPECTED_FIELDS)
    result = extract_termsheet_data(SAMPLE_TEXT, client=client)
    assert result.raw_text == SAMPLE_TEXT


def test_extract_handles_missing_fields():
    partial_payload = {"deal_name": "Project Beta", "borrower": "Beta Corp"}
    client = _make_mock_client(partial_payload)
    result = extract_termsheet_data(SAMPLE_TEXT, client=client)

    assert result.deal_name == "Project Beta"
    assert result.borrower == "Beta Corp"
    assert result.interest_rate is None
    assert result.maturity_date is None


def test_extract_uses_env_model(monkeypatch):
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
    client = _make_mock_client(EXPECTED_FIELDS)
    extract_termsheet_data(SAMPLE_TEXT, client=client)

    call_kwargs = client.chat.completions.create.call_args
    assert call_kwargs.kwargs["model"] == "gpt-4o"


def test_extract_creates_client_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    payload = {"deal_name": "Env Test"}
    with patch("src.extractor.OpenAI") as mock_openai_cls:
        mock_client = _make_mock_client(payload)
        mock_openai_cls.return_value = mock_client

        result = extract_termsheet_data("some text")

    mock_openai_cls.assert_called_once_with(api_key="test-key")
    assert result.deal_name == "Env Test"
