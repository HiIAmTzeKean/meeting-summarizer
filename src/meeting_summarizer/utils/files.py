"""File I/O utilities."""

import dataclasses
import json
from pathlib import Path

from meeting_summarizer.models import MeetingSummary


def save_summary_json(summary: MeetingSummary, output_path: str | Path) -> None:
    """Export the full summary as a JSON file (preserves CJK characters)."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataclasses.asdict(summary), f, indent=2, ensure_ascii=False)
    print(f"Saved: {output_path}")
