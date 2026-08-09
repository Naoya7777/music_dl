"""Tests for the threaded yt-dlp adapter."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from src.core.config import AppConfig
from src.core.download_service import DownloadService


class FakeDownloader:
    """Small context-manager replacement for yt-dlp in unit tests."""

    def __init__(
        self,
        options: dict[str, Any],
        *,
        result: dict[str, Any] | None = None,
        error: Exception | None = None,
        blocker: threading.Event | None = None,
    ) -> None:
        self.options = options
        self.result = result or {"title": "Test Song"}
        self.error = error
        self.blocker = blocker
        self.calls: list[tuple[str, bool]] = []

    def __enter__(self) -> FakeDownloader:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def extract_info(self, url: str, *, download: bool) -> dict[str, Any]:
        self.calls.append((url, download))
        if self.blocker is not None:
            self.blocker.wait(timeout=2)
        if self.error is not None:
            raise self.error
        return self.result


def test_validate_environment() -> None:
    available = DownloadService(executable_finder=lambda _name: "ffmpeg.exe")
    unavailable = DownloadService(executable_finder=lambda _name: None)

    assert available.validate_environment()
    assert not unavailable.validate_environment()


def test_successful_download_builds_expected_options(tmp_path: Path) -> None:
    created: list[FakeDownloader] = []

    def factory(options: dict[str, Any]) -> FakeDownloader:
        downloader = FakeDownloader(options)
        created.append(downloader)
        return downloader

    service = DownloadService(ydl_factory=factory, executable_finder=lambda _name: "ffmpeg.exe")
    progress: list[tuple[float, str]] = []
    logs: list[tuple[str, str]] = []
    finishes: list[tuple[bool, str]] = []

    started = service.run_download(
        "https://www.youtube.com/watch?v=abc123",
        AppConfig(save_dir=str(tmp_path), bitrate="320"),
        lambda value, message: progress.append((value, message)),
        lambda message, level: logs.append((message, level)),
        lambda success, message: finishes.append((success, message)),
    )

    assert started
    assert service.wait(timeout=2)
    assert not service.is_running
    assert finishes == [(True, "MP3 の保存が完了しました。")]
    assert created[0].calls == [("https://www.youtube.com/watch?v=abc123", True)]
    assert created[0].options["noplaylist"] is True
    assert created[0].options["socket_timeout"] == 30
    assert created[0].options["postprocessors"][0]["preferredquality"] == "320"
    assert any(level == "success" for _, level in logs)


def test_progress_hook_uses_byte_counts(tmp_path: Path) -> None:
    options: dict[str, Any] = {}

    def factory(received: dict[str, Any]) -> FakeDownloader:
        options.update(received)
        return FakeDownloader(received)

    progress: list[tuple[float, str]] = []
    service = DownloadService(ydl_factory=factory, executable_finder=lambda _name: "ffmpeg.exe")
    service.run_download(
        "https://youtu.be/abc123",
        AppConfig(save_dir=str(tmp_path)),
        lambda value, message: progress.append((value, message)),
        lambda _message, _level: None,
        lambda _success, _message: None,
    )
    assert service.wait(timeout=2)

    hook = options["progress_hooks"][0]
    hook({"status": "downloading", "downloaded_bytes": 25, "total_bytes": 100, "_eta_str": "3s"})
    hook({"status": "finished"})

    assert progress == [(0.25, "ダウンロード中 · 残り 3s"), (0.95, "MP3 に変換しています")]


def test_failure_masks_url_and_finishes(tmp_path: Path) -> None:
    def factory(options: dict[str, Any]) -> FakeDownloader:
        return FakeDownloader(options, error=RuntimeError("failed at https://secret.example/video"))

    logs: list[tuple[str, str]] = []
    finishes: list[tuple[bool, str]] = []
    service = DownloadService(ydl_factory=factory, executable_finder=lambda _name: "ffmpeg.exe")

    service.run_download(
        "https://youtu.be/abc123",
        AppConfig(save_dir=str(tmp_path)),
        lambda _value, _message: None,
        lambda message, level: logs.append((message, level)),
        lambda success, message: finishes.append((success, message)),
    )

    assert service.wait(timeout=2)
    assert finishes == [(False, "ダウンロードに失敗しました。詳細ログを確認してください。")]
    assert "https://secret.example" not in logs[-1][0]
    assert "[URL]" in logs[-1][0]


def test_rejects_second_download_while_running(tmp_path: Path) -> None:
    release = threading.Event()

    def factory(options: dict[str, Any]) -> FakeDownloader:
        return FakeDownloader(options, blocker=release)

    service = DownloadService(ydl_factory=factory, executable_finder=lambda _name: "ffmpeg.exe")
    callbacks = (lambda *_args: None, lambda *_args: None, lambda *_args: None)

    first = service.run_download(
        "https://youtu.be/first",
        AppConfig(save_dir=str(tmp_path)),
        *callbacks,
    )
    second = service.run_download(
        "https://youtu.be/second",
        AppConfig(save_dir=str(tmp_path)),
        *callbacks,
    )
    release.set()

    assert first
    assert not second
    assert service.wait(timeout=2)
