"""
Core agent logic.

The :class:`Agent` class orchestrates interactions between the user, the
language model backend, and the registered tools. It maintains a conversation
history and can operate in two modes:

1. Pure chat mode: the agent simply forwards messages to the model and
   returns its responses.
2. Tool-enabled mode: the model is instructed about available tools and may
   request tool invocations by returning a JSON structure. The agent parses
   these requests, calls the appropriate tool, and returns the tool output
   back to the user.

This implementation uses a simple protocol where the model should respond
with a JSON object of the form ``{"tool": {"name": ..., "args": {...}}}`` to
invoke a tool. Any other response is treated as a normal assistant reply.
"""

from __future__ import annotations

import importlib
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml

from .llm_backend import LLMBackend
from .tools import Tool

logger = logging.getLogger(__name__)


@dataclass
class Agent:
    """Local AI agent orchestrating an LLM and a set of tools."""

    backend: LLMBackend
    tools_config: str
    history: List[Dict[str, str]] = field(default_factory=list)
    tools: Dict[str, Tool] = field(init=False)

    def __post_init__(self) -> None:
        self.tools = self._load_tools(self.tools_config)

    def _load_tools(self, config_path: str) -> Dict[str, Tool]:
        """Load tools defined in a YAML configuration file."""
        if not os.path.isabs(config_path):
            # resolve relative to repository root
            config_path = os.path.join(os.path.dirname(__file__), os.pardir, config_path)
            config_path = os.path.abspath(config_path)
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        tools: Dict[str, Tool] = {}
        for entry in config.get("tools", []):
            name = entry["name"]
            module_name = entry["module"]
            class_name = entry.get("class") or name.capitalize() + "Tool"
            logger.debug("Loading tool %s from %s:%s", name, module_name, class_name)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            tools[name] = cls()
        return tools

    def _build_system_prompt(self) -> str:
        """Construct a system prompt describing the available tools."""
        lines = [
            "You are a local AI agent. The user may ask you to perform tasks.",
            "You have access to the following tools:",
        ]
        for tool in self.tools.values():
            lines.append(f"- {tool.name}: {tool.description}. Input schema: {tool.input_schema}")
        lines.append(
            "When you decide to use a tool, respond with a JSON object in the following format:"
        )
        lines.append(
            '{"tool": {"name": "<tool_name>", "args": {"param1": "value", ...}}}'
        )
        lines.append(
            "Do not wrap the JSON in code fences or include any additional text."
        )
        return "\n".join(lines)

    def chat(self, message: str, *, use_tools: bool = False) -> str:
        """
        Handle a single message from the user and return the agent's reply.

        :param message: The user's message.
        :param use_tools: Whether to allow the model to call tools.
        :returns: The agent's reply (either the model's answer or tool output).
        """
        logger.info("User: %s", message)
        system_prompt: Optional[str] = None
        prompt = message
        if use_tools:
            system_prompt = self._build_system_prompt()
        response = self.backend.generate(prompt=prompt, history=self.history, system_prompt=system_prompt)
        # Try to parse a tool request
        reply = response.strip()
        if use_tools and reply.startswith("{"):
            try:
                data = json.loads(reply)
                tool_info = data.get("tool")
                if tool_info:
                    tool_name: str = tool_info.get("name")
                    args: Dict[str, Any] = tool_info.get("args", {})
                    tool = self.tools.get(tool_name)
                    if not tool:
                        raise ValueError(f"Unknown tool: {tool_name}")
                    logger.info("Invoking tool %s with args %s", tool_name, args)
                    result = tool.run(**args)
                    # Add the tool invocation to the history
                    self.history.append({"role": "user", "content": message})
                    self.history.append({"role": "assistant", "content": reply})
                    # Provide tool result as assistant message
                    result_str = json.dumps(result, ensure_ascii=False)
                    self.history.append({"role": "assistant", "content": result_str})
                    return result_str
            except Exception as e:
                logger.exception("Failed to parse tool call: %s", e)
                # Fall through to normal response
        # Otherwise treat as normal chat
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": reply})
        return reply