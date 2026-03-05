"""Ollama provider — local models, no API key needed."""

from __future__ import annotations

from typing import AsyncIterator

import httpx

from .base import BaseProvider, Message


class OllamaProvider(BaseProvider):
    name = "ollama"
    display_name = "Ollama (Local)"
    is_local = True

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        section = config.get("ollama", {})
        self.base_url = section.get("base_url", "http://localhost:11434").rstrip("/")
        self.default_model = section.get("model", "llama3.2")

    async def check_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            return sorted([m["name"] for m in data.get("models", [])])

    async def stream_chat(
        self,
        messages: list[Message],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        model = model or self.default_model
        api_messages = [{"role": m.role, "content": m.content} for m in messages]
        payload = {
            "model": model,
            "messages": api_messages,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload,
            ) as resp:
                resp.raise_for_status()
                import json

                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    content = chunk.get("message", {}).get("content", "")
                    if content:
                        yield content
