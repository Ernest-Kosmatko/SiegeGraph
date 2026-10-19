"""OpenAI / Codex-family backend - requires OPENAI_API_KEY, opt-in per engagement."""
from __future__ import annotations

import os

import httpx

from siegegraph.ai.base import AdviceResult, AdvisorProvider


class OpenAIProvider(AdvisorProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-5", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")

    def advise(self, prompt: str) -> AdviceResult:
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "messages": [{"role": "user", "content": prompt}]},
            timeout=120,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        return AdviceResult(provider=self.name, text=text)
