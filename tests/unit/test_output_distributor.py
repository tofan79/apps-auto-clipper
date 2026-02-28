from __future__ import annotations

from services.ai_engine.output_distributor import distribute_output_modes


def test_distribute_output_modes_ratio_for_six() -> None:
    modes = distribute_output_modes(6)
    assert modes == ["portrait", "portrait", "landscape", "portrait", "portrait", "landscape"]


def test_distribute_output_modes_ratio_for_ten() -> None:
    modes = distribute_output_modes(10)
    assert modes.count("portrait") == 7
    assert modes.count("landscape") == 3


def test_distribute_output_modes_zero_is_empty() -> None:
    assert distribute_output_modes(0) == []
