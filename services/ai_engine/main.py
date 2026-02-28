from __future__ import annotations
# pylint: disable=wrong-import-position
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.config.bootstrap import init_service_runtime
from packages.config.gpu_detector import get_whisper_device
from packages.config.logging_setup import get_logger


def main() -> None:
    state = init_service_runtime("ai_engine")
    logger = get_logger("services.ai_engine.main")
    logger.info(
        "AI Engine bootstrap complete. Device=%s, model=%s",
        get_whisper_device(),
        state.profile.whisper_model,
    )


if __name__ == "__main__":
    main()
