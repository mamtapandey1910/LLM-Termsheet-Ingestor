from __future__ import annotations

from pathlib import Path

import fitz  # pymupdf


def parse_pdf_text(file_path: str) -> str:
    """Extract all text from a PDF file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected .pdf file, got {path.suffix}")

    doc = fitz.open(file_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()

    return "\n".join(text_parts)
