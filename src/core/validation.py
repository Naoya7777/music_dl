"""Validation helpers for untrusted user input."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class InputValidationError(ValueError):
    """Raised when user input cannot be accepted safely."""


def validate_youtube_url(value: str) -> str:
    """Validate and normalize a single-video YouTube URL.

    Args:
        value: User-provided URL.

    Returns:
        The stripped URL.

    Raises:
        InputValidationError: If the URL is unsupported or references a playlist.
    """

    url = value.strip()
    if not url:
        raise InputValidationError("YouTube の URL を入力してください。")

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    is_youtube_host = host == "youtube.com" or host.endswith(".youtube.com")
    is_short_host = host == "youtu.be" or host.endswith(".youtu.be")
    if parsed.scheme not in {"http", "https"} or not (is_youtube_host or is_short_host):
        raise InputValidationError("対応している YouTube の URL を入力してください。")

    query = parse_qs(parsed.query)
    if "list" in query:
        raise InputValidationError("プレイリストではなく単一動画の URL を入力してください。")

    has_video_target = bool(parsed.path.strip("/"))
    if host.endswith("youtube.com") and parsed.path.rstrip("/") == "/watch":
        has_video_target = bool(query.get("v", [""])[0])
    if not has_video_target:
        raise InputValidationError("動画を特定できる YouTube の URL を入力してください。")
    return url


def validate_output_directory(value: str) -> Path:
    """Validate that an output directory exists and is writable."""

    directory = Path(value).expanduser()
    if not directory.exists():
        raise InputValidationError("保存先フォルダが存在しません。")
    if not directory.is_dir():
        raise InputValidationError("保存先にはフォルダを指定してください。")
    if not os.access(directory, os.W_OK):
        raise InputValidationError("保存先フォルダへの書き込み権限がありません。")
    return directory.resolve()
