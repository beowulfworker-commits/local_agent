from __future__ import annotations

import datetime
import os
from typing import Any, Dict
from . import Tool

class LoggerTool:
    """Append a note to notes.txt in the repository root."""

    name = "logger"
    description = "Append a note with timestamp to notes.txt."
    input_schema = {
        "note": {"type": "string", "required": True, "description": "Text to append"},
    }

    def __init__(self, repo_root: str | None = None) -> None:
        self.repo_root = os.path.abspath(
            repo_root or os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
        )
        self.notes_path = os.path.join(self.repo_root, "notes.txt")

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        note = kwargs.get("note")
        if not note:
            raise ValueError("'note' argument is required")
        timestamp = datetime.datetime.now().isoformat(timespec="seconds")
        with open(self.notes_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {note}\n")
        return {"path": os.path.relpath(self.notes_path, self.repo_root), "note": note}
