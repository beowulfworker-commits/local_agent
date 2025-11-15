from __future__ import annotations

import os
from typing import Any, Dict
from . import Tool

class FileReaderTool:
    """Read a text file from the repository with safe path checks."""

    name = "file_reader"
    description = "Read the contents of a file within the repository."
    input_schema = {
        "path": {"type": "string", "required": True, "description": "Relative path inside repo"},
        "max_chars": {"type": "integer", "default": 2000, "description": "Limit output length"},
    }

    def __init__(self, repo_root: str | None = None) -> None:
        self.repo_root = os.path.abspath(
            repo_root or os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
        )

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        path = kwargs.get("path")
        max_chars = int(kwargs.get("max_chars", 2000))
        if not path:
            raise ValueError("'path' argument is required")

        abs_path = os.path.abspath(os.path.join(self.repo_root, path))
        if not abs_path.startswith(self.repo_root):
            raise ValueError("Access outside the repository is not allowed")
        if not os.path.isfile(abs_path):
            raise FileNotFoundError(f"File not found: {path}")

        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
        return {"content": content, "truncated": len(content) >= max_chars}
