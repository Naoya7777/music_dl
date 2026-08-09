"""Threaded audio download service backed by yt-dlp."""

from __future__ import annotations

import re
import shutil
import threading
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Final

import yt_dlp

from .config import AppConfig
from .validation import validate_output_directory, validate_youtube_url

ProgressCallback = Callable[[float, str], None]
LogCallback = Callable[[str, str], None]
FinishCallback = Callable[[bool, str], None]

_URL_PATTERN: Final[re.Pattern[str]] = re.compile(r"https?://\S+", re.IGNORECASE)


def _create_downloader(options: Any) -> Any:
    """Create the external downloader behind a testable, typed boundary."""

    return yt_dlp.YoutubeDL(options)


class DownloadService:
    """Run one audio download at a time without blocking the caller."""

    def __init__(
        self,
        *,
        ydl_factory: Callable[[dict[str, Any]], Any] = _create_downloader,
        executable_finder: Callable[[str], str | None] = shutil.which,
    ) -> None:
        self._ydl_factory = ydl_factory
        self._executable_finder = executable_finder
        self._state_lock = threading.Lock()
        self._is_running = False
        self._worker_thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        """Return whether a download owns the service execution slot."""

        with self._state_lock:
            return self._is_running

    def validate_environment(self) -> bool:
        """Return whether FFmpeg is available on PATH."""

        return self._executable_finder("ffmpeg") is not None

    def run_download(
        self,
        url: str,
        config: AppConfig,
        progress_callback: ProgressCallback,
        log_callback: LogCallback,
        finish_callback: FinishCallback,
    ) -> bool:
        """Validate and start a background audio download.

        Returns:
            ``True`` when a worker was started, or ``False`` if another worker is active.

        Raises:
            InputValidationError: If the URL or output directory is invalid.
            RuntimeError: If FFmpeg is unavailable.
        """

        normalized_url = validate_youtube_url(url)
        output_directory = validate_output_directory(config.save_dir)
        if not self.validate_environment():
            raise RuntimeError("FFmpeg が見つかりません。PATH の設定を確認してください。")

        with self._state_lock:
            if self._is_running:
                return False
            self._is_running = True

        worker = threading.Thread(
            target=self._download_worker,
            args=(
                normalized_url,
                output_directory,
                config,
                progress_callback,
                log_callback,
                finish_callback,
            ),
            name="music-dl-worker",
            daemon=True,
        )
        self._worker_thread = worker
        try:
            worker.start()
        except RuntimeError:
            with self._state_lock:
                self._is_running = False
            self._worker_thread = None
            raise
        return True

    def wait(self, timeout: float | None = None) -> bool:
        """Wait for the active worker; intended for shutdown checks and tests."""

        worker = self._worker_thread
        if worker is None:
            return True
        worker.join(timeout)
        return not worker.is_alive()

    def _download_worker(
        self,
        url: str,
        output_directory: Path,
        config: AppConfig,
        progress_callback: ProgressCallback,
        log_callback: LogCallback,
        finish_callback: FinishCallback,
    ) -> None:
        success = False
        finish_message = "ダウンロードに失敗しました。詳細ログを確認してください。"
        try:
            log_callback(f"処理を開始しました ({config.bitrate} kbps)。", "info")
            options = self._build_options(output_directory, config, progress_callback)
            with self._ydl_factory(options) as downloader:
                info = downloader.extract_info(url, download=True)
            title = self._safe_title(info)
            log_callback(f"保存が完了しました: {title}", "success")
            success = True
            finish_message = "MP3 の保存が完了しました。"
        except Exception as error:
            safe_error = self._safe_error_message(error)
            log_callback(f"処理に失敗しました: {safe_error}", "error")
        finally:
            with self._state_lock:
                self._is_running = False
            finish_callback(success, finish_message)

    @staticmethod
    def _build_options(
        output_directory: Path,
        config: AppConfig,
        progress_callback: ProgressCallback,
    ) -> dict[str, Any]:
        def progress_hook(data: Mapping[str, Any]) -> None:
            status = data.get("status")
            if status == "downloading":
                progress = DownloadService._calculate_progress(data)
                eta = str(data.get("_eta_str") or "計算中").strip()
                progress_callback(progress, f"ダウンロード中 · 残り {eta}")
            elif status == "finished":
                progress_callback(0.95, "MP3 に変換しています")

        return {
            "format": "bestaudio/best",
            "outtmpl": str(output_directory / "%(title)s.%(ext)s"),
            "noplaylist": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": config.bitrate,
                }
            ],
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30,
            "retries": 3,
            "fragment_retries": 3,
        }

    @staticmethod
    def _calculate_progress(data: Mapping[str, Any]) -> float:
        downloaded = data.get("downloaded_bytes")
        total = data.get("total_bytes") or data.get("total_bytes_estimate")
        if isinstance(downloaded, (int, float)) and isinstance(total, (int, float)) and total > 0:
            return max(0.0, min(float(downloaded) / float(total), 0.94))

        percent_text = str(data.get("_percent_str") or "0")
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)", percent_text)
        if match:
            return max(0.0, min(float(match.group(1)) / 100.0, 0.94))
        return 0.0

    @staticmethod
    def _safe_title(info: Any) -> str:
        if not isinstance(info, Mapping):
            return "タイトル不明"
        title = str(info.get("title") or "タイトル不明")
        sanitized = "".join(character for character in title if character.isprintable())
        return sanitized[:100]

    @staticmethod
    def _safe_error_message(error: Exception) -> str:
        message = _URL_PATTERN.sub("[URL]", str(error))
        message = " ".join(message.split())
        return message[:300] or error.__class__.__name__
