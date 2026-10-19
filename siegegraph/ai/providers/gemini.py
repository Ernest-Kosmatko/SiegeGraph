"""Google Gemini backend - requires GEMINI_API_KEY, opt-in per engagement."""
from __future__ import annotations

import os

import httpx

from siegegraph.ai.base import AdviceResult, AdvisorProvider


class GeminiProvider(AdvisorProvider):
    name = "gemini"

    def __init__(self, model: str = "gemini-2.5-pro", api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

    def advise(self, prompt: str) -> AdviceResult:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        resp = httpx.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return AdviceResult(provider=self.name, text=text)
