# Music DL

YouTube の単一動画から音声を取得し、MP3 として保存する Windows 向けアプリです。
権利または許諾を持つコンテンツに限って使用してください。

## 必要なもの

- Python 3.14
- PATH が通った FFmpeg

## 実行

プロジェクトのフォルダで、次の1コマンドを実行します。

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

初回のみ仮想環境を作成し、必要な Python パッケージを導入してからアプリを起動します。

詳しい導入方法とトラブル対応は [使い方ガイド](docs/Usage.md)、仕様は
[プロジェクト概要](docs/ProjectContext.md) を参照してください。
