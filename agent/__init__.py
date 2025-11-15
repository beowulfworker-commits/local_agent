"""
Agent package initialization.

This package contains the core logic for the local AI agent and a collection of
tools that can be used by the agent. See docs/LOCAL_AGENT.md for details.
"""

from .core import Agent
from .llm_backend import LLMBackend, OllamaBackend

__all__ = ["Agent", "LLMBackend", "OllamaBackend"]