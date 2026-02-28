from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.config.bootstrap import init_service_runtime
from packages.config.logging_setup import get_logger
from packages.config.memory_guard import MemoryGuard


def main() -> None:
    state = init_service_runtime("worker")
    logger = get_logger("services.worker.main")
    memory_guard = MemoryGuard(limit_gb=state.profile.ram_limit_gb)
    memory_guard.check("worker-startup")
    logger.info("Worker bootstrap complete. Profile: %s", state.profile.name)


if __name__ == "__main__":
    main()
