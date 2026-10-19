"""Local Ollama backend - default, no API key, no data leaves the machine."""
from __future__ import annotations

import httpx

from siegegraph.ai.base import AdviceResult, AdvisorProvider


class OllamaProvider(AdvisorProvider):
    name = "ollama"

    def __init__(self, model: str = "llama3.1", host: str = "http://localhost:11434") -> None:
        self.model = model
        self.host = host.rstrip("/")

    def advise(self, prompt: str) -> AdviceResult:
        resp = httpx.post(
            f"{self.host}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return AdviceResult(provider=self.name, text=resp.json().get("response", ""))
