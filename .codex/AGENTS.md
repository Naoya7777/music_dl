# Music DL向けCodex指示

## 1. 優先して読む文書

1. リポジトリルートの `AGENTS.md`
2. `.agents/MasterPrompt.md`
3. 本書
4. 自分の役割に対応する `.agents/ParentAgent.md` または `.agents/ChildAgent.md`
5. `.codex/ProjectStatus.md`
6. 変更対象に対応する `.docs/` 内の設計文書

ユーザーの依頼全体を受け、分解、割当、統合、完了判定を担うエージェントは親として `.agents/ParentAgent.md` を読みます。親から範囲を限定して割り当てられた作業を担うエージェントは子として `.agents/ChildAgent.md` を読みます。役割が明示されておらず、ユーザーの依頼を直接受けた場合は親として扱います。

仕様と実装が異なる場合は、Git上の現在のコードとテストを実行時契約として確認し、差異を報告してください。実装に合わせて共通規約を変更しません。現在地点や一時的な課題は本書ではなく `.codex/ProjectStatus.md` に記録します。

省トークン運用は[共通規約 第14章](../.agents/MasterPrompt.md#14-文書配置とエージェント運用)を正本とします。上記は参照順であり、既読の未変更文書を循環して読み直す指示ではありません。本書はルート入口から明示参照されるプロジェクト固有の補足です。配置だけでリポジトリ全体への自動適用を仮定しません。

## 2. リポジトリ構成

- `src/main.py`: GUIアプリケーションの起動境界
- `src/ui/`: CustomTkinterによる画面、テーマ、画面スレッドへの通知
- `src/core/`: 設定、入力検証、`yt-dlp`を使う取得・FFmpeg変換サービス
- `tests/`: 外部サービスと実FFmpegを代替したpytest単体テスト
- `assets/`: アプリケーションのアイコン
- `.agents/`: 共通規約と親・子エージェントの役割定義
- `.docs/`: 要求、設計、利用・運用手順
- `.codex/ProjectStatus.md`: 現在地点を記録する唯一の状態文書
- `run.ps1`: Windows環境の確認、必要時の仮想環境・依存導入、GUI起動
- `settings.json`: 利用者の保存先と音声ビットレートを保持するローカル設定

要求と対象範囲の基準は `.docs/ProjectContext.md`、構造・データ・処理の基準は `.docs/Architecture.md`、導入・操作・手動受入は `.docs/Usage.md` です。

## 3. 実行環境と品質コマンド

- 対象OSはWindows、実行環境の基準はPython 3.14です。
- 実行依存関係は `requirements.txt`、開発依存関係は `requirements-dev.txt` を確認します。
- テスト: `.\.venv\Scripts\python.exe -m pytest`
- lint: `.\.venv\Scripts\python.exe -m ruff check src tests`
- 型検査: `.\.venv\Scripts\python.exe -m pyright`
- formatter確認: `.\.venv\Scripts\python.exe -m black --check src tests`

独立したbuildコマンドはありません。既存の `.venv` が利用可能なら再利用し、依存関係の変更や仮想環境の再作成を検証回避策として勝手に行わないでください。`run.ps1` は環境によって仮想環境作成、パッケージ導入、GUI起動を行うため、読取専用の検査コマンドとして実行しません。

`pyproject.toml` ではBlackの対象がPython 3.13、RuffとPyrightの対象がPython 3.14です。実行要件と文書はPython 3.14を基準としており、Black設定との差異は未解決事項として `.codex/ProjectStatus.md` で管理します。

## 4. 実装規約とデータ整合性

- `pyproject.toml` をBlack、Ruff、Pyright、pytest設定の正本とし、行長100、Ruffの既存選択ルール、Pyright basicに従います。
- GUI、取得・変換、設定、入力検証の責務と、`src/ui` から `src/core` への依存方向を維持します。
- `DownloadService` の単一実行制御とロック、ワーカースレッドからGUIキューを介する通知境界を維持します。
- URL、保存先、ビットレート、FFmpeg、外部応答を境界で検証します。単一動画URLの要求と現行検証の差異を、黙って仕様変更として扱いません。
- `settings.json` はUTF-8の一時ファイルを書き、フラッシュと置換を行う既存の保存境界を維持します。未知項目、破損時の既定値復帰、許可ビットレートの扱いを変更する場合は互換性を確認します。
- `yt-dlp`、YouTube、FFmpeg、ファイルシステムを使う副作用と、検証・設定ロジックを分離します。
- `# noqa` や `# type: ignore` は原因を先に解消し、必要な場合だけ対象と理由を限定します。

## 5. セキュリティと変更禁止範囲

- APIキー、パスワード、Cookie、個人情報、秘密情報を表示、編集、stage、commitしません。`settings.json` やログにも秘密情報を追加しません。
- 利用者が保存する権利または許諾を持つコンテンツだけを対象とし、DRM回避や権利確認の代行を実装しません。
- 実際のYouTubeへの接続、音声取得、FFmpeg変換、MP3・部分ファイルの作成は外部操作と副作用を伴います。ユーザーの明示的な運用意図と対象を確認せず実行しません。
- GUI起動、ブラウザ起動、`run.ps1`、依存パッケージの導入・更新、仮想環境の作成・削除を、検査だけを目的として実行しません。
- `settings.json`、利用者の保存先、生成済みMP3、部分ファイルを、明示指示なく変更・削除しません。
- YouTube URL、動画タイトル、保存先など利用者固有の情報を報告やログへ不要に露出させません。

## 6. Git運用と完了条件

- `main` 上で作業する場合も、開始時HEAD、worktree、index、未追跡ファイルを記録し、ユーザー変更を保護します。
- stage対象は今回変更したファイルを個別指定し、commit前に `git diff --cached` を確認します。pushは明示指示があるまで行いません。
- 変更リスクに応じてpytest、Ruff、Pyright、Blackを実行し、実施結果と未実施事項を区別します。
- 外部サービス、実FFmpeg、GUI、MP3再生を使う検証は自動単体検査と区別し、未実施ならその残存リスクを報告します。
- 実装、テスト、README、関連する `.docs/`、`.codex/ProjectStatus.md` の整合性と、対象範囲外の変更がないことを確認して完了を判定します。
