from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """
    Abstract base class for all AI tools.

    Every tool must provide:
    - A unique name
    - A human-readable description
    - A run() method that returns structured data
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tool identifier."""
        pass

    @property
    def display_name(self) -> str:
        """Human-readable tool name for UI rendering."""
        return f"{self.name.replace('_', ' ').title()} Tool"

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does."""
        pass

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> dict:
        """
        Execute the tool.

        Returns:
            dict: Structured output for downstream reasoning.
        """
        pass
