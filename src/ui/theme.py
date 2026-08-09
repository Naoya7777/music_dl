"""Visual design tokens for the desktop application."""

from typing import Final


class Theme:
    """Centralized colors, typography, spacing, and component states."""

    WINDOW: Final = "#090D14"
    SURFACE: Final = "#111722"
    SURFACE_RAISED: Final = "#17202D"
    SURFACE_HOVER: Final = "#1D2938"
    BORDER: Final = "#263345"
    BORDER_FOCUS: Final = "#4F7CFF"

    PRIMARY: Final = "#5B7CFA"
    PRIMARY_HOVER: Final = "#6D8BFF"
    PRIMARY_DISABLED: Final = "#33405E"
    ACCENT: Final = "#70E1C8"

    TEXT: Final = "#F4F7FC"
    TEXT_SECONDARY: Final = "#9AA8BA"
    TEXT_MUTED: Final = "#66758A"

    SUCCESS: Final = "#44D7A8"
    SUCCESS_BG: Final = "#12352F"
    WARNING: Final = "#F5C56B"
    WARNING_BG: Final = "#3B2E17"
    ERROR: Final = "#FF7D8A"
    ERROR_BG: Final = "#401E27"
    INFO_BG: Final = "#17264A"

    FONT_HERO: Final = ("Segoe UI Variable Display", 30, "bold")
    FONT_TITLE: Final = ("Segoe UI Variable Display", 18, "bold")
    FONT_BODY: Final = ("Segoe UI Variable Text", 13)
    FONT_BODY_BOLD: Final = ("Segoe UI Variable Text", 13, "bold")
    FONT_SMALL: Final = ("Segoe UI Variable Text", 11)
    FONT_LABEL: Final = ("Segoe UI Variable Text", 10, "bold")
    FONT_MONO: Final = ("Cascadia Mono", 10)

    RADIUS_CARD: Final = 18
    RADIUS_CONTROL: Final = 11
