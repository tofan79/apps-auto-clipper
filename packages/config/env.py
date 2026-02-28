from __future__ import annotations

import os
from pathlib import Path


def load_env(env_path: Path | None = None) -> bool:
    """
    Load environment variables from .env.
    Returns True if file exists and was parsed.
    """
    path = env_path or Path.cwd() / ".env"
    if not path.exists():
        return False

    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(path, override=False)
        return True
    except Exception:
        # Minimal fallback parser when python-dotenv is not installed.
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
        return True
