# 要件定義（Music DL）

本書は、Music DL（`music_dl`）が満たすべき機能要件、非機能要件、利用前提、受入条件、および現行実装との差異・トレーサビリティを定義します。

---

## 1. 基本原則と利用前提

### 1.1 設計・運用の5原則

1. **権利と法令の遵守**：著作権、YouTube利用規約、および必要な許諾を利用者自身が確認したコンテンツのみを対象とする。
2. **境界での事前検証**：URL、保存先フォルダ、音質設定、外部プログラム（FFmpeg）を処理開始前に検証する。
3. **UI応答性の維持**：ネットワーク取得と音声変換はバックグラウンドスレッドで実行し、GUIイベントループをブロックしない。
4. **設定の破損防止**：設定ファイルの読み書きは検証とアトミック置換を組み合わせ、途中終了による破損を防ぐ。
5. **プライバシー保護**：認証情報や履歴を保存せず、エラーログ出力時にはURLを `[URL]` へマスクする。

### 1.2 動作環境の前提

- **OS**：Windows（PowerShellおよびGUI表示が可能な環境）
- **Python環境**：Python 3.14 および Python Launcher（`py` コマンド）
- **外部プログラム**：`ffmpeg` がシステムの `PATH` 環境変数に登録され、コマンドラインから実行可能であること
- **必須Pythonパッケージ**：`customtkinter==5.2.2`、`yt-dlp==2026.3.17`（`requirements.txt` 基準）
- **保存先条件**：指定された保存先フォルダが存在し、書き込み権限と十分な空き容量があること

---

## 2. 機能要件（FR）

| 要件ID | 要件名 | 受入条件 | 実装・検証状況 |
| :--- | :--- | :--- | :--- |
| **`FR-01`** | **単一動画URLの入力** | URL入力欄への手入力および「貼り付け」ボタンによるクリップボード貼り付けの両方が利用できること。 | 実装済（単体検証済） |
| **`FR-02`** | **音声取得とMP3変換** | 有効なYouTube単一動画URLから音声を取得し、指定した保存先に再生可能なMP3ファイルを生成できること。 | 実装済（モック単体検証済・実動画再生は手動受入対象） |
| **`FR-03`** | **音声ビットレート選択** | `128`、`192`、`320` kbpsの3段階から音質を選択でき、FFmpeg変換設定（`preferredquality`）へ反映されること。 | 実装済（単体検証済） |
| **`FR-04`** | **保存先フォルダの選択** | フォルダ選択ダイアログから、存在し書き込み可能な保存先ディレクトリを指定できること。 | 実装済（単体検証済） |
| **`FR-05`** | **設定の永続化と復元** | 選択した保存先フォルダとビットレートを `settings.json` に保存し、次回起動時に自動復元できること。 | 実装済（単体検証済） |
| **`FR-06`** | **処理状況とログの表示** | 待機（`READY`）、処理中（`WORKING`）、完了（`DONE`）、確認（`CHECK`）、失敗（`ERROR`）の状態、進捗バー、および画面内詳細ログを表示できること。 | 実装済（単体検証済） |
| **`FR-07`** | **重複実行の防止** | ダウンロード・変換処理の実行中は2件目の処理開始を拒否し、入力・開始操作を無効化すること。 | 実装済（単体検証済） |
| **`FR-08`** | **不正入力・対象外の拒否** | 空URL、YouTube以外のドメイン、`list` パラメータを含むプレイリストURL、存在しない/書き込み不可の保存先を開始前に拒否すること。 | 一部実装差異あり（後述5.1参照） |
| **`FR-09`** | **単一スクリプト起動** | `run.ps1` の実行により、Python/FFmpeg確認、`.venv` 作成、依存パッケージ確認を経てアプリを起動できること。 | 実装済 |
| **`FR-10`** | **FFmpeg不在時の事前通知** | FFmpegが `PATH` 上に見つからない場合、画面に理由を表示してダウンロード開始を防止すること。 | 実装済（単体検証済） |

---

## 3. 非機能要件（NFR）

| 要件ID | 分類 | 要件・判断基準 | 実装・検証状況 |
| :--- | :--- | :--- | :--- |
| **`NFR-01`** | **対応環境** | WindowsおよびPython 3.14を基準環境として動作すること。 | Python 3.14.2で単体テスト・静的解析通過済 |
| **`NFR-02`** | **UI応答性** | 取得・変換をワーカースレッドへ分離し、`queue.Queue` 経由の非同期更新により画面フリーズを防ぐこと。 | 実装済 |
| **`NFR-03`** | **入力境界の安全性** | URL・保存先・FFmpegを境界で検証し、APIキーやCookie等の秘密情報を設定・ログに保持しないこと。 | 実装済（URL厳密性は5.1参照） |
| **`NFR-04`** | **設定データ整合性** | `settings.json` 保存時は一時ファイルへの書き込み・`flush`・`os.fsync` 後に `os.replace` でアトミックに置換し、破損時は既定値へ安全にフォールバックすること。 | 実装済（単体検証済） |
| **`NFR-05`** | **通信タイムアウト・再試行** | `yt-dlp` に対し、通信タイムアウト `socket_timeout=30` 秒、通常再試行 `retries=3` 回、フラグメント再試行 `fragment_retries=3` 回を設定すること。 | 実装済（単体検証・コード確認済） |
| **`NFR-06`** | **保守性・責務分離** | GUI層（`src/ui`）とコア層（`src/core`）の依存を単一方向（`ui -> core`）に保ち、Ruff / Black / Pyright検査を通過すること。 | 実装済（静的検査通過済） |
| **`NFR-07`** | **プライバシー保護** | 独自のテレメトリ送信を行わず、エラーメッセージ内のHTTP/HTTPS URLを `[URL]` に置換してログ出力すること。 | 実装済（単体検証済） |
| **`NFR-08`** | **運用観測性** | 画面内の詳細ログパネル（メモリ内保持）により、環境確認・設定変更・処理開始・完了・エラー原因を確認できること。 | 実装済 |
| **`NFR-09`** | **アクセシビリティ** | ダークテーマの配色管理、基本ショートカット（`Enter` 開始、`Ctrl+L` URLフォーカス）、色とテキストの併用を行うこと。 | 基本実装済（厳密な適合基準は未設定） |
| **`NFR-10`** | **性能目標** | 外部回線速度と動画長に依存するため、アプリ固有の固定処理時間SLAは設けない。 | 対象外（未設定） |

