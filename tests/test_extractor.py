import os
import unittest
from unittest.mock import patch

from src.schema.product_schema import TermsheetExtract

from src.extractor import llm_agent
from src.extractor.errors import OpenAICallError, SchemaValidationError


class FakeMessage:
    def __init__(self, parsed):
        self.parsed = parsed


class FakeChoice:
    def __init__(self, parsed):
        self.message = FakeMessage(parsed)


class FakeResponse:
    def __init__(self, parsed):
        self.choices = [FakeChoice(parsed)]


class TestLLMAgent(unittest.TestCase):
    def setUp(self):
        # ensure API key present for tests
        os.environ["OPENAI_API_KEY"] = "test-key"

    def tearDown(self):
        os.environ.pop("OPENAI_API_KEY", None)

    def test_extract_termsheet_success(self):
        parsed = {
            "isin": "GB00TEST1234",
            "issuer": "Test Issuer",
            "issue_date": "2024-01-01",
            "trade_date": "2024-01-02",
            "maturity_date": "2025-01-01",
        }

        with patch.object(llm_agent, "call_with_backoff", return_value=FakeResponse(parsed)):
            result = llm_agent.extract_termsheet("dummy pdf text")
            self.assertIsInstance(result, TermsheetExtract)
            self.assertEqual(result.isin, parsed["isin"])
            self.assertEqual(result.issuer, parsed["issuer"]) 

    def test_extract_termsheet_openai_error(self):
        with patch.object(llm_agent, "call_with_backoff", side_effect=OpenAICallError("fail")):
            with self.assertRaises(OpenAICallError):
                llm_agent.extract_termsheet("dummy pdf text")

    def test_extract_termsheet_schema_error(self):
        # missing required fields (no isin)
        parsed = {
            "issuer": "Test Issuer",
            "issue_date": "2024-01-01",
            "trade_date": "2024-01-02",
            "maturity_date": "2025-01-01",
        }
        with patch.object(llm_agent, "call_with_backoff", return_value=FakeResponse(parsed)):
            with self.assertRaises(SchemaValidationError):
                llm_agent.extract_termsheet("dummy pdf text")


if __name__ == "__main__":
    unittest.main()
