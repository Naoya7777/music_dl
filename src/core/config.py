"""Application configuration and persistence."""

from __future__ import annotations

import json
import os
from contextlib import suppress
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Final

SUPPORTED_BITRATES: Final[tuple[str, ...]] = ("128", "192", "320")


class ConfigurationError(RuntimeError):
    """Raised when application settings cannot be saved."""


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Validated user settings.

    Args:
        save_dir: Directory where converted audio is stored.
        bitrate: MP3 bitrate in kbps.
    """

    save_dir: str
    bitrate: str = "192"

    def __post_init__(self) -> None:
        if not self.save_dir.strip():
            raise ValueError("保存先を指定してください。")
        normalized_dir = str(Path(self.save_dir).expanduser())
        if self.bitrate not in SUPPORTED_BITRATES:
            supported = ", ".join(SUPPORTED_BITRATES)
            raise ValueError(f"音質は {supported} kbps から選択してください。")
        object.__setattr__(self, "save_dir", normalized_dir)

    @staticmethod
    def get_default_dir() -> str:
        """Return the default downloads directory for the current user."""

        return str(Path.home() / "Downloads")

    @classmethod
    def default(cls) -> AppConfig:
        """Build the default configuration."""

        return cls(save_dir=cls.get_default_dir())

    def with_save_dir(self, save_dir: str) -> AppConfig:
        """Return a copy with a different output directory."""

        return replace(self, save_dir=save_dir)

    def with_bitrate(self, bitrate: str) -> AppConfig:
        """Return a copy with a different bitrate."""

        return replace(self, bitrate=bitrate)


class ConfigManager:
    """Load and atomically save application settings."""

    FILE_PATH: Final[Path] = Path("settings.json")

    def __init__(self, file_path: str | Path | None = None) -> None:
        self.file_path = Path(file_path) if file_path is not None else self.FILE_PATH
        self.last_warning: str | None = None

    def load(self) -> AppConfig:
        """Load settings, falling back to defaults when input is invalid."""

        self.last_warning = None
        if not self.file_path.exists():
            return AppConfig.default()

        try:
            with self.file_path.open("r", encoding="utf-8") as settings_file:
                data: Any = json.load(settings_file)
            if not isinstance(data, dict):
                raise ValueError("設定のルートはオブジェクトである必要があります。")
            save_dir = data.get("save_dir", AppConfig.get_default_dir())
            bitrate = data.get("bitrate", "192")
            if not isinstance(save_dir, str) or not isinstance(bitrate, str):
                raise ValueError("設定値の形式が正しくありません。")
            return AppConfig(save_dir=save_dir, bitrate=bitrate)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            self.last_warning = f"設定を読み込めないため既定値を使用します: {error}"
            return AppConfig.default()

    def save(self, config: AppConfig) -> None:
        """Persist settings with an atomic replacement.

        Args:
            config: Validated settings to persist.

        Raises:
            ConfigurationError: If settings cannot be written.
        """

        parent = self.file_path.parent
        temporary_path = self.file_path.with_suffix(f"{self.file_path.suffix}.tmp")
        try:
            parent.mkdir(parents=True, exist_ok=True)
            with temporary_path.open("w", encoding="utf-8", newline="\n") as settings_file:
                json.dump(asdict(config), settings_file, ensure_ascii=False, indent=2)
                settings_file.write("\n")
                settings_file.flush()
                os.fsync(settings_file.fileno())
            temporary_path.replace(self.file_path)
        except OSError as error:
            with suppress(OSError):
                temporary_path.unlink(missing_ok=True)
            raise ConfigurationError(f"設定を保存できませんでした: {error}") from error
