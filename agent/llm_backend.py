from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import requests

logger = logging.getLogger(__name__)

class LLMBackend(Protocol):
    def generate(
        self,
        prompt: str,
        history: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str: ...

@dataclass
class OllamaBackend:
    """HTTP client for a local Ollama server."""
    model: str
    base_url: str = "http://localhost:11434"
    timeout: int = 120

    def _chat(self, messages: List[Dict[str, Any]], model: Optional[str] = None) -> Dict[str, Any]:
        payload = {"model": model or self.model, "messages": messages, "stream": False}
        logger.debug("POST %s/api/chat payload=%s", self.base_url, payload)
        resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def generate(
        self,
        prompt: str,
        history: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        messages.append({"role": "user", "content": prompt})
        result = self._chat(messages, model=model)
        content = result.get("message", {}).get("content")
        if content is None:
            raise ValueError(f"No content in Ollama response: {result}")
        return content
