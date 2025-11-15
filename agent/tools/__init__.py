from __future__ import annotations

from typing import Any, Dict, Protocol

class Tool(Protocol):
    """Protocol for agent tools."""
    name: str
    description: str
    input_schema: Dict[str, Any]

    def run(self, **kwargs: Any) -> Any:
        """Execute the tool and return a JSON-serialisable result."""
        ...
