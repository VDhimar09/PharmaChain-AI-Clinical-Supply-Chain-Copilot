"""LLM provider abstraction.

The rest of the RAG generation pipeline (context assembly -> prompting ->
citation resolution) depends only on this interface, never on a concrete
LLM vendor. Swapping providers (OpenAI, Azure OpenAI, ...) means adding
another implementation here.
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod


class LLMError(Exception):
    """Raised when LLM completion generation fails."""


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        """Generate a completion for the given system/user prompts.

        Implementations must raise `LLMError` (not a provider-specific
        exception) on failure - including timeouts - and must never
        include credentials or full prompt content in any raised message
        or log line.
        """
