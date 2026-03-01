"""Tests for src.ingestor module."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.ingestor import TERM_SHEET_FIELDS, _build_user_prompt, ingest


SAMPLE_EXTRACTED = {
    "company_name": "Acme Technologies, Inc.",
    "investment_amount": "$5,000,000",
    "pre_money_valuation": "$20,000,000",
    "post_money_valuation": "$25,000,000",
    "valuation_cap": None,
    "discount_rate": None,
    "interest_rate": "8% per annum",
    "security_type": "Series A Preferred Stock",
    "investors": ["Sequoia Capital", "Andreessen Horowitz"],
    "lead_investor": "Sequoia Capital",
    "closing_date": "March 31, 2026",
    "liquidation_preference": "1x non-participating",
    "participation": None,
    "anti_dilution": "Weighted-average",
    "board_composition": "2 Common, 1 Series A, 1 Independent",
    "pro_rata_rights": True,
    "information_rights": "Monthly statements for holders of ≥5% Series A",
    "governing_law": "State of Delaware",
}


class TestBuildUserPrompt:
    def test_includes_all_fields(self):
        prompt = _build_user_prompt("some text")
        for field in TERM_SHEET_FIELDS:
            assert field in prompt

    def test_includes_text(self):
        prompt = _build_user_prompt("unique_marker_xyz")
        assert "unique_marker_xyz" in prompt


class TestIngest:
    def _make_mock_openai(self, payload: dict) -> MagicMock:
        """Return a mock openai module whose client returns payload."""
        mock_choice = MagicMock()
        mock_choice.message.content = json.dumps(payload)

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        mock_openai = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        return mock_openai

    def test_returns_parsed_dict(self):
        mock_openai = self._make_mock_openai(SAMPLE_EXTRACTED)

        import src.ingestor as ingestor_mod
        with patch.object(ingestor_mod, "openai", mock_openai):
            result = ingest("some term sheet text", api_key="test-key")

        assert result["company_name"] == "Acme Technologies, Inc."
        assert result["security_type"] == "Series A Preferred Stock"

    def test_passes_model_to_api(self):
        mock_openai = self._make_mock_openai(SAMPLE_EXTRACTED)
        mock_client = mock_openai.OpenAI.return_value

        import src.ingestor as ingestor_mod
        with patch.object(ingestor_mod, "openai", mock_openai):
            ingest("text", model="gpt-3.5-turbo", api_key="test-key")

        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs.kwargs["model"] == "gpt-3.5-turbo"

    def test_raises_value_error_on_invalid_json(self):
        mock_choice = MagicMock()
        mock_choice.message.content = "not valid json {"

        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response

        mock_openai = MagicMock()
        mock_openai.OpenAI.return_value = mock_client

        import src.ingestor as ingestor_mod
        with patch.object(ingestor_mod, "openai", mock_openai):
            with pytest.raises(ValueError, match="non-JSON"):
                ingest("text", api_key="test-key")

    def test_raises_import_error_without_openai(self):
        import src.ingestor as ingestor_mod
        with patch.object(ingestor_mod, "openai", None):
            with pytest.raises(ImportError, match="openai package"):
                ingest("text", api_key="test-key")
