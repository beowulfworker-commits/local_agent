"""
Abstractions for interacting with large language models (LLMs).

The local agent communicates with a model backend through an interface defined
by :class:`LLMBackend`. The default implementation uses Ollama's HTTP API to
send chat messages to a locally running model. You can implement your own
backend (e.g. vLLM, transformers, llama.cpp) by implementing the same
interface.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import requests

logger = logging.getLogger(__name__)


class LLMBackend(Protocol):
    """Protocol for language model backends.

    Concrete backends should implement a method that accepts a prompt and
    conversation history and returns a string response from the model.
    """

    def generate(
        self,
        prompt: str,
        history: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """Generate a response from the model.

        :param prompt: The user's prompt.
        :param history: A list of past messages in the conversation. Each item
            should be a dict with keys ``role`` ("user" or "assistant") and
            ``content``.
        :param system_prompt: Optional system prompt that will be prepended to
            the message list.
        :param model: Optional model name override.
        :returns: The text response from the model.
        """
        ...  # pragma: no cover


@dataclass
class OllamaBackend:
    """Backend that communicates with a locally running Ollama server.

    This class sends chat requests to the Ollama API at ``base_url``. See
    ``docs/LOCAL_AGENT.md`` for more details on running the server.
    """

    model: str
    base_url: str = "http://localhost:11434"
    timeout: int = 120

    def _chat(self, messages: List[Dict[str, Any]], model: Optional[str] = None) -> Dict[str, Any]:
        """Send a chat request to the Ollama API and return the JSON response."""
        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": False,
        }
        logger.debug("Sending request to Ollama: %s", payload)
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
        """Generate a response using the Ollama chat API.

        The conversation history and optional system prompt are combined with the
        current prompt to form the message list. The latest message is always
        sent as a user message. The model's response text is returned.
        """
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        # append history
        messages.extend(history)
        # current user message
        messages.append({"role": "user", "content": prompt})
        result = self._chat(messages, model=model)
        # result format: {"message": {"role": "assistant", "content": "..."}, ...}
        content = result.get("message", {}).get("content")
        if content is None:
            raise ValueError(f"No content in Ollama response: {result}")
        logger.debug("Received response from Ollama: %s", content)
        return content