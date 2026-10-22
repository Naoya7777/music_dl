# Music DL 用語・定義集

文書版数: 1.0 / 最終更新日: 2026-10-23 / 対象システム版: リリース版数未定義（基準HEADの実装）
確認基準HEAD: `b816b2f7ddd06b30a9006ff0de1ceec73765a962` / 対象読者: 全読者
対象範囲: 旧ProjectContextの正式用語を一元化。

目的は、画面上の音質とbitrate、設定保存と保存先の実書込可能性を区別することである。

## 1. 正式用語

| 正式名称 | 別名・識別子 | 定義 |
| --- | --- | --- |
| Music DL | 本アプリケーション | YouTube の単一動画から音声を取得して MP3 に変換する Windows デスクトップアプリケーション |
| 単一動画 URL | URL | プレイリストを示す `list` パラメーターを含まず、1 本の YouTube 動画を特定する HTTP または HTTPS のアドレス |
| 保存先フォルダ | `save_dir` | MP3 を保存する、存在して書き込み可能なフォルダ |
| 音声ビットレート | `bitrate`、画面上の音質 | 1 秒当たりの音声データ量。単位は kbps（キロビット毎秒）で、許可値は 128、192、320 |
| FFmpeg | `ffmpeg` | 取得した音声を MP3 に変換する外部プログラム |
| `yt-dlp` | 取得ライブラリ | YouTube からメディア情報と音声を取得し、FFmpeg の後処理を呼び出す外部ライブラリ |
| PATH | 環境変数 PATH | Windows が実行プログラムを探すフォルダの一覧 |
| 仮想環境 | `.venv` | このプロジェクトの Python とパッケージを分離する実行環境 |
| DRM | デジタル著作権管理 | コンテンツの利用や複製を技術的に制御する仕組み |
| GUI | 画面 | Graphical User Interface（グラフィカルユーザーインターフェース）。ボタンや入力欄で操作する画面 |

## 2. 読み・状態・識別子

MP3（エムピースリー）は本アプリの音声出力形式、kbpsはkilobits per second。yt-dlp（ワイティー・ディーエルピー）は外部取得library、FFmpeg（エフエフエムペグ）は外部変換program。画面上の「音質」は音声bitrate選択であり原音の品質向上を保証しない。

READY/WORKING/DONE/CHECK/ERRORはUIの待機/処理/成功/注意/失敗。workerは取得・変換用daemon thread、UI queueは画面threadへ通知を渡す待ち行列。FR-01〜10/NFR-01〜10は既存IDを維持、UI-001〜004は今回の追跡用。旧名/別名「本アプリケーション」はMusic DLを指し別製品ではない。

## 3. 関連する正本

データ項目・型は[Architecture§6](Architecture.md#6-データ構造スキーマ計算ロジック)、要件は[ProjectContext](ProjectContext.md)、UI状態は[UI](UI_design.md)、SDK契約は[外部連携](ExternalIntegrations.md)へ分担する。
