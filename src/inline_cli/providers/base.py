"""Base provider interface for AI backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class Message:
    """A single chat message."""

    role: str  # "user", "assistant", or "system"
    content: str


@dataclass
class ProviderInfo:
    """Metadata about a provider."""

    name: str
    display_name: str
    requires_api_key: bool = True
    is_local: bool = False
    available: bool = False
    models: list[str] = field(default_factory=list)


class BaseProvider(ABC):
    """Abstract base for all AI providers."""

    name: str = ""
    display_name: str = ""

    def __init__(self, config: dict) -> None:
        self.config = config

    @abstractmethod
    async def check_available(self) -> bool:
        """Return True if this provider is reachable / configured."""
        ...

    @abstractmethod
    async def list_models(self) -> list[str]:
        """Return available model IDs."""
        ...

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Yield text chunks for a streaming chat completion."""
        ...
        yield ""  # make type-checker see this as an async generator

    async def get_info(self) -> ProviderInfo:
        available = await self.check_available()
        models: list[str] = []
        if available:
            try:
                models = await self.list_models()
            except Exception:
                pass
        return ProviderInfo(
            name=self.name,
            display_name=self.display_name,
            requires_api_key=not getattr(self, "is_local", False),
            is_local=getattr(self, "is_local", False),
            available=available,
            models=models,
        )