---

## 4. 要件トレーサビリティマトリクス

各要件に対応する設計箇所、実装モジュール、および単体テストの対応関係は以下のとおりです。

| 要件ID | 対応する設計セクション | 実装モジュール・主要クラス/関数 | 対応する単体テスト（`tests/`） |
| :--- | :--- | :--- | :--- |
| `FR-01` | [UI_design.md](./UI_design.md) (`UI-001`) | `src/ui/app_window.py` (`ModernUI._paste_clipboard`, `_start_download`) | `test_validation.py` (`test_accepts_supported_video_urls`) |
| `FR-02` | [Architecture.md](./Architecture.md) §4 | `src/core/download_service.py` (`DownloadService._download_worker`) | `test_download_service.py` (`test_successful_download_builds_expected_options`) |
| `FR-03` | [UI_design.md](./UI_design.md) (`UI-001`) | `src/core/config.py` (`AppConfig.with_bitrate`), `DownloadService._build_options` | `test_config.py`, `test_download_service.py` |
| `FR-04` | [UI_design.md](./UI_design.md) (`UI-002`) | `src/ui/app_window.py` (`_change_directory`), `src/core/validation.py` (`validate_output_directory`) | `test_validation.py` (`test_rejects_blank_output_directory` 他) |
| `FR-05` | [Architecture.md](./Architecture.md) §5 | `src/core/config.py` (`ConfigManager.load`, `save`) | `test_config.py` (`test_round_trip_settings`, `test_save_failure_is_reported`) |
| `FR-06` | [UI_design.md](./UI_design.md) (`UI-001`, `UI-003`) | `src/ui/app_window.py` (`_on_progress`, `_on_finish`, `_drain_ui_queue`) | `test_download_service.py` (`test_progress_hook_uses_byte_counts`) |
| `FR-07` | [Architecture.md](./Architecture.md) §4 | `src/core/download_service.py` (`run_download`, `is_running`) | `test_download_service.py` (`test_rejects_second_download_while_running`) |
| `FR-08` | [Architecture.md](./Architecture.md) §6 | `src/core/validation.py` (`validate_youtube_url`, `validate_output_directory`) | `test_validation.py` |
| `FR-09` | [UI_design.md](./UI_design.md) §4 | `run.ps1`, `src/main.py` (`main`) | 手動起動確認手順（[UI_design.md](./UI_design.md) §7） |
| `FR-10` | [ExternalIntegrations.md](./ExternalIntegrations.md) §2 | `src/core/download_service.py` (`validate_environment`) | `test_download_service.py` (`test_validate_environment`) |
| `NFR-04` | [Architecture.md](./Architecture.md) §5 | `src/core/config.py` (`ConfigManager.save`) | `test_config.py` |
| `NFR-05` | [ExternalIntegrations.md](./ExternalIntegrations.md) §3 | `src/core/download_service.py` (`_build_options`) | `test_download_service.py` (`socket_timeout=30` 検証) |
| `NFR-07` | [ExternalIntegrations.md](./ExternalIntegrations.md) §4 | `src/core/download_service.py` (`_safe_error_message`) | `test_download_service.py` (`test_failure_masks_url_and_finishes`) |

---

## 5. 既知の実装差異・制約事項・保守方針

### 5.1 現行実装と要件の微細差異

| 項目 | 現行実装の挙動 | 影響と扱い |
| :--- | :--- | :--- |
| **URL形式検証の許容範囲**（`FR-08`） | `validate_youtube_url()` は `/watch` パスの場合に `v` クエリパラメータを必須とする一方、それ以外のパス（`/shorts/...` やチャンネルページ等）ではパスが空でなければ通過させる。 | 動画ページ以外のYouTube URLが入力された場合、開始前検証を通過して `yt-dlp` 実行時にエラーとなる。現状維持方針のもと、既知の仕様差異として管理する。 |
| **`run.ps1` の既存仮想環境再利用** | `.venv` が既に存在し、`customtkinter` と `yt_dlp` がインポート可能な場合、Pythonマイナーバージョンやパッケージの厳密な固定バージョン一致を再検査しない。 | 環境更新時に不整合が疑われる場合は、運用手順に従い `.venv` を再作成する。 |

### 5.2 運用・保守方針

本プロジェクトは主要機能の実装を完了しており、**機能凍結（現状維持）** とします。キャンセル機能、部分ファイル自動清掃、永続ログ等を含む新規機能の追加は行わず、外部仕様変更や重大不具合発生時のみ最小限の修正を検討します。
