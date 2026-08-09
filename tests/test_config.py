"""Tests for validated and persistent application configuration."""

import json
from pathlib import Path

import pytest

from src.core.config import AppConfig, ConfigManager, ConfigurationError


def test_default_values() -> None:
    config = AppConfig(save_dir="downloads")

    assert config.bitrate == "192"
    assert config.save_dir == "downloads"


def test_rejects_unsupported_bitrate() -> None:
    with pytest.raises(ValueError, match="音質"):
        AppConfig(save_dir="downloads", bitrate="999")


def test_rejects_empty_output_directory() -> None:
    with pytest.raises(ValueError, match="保存先"):
        AppConfig(save_dir="   ")


def test_round_trip_settings(tmp_path: Path) -> None:
    manager = ConfigManager(tmp_path / "settings.json")
    expected = AppConfig(save_dir=str(tmp_path), bitrate="320")

    manager.save(expected)

    assert manager.load() == expected
    assert manager.last_warning is None


def test_load_invalid_json_uses_defaults(tmp_path: Path) -> None:
    settings = tmp_path / "settings.json"
    settings.write_text("not-json", encoding="utf-8")
    manager = ConfigManager(settings)

    config = manager.load()

    assert config == AppConfig.default()
    assert manager.last_warning is not None


def test_load_invalid_values_uses_defaults(tmp_path: Path) -> None:
    settings = tmp_path / "settings.json"
    settings.write_text(
        json.dumps({"save_dir": str(tmp_path), "bitrate": "640"}),
        encoding="utf-8",
    )
    manager = ConfigManager(settings)

    assert manager.load() == AppConfig.default()
    assert manager.last_warning is not None


def test_save_failure_is_reported(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    manager = ConfigManager(tmp_path / "settings.json")

    def fail_replace(_self: Path, _target: Path) -> None:
        raise OSError("disk unavailable")

    monkeypatch.setattr(Path, "replace", fail_replace)

    with pytest.raises(ConfigurationError, match="設定を保存できませんでした"):
        manager.save(AppConfig(save_dir=str(tmp_path)))

    assert not (tmp_path / "settings.json.tmp").exists()
