from __future__ import annotations

from dataclasses import dataclass

from packages.config.app_paths import RuntimePaths, ensure_runtime_paths
from packages.config.config_manager import ConfigManager
from packages.config.env import load_env
from packages.config.gpu_detector import GPUInfo, detect_gpu
from packages.config.logging_setup import get_logger, setup_logging
from packages.config.spec_detector import SystemProfile, detect_profile


@dataclass(slots=True)
class BootstrapState:
    paths: RuntimePaths
    config: ConfigManager
    gpu: GPUInfo
    profile: SystemProfile


def init_service_runtime(service_name: str) -> BootstrapState:
    paths = ensure_runtime_paths()
    load_env()

    config = ConfigManager(paths.config_path)
    cfg = config.get()
    setup_logging(paths.logs_dir, level=cfg.LOG_LEVEL)
    logger = get_logger(service_name)

    gpu = detect_gpu()
    profile = detect_profile()

    # Persist selected profile defaults for downstream services.
    config.set_many(
        {
            "APP_DATA_PATH": str(paths.root),
            "WHISPER_MODEL": profile.whisper_model,
            "MAX_CONCURRENT_JOBS": profile.max_concurrent_jobs,
            "FFMPEG_PRESET": profile.ffmpeg_preset,
            "WHISPER_DEVICE": gpu.device if cfg.WHISPER_DEVICE == "auto" else cfg.WHISPER_DEVICE,
        }
    )

    logger.info(
        "Runtime initialized | service=%s | app_data=%s | gpu=%s | profile=%s",
        service_name,
        paths.root,
        gpu.name if gpu.available else "cpu",
        profile.name,
    )
    return BootstrapState(paths=paths, config=config, gpu=gpu, profile=profile)
