"""
Unit tests for agent tools.
"""

import os
import tempfile

from agent.tools.file_reader import FileReaderTool
from agent.tools.file_search import FileSearchTool
from agent.tools.logger import LoggerTool


def test_file_reader(tmp_path):
    # Create a temporary file
    file_path = tmp_path / "hello.txt"
    content = "Hello world"
    file_path.write_text(content)
    reader = FileReaderTool(repo_root=str(tmp_path))
    result = reader.run(path="hello.txt")
    assert result["content"] == content
    assert not result["truncated"]


def test_file_search(tmp_path):
    # Create files
    (tmp_path / "a.txt").write_text("foo bar\nhello world")
    (tmp_path / "b.md").write_text("another foo line\nno match")
    search_tool = FileSearchTool(repo_root=str(tmp_path))
    result = search_tool.run(query="foo", max_results=10)
    matches = result["matches"]
    assert len(matches) == 2
    assert any(m["file"].endswith("a.txt") for m in matches)


def test_logger(tmp_path):
    logger_tool = LoggerTool(repo_root=str(tmp_path))
    note = "Test note"
    result = logger_tool.run(note=note)
    notes_file = tmp_path / result["path"]
    assert notes_file.exists()
    contents = notes_file.read_text()
    assert note in contents