# Music DL 外部サービス・API連携設計書

文書版数: 3.0 / 更新日: 2026-10-25 / 確認基準Git: `95c2ec0d9b289f8548d990d1feb882462ce7f0e0` / 検証区分: 静的確認のみ（製品・正式Gate未実行）


目的は、外部SDKの設定・通信と、固定単体テストで保証できる範囲を分けることである。秘密値・実URL・保存先の個人情報は転記しない。

## 1. 接続一覧と環境

| 相手 | 方式・役割・認証 | 実装根拠 |
| --- | --- | --- |
| YouTube | 利用者指定URLへyt-dlp経由で取得。APIキー/Cookie設定を本アプリは持たない | `src/core/download_service.py: _create_downloader, _download_worker` |
| yt-dlp | Python SDK YoutubeDL、requirementsでは2026.3.17固定 | 同ファイル。provider固有endpointはSDKへ委譲 |
| FFmpeg | PATHで検出し、yt-dlp postprocessorからMP3変換 | `DownloadService.validate_environment`, `_build_options` |
| ローカル保存先 | 音声・部分ファイルの保存、settings置換 | `validation.py`, `config.py`。実行時の副作用 |

YouTubeの公開endpointや現行利用条件を今回オンライン調査していない。既存対象は権利・許諾を持つ動画のみ。認証/DRM回避を補完実装しない。

## 2. SDK入出力と連携フロー

`run_download` がURL/保存先/FFmpeg検証→単一実行枠→worker開始。workerは `YoutubeDL(options)` のcontextで `extract_info(url, download=True)` を呼ぶ。SDK応答のtitleを安全化してログ、成功/失敗をcallbackへ返す。HTTP REST APIをアプリが直接提供する構成ではない。

| option | 現行値・意味 |
| --- | --- |
| format | bestaudio/best |
| outtmpl | 保存先/`%(title)s.%(ext)s` |
| noplaylist | True |
| postprocessors | FFmpegExtractAudio、preferredcodec=mp3、preferredquality=AppConfig.bitrate |
| progress_hooks | downloadingで進捗、finishedで変換中0.95通知 |
| quiet / no_warnings | True。独自UI通知へ集約 |

## 3. 制限・timeout・再試行・復旧

socket_timeout=30秒、retries=3、fragment_retries=3はSDKへ渡す設定であり、全処理の上限時間やrate limit保証ではない。429専用の待機制御やcancel、resumable job管理はない。同名出力・一時ファイルの挙動は独自制御外をSDKへ委譲する。serviceのlockは同一instanceの二重実行を防ぐが、複数processや再送に対する冪等性は保証しない。失敗/終了後の部分ファイル整理は未実装。

## 4. 例外・秘密情報

workerはExceptionを捕捉しHTTP/HTTPS URLを[URL]へ置換、空白正規化し最大300文字をlogへ送る。タイトルは表示可能文字のみ最大100文字。URL以外の環境情報まで完全に匿名化する保証はない。認証情報を設定/文書へ持ち込まず、取得時の通常通信情報は接続先へ送られる点を保持する。GUI logは非永続。

## 5. テストと未確認

`tests/test_download_service.py` のFakeDownloader/実行ファイルfinder代替で、option、進捗、失敗URL隠蔽、単一実行、FFmpeg不足を検査する定義がある。今回未実行で静的照合のみ。YouTube接続・実FFmpeg・MP3生成/再生・network障害の手動受入は未確認。必要時の実機受入手順は[Usage§9.2](UI_design.md#h-75f337dae8a8)。
