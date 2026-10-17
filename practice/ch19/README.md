# ledger — 命令列記帳小工具

K26 第 19 章練習：用 GitHub Spec Kit 規格驅動開發（constitution → specify → plan → tasks → implement）做出的小工具。
規格文件在 `specs/001-cli-expense-tracker/`。

## 安裝與測試

```bash
uv sync
uv run pytest -q
```

## 用法

```bash
uv run ledger add 120 餐飲 --note 午餐 --date 2026-10-01   # 新增（日期省略 = 今天）
uv run ledger list                                         # 列出全部
uv run ledger list --month 2026-10                         # 只列某月
uv run ledger total 2026-10                                # 月合計＋類別小計
```

## 資料檔位置

優先序：`--file PATH` > 環境變數 `LEDGER_FILE` > `~/.ledger/ledger.json`。
格式為 UTF-8 JSON，金額以字串保存（例 `"120.00"`）避免浮點誤差。
