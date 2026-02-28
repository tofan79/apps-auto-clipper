from __future__ import annotations

import os
from typing import Callable

from packages.shared.schemas import AppConfig
from services.ai_engine.providers.base import BaseLLMProvider
from services.ai_engine.providers.ollama_provider import OllamaProvider
from services.ai_engine.providers.openrouter_provider import OpenRouterProvider


ApiKeyResolver = Callable[[str], str]


def build_llm_provider(config: AppConfig, api_key_resolver: ApiKeyResolver | None = None) -> BaseLLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", config.LLM_PROVIDER).strip().lower()
    if provider_name in {"", "ollama"}:
        model_name = os.getenv("OLLAMA_MODEL", config.OLLAMA_MODEL).strip() or config.OLLAMA_MODEL
        return OllamaProvider(model=model_name)

    if provider_name == "openrouter":
        key = ""
        if api_key_resolver is not None:
            try:
                key = api_key_resolver("openrouter")
            except Exception:
                key = ""
        if not key:
            key = os.getenv("OPENROUTER_API_KEY", "")
        if not key:
            raise RuntimeError("OpenRouter provider selected but API key is missing")
        model_name = os.getenv("OPENROUTER_MODEL", config.OPENROUTER_MODEL).strip() or config.OPENROUTER_MODEL
        return OpenRouterProvider(model=model_name, api_key=key)

    raise ValueError(f"Unsupported LLM provider: {provider_name}")
