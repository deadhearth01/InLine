"""Provider registry — instantiates and manages all AI backends."""

from __future__ import annotations

from typing import Any

from .base import BaseProvider, ProviderInfo
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from .ollama_provider import OllamaProvider

PROVIDER_CLASSES: list[type[BaseProvider]] = [
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
    GroqProvider,
]


class ProviderRegistry:
    """Manages all provider instances."""

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.providers: dict[str, BaseProvider] = {}
        for cls in PROVIDER_CLASSES:
            provider = cls(config)
            self.providers[provider.name] = provider

    def get(self, name: str) -> BaseProvider | None:
        return self.providers.get(name)

    def names(self) -> list[str]:
        return list(self.providers.keys())

    async def scan_availability(self) -> list[ProviderInfo]:
        """Check all providers and return their info."""
        results: list[ProviderInfo] = []
        for provider in self.providers.values():
            info = await provider.get_info()
            results.append(info)
        return results

    async def detect_default(self) -> str:
        """Pick the best available provider (prefer local first)."""
        # Prefer Ollama if running
        ollama = self.providers.get("ollama")
        if ollama and await ollama.check_available():
            return "ollama"
        # Then try cloud providers in order of preference
        for name in ("anthropic", "openai", "gemini", "groq"):
            prov = self.providers.get(name)
            if prov and await prov.check_available():
                return name
        return "ollama"
