from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    @abstractmethod
    def health_check(self) -> bool:
        """Return True if provider endpoint is reachable."""

    @abstractmethod
    def generate_hooks(self, transcript_text: str, *, max_candidates: int = 15) -> list[dict[str, Any]]:
        """Generate viral hook candidates as JSON-like dicts."""

    @abstractmethod
    def generate_metadata(self, transcript_text: str, *, platform: str) -> dict[str, Any]:
        """Generate platform metadata such as title/caption/hashtags."""
