# Music DL プロジェクト状況

| 管理項目 | 内容 |
| --- | --- |
| 最終更新日 | 2026-10-16 |
| 対象ブランチ | `main` |
| 状態 | 保存先ディレクトリ検証改善を反映・全品質Gate PASS。主要機能実装済み・原則として現状維持 |

## 1. 現在地点

- Music DLは、権利または許諾を持つYouTube単一動画から音声を取得し、Windows PCへMP3として保存するデスクトップアプリケーションです。
- GUI、取得・変換サービス、設定、入力検証と、対応する単体テストが存在します。
- `.docs/ProjectContext.md` は、今後の機能追加・改良を原則予定せず、依存環境への追従または重大な不具合への対応だけを個別判断する方針を定めています。
- 要求と実装状況は `.docs/ProjectContext.md`、設計は `.docs/Architecture.md`、利用・運用・手動受入は `.docs/Usage.md` を基準とします。

## 2. 確認済みの検証履歴

- 既存文書には、2026-08-19にPython 3.14.2でpytest 24件、Ruff 0.15.7、Black 24.10.0、Pyright 1.1.408が成功した記録があります。
- 上記は既存文書の履歴であり、今回の運用文書整備時に同じアプリケーション検査を再実行したことを意味しません。

## 3. 未解決事項と残存リスク

- 単一動画だけを対象とする要求に対し、現行URL検証はYouTubeドメイン上の動画以外の一部URLを通す可能性があります。
- 実YouTube・実FFmpegを使う自動結合試験、GUI自動試験、実MP3の再生確認、性能試験、アクセシビリティ試験は未整備です。
- 取得中の終了、キャンセル、部分ファイル整理、保存先の空き容量確認には既知の制約があります。
- `pyproject.toml` のBlack `target-version` は `py313`、RuffとPyrightおよびプロジェクト文書の基準はPython 3.14です。意図は未確認です。
- プロジェクト責任者と文書管理責任者、配布形式、コード署名、自動更新、アクセシビリティ基準、性能目標は未決定です。

## 4. 2026-09-06 エージェント運用文書整備

- 添付正本に基づき `.agents/MasterPrompt.md` を置換し、`.agents/ParentAgent.md` と `.agents/ChildAgent.md` を追加しました。
- Music DLの構成、品質コマンド、副作用境界、固有制約に合わせて `.codex/AGENTS.md` を作成しました。
- ルート `AGENTS.md` を読み込み入口として作成し、共通規約、運用手順、親・子の役割文書、本書、既存の `.docs` へ接続しました。
- 既存の `.docs` 3文書は固有情報の正本として保持し、移動または内容変更を行っていません。
- 子エージェントは利用していません。参照経路は静的に確認し、エージェントの新規起動による自動読込確認は実施していません。

### 4.1. 添付正本の記録

入力ディレクトリは `C:\Users\cogit\OneDrive\デスクトップ\新しいフォルダー` です。

| 入力ファイル | SHA-256 |
| --- | --- |
| `MasterPrompt.md` | `D72D5FE1DA3EB0A1ED82F2541156173641E890756118F32F4B4129223167BF2C` |
| `ParentAgent.md` | `837E7873A7594537783F9D60CAFEA5481F538CCE636D4DA20546FD9F076BC87A` |
| `ChildAgent.md` | `9D3F990E309A0BA74776DD15BF59E4A871101DDBC3F20F7716D3FC81D2076765` |
| `AGENTS.md` | `6732074577235B3EA2FE654ACF5F02226C956EA0C0917A127841F78FC4EF99D3` |

共通3文書は配置後のSHA-256が入力と一致しました。3文書の入力と作業ツリーはいずれもLF改行で、`MasterPrompt.md` の第13章は一つだけです。Gitの `core.autocrlf` は `true` で `.gitattributes` は存在しないため、Gitが今後作業ツリーへ触れる際にCRLFへ変換する可能性があります。今回のローカル配置時点のバイト一致と、将来のcheckout時の作業ツリー表現は区別して扱います。

### 4.2. 2026-09-06の検証結果

- 必須6文書の存在と、Markdownで記載した相対リンクの解決を静的に確認しました。
- `MasterPrompt.md` の第1章から第13章が各一つであることを確認しました。
- Music DL向けに作成したルート `AGENTS.md`、`.codex/AGENTS.md`、本書にSLOT固有語がないことを確認しました。
- 変更文書に行末空白がないことと、追跡済み差分に対する `git diff --check` がエラーなしであることを確認しました。`core.autocrlf=true` によるLFからCRLFへの将来変換警告は残ります。
- 文書のみの変更であるため、アプリケーションテスト、Ruff、Black、Pyright、GUI起動、外部サービス、実FFmpegを使う検証は今回実施していません。
- commitとpushは実施していません。

## 5. 2026-09-07 省トークン運用

