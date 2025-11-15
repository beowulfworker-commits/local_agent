from __future__ import annotations

import os
import re
from typing import Any, Dict, List
from . import Tool

class FileSearchTool:
    """Search for a string or regex pattern across repository files."""

    name = "file_search"
    description = "Search for a string or regex pattern in repository files."
    input_schema = {
        "query": {"type": "string", "required": True, "description": "Search text or regex"},
        "regex": {"type": "boolean", "default": False},
        "max_results": {"type": "integer", "default": 100},
    }

    _IGNORE_DIRS = {".git", "__pycache__", "venv", "node_modules", ".mypy_cache"}
    _TEXT_EXT = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".sh", ".ps1", ".html", ".css", ".js"}

    def __init__(self, repo_root: str | None = None) -> None:
        self.repo_root = os.path.abspath(
            repo_root or os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
        )

    def _is_text_file(self, path: str) -> bool:
        return os.path.splitext(path)[1].lower() in self._TEXT_EXT

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        query = kwargs.get("query")
        regex = bool(kwargs.get("regex", False))
        max_results = int(kwargs.get("max_results", 100))
        if not query:
            raise ValueError("'query' argument is required")

        pattern = re.compile(query if regex else re.escape(query), re.IGNORECASE)
        matches: List[Dict[str, Any]] = []

        for root, dirs, files in os.walk(self.repo_root):
            # prune ignored directories
            dirs[:] = [d for d in dirs if d not in self._IGNORE_DIRS]
            for fn in files:
                full = os.path.join(root, fn)
                if not self._is_text_file(full):
                    continue
                rel = os.path.relpath(full, self.repo_root)
                try:
                    with open(full, "r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, 1):
                            if pattern.search(line):
                                matches.append({"file": rel, "line": lineno, "text": line.rstrip("\n")})
                                if len(matches) >= max_results:
                                    return {"matches": matches, "truncated": True}
                except Exception:
                    continue
        return {"matches": matches, "truncated": False}
