from __future__ import annotations


def distribute_output_modes(total_clips: int) -> list[str]:
    """
    Returns mode assignments with default portrait:landscape ratio ~= 2:1.
    """
    if total_clips <= 0:
        return []

    modes: list[str] = []
    pattern = ["portrait", "portrait", "landscape"]
    while len(modes) < total_clips:
        modes.extend(pattern)
    return modes[:total_clips]
