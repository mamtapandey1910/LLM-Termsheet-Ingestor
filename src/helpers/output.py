"""Output handling for extraction results."""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schema.product_schema import TermsheetExtract

OUTPUT_DIR = Path("output")


def generate_run_id() -> str:
    """Generate unique run ID with timestamp and UUID."""
    return datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]


def save_extraction_json(result: TermsheetExtract, run_id: str) -> Path:
    """Save extraction result to JSON file."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / f"extraction_{run_id}.json"
    
    json_output = result.model_dump(mode="json")
    with open(output_file, "w") as f:
        json.dump(json_output, f, indent=2, default=str)
    
    return output_file


def print_json(result: TermsheetExtract) -> None:
    """Print extraction result as formatted JSON."""
    print("\n--- Extracted Termsheet Data (JSON) ---")
    print(json.dumps(result.model_dump(mode="json"), indent=2, default=str))
