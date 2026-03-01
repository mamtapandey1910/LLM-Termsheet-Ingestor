"""Command-line interface for the LLM Termsheet Ingestor."""

from __future__ import annotations

import argparse
import json
import sys

from src.ingestor import ingest_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="termsheet-ingestor",
        description=(
            "Extract structured data from a term sheet document "
            "using an LLM (OpenAI)."
        ),
    )
    parser.add_argument(
        "file",
        help="Path to the term sheet file (.txt, .md, .pdf, or .docx).",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=(
            "OpenAI model to use (e.g. gpt-4o). "
            "Defaults to the OPENAI_MODEL environment variable or 'gpt-4o'."
        ),
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help=(
            "OpenAI API key. "
            "Defaults to the OPENAI_API_KEY environment variable."
        ),
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write JSON output to this file instead of stdout.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2).",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = ingest_file(args.file, model=args.model, api_key=args.api_key)
    except (FileNotFoundError, ValueError, ImportError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(result, indent=args.indent, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
