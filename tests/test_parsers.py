"""Tests for src.parsers module."""

from __future__ import annotations

import os
import tempfile

import pytest

from src.parsers import load_document, parse_text


SAMPLE_TEXT = "Hello, this is a test term sheet."


class TestParseText:
    def test_reads_plain_text_file(self, tmp_path):
        p = tmp_path / "sheet.txt"
        p.write_text(SAMPLE_TEXT, encoding="utf-8")
        assert parse_text(str(p)) == SAMPLE_TEXT

    def test_reads_markdown_file(self, tmp_path):
        p = tmp_path / "sheet.md"
        p.write_text("# Title\nSome content.", encoding="utf-8")
        result = parse_text(str(p))
        assert "Title" in result


class TestLoadDocument:
    def test_loads_txt(self, tmp_path):
        p = tmp_path / "doc.txt"
        p.write_text(SAMPLE_TEXT, encoding="utf-8")
        assert load_document(str(p)) == SAMPLE_TEXT

    def test_loads_md(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text("## Section\nDetails here.", encoding="utf-8")
        result = load_document(str(p))
        assert "Section" in result

    def test_raises_for_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_document(str(tmp_path / "nonexistent.txt"))

    def test_raises_for_unsupported_extension(self, tmp_path):
        p = tmp_path / "doc.xyz"
        p.write_text("data", encoding="utf-8")
        with pytest.raises(ValueError, match="Unsupported file extension"):
            load_document(str(p))
