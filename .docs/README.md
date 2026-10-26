# Music DL ドキュメント索引

本書は、YouTubeの単一動画から音声を取得してMP3として保存するWindowsデスクトップアプリケーション **Music DL（`music_dl`）** の公式ドキュメント体系（`.docs/`）の案内窓口です。

---

## 1. ドキュメント構成と役割分担

本プロジェクトの仕様・設計・操作手順は、役割ごとに整理された以下の **基本6文書** で構成されています。

| 文書ファイル | 役割と主な記載内容 | 主な対象読者 |
| :--- | :--- | :--- |
| [SystemOverview.md](./SystemOverview.md) | **システム概要**：目的、解決する課題、対象範囲（単一動画・MP3出力）、全体構成、利用から保存までの流れ、現在の実装状況と制約 | 全読者（利用者・PM・開発者） |
| [ProjectContext.md](./ProjectContext.md) | **要件定義**：利用前提・権利遵守原則、機能要件（`FR-01`〜`FR-10`）、非機能要件（`NFR-01`〜`NFR-10`）、実装差異・未決定事項、要件トレーサビリティ | PM・開発者・QA担当者 |
| [Architecture.md](./Architecture.md) | **詳細設計（アーキテクチャ）**：レイヤード構成（`src/ui` / `src/core`）、起動・設定・取得フロー、ワーカースレッドとUI通知キュー、`settings.json` スキーマ、進捗計算式、例外・セキュリティ制御 | 開発者・保守担当者 |
| [UI_design.md](./UI_design.md) | **UI設計・操作ガイド**：画面構成（`UI-001`〜`UI-004`）、状態表示（`READY` / `WORKING` / `DONE` / `CHECK` / `ERROR`）、環境準備・起動手順（`run.ps1`）、トラブルシューティング、手動受入試験項目 | 利用者・運用担当者・開発者 |
| [Glossary.md](./Glossary.md) | **用語集**：アプリケーション用語、画面状態、設定キー、外部ツール（`yt-dlp`, FFmpeg）、要件・画面IDの定義 | 全読者 |
| [ExternalIntegrations.md](./ExternalIntegrations.md) | **外部サービス・API連携**：YouTube・`yt-dlp`・FFmpeg・ローカルファイルシステムとの連携仕様、SDKオプション契約、タイムアウト・再試行制御、URLマスキング仕様 | 開発者・運用担当者 |

---

## 2. 目的別の推奨読書順序

1. **アプリケーションの目的と全体像を素早く把握したい場合**
   - [SystemOverview.md](./SystemOverview.md) → [Glossary.md](./Glossary.md)
2. **導入・起動方法、画面の操作手順、エラー時の対処法を知りたい場合**
   - [UI_design.md](./UI_design.md)
3. **要件・受入条件と、現在の実装範囲・制約を確認したい場合**
   - [ProjectContext.md](./ProjectContext.md)
4. **コード構造、スレッド設計、`yt-dlp` / FFmpeg呼び出し仕様を確認したい場合**
   - [Architecture.md](./Architecture.md) → [ExternalIntegrations.md](./ExternalIntegrations.md)

---

## 3. 関連するリポジトリ内規約・管理ファイル

- [AGENTS.md](../AGENTS.md) / [.codex/AGENTS.md](../.codex/AGENTS.md)：開発エージェント向け作業規約
- [.agents/MasterPrompt.md](../.agents/MasterPrompt.md)：共通ガバナンス・品質基準
- [.codex/ProjectStatus.md](../.codex/ProjectStatus.md)：プロジェクトの現在地・検証記録
- [README.md](../README.md)：リポジトリルートのクイックスタート案内