- 親1体で実施し、子の起動は0体です。開始時ブランチは `main`、HEADは `f5d404fa4ba4e4dd0fc8f1e7f8e15d0c31a68e8d`、作業場所はMusic DLの既存checkoutです。
- 開始時の共通規約の未stage差分、親・子文書、ルート入口、`.codex/AGENTS.md`、本書の未追跡状態を保持して編集しました。開始時indexは空です。stage・commit・pushは行いません。
- [共通規約 第14章](../.agents/MasterPrompt.md#14-省トークン運用の共通ルール)を省トークン運用の正本とし、役割文書と入口の参照を整備しました。第4.1節のハッシュ一致は前回配置時の記録であり、今回編集後の一致を意味しません。
- 添付の共通3文書は編集開始時のローカル文書と同一でした。添付の入口は別プロジェクト用の参照資料として扱い、Music DLの固有設定・品質ゲート・禁止事項を保持しました。アプリ、依存関係、データ、CI、既存 `.docs/` は変更対象外です。
- 文書検証1巡で、6文書の実差分、12件の相対リンクと見出し参照、UTF-8・空白、第1〜14章の一意性、旧委任規定の除去を確認しました。共通規約の第1〜12章とMusic DL固有の第2〜6節は開始時と一致し、HEAD・index・変更対象も維持しています。git diff --checkは成功しました（既存のLF→CRLF警告あり）。検証失敗による追加修正は0巡です。アプリ全体のテストや外部操作は文書変更に不要なため実行していません。
- 厳密なトークン上限・メモリ解放・起動数制限の強制制御、消費計測、自動読込の新規起動確認は未実施です。モデル設定は変更せず、消費量や削減率は不明として扱います。

## 6. 2026-10-16 保存先ディレクトリ検証改善の反映

- ユーザーの明示指示により、DevNexusで実Review APPROVEDとなった既存patchを元Music DLへ反映しました。空文字・空白のみの入力をPath解釈前に拒否し、空白を含む有効なパス、expanduser・resolve・存在・種別・書き込み権限検査を維持しています。
- 開始時は `main`、HEAD `bc6268008b48330366f9918ecfc7998089bce8ec`、worktree・indexともcleanでした。コード変更は `src/core/validation.py` と `tests/test_validation.py` のみで、本書は運用記録です。
- 承認正本はDevNexus commit `9353c935b396e6ff5b03bdbb8e6d349fb5f475c2` の[保存済みDecision](../../DevNexus/.docs/evidence/music-directory-recovery-20261016/validated/decision.json)と[回復証拠](../../DevNexus/.docs/evidence/music-directory-recovery-20261016/README.md)です。Work `music-directory-review-transport-recovery-fe1c2a3d68fb481dbe504af0dead5168`、Decision `APPROVED`、required_changes・risksはいずれも空です。
- patch SHA-256 `1248ec36258e1d34fc94d006e10b57ddafd4d76a0f629b8fafca0631223e7cb3` を照合し、元HEAD・適用後の実差分が承認対象と完全一致しました。証拠manifestの全103ファイルをGit・ディスク双方から照合し、旧Workの保存archiveと実Reviewer応答の全Decision field一致も確認しました。既存Work・失敗Run・実Reviewの再dispatchは0件、実装修正は0件です。
- 元Projectの既存 `.venv` を再利用しました。Python 3.14.2、yt-dlp 2026.3.17、customtkinter 5.2.2、pytest 9.0.2、Ruff 0.15.7、Black 24.10.0、Pyright 1.1.408で、依存の追加・更新はありません。
- 元Project上の固定Gateは独立保存先検査11項目PASS、pytest全32件PASS（0.15秒）、Ruff PASS、Black PASS（11ファイル変更不要）、Pyright PASS（0 errors / 0 warnings）、protected・scope・git diff --check PASSです。pytestの出力先だけ新規TEMPへ変更し、既存Gateの引数・required・timeoutを維持しました。Pyrightは既存 `.venv` の探索先を明示しました。Pyrightの更新案内は残りますが更新は行っていません。
- 今回の実行ログは `C:/Users/cogit/AppData/Local/Temp/MusicDL-source-promotion-8v9nfnmf/` の `preflight.json`、`gates.json`、`result.json` に保存しました。`gates.json` SHA-256は `962bef02cf055c03e34f01005f77867f8b98540a9f27521c2237cfef3b54f6c2` です。TEMPログは恒久保管を保証しません。検証結果と承認識別子は本節を含むlocal commitへ記録します。
- DevNexusのHEAD・worktreeと既存証拠を保全し、Music DLの対象外追跡ファイル・利用者設定が不変であることを確認しました。Protected Asset・Security Policy変更、push・deploy、外部サービス接続、実FFmpeg・GUI・MP3再生検証は行っていません。既存のURL厳密性・GUI・実サービス等の制約は第3節に残ります。今回の修正に追加の未解決事項はありません。
- 要求・設計・利用文書の保存先検証契約との整合を確認しました。今回の反映は既存要求の境界不具合修正です。次の作業は原則現状維持で、追加開発は別の明示依頼を待ちます。
