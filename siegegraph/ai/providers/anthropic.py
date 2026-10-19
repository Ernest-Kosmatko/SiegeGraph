"""Claude backend - requires ANTHROPIC_API_KEY, opt-in per engagement."""
from __future__ import annotations

import os

import httpx

from siegegraph.ai.base import AdviceResult, AdvisorProvider


class AnthropicProvider(AdvisorProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-sonnet-5-5", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")

    def advise(self, prompt: str) -> AdviceResult:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        text = "".join(block.get("text", "") for block in data.get("content", []))
        return AdviceResult(provider=self.name, text=text)
