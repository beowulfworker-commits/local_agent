"""
File reader tool for the agent.

This tool reads the contents of a file within the repository. It accepts a
relative path and returns the file contents. To mitigate large outputs, the
returned text is truncated to a maximum number of characters.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from . import Tool


class FileReaderTool:
    """Tool for reading files from the repository."""

    name = "file_reader"
    description = "Read the contents of a file within the repository given its relative path."
    input_schema: Dict[str, Any] = {
        "path": {
            "type": "string",
            "description": "Relative path to the file (relative to the repository root).",
        },
        "max_chars": {
            "type": "integer",
            "description": "Optional limit on the number of characters to return.",
            "default": 2000,
        },
    }

    def __init__(self, repo_root: str | None = None) -> None:
        # Determine the repository root relative to this file if not provided
        if repo_root is None:
            self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        else:
            self.repo_root = repo_root

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        path = kwargs.get("path")
        max_chars = int(kwargs.get("max_chars", 2000))
        if not path:
            raise ValueError("'path' argument is required")
        # Resolve path safely within repo
        abs_path = os.path.abspath(os.path.join(self.repo_root, path))
        if not abs_path.startswith(self.repo_root):
            raise ValueError("Access outside the repository is not allowed")
        if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(max_chars)
        return {"content": content, "truncated": len(content) >= max_chars}


ToolImpl = FileReaderTool