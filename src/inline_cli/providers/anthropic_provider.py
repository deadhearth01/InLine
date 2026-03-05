"""Anthropic / Claude provider."""

from __future__ import annotations

from typing import AsyncIterator

from anthropic import AsyncAnthropic

from .base import BaseProvider, Message


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    display_name = "Claude (Anthropic)"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        section = config.get("anthropic", {})
        api_key = section.get("api_key", "")
        self.default_model = section.get("model", "claude-sonnet-4-20250514")
        self.client = AsyncAnthropic(api_key=api_key or "sk-placeholder")

    async def check_available(self) -> bool:
        if not self.client.api_key or self.client.api_key == "sk-placeholder":
            return False
        try:
            async with self.client.messages.stream(
                model=self.default_model,
                max_tokens=1,
                messages=[{"role": "user", "content": "hi"}],
            ) as stream:
                async for _ in stream.text_stream:
                    break
            return True
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        return [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-3-5-haiku-20241022",
        ]

    async def stream_chat(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        model = model or self.default_model
        system_prompt = ""
        api_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt = m.content
            else:
                api_messages.append({"role": m.role, "content": m.content})

        kwargs: dict = {
            "model": model,
            "max_tokens": 8192,
            "messages": api_messages,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text
