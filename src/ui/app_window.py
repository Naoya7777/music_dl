"""CustomTkinter presentation layer for Music DL."""

from __future__ import annotations

import queue
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from tkinter import TclError, filedialog, messagebox
from typing import Any, Final

import customtkinter as ctk

from ..core.config import SUPPORTED_BITRATES, AppConfig, ConfigManager, ConfigurationError
from ..core.download_service import DownloadService
from ..core.validation import InputValidationError, validate_youtube_url
from .theme import Theme

_POLL_INTERVAL_MS: Final = 50


class ModernUI(ctk.CTk):
    """Main window coordinating user actions and application services."""

    def __init__(
        self,
        config_manager: ConfigManager | None = None,
        downloader: DownloadService | None = None,
    ) -> None:
        super().__init__()
        self.config_manager = config_manager or ConfigManager()
        self.downloader = downloader or DownloadService()
        self.config = self.config_manager.load()

        self._ui_queue: queue.Queue[tuple[Callable[..., None], tuple[Any, ...]]] = queue.Queue()
        self._closing = False
        self._logs_visible = False

        self.url_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="URLを入力して開始してください")
        self.path_var = ctk.StringVar(value=self._display_path(self.config.save_dir))

        self._configure_window()
        self._build_layout()
        self._bind_shortcuts()
        self._check_environment()
        self.after(_POLL_INTERVAL_MS, self._drain_ui_queue)

    def _configure_window(self) -> None:
        ctk.set_appearance_mode("Dark")
        self.title("Music DL")
        self.geometry("760x720")
        self.minsize(700, 660)
        self.configure(fg_color=Theme.WINDOW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_layout(self) -> None:
        shell = ctk.CTkFrame(self, fg_color="transparent")
        shell.grid(row=0, column=0, rowspan=2, padx=34, pady=(28, 24), sticky="nsew")
        shell.grid_columnconfigure(0, weight=1)
        shell.grid_rowconfigure(4, weight=1)

        self._build_header(shell)
        self._build_download_card(shell)
        self._build_status_card(shell)
        self._build_settings_row(shell)
        self._build_log_panel(shell)

    def _build_header(self, parent: ctk.CTkFrame) -> None:
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, pady=(0, 22), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        mark = ctk.CTkFrame(
            header,
            width=52,
            height=52,
            corner_radius=16,
            fg_color=Theme.PRIMARY,
        )
        mark.grid(row=0, column=0, rowspan=2, padx=(0, 15))
        mark.grid_propagate(False)
        ctk.CTkLabel(
            mark,
            text="M",
            font=("Segoe UI Variable Display", 22, "bold"),
            text_color="#FFFFFF",
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            header,
            text="Music DL",
            font=Theme.FONT_HERO,
            text_color=Theme.TEXT,
        ).grid(row=0, column=1, sticky="sw")
        ctk.CTkLabel(
            header,
            text="YouTube audio · clean, focused, local",
            font=Theme.FONT_SMALL,
            text_color=Theme.TEXT_SECONDARY,
        ).grid(row=1, column=1, sticky="nw")

        badge = ctk.CTkLabel(
            header,
            text="  MP3  ",
            height=28,
            corner_radius=14,
            fg_color=Theme.SUCCESS_BG,
            text_color=Theme.ACCENT,
            font=Theme.FONT_LABEL,
        )
        badge.grid(row=0, column=2, rowspan=2, sticky="e")

    def _build_download_card(self, parent: ctk.CTkFrame) -> None:
        card = self._card(parent)
        card.grid(row=1, column=0, pady=(0, 14), sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="VIDEO URL",
            font=Theme.FONT_LABEL,
            text_color=Theme.TEXT_MUTED,
        ).grid(row=0, column=0, padx=22, pady=(20, 8), sticky="w")

        input_row = ctk.CTkFrame(card, fg_color="transparent")
        input_row.grid(row=1, column=0, padx=22, sticky="ew")
        input_row.grid_columnconfigure(0, weight=1)

        self.url_entry = ctk.CTkEntry(
            input_row,
            textvariable=self.url_var,
            placeholder_text="https://www.youtube.com/watch?v=...",
            height=52,
            corner_radius=Theme.RADIUS_CONTROL,
            border_width=1,
            border_color=Theme.BORDER,
            fg_color=Theme.WINDOW,
            text_color=Theme.TEXT,
            placeholder_text_color=Theme.TEXT_MUTED,
            font=Theme.FONT_BODY,
        )
        self.url_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.paste_button = ctk.CTkButton(
            input_row,
            text="貼り付け",
            width=92,
            height=52,
            corner_radius=Theme.RADIUS_CONTROL,
            fg_color=Theme.SURFACE_RAISED,
            hover_color=Theme.SURFACE_HOVER,
            border_width=1,
            border_color=Theme.BORDER,
            text_color=Theme.TEXT,
            font=Theme.FONT_BODY_BOLD,
            command=self._paste_clipboard,
        )
        self.paste_button.grid(row=0, column=1)

        self.download_button = ctk.CTkButton(
            card,
            text="MP3をダウンロード",
            height=54,
            corner_radius=Theme.RADIUS_CONTROL,
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER,
            text_color="#FFFFFF",
            font=Theme.FONT_BODY_BOLD,
            command=self._start_download,
        )
        self.download_button.grid(row=2, column=0, padx=22, pady=(14, 22), sticky="ew")

    def _build_status_card(self, parent: ctk.CTkFrame) -> None:
        card = self._card(parent)
        card.grid(row=2, column=0, pady=(0, 14), sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        self.status_badge = ctk.CTkLabel(
            card,
            text="READY",
            width=66,
            height=28,
            corner_radius=14,
            fg_color=Theme.INFO_BG,
            text_color=Theme.PRIMARY_HOVER,
            font=Theme.FONT_LABEL,
        )
        self.status_badge.grid(row=0, column=0, padx=(20, 12), pady=(17, 11))

        self.status_label = ctk.CTkLabel(
            card,
            textvariable=self.status_var,
            anchor="w",
            font=Theme.FONT_BODY,
            text_color=Theme.TEXT_SECONDARY,
        )
        self.status_label.grid(row=0, column=1, padx=(0, 20), pady=(17, 11), sticky="ew")

        self.progress = ctk.CTkProgressBar(
            card,
            height=7,
            corner_radius=4,
            fg_color=Theme.BORDER,
            progress_color=Theme.PRIMARY,
        )
        self.progress.set(0)
        self.progress.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 18), sticky="ew")

    def _build_settings_row(self, parent: ctk.CTkFrame) -> None:
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.grid(row=3, column=0, pady=(0, 14), sticky="ew")
        row.grid_columnconfigure(0, weight=3)
        row.grid_columnconfigure(1, weight=2)

        destination_card = self._card(row)
        destination_card.grid(row=0, column=0, padx=(0, 7), sticky="nsew")
        destination_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            destination_card,
            text="保存先",
            font=Theme.FONT_LABEL,
            text_color=Theme.TEXT_MUTED,
        ).grid(row=0, column=0, padx=18, pady=(16, 2), sticky="w")
        self.directory_button = ctk.CTkButton(
            destination_card,
            textvariable=self.path_var,
            height=38,
            anchor="w",
            fg_color="transparent",
            hover_color=Theme.SURFACE_HOVER,
            text_color=Theme.TEXT,
            font=Theme.FONT_SMALL,
            command=self._change_directory,
        )
        self.directory_button.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        quality_card = self._card(row)
        quality_card.grid(row=0, column=1, padx=(7, 0), sticky="nsew")
        quality_card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            quality_card,
            text="音質",
            font=Theme.FONT_LABEL,
            text_color=Theme.TEXT_MUTED,
        ).grid(row=0, column=0, padx=18, pady=(16, 7), sticky="w")
        values = [f"{bitrate}k" for bitrate in SUPPORTED_BITRATES]
        self.quality_selector = ctk.CTkSegmentedButton(
            quality_card,
            values=values,
            height=32,
            corner_radius=9,
            fg_color=Theme.WINDOW,
            selected_color=Theme.PRIMARY,
            selected_hover_color=Theme.PRIMARY_HOVER,
            unselected_color=Theme.WINDOW,
            unselected_hover_color=Theme.SURFACE_HOVER,
            text_color=Theme.TEXT,
            font=Theme.FONT_SMALL,
            command=self._update_quality,
        )
        self.quality_selector.set(f"{self.config.bitrate}k")
        self.quality_selector.grid(row=1, column=0, padx=16, pady=(0, 15), sticky="ew")

    def _build_log_panel(self, parent: ctk.CTkFrame) -> None:
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=4, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)

        self.log_toggle = ctk.CTkButton(
            container,
            text="詳細ログを表示  +",
            height=30,
            anchor="w",
            fg_color="transparent",
            hover_color=Theme.SURFACE,
            text_color=Theme.TEXT_MUTED,
            font=Theme.FONT_SMALL,
            command=self._toggle_logs,
        )
        self.log_toggle.grid(row=0, column=0, sticky="ew")

        self.log_panel = self._card(container)
        self.log_panel.grid(row=1, column=0, pady=(8, 0), sticky="nsew")
        self.log_panel.grid_columnconfigure(0, weight=1)
        self.log_panel.grid_rowconfigure(0, weight=1)

        self.log_box = ctk.CTkTextbox(
            self.log_panel,
            height=135,
            corner_radius=12,
            border_width=0,
            fg_color=Theme.WINDOW,
            text_color=Theme.TEXT_SECONDARY,
            font=Theme.FONT_MONO,
            activate_scrollbars=True,
        )
        self.log_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.log_box.configure(state="disabled")
        self.log_panel.grid_remove()

    @staticmethod
    def _card(parent: ctk.CTkBaseClass) -> ctk.CTkFrame:
        return ctk.CTkFrame(
            parent,
            corner_radius=Theme.RADIUS_CARD,
            fg_color=Theme.SURFACE,
            border_width=1,
            border_color=Theme.BORDER,
        )

    def _bind_shortcuts(self) -> None:
        self.bind("<Return>", lambda _event: self._start_download())
        self.bind("<Control-l>", lambda _event: self._focus_url())
        self.url_entry.focus_set()

    def _focus_url(self) -> None:
        self.url_entry.focus_set()
        self.url_entry.select_range(0, "end")

    def _check_environment(self) -> None:
        if not self.downloader.validate_environment():
            self._show_status("FFmpegが見つかりません。PATHを確認してください", "error")
            self.download_button.configure(state="disabled")
            self._log("FFmpeg のシステムチェックに失敗しました。", "error")
            return
        self._log("システムチェックが完了しました。", "info")
        if self.config_manager.last_warning:
            self._log(self.config_manager.last_warning, "warning")

    def _paste_clipboard(self) -> None:
        try:
            text = self.clipboard_get().strip()
        except TclError:
            self._show_status("クリップボードから文字列を取得できません", "warning")
            return
        if text:
            self.url_var.set(text)
            self._show_status("URLを貼り付けました", "ready")

    def _change_directory(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.config.save_dir, parent=self)
        if not selected:
            return
        updated = self.config.with_save_dir(selected)
        if self._persist_config(updated):
            self.path_var.set(self._display_path(selected))
            self._log(f"保存先を変更しました: {selected}", "info")

    def _update_quality(self, choice: str) -> None:
        updated = self.config.with_bitrate(choice.removesuffix("k"))
        if self._persist_config(updated):
            self._log(f"音質を {updated.bitrate} kbps に変更しました。", "info")
        else:
            self.quality_selector.set(f"{self.config.bitrate}k")

    def _persist_config(self, updated: AppConfig) -> bool:
        try:
            self.config_manager.save(updated)
        except ConfigurationError as error:
            self._show_status(str(error), "error")
            self._log(str(error), "error")
            return False
        self.config = updated
        return True

    def _start_download(self) -> None:
        if self.downloader.is_running:
            return
        try:
            url = validate_youtube_url(self.url_var.get())
            started = self.downloader.run_download(
                url=url,
                config=self.config,
                progress_callback=lambda value, message: self._post_ui(
                    self._on_progress, value, message
                ),
                log_callback=lambda message, level: self._post_ui(self._log, message, level),
                finish_callback=lambda success, message: self._post_ui(
                    self._on_finish, success, message
                ),
            )
        except (InputValidationError, RuntimeError) as error:
            self._show_status(str(error), "error")
            return

        if not started:
            self._show_status("別のダウンロードを処理中です", "warning")
            return
        self._set_busy(True)
        self.progress.set(0)
        self._show_status("ダウンロードを準備しています", "working")

    def _on_progress(self, value: float, message: str) -> None:
        self.progress.set(max(0.0, min(value, 1.0)))
        self._show_status(message, "working")

    def _on_finish(self, success: bool, message: str) -> None:
        self._set_busy(False)
        self.progress.set(1.0 if success else 0.0)
        if success:
            self.url_var.set("")
            self._show_status(message, "success")
        else:
            self._show_status(message, "error")

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.url_entry.configure(state=state)
        self.paste_button.configure(state=state)
        self.directory_button.configure(state=state)
        self.quality_selector.configure(state=state)
        self.download_button.configure(
            state=state,
            text="処理しています…" if busy else "MP3をダウンロード",
            fg_color=Theme.PRIMARY_DISABLED if busy else Theme.PRIMARY,
        )

    def _show_status(self, message: str, tone: str) -> None:
        styles = {
            "ready": ("READY", Theme.INFO_BG, Theme.PRIMARY_HOVER),
            "working": ("WORKING", Theme.INFO_BG, Theme.PRIMARY_HOVER),
            "success": ("DONE", Theme.SUCCESS_BG, Theme.SUCCESS),
            "warning": ("CHECK", Theme.WARNING_BG, Theme.WARNING),
            "error": ("ERROR", Theme.ERROR_BG, Theme.ERROR),
        }
        badge, background, color = styles[tone]
        self.status_var.set(message)
        self.status_badge.configure(text=badge, fg_color=background, text_color=color)
        self.status_label.configure(text_color=color if tone == "error" else Theme.TEXT_SECONDARY)

    def _log(self, message: str, level: str) -> None:
        prefixes = {"error": "ERR", "warning": "WRN", "success": "OK ", "info": "INF"}
        timestamp = datetime.now().astimezone().strftime("%H:%M:%S")
        line = f"{timestamp}  {prefixes.get(level, 'INF')}  {message}\n"
        self.log_box.configure(state="normal")
        self.log_box.insert("end", line)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        if level == "error" and not self._logs_visible:
            self._toggle_logs()

    def _toggle_logs(self) -> None:
        self._logs_visible = not self._logs_visible
        if self._logs_visible:
            self.log_panel.grid()
            self.log_toggle.configure(text="詳細ログを隠す  -")
            self.geometry("760x860")
        else:
            self.log_panel.grid_remove()
            self.log_toggle.configure(text="詳細ログを表示  +")
            self.geometry("760x720")

    def _post_ui(self, callback: Callable[..., None], *args: Any) -> None:
        if not self._closing:
            self._ui_queue.put((callback, args))

    def _drain_ui_queue(self) -> None:
        if self._closing:
            return
        try:
            while True:
                callback, args = self._ui_queue.get_nowait()
                callback(*args)
        except queue.Empty:
            pass
        self.after(_POLL_INTERVAL_MS, self._drain_ui_queue)

    def _on_close(self) -> None:
        if self.downloader.is_running:
            should_close = messagebox.askyesno(
                "処理を終了しますか?",
                "ダウンロード中です。終了すると処理は完了しません。",
                parent=self,
            )
            if not should_close:
                return
        self._closing = True
        self.destroy()

    @staticmethod
    def _display_path(value: str, maximum: int = 46) -> str:
        path = str(Path(value))
        if len(path) <= maximum:
            return path
        return f"…{path[-(maximum - 1):]}"
