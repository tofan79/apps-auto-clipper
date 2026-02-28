from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen

from packages.config.app_paths import ensure_runtime_paths


GITHUB_RELEASE_API = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"


@dataclass(slots=True)
class YtDlpUpdater:
    binary_path: Path

    @classmethod
    def from_runtime(cls) -> "YtDlpUpdater":
        runtime = ensure_runtime_paths()
        tools_dir = runtime.storage_dir / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        suffix = ".exe" if platform.system().lower().startswith("win") else ""
        return cls(binary_path=tools_dir / f"yt-dlp{suffix}")

    def installed_version(self) -> str | None:
        if not self.binary_path.exists():
            return None
        try:
            result = subprocess.run(
                [str(self.binary_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.returncode != 0:
                return None
            return result.stdout.strip() or None
        except Exception:
            return None

    def latest_release_tag(self) -> str | None:
        request = Request(
            GITHUB_RELEASE_API,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "autoclipper-ai",
            },
        )
        try:
            with urlopen(request, timeout=8) as response:
                payload = json.loads(response.read().decode("utf-8"))
            tag = str(payload.get("tag_name", "")).strip()
            return tag or None
        except Exception:
            return None

    def needs_update(self) -> bool:
        current = self.installed_version()
        latest = self.latest_release_tag()
        if latest is None:
            return False
        if current is None:
            return True
        return current != latest
