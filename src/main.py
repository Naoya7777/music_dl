"""Application entry point."""

from .ui.app_window import ModernUI


def main() -> None:
    """Start the Music DL desktop application."""

    app = ModernUI()
    app.mainloop()


if __name__ == "__main__":
    main()
