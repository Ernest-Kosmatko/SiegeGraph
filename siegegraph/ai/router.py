"""Resolves a provider name to an implementation and runs the advisor call,
logging every request/response pair into the engagement database so the
client can audit exactly what left the machine and what came back."""
from __future__ import annotations

from siegegraph.ai.base import AdviceResult
from siegegraph.core.graph import Project

_REGISTRY = {
    "ollama": ("siegegraph.ai.providers.ollama", "OllamaProvider"),
    "anthropic": ("siegegraph.ai.providers.anthropic", "AnthropicProvider"),
    "openai": ("siegegraph.ai.providers.openai", "OpenAIProvider"),
    "gemini": ("siegegraph.ai.providers.gemini", "GeminiProvider"),
}


def get_provider(name: str, **kwargs):
    if name not in _REGISTRY:
        raise ValueError(f"Unknown AI provider '{name}'. Available: {', '.join(_REGISTRY)}")
    module_path, class_name = _REGISTRY[name]
    import importlib

    module = importlib.import_module(module_path)
    return getattr(module, class_name)(**kwargs)


def advise(project: Project, provider_name: str, prompt: str, node_id: str | None = None) -> AdviceResult:
    provider = get_provider(provider_name)
    result = provider.advise(prompt)
    project.log_ai_call(provider=provider_name, node_id=node_id, prompt=prompt, response=result.text)
    return result
