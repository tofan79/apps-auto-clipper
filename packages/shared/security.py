from __future__ import annotations

import re
from pathlib import Path


_SAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]+")
_MULTI_UNDERSCORE = re.compile(r"_+")


def sanitize_filename(name: str, *, default: str = "file") -> str:
    """
    Return a filesystem-safe filename fragment.
    """
    cleaned = _SAFE_FILENAME_CHARS.sub("_", name.strip())
    cleaned = _MULTI_UNDERSCORE.sub("_", cleaned)
    cleaned = cleaned.strip("._- ")
    if not cleaned:
        cleaned = default
    return cleaned[:255]


def sanitize_file_path(raw_path: str | Path, *, base_dir: Path) -> Path:
    """
    Resolve `raw_path` and ensure it remains inside `base_dir`.
    """
    base = base_dir.resolve()
    candidate = Path(raw_path).expanduser().resolve()
    try:
        candidate.relative_to(base)
    except ValueError as exc:
        raise ValueError("Path traversal detected; path must stay inside base_dir") from exc
    return candidate
