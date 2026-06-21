"""
agents/base_agent.py — Abstract base class for all DailyBrief agents.

Each agent follows the same two-step contract:
  1. fetch()   — retrieve raw data from an external source (MCP client)
  2. analyze() — transform raw data into typed schema objects

Subclasses may use the _llm_classify() helper to delegate classification
work to the Gemini LLM.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from services.gemini_service import GeminiService


class BaseAgent(ABC):
    """Abstract base for all DailyBrief data agents.

    Args:
        gemini_service: A configured GeminiService instance. Some agents
                        don't use the LLM (e.g. CalendarAgent), but it is
                        available on all agents for consistency.
    """

    def __init__(self, gemini_service: GeminiService) -> None:
        self.gemini_service = gemini_service

    @abstractmethod
    async def fetch(self, *args: Any, **kwargs: Any) -> list[dict]:
        """Retrieve raw data from an external source.

        Concrete agents define their own specific signature via the
        *args/**kwargs pattern. This method should call an MCP client
        and return the raw list of dicts.

        Returns:
            A list of raw data dicts (untyped, as returned by the MCP server).
        """
        ...

    @abstractmethod
    async def analyze(self, *args: Any, **kwargs: Any) -> Any:
        """Transform raw data into typed schema objects.

        Concrete agents define their own specific signature. This method
        is responsible for classification, validation, and enrichment.

        Returns:
            Agent-specific typed output (e.g. list[ClassifiedEmail]).
        """
        ...

    async def _llm_classify(self, prompt: str, schema: type | None = None) -> str:
        """Helper: send a classification prompt to the Gemini LLM.

        Args:
            prompt: The full prompt string, including any data to classify.
            schema: Optional Pydantic model for JSON-mode responses.

        Returns:
            The LLM's raw text response. Caller is responsible for parsing.
        """
        # TODO: add retry / error handling for malformed LLM responses
        return await self.gemini_service.generate(prompt, response_schema=schema)
