"""
Logger tool for the agent.

This tool appends a note to a ``notes.txt`` file in the repository. It is
useful for capturing reminders or ideas during a session. If the file does not
exist, it will be created. The tool returns the path to the notes file and the
note that was written.
"""

from __future__ import annotations

import datetime
import os
from typing import Any, Dict

from . import Tool


class LoggerTool:
    """Tool for logging notes to a file."""

    name = "logger"
    description = "Append a note to notes.txt in the repository."
    input_schema: Dict[str, Any] = {
        "note": {
            "type": "string",
            "description": "The note to append.",
        }
    }

    def __init__(self, repo_root: str | None = None) -> None:
        self.repo_root = (
            repo_root
            if repo_root is not None
            else os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        )
        self.notes_path = os.path.join(self.repo_root, "notes.txt")

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        note = kwargs.get("note")
        if not note:
            raise ValueError("'note' argument is required")
        timestamp = datetime.datetime.now().isoformat()
        entry = f"[{timestamp}] {note}\n"
        with open(self.notes_path, "a", encoding="utf-8") as f:
            f.write(entry)
        return {"path": os.path.relpath(self.notes_path, self.repo_root), "note": note}


ToolImpl = LoggerTool