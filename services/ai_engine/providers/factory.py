from __future__ import annotations

import os
from typing import Callable

from packages.shared.schemas import AppConfig
from services.ai_engine.providers.base import BaseLLMProvider
from services.ai_engine.providers.ollama_provider import OllamaProvider
from services.ai_engine.providers.openrouter_provider import OpenRouterProvider


ApiKeyResolver = Callable[[str], str]


def build_llm_provider(config: AppConfig, api_key_resolver: ApiKeyResolver | None = None) -> BaseLLMProvider:
    provider_name = config.LLM_PROVIDER.strip().lower()
    if provider_name in {"", "ollama"}:
        return OllamaProvider(model=config.OLLAMA_MODEL)

    if provider_name == "openrouter":
        key = ""
        if api_key_resolver is not None:
            key = api_key_resolver("openrouter")
        if not key:
            key = os.getenv("OPENROUTER_API_KEY", "")
        if not key:
            raise RuntimeError("OpenRouter provider selected but API key is missing")
        return OpenRouterProvider(model="openrouter/auto", api_key=key)

    raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}")
