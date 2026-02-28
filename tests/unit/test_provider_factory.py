from __future__ import annotations

import pytest

from packages.shared.schemas import AppConfig
from services.ai_engine.providers.factory import build_llm_provider
from services.ai_engine.providers.ollama_provider import OllamaProvider
from services.ai_engine.providers.openrouter_provider import OpenRouterProvider


def test_build_provider_defaults_to_ollama(monkeypatch) -> None:
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    cfg = AppConfig()
    provider = build_llm_provider(cfg)
    assert isinstance(provider, OllamaProvider)


def test_build_provider_openrouter_uses_resolver() -> None:
    cfg = AppConfig(LLM_PROVIDER="openrouter")
    provider = build_llm_provider(cfg, api_key_resolver=lambda _name: "key-123")
    assert isinstance(provider, OpenRouterProvider)


def test_build_provider_openrouter_without_key_raises(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    cfg = AppConfig(LLM_PROVIDER="openrouter")
    with pytest.raises(RuntimeError):
        build_llm_provider(cfg, api_key_resolver=lambda _name: "")


def test_build_provider_openrouter_falls_back_to_env_when_resolver_fails(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    cfg = AppConfig(LLM_PROVIDER="openrouter")

    def _resolver(_name: str) -> str:
        raise ValueError("missing encrypted key")

    provider = build_llm_provider(cfg, api_key_resolver=_resolver)
    assert isinstance(provider, OpenRouterProvider)
    assert provider.api_key == "env-key"


def test_build_provider_uses_env_provider_override(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    cfg = AppConfig(LLM_PROVIDER="ollama", OLLAMA_MODEL="llama3.2:3b")
    provider = build_llm_provider(cfg)
    assert isinstance(provider, OpenRouterProvider)
    assert provider.model == "openai/gpt-4o-mini"


def test_build_provider_openrouter_uses_config_model_fallback(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
    cfg = AppConfig(LLM_PROVIDER="openrouter", OPENROUTER_MODEL="anthropic/claude-3.5-sonnet")
    provider = build_llm_provider(cfg, api_key_resolver=lambda _name: "key-123")
    assert isinstance(provider, OpenRouterProvider)
    assert provider.model == "anthropic/claude-3.5-sonnet"
