# Research: 命令列記帳小工具

Technical Context 沒有 NEEDS CLARIFICATION，以下記錄主要技術決策。

## 1. 命令列解析

- **Decision**: 標準函式庫 `argparse` + subparsers。
- **Rationale**: 憲章原則 V 只用標準庫；三個子指令的規模 argparse 綽綽有餘。
- **Alternatives considered**: Click／Typer（體驗較好，但多一個依賴）。

## 2. 金額表示

- **Decision**: 程式內用 `decimal.Decimal`，JSON 內以字串保存（例：`"120.50"`），量化到 0.01。
- **Rationale**: 憲章原則 IV；字串保存可避免 JSON number 被當成 float 讀回。
- **Alternatives considered**: 整數「分」（精確但檔案可讀性差）；float（違反憲章）。

## 3. 資料檔格式與寫入

- **Decision**: `{"version": 1, "expenses": [...]}`；寫入先寫同目錄暫存檔再 `os.replace`。
- **Rationale**: 版本號留給未來格式遷移；`os.replace` 在 Windows／POSIX 都是原子取代。
- **Alternatives considered**: SQLite（過度設計）、CSV（型別與跳脫較麻煩）。

## 4. 資料檔位置

- **Decision**: 優先序 `--file` 參數 > 環境變數 `LEDGER_FILE` > `Path.home() / ".ledger" / "ledger.json"`。
- **Rationale**: 不硬編碼使用者路徑；測試可用參數指到 `tmp_path`。

## 5. 專案管理與測試

- **Decision**: uv（`uv init --package` 風格 src layout、`uv add --dev pytest`），pytest。
- **Rationale**: 使用者指定；`uv run pytest` 一指令完成環境建立與測試。
