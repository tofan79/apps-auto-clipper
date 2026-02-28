from __future__ import annotations

import gc
import logging
import os
import time

logger = logging.getLogger(__name__)


class MemoryGuard:
    """
    Runtime RAM guard for worker safety.
    """

    def __init__(self, limit_gb: float = 5.0, warning_threshold: float = 0.85) -> None:
        self.limit_bytes = int(limit_gb * 1024**3)
        self.warning_threshold = warning_threshold

    def check(self, context: str = "") -> bool:
        used_bytes = _process_rss_bytes()
        ratio = used_bytes / self.limit_bytes if self.limit_bytes > 0 else 0.0

        if ratio > self.warning_threshold:
            logger.warning(
                "[MemGuard] High memory usage %s during %s (used=%dMB limit=%dMB)",
                f"{ratio:.0%}",
                context or "runtime",
                int(used_bytes / 1024**2),
                int(self.limit_bytes / 1024**2),
            )
            gc.collect()
            time.sleep(2)

        if ratio > 0.95:
            logger.error("[MemGuard] Critical memory usage %s; pausing job", f"{ratio:.0%}")
            return False
        return True

    def wait_until_safe(self, timeout: int = 60) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            if self.check():
                return True
            time.sleep(5)
        raise MemoryError("RAM usage remained above threshold until timeout")


def _process_rss_bytes() -> int:
    try:
        import psutil  # type: ignore

        return int(psutil.Process().memory_info().rss)
    except Exception:
        # Fallback when psutil is unavailable.
        return int(getattr(os, "getpid", lambda: 0)() * 0)
