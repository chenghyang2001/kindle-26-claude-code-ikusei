# Data Model: 命令列記帳小工具

## Expense（支出紀錄）

| 欄位 | 型別 | 規則 |
| --- | --- | --- |
| `id` | int | 從 1 起遞增，新增時 = 目前最大 id + 1 |
| `date` | date（ISO `YYYY-MM-DD`） | 必須是合法日期；未指定時為今天 |
| `amount` | Decimal（JSON 存字串） | > 0，至多 2 位小數，存成 2 位（`"120.00"`） |
| `category` | str | 去頭尾空白後不可為空 |
| `note` | str | 可為空字串 |

## Ledger（帳本檔）

```json
{
  "version": 1,
  "expenses": [
    {"id": 1, "date": "2026-10-01", "amount": "120.00", "category": "餐飲", "note": "午餐"}
  ]
}
```

- 檔案不存在 → 視為空帳本。
- JSON 解析失敗、缺 `expenses`、欄位型別錯 → 拋出 `LedgerError`（CLI 轉成錯誤訊息＋結束碼 1），不覆寫原檔。

## 衍生資料

- **MonthlyTotal**：`month`（`YYYY-MM`）、`total`（Decimal）、`by_category`（dict[str, Decimal]，依金額由大到小）。
