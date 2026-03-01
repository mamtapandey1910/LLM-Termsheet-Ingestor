"""Tests for src.cli module."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from src.cli import build_parser, main


SAMPLE_RESULT = {"company_name": "Acme", "investment_amount": "$5M"}


class TestBuildParser:
    def test_requires_file_argument(self):
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_parses_file_argument(self):
        parser = build_parser()
        args = parser.parse_args(["sheet.txt"])
        assert args.file == "sheet.txt"

    def test_parses_optional_model(self):
        parser = build_parser()
        args = parser.parse_args(["sheet.txt", "--model", "gpt-4"])
        assert args.model == "gpt-4"

    def test_parses_output_flag(self):
        parser = build_parser()
        args = parser.parse_args(["sheet.txt", "-o", "out.json"])
        assert args.output == "out.json"


class TestMain:
    def test_prints_json_to_stdout(self, capsys):
        import src.cli as cli_mod
        with patch.object(cli_mod, "ingest_file", return_value=SAMPLE_RESULT):
            main(["samples/sample_termsheet.txt"])

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["company_name"] == "Acme"

    def test_exits_on_file_not_found(self):
        import src.cli as cli_mod
        with patch.object(cli_mod, "ingest_file", side_effect=FileNotFoundError("not found")):
            with pytest.raises(SystemExit) as exc_info:
                main(["nonexistent.txt"])

        assert exc_info.value.code == 1

    def test_writes_to_output_file(self, tmp_path):
        out_file = tmp_path / "result.json"
        import src.cli as cli_mod
        with patch.object(cli_mod, "ingest_file", return_value=SAMPLE_RESULT):
            main(["sheet.txt", "-o", str(out_file)])

        assert out_file.exists()
        data = json.loads(out_file.read_text())
        assert data["company_name"] == "Acme"
