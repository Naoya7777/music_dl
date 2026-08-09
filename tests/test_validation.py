"""Tests for user-controlled input validation."""

from pathlib import Path

import pytest

from src.core.validation import (
    InputValidationError,
    validate_output_directory,
    validate_youtube_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/watch?v=abc123",
        "https://music.youtube.com/watch?v=abc123",
        "https://youtu.be/abc123",
        "https://www.youtube.com/shorts/abc123",
    ],
)
def test_accepts_supported_video_urls(url: str) -> None:
    assert validate_youtube_url(f"  {url}  ") == url


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not-a-url",
        "file:///C:/video.mp4",
        "https://example.com/watch?v=abc123",
        "https://www.youtube.com/",
        "https://www.youtube.com/watch?list=playlist-id&v=abc123",
    ],
)
def test_rejects_unsupported_urls(url: str) -> None:
    with pytest.raises(InputValidationError):
        validate_youtube_url(url)


def test_accepts_existing_output_directory(tmp_path: Path) -> None:
    assert validate_output_directory(str(tmp_path)) == tmp_path.resolve()


def test_rejects_missing_output_directory(tmp_path: Path) -> None:
    with pytest.raises(InputValidationError, match="存在しません"):
        validate_output_directory(str(tmp_path / "missing"))
