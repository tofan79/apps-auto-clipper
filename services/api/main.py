from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.config.bootstrap import init_service_runtime
from packages.config.logging_setup import get_logger


def main() -> None:
    state = init_service_runtime("api")
    logger = get_logger("services.api.main")
    logger.info("API bootstrap complete. Config path: %s", state.paths.config_path)


if __name__ == "__main__":
    main()
