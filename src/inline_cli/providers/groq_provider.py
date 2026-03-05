"""Groq provider (fast inference)."""

from __future__ import annotations

from typing import AsyncIterator

from groq import AsyncGroq

from .base import BaseProvider, Message


class GroqProvider(BaseProvider):
    name = "groq"
    display_name = "Groq"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        section = config.get("groq", {})
        api_key = section.get("api_key", "")
        self.default_model = section.get("model", "llama-3.3-70b-versatile")
        self.client = AsyncGroq(api_key=api_key or "placeholder")

    async def check_available(self) -> bool:
        if not self.client.api_key or self.client.api_key == "placeholder":
            return False
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        resp = await self.client.models.list()
        return sorted([m.id for m in resp.data])

    async def stream_chat(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        model = model or self.default_model
        api_messages = [{"role": m.role, "content": m.content} for m in messages]
        stream = await self.client.chat.completions.create(
            model=model,
            messages=api_messages,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                yield delta.content
