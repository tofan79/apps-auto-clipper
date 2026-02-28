from __future__ import annotations

import pytest

from packages.shared.schemas import AppConfig
from services.ai_engine.providers.factory import build_llm_provider
from services.ai_engine.providers.ollama_provider import OllamaProvider
from services.ai_engine.providers.openrouter_provider import OpenRouterProvider


def test_build_provider_defaults_to_ollama() -> None:
    cfg = AppConfig()
    provider = build_llm_provider(cfg)
    assert isinstance(provider, OllamaProvider)


def test_build_provider_openrouter_uses_resolver() -> None:
    cfg = AppConfig(LLM_PROVIDER="openrouter")
    provider = build_llm_provider(cfg, api_key_resolver=lambda _name: "key-123")
    assert isinstance(provider, OpenRouterProvider)


def test_build_provider_openrouter_without_key_raises() -> None:
    cfg = AppConfig(LLM_PROVIDER="openrouter")
    with pytest.raises(RuntimeError):
        build_llm_provider(cfg, api_key_resolver=lambda _name: "")
