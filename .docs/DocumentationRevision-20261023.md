# Music DL 文書改訂・全資料移行台帳

文書版数: 1.0 / 最終更新日: 2026-10-23 / 対象システム版: リリース版数未定義（基準HEADの実装）
確認基準HEAD: `b816b2f7ddd06b30a9006ff0de1ceec73765a962` / 対象読者: 改訂担当・Review担当
対象範囲: 2026-10-23の文書変更と現行コード静的照合。

## 1. 基準・保全

main、開始時index/worktree/未追跡clean。全追跡hash/indexを作業TEMP `docs-group-a-baseline-20261023.json` に保存。保護指示・実装・設定・テスト・利用者settings.jsonを変更せず、stage/commit/push/deployなし。

## 2. 全既存文書台帳

| パス | 役割・内容/正確性 | 重複・参照と移行方針 |
| --- | --- | --- |
| `.docs/ProjectContext.md` | 要求・対象外・FR/NFR・受入。過去単体成功は当時の結果 | 維持・改訂。既存ID・現状維持方針を保存し、全ID追跡と2026-10-16保存先修正を反映。用語はGlossaryへ統合 |
| `.docs/Architecture.md` | 内部層・config schema・thread・進捗・例外 | 維持・改訂。保存先空値の現在境界を追記。UI状態をUIへ、SDK optionをExternalへ、要件追跡をProjectContextへ集約 |
| `.docs/Usage.md` | 導入・操作・障害対応・手動受入 | 補助正本として維持・管理情報改訂、固有手順を保存 |
| `.docs/README.md` | 旧索引 | 維持・改訂、6正本と補助の読順 |
| `.docs/DocumentationRollout.md` | 過去の横断移行Evidence | 履歴保管、原文維持 |
| `README.md` | root起動案内 | 維持、詳細は索引/Usage参照 |
| `requirements.txt`, `requirements-dev.txt` | dependency宣言、文書ではなく実装根拠 | 読取・原バイト維持 |
| `.codex/ProjectStatus.md` | 現在地点・2026-10-16承認/検証 | 維持、親へ必要更新事項を返す |
| `.codex/ProjectStatus.history-20261017.md` | 過去状態snapshot | 履歴保管、原バイト維持 |
| `AGENTS.md`, `.agents/*.md`, `.codex/AGENTS.md` | 保護指示 | 維持、変更禁止 |

既存Markdown/text仕様・READMEは全パスを棚卸し。削除・移動なし。旧要件・制約・判断は保持し、API/UI/用語/traceabilityの重複を相対リンクへ変えた。生成物・cache・venv文書は第三者/一時物として除外。

## 3. 実装調査

`src/main.py`, `src/core/{config,validation,download_service}.py`, `src/ui/{app_window,theme}.py`, `run.ps1`, `requirements*.txt`, `pyproject.toml`, `tests/test_{config,validation,download_service}.py` を確認。ConfigManagerの原子保存、Path解釈前の空値拒否、空白保持、single worker lock、queue/after=50ms、SDK option、UIのbusy/finish/closeを照合した。

## 4. 不一致・未決定

旧文書の保存先境界説明は2026-10-16修正を十分示さなかったため更新。単一動画要件とURLの広い非空path許可の差は継承し、今回コードを変更しない。Black target py313とRuff/Pyright py314は既知差異、配布/署名/自動更新、アクセシビリティ/性能基準は未決定。現状維持方針とキャンセル等の対象外を保持する。

## 5. 検証・残課題

文書link、章数、UTF-8、識別子、diff、非文書hash/index保全を自己検証。製品pytest/lint/型/build・GUI・YouTube/FFmpeg・MP3生成/再生は文書のみの変更のため未実行。過去2026-10-16のpytest32等は今回の成功としない。独立Gate/Review・commitは親が直列実施、本記録作成時REVIEW待ち。製品の最終受入と文書改訂は別判定。状態更新事項: 既存正式文書を保った6役割整備と現在境界の静的確認、既存制約は維持。

## 6. 独立Review修正

NFR-05の検証根拠を修正。socket_timeout=30は対応単体テストの検査対象、retries=3・fragment_retries=3はコード静的確認のみ。今回テスト未実行と過去成功を区別し、コード・テストは変更しない。

## 7. 統合後の最終判定

2026-10-23: 既存DevNexusの独立Gate PASS、実CodexReviewer APPROVED（review-music_dl-2.json）。文書改訂COMPLETED。実装整合性は基準HEADの静的照合であり、記録した未実装・不一致・未決定を解決済みにしません。既存アプリテストは今回再実行していません。今回の文書のみlocal commitし、push/deployは行いません。[全体Evidenceとcommit台帳](../../DevNexus/.docs/evidence/document-revision-20261023/README.md)。
