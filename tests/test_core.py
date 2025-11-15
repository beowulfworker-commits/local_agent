"""
Tests for the Agent core.
"""

from typing import Any, Dict, List

from agent.core import Agent


class DummyBackend:
    """A dummy backend that echoes the last user message prefixed with 'echo'."""

    def generate(self, prompt: str, history: List[Dict[str, str]], system_prompt=None, model=None) -> str:
        return f"echo: {prompt}"


def test_agent_chat_no_tools(tmp_path):
    # Use a dummy tools config with no tools
    config = tmp_path / "tools.yaml"
    config.write_text("tools: []\n")
    backend = DummyBackend()
    agent = Agent(backend=backend, tools_config=str(config))
    reply = agent.chat("hello", use_tools=False)
    assert reply == "echo: hello"


def test_agent_chat_with_tools(tmp_path):
    # Use dummy tool config and dummy backend that returns JSON to trigger tool call
    tools_yaml = tmp_path / "tools.yaml"
    # Create a simple tool that returns args
    tools_yaml.write_text(
        """
tools:
  - name: dummy
    module: tests.dummy_tool
    class: DummyTool
    description: Dummy tool
"""
    )
    # Create dummy tool module in tmp path
    dummy_tool_py = tmp_path / "tests" / "dummy_tool.py"
    dummy_tool_py.parent.mkdir(exist_ok=True)
    dummy_tool_py.write_text(
        """
class DummyTool:
    name = 'dummy'
    description = 'dummy'
    input_schema = {}
    def run(self, **kwargs):
        return {'ran': True, 'args': kwargs}
"""
    )
    import sys
    sys.path.insert(0, str(tmp_path))

    class JsonBackend:
        def __init__(self):
            self.called = False
        def generate(self, prompt: str, history: List[Dict[str, str]], system_prompt=None, model=None) -> str:
            # Always return a tool invocation
            return '{"tool": {"name": "dummy", "args": {"x": 1}}}'

    backend = JsonBackend()
    agent = Agent(backend=backend, tools_config=str(tools_yaml))
    reply = agent.chat("test", use_tools=True)
    assert reply == '{"ran": true, "args": {"x": 1}}'