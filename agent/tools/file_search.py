"""
File search tool for the agent.

This tool searches for a text query within files in the repository. It returns
the list of occurrences with file paths and line numbers, up to a maximum
number of matches. Only text files (with certain extensions) are scanned.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List

from . import Tool


class FileSearchTool:
    """Tool for searching text in files within the repository."""

    name = "file_search"
    description = "Search for a string or regex pattern in repository files and return occurrences."
    input_schema: Dict[str, Any] = {
        "query": {
            "type": "string",
            "description": "String or regular expression to search for.",
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum number of matches to return.",
            "default": 20,
        },
    }

    # Define a simple list of file extensions to include in the search
    TEXT_EXTENSIONS = {
        ".py", ".md", ".txt", ".yaml", ".yml", ".json", ".sh", ".ps1",
        ".ini", ".cfg", ".toml", ".js", ".ts", ".html", ".css"
    }

    def __init__(self, repo_root: str | None = None) -> None:
        self.repo_root = (
            repo_root
            if repo_root is not None
            else os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        )

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        query = kwargs.get("query")
        max_results = int(kwargs.get("max_results", 20))
        if not query:
            raise ValueError("'query' argument is required")
        pattern = re.compile(query, re.IGNORECASE)
        matches: List[Dict[str, Any]] = []

        for root, dirs, files in os.walk(self.repo_root):
            for fname in files:
                _, ext = os.path.splitext(fname)
                if ext.lower() not in self.TEXT_EXTENSIONS:
                    continue
                file_path = os.path.join(root, fname)
                rel_path = os.path.relpath(file_path, self.repo_root)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for lineno, line in enumerate(f, start=1):
                            if pattern.search(line):
                                matches.append({
                                    "file": rel_path,
                                    "line": lineno,
                                    "text": line.strip(),
                                })
                                if len(matches) >= max_results:
                                    return {"matches": matches, "truncated": True}
                except Exception:
                    # Ignore files we cannot read
                    continue
        return {"matches": matches, "truncated": False}


ToolImpl = FileSearchTool