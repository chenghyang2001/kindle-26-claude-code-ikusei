# Quickstart: 命令列記帳小工具

## 前置

- 已安裝 uv。

## 跑測試

```bash
uv run pytest -q
```

預期：全部通過。

## 手動驗證（使用暫存資料檔，不影響真實帳本）

```bash
uv run ledger --file demo.json add 120 餐飲 --note 午餐 --date 2026-10-01
uv run ledger --file demo.json add 80 餐飲 --date 2026-10-03
uv run ledger --file demo.json add 300 交通 --date 2026-10-05
uv run ledger --file demo.json add 500 房租 --date 2026-09-30
uv run ledger --file demo.json list --month 2026-10   # 3 筆
uv run ledger --file demo.json total 2026-10          # 合計 500.00，交通 300、餐飲 200
uv run ledger --file demo.json add -5 餐飲            # 錯誤、結束碼 1
```

輸出格式見 [contracts/cli.md](./contracts/cli.md)。
