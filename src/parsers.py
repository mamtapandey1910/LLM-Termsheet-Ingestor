"""Parsers for various term sheet document formats."""

from __future__ import annotations

import os


def parse_text(file_path: str) -> str:
    """Read a plain-text or Markdown file and return its contents."""
    with open(file_path, encoding="utf-8") as fh:
        return fh.read()


def parse_pdf(file_path: str) -> str:
    """Extract all text from a PDF file using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ImportError(
            "pypdf is required to parse PDF files. "
            "Install it with: pip install pypdf"
        ) from exc

    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def parse_docx(file_path: str) -> str:
    """Extract all text from a .docx file using python-docx."""
    try:
        from docx import Document
    except ImportError as exc:
        raise ImportError(
            "python-docx is required to parse DOCX files. "
            "Install it with: pip install python-docx"
        ) from exc

    doc = Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs]
    return "\n".join(paragraphs)


def load_document(file_path: str) -> str:
    """Detect the file type by extension and return its text content.

    Supported extensions: .txt, .md, .pdf, .docx
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Document not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext in {".txt", ".md"}:
        return parse_text(file_path)
    if ext == ".pdf":
        return parse_pdf(file_path)
    if ext == ".docx":
        return parse_docx(file_path)

    raise ValueError(
        f"Unsupported file extension '{ext}'. "
        "Supported formats: .txt, .md, .pdf, .docx"
    )
