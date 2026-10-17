# Implementation Plan: 命令列記帳小工具

**Branch**: `001-cli-expense-tracker` | **Date**: 2026-10-18 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-cli-expense-tracker/spec.md`

## Summary

提供 `ledger` 命令列工具，三個子指令：`add`（新增支出）、`list`（列出，可依月份篩選）、
`total`（月合計＋類別小計）。資料存在單一 UTF-8 JSON 檔，金額用 `Decimal` 處理，
以 uv 管理專案、pytest 測試。只用標準函式庫（argparse、json、decimal、datetime、pathlib）。

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: 執行期無第三方依賴；開發依賴 pytest

**Storage**: 本機 JSON 檔（預設 `~/.ledger/ledger.json`，可用 `--file` 或環境變數 `LEDGER_FILE` 覆寫）

**Testing**: pytest（`uv run pytest`），使用 `tmp_path` 隔離資料檔

**Target Platform**: Windows／macOS／Linux 終端機

**Project Type**: cli

**Performance Goals**: 1,000 筆紀錄下 list／total < 1 秒（全量讀入記憶體即可達成）

**Constraints**: 離線、單一使用者、寫入需原子化

**Scale/Scope**: 個人使用，預期 < 10,000 筆

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 檢查 | 結果 |
| --- | --- | --- |
| I. 命令列優先 | add／list／total 子指令；錯誤走 stderr＋非 0 結束碼 | ✅ |
| II. 測試先行 | 每個故事先寫 pytest；測試用 `tmp_path`，不碰真實檔 | ✅ |
| III. 簡單資料儲存 | 單一 JSON、`ensure_ascii=False`、暫存檔＋`os.replace` | ✅ |
| IV. 金額精確 | `Decimal`，JSON 中以字串保存；拒絕 ≤ 0 與 > 2 位小數 | ✅ |
| V. 保持簡單 | 只用標準函式庫；不做編輯／刪除 | ✅ |

Phase 1 設計完成後重新檢查：仍全數通過，無違規，Complexity Tracking 留空。

## Project Structure

### Documentation (this feature)

```text
specs/001-cli-expense-tracker/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml
src/
└── ledger/
    ├── __init__.py
    ├── __main__.py      # python -m ledger
    ├── models.py        # Expense 資料類別與輸入解析／驗證
    ├── storage.py       # JSON 讀寫（原子寫入、損毀偵測）
    ├── service.py       # add／list／total 商業邏輯
    └── cli.py           # argparse 子指令與輸出格式
tests/
├── conftest.py
├── unit/
│   ├── test_models.py
│   ├── test_storage.py
│   └── test_service.py
└── integration/
    └── test_cli.py
```

**Structure Decision**: 單一專案、src layout。模型／儲存／服務／CLI 分層，讓單元測試可直接測服務層，
整合測試以 `cli.main(argv)` 驗證完整指令行為與結束碼。

## Complexity Tracking

無違規，不需填寫。
