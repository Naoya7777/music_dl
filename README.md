# Music DL

YouTube の単一動画から音声を取得し、MP3 として保存する Windows 向けアプリです。
権利または許諾を持つコンテンツに限って使用してください。

## 必要なもの

- Python 3.14
- PATH が通った FFmpeg

## 実行

### デスクトップから起動する

このPCには「Music DL」デスクトップショートカットが作成されています。ショートカットを
ダブルクリックすると `run.ps1` が呼び出され、必要な準備を行ってからアプリが起動します。

```text
「Music DL」ショートカット
  → run.ps1
    → Python 3.14とFFmpegを確認
    → .venv仮想環境を必要に応じて作成
    → Pythonパッケージを必要に応じて導入
    → Music DLを起動
```

`run.ps1` は、Music DLを同じ手順で確実に起動するためのWindows PowerShellスクリプトです。
ショートカットはアプリ本体を直接起動するのではなく、このスクリプトを呼び出します。

### PowerShellから起動する

プロジェクトのフォルダで、次の1コマンドを実行します。

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

初回または必要なファイルがない場合だけ環境を準備します。既に準備済みの場合は、その環境を
再利用してアプリを起動します。

詳しい導入方法とトラブル対応は [使い方ガイド](docs/Usage.md)、仕様は
[プロジェクト概要](docs/ProjectContext.md) を参照してください。
