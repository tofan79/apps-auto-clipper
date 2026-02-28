from __future__ import annotations
# pylint: disable=wrong-import-position
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.config.bootstrap import init_service_runtime
from packages.config.model_manager import ModelManager
from packages.config.gpu_detector import get_whisper_device
from packages.config.logging_setup import get_logger
from services.ai_engine.input_handler import InputHandler
from services.ai_engine.providers.factory import build_llm_provider
from services.ai_engine.transcriber import Transcriber


def main() -> None:
    state = init_service_runtime("ai_engine")
    logger = get_logger("services.ai_engine.main")
    config = state.config.get()

    input_handler = InputHandler()
    transcriber = Transcriber(
        model_name=config.WHISPER_MODEL,
        device=config.WHISPER_DEVICE,
        chunk_duration_sec=state.profile.chunk_duration,
    )
    model_manager = ModelManager.from_runtime()

    provider_health = "unavailable"
    try:
        provider = build_llm_provider(config, api_key_resolver=state.config.get_encrypted_key)
        provider_health = "ok" if provider.health_check() else "degraded"
    except Exception:
        provider_health = "not-configured"

    logger.info(
        "AI Engine bootstrap complete. Device=%s, model=%s, provider=%s, provider_health=%s",
        get_whisper_device(),
        state.profile.whisper_model,
        config.LLM_PROVIDER,
        provider_health,
    )
    logger.debug(
        "Stage 3 components ready | input_handler=%s transcriber_model=%s model_root=%s",
        input_handler.__class__.__name__,
        transcriber.model_name,
        model_manager.model_root,
    )


if __name__ == "__main__":
    main()
