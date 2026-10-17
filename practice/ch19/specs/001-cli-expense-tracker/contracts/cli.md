# CLI Contract: `ledger`

全域選項：`--file PATH`（資料檔位置，見 research.md §4）。

結束碼：`0` 成功；`1` 資料／輸入錯誤（訊息寫到 stderr，前綴 `錯誤：`）；`2` 參數語法錯誤（argparse 預設）。

## `ledger add AMOUNT CATEGORY [--note TEXT] [--date YYYY-MM-DD]`

stdout：

```text
已新增 #1：2026-10-01  餐飲  120.00  午餐
```

## `ledger list [--month YYYY-MM]`

stdout（依日期、再依 id 排序）：

```text
#1  2026-10-01  餐飲  120.00  午餐
#2  2026-10-05  交通  300.00
```

無資料時輸出 `目前沒有紀錄`。

## `ledger total YYYY-MM`

stdout：

```text
2026-10 合計：500.00
  交通  300.00
  餐飲  200.00
```

無資料時只輸出 `2026-10 合計：0.00`。
