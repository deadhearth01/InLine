"""OpenAI / ChatGPT provider."""

from __future__ import annotations

from typing import AsyncIterator

from openai import AsyncOpenAI

from .base import BaseProvider, Message


class OpenAIProvider(BaseProvider):
    name = "openai"
    display_name = "ChatGPT (OpenAI)"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        section = config.get("openai", {})
        api_key = section.get("api_key", "")
        base_url = section.get("base_url", "https://api.openai.com/v1")
        self.default_model = section.get("model", "gpt-4o")
        self.client = AsyncOpenAI(api_key=api_key or "sk-placeholder", base_url=base_url)

    async def check_available(self) -> bool:
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        resp = await self.client.models.list()
        return sorted([m.id for m in resp.data if "gpt" in m.id or "o1" in m.id or "o3" in m.id])

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
