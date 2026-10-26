# 外部サービス・API連携設計（Music DL）

本書は、Music DL（`music_dl`）が外部サービス（YouTube）、外部SDK・実行バイナリ（`yt-dlp`, FFmpeg）、およびローカルファイルシステムと連携する際のインターフェース契約、タイムアウト・再試行設定、およびプライバシー・セキュリティ制御を定義します。

---

## 1. 外部連携先の一覧と境界

Music DLは独自のバックエンドサーバーや外部データベースを持たず、以下の外部要素と連携して動作します。

| 連携先 | 種別 | 役割・通信方式 | 認証・秘密情報の扱い | 実装モジュール |
| :--- | :--- | :--- | :--- | :--- |
| **YouTube** | 外部Webサービス | 利用者が指定した単一動画URLからのメディア情報・音声ストリーム取得（HTTPS） | APIキー、OAuthトークン、ブラウザCookie等の認証情報は一切保持・送信しない | `src/core/download_service.py` |
| **`yt-dlp`** | Python SDK (`YoutubeDL`) | YouTubeからのストリーム解析・ダウンロード制御、および後処理（FFmpeg）の呼び出し（`requirements.txt` 固定版：`2026.3.17`） | なし | `src/core/download_service.py` (`_create_downloader`, `_build_options`) |
| **FFmpeg** | 外部実行バイナリ (`ffmpeg.exe`) | ダウンロードした音声ストリームのMP3エンコード変換（OSの `PATH` 経由で実行） | なし | `DownloadService.validate_environment()` |
| **ローカルファイルシステム** | OSストレージ | 設定ファイル（`settings.json`）のアトミック保存、および変換済みMP3ファイルの出力 | ユーザー指定パス（ログ出力時はURLマスク対象） | `src/core/config.py`, `src/core/validation.py` |

---

## 2. `yt-dlp` SDK オプション契約と変換フロー

`DownloadService._build_options()` が構築し、`yt_dlp.YoutubeDL(options)` へ渡す設定パラメータの契約は以下のとおりです。

| オプションキー | 設定値 | 設計上の意図・役割 |
| :--- | :--- | :--- |
| `format` | `"bestaudio/best"` | 利用可能な最も高品質な音声ストリーム（またはフォールバックとして最良フォーマット）を選択する。 |
| `outtmpl` | `str(Path(save_dir) / "%(title)s.%(ext)s")` | 指定された保存先フォルダ配下に、動画タイトルをベースとしたファイル名で出力する。 |
| `noplaylist` | `True` | URL検証に加え、SDK側でもプレイリスト展開を明示的に無効化する。 |
| `postprocessors` | `[{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": bitrate}]` | 取得完了後にFFmpegを呼び出し、選択されたビットレート（`"128"`, `"192"`, `"320"`）のMP3へ変換する。 |
| `progress_hooks` | `[self._progress_hook]` | ダウンロード中（`downloading`）のバイト進捗と、取得完了・変換開始（`finished` → 進捗 `0.95`）を捕捉する。 |
| `socket_timeout` | `30` | ソケット通信の無応答タイムアウトを30秒に制限する（`NFR-05`）。 |
| `retries` | `3` | HTTP通信エラー時の通常リトライ回数を最大3回とする（`NFR-05`）。 |
| `fragment_retries` | `3` | 分割ストリーム（フラグメント）取得失敗時のリトライ回数を最大3回とする（`NFR-05`）。 |
| `quiet` / `no_warnings` | `True` / `True` | 標準出力への直接出力を抑制し、GUIの通知キュー（`queue.Queue`）へメッセージを一元化する。 |

---

## 3. タイムアウト・再試行・障害時の挙動

1. **通信タイムアウトと再試行の範囲**
   - `socket_timeout=30`、`retries=3`、`fragment_retries=3` は個々のソケット通信およびフラグメント取得に対する設定であり、動画全体のダウンロード完了時間を30秒に制限するものではありません。
   - YouTube側のレート制限（HTTP 429）に対する独自のバックオフ待機や、途中キャンセル・レジューム再開機構は持たず、リトライ上限超過時は例外として捕捉しステータスを `ERROR` へ遷移させます。
2. **ファイル名衝突・一時ファイルの扱い**
   - Windows禁止文字の置換、同名ファイル存在時の挙動、および変換失敗時に残る一時ファイル（`.part` 等）の扱いは `yt-dlp` の標準動作に委譲しています。
3. **FFmpegの事前・実行時確認**
   - アプリ起動時および `run_download()` 開始時に `shutil.which("ffmpeg")` を実行し、`PATH` 上にFFmpegが存在しない場合はネットワーク通信を行う前に処理を拒否します（`FR-10`）。

---

## 4. セキュリティ・プライバシー保護とテスト境界

### 4.1 エラーメッセージのURLマスキングとタイトル無害化

- **URLマスキング（`NFR-07`）**：`yt-dlp` やネットワーク層が送出した例外メッセージには入力URLが含まれる場合があるため、`DownloadService._safe_error_message()` において正規表現 `https?://\S+` をすべて **`[URL]`** に置換し、最大300文字に整形してからGUIログへ渡します。
- **動画タイトルのサニタイズ**：完了ログに出力する動画タイトルは `_sanitize_title()` によって制御文字を除去し、最大100文字に制限します。

### 4.2 自動単体テストと実機確認の境界

- `tests/test_download_service.py` では、`FakeDownloader`（モック）および実行ファイル検索の差し替えを用いて、オプション生成（`socket_timeout=30`、ビットレート反映等）、バイト数からの進捗計算、エラー時の `[URL]` マスキング、二重実行拒否、FFmpeg不在検知を外部通信なしで検証しています。
- 実際のYouTubeサーバーへの接続、FFmpegによる実MP3ファイル生成、および音声再生確認は、[UI_design.md](./UI_design.md) 第6.2節の手動受入チェックリストで実施します。
