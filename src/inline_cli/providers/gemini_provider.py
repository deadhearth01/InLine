"""Google Gemini provider."""

from __future__ import annotations

from typing import AsyncIterator

from google import genai

from .base import BaseProvider, Message


class GeminiProvider(BaseProvider):
    name = "gemini"
    display_name = "Gemini (Google)"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        section = config.get("gemini", {})
        api_key = section.get("api_key", "")
        self.default_model = section.get("model", "gemini-2.0-flash")
        self.client = genai.Client(api_key=api_key or "placeholder")
        self._api_key = api_key

    async def check_available(self) -> bool:
        if not self._api_key:
            return False
        try:
            pager = await self.client.aio.models.list()
            async for m in pager:
                return True
            return True
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        models = []
        pager = await self.client.aio.models.list()
        async for m in pager:
            if m.name and "gemini" in m.name.lower():
                # Strip "models/" prefix
                model_id = m.name.replace("models/", "")
                models.append(model_id)
        return sorted(models)

    async def stream_chat(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        model = model or self.default_model

        # Build contents list for Gemini
        contents = []
        for m in messages:
            if m.role == "system":
                # Prepend system as user context
                contents.append({"role": "user", "parts": [{"text": f"[System]: {m.content}"}]})
            elif m.role == "user":
                contents.append({"role": "user", "parts": [{"text": m.content}]})
            elif m.role == "assistant":
                contents.append({"role": "model", "parts": [{"text": m.content}]})

        response = await self.client.aio.models.generate_content_stream(
            model=model,
            contents=contents,
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text
