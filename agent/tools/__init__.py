"""
Tools for the agent.

Each tool is implemented as a class with a ``run`` method. Tools must expose
the following attributes:

* ``name``: unique identifier of the tool.
* ``description``: short description of what the tool does.
* ``input_schema``: a dictionary describing required and optional input
  parameters. This schema is intended for display to the language model so it
  knows how to call the tool correctly.

Tools are registered via the YAML file ``agent/config/tools.yaml``. The agent
reads this configuration at startup and dynamically imports the tool classes
listed there.
"""

from __future__ import annotations

from typing import Any, Dict, Protocol


class Tool(Protocol):
    """Protocol that all tools must implement."""

    name: str
    description: str
    input_schema: Dict[str, Any]

    def run(self, **kwargs: Any) -> Any:
        """
        Execute the tool with the given keyword arguments.

        :param kwargs: Arguments to the tool. They must conform to the
            ``input_schema`` definition.
        :returns: The result of the tool execution, which should be serialisable
            (e.g. dict or string) so that it can be fed back into the model.
        """
        ...  # pragma: no cover


__all__ = ["Tool"]