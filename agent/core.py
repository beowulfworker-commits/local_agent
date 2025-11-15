from __future__ import annotations

import importlib
import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml

from .llm_backend import LLMBackend
from agent.tools import Tool  # type: ignore

logger = logging.getLogger(__name__)

@dataclass
class Agent:
    """Local AI agent orchestrating an LLM and a set of tools."""
    backend: LLMBackend
    tools_config: str = "agent/config/tools.yaml"
    history: List[Dict[str, str]] = field(default_factory=list)
    tools: Dict[str, Tool] = field(init=False)

    def __post_init__(self) -> None:
        self.tools = self._load_tools(self.tools_config)

    def _load_tools(self, config_path: str) -> Dict[str, Tool]:
        if not os.path.isabs(config_path):
            config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, config_path))
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        tools: Dict[str, Tool] = {}
        for entry in config.get("tools", []):
            name = entry["name"]
            module_name = entry["module"]
            class_name = entry.get("class") or f"{name.capitalize()}Tool"
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            tools[name] = cls()
            logger.info("Loaded tool: %s from %s:%s", name, module_name, class_name)
        return tools

    def _build_system_prompt(self) -> str:
        lines = [
            "You are a local assistant with tool-calling ability.",
            "Available tools:",
        ]
        for tool in self.tools.values():
            lines.append(f"- {tool.name}: {tool.description}. Input schema: {tool.input_schema}")
        lines.append('When you decide to use a tool, respond with JSON exactly as:')
        lines.append('{"tool": {"name": "<tool_name>", "args": {"param1": "value"}}}')
        lines.append("No code fences. No extra text.")
        return "\n".join(lines)

    def _try_extract_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        text = text.strip()
        # Fast path: whole message is JSON
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "tool" in obj:
                return obj
        except Exception:
            pass
        # Tolerant path: try first {...} block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            try:
                obj = json.loads(text[start : end + 1])
                if isinstance(obj, dict) and "tool" in obj:
                    return obj
            except Exception:
                pass
        return None

    def chat(self, message: str, *, use_tools: bool = False) -> str:
        logger.info("User: %s", message)
        system_prompt = self._build_system_prompt() if use_tools else None
        response = self.backend.generate(prompt=message, history=self.history, system_prompt=system_prompt)
        reply = response.strip()

        if use_tools:
            tool_obj = self._try_extract_tool_call(reply)
            if tool_obj:
                try:
                    req = tool_obj["tool"]
                    name = req.get("name")
                    args: Dict[str, Any] = req.get("args") or {}
                    tool = self.tools.get(name)
                    if not tool:
                        return json.dumps({"error": f"Unknown tool: {name}"}, ensure_ascii=False)
                    result = tool.run(**args)
                    # log into history
                    self.history.append({"role": "user", "content": message})
                    self.history.append({"role": "assistant", "content": reply})
                    self.history.append({"role": "assistant", "content": json.dumps(result, ensure_ascii=False)})
                    return json.dumps(result, ensure_ascii=False)
                except Exception as e:
                    logger.exception("Tool call failed: %s", e)
                    return json.dumps({"error": str(e)}, ensure_ascii=False)

        # normal chat
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": reply})
        return reply
