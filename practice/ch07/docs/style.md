# 程式風格指南（docs/style.md）

> 本檔由 `CLAUDE.md` 以 `@docs/style.md` 匯入。

- Python 縮排 4 個空格，命名用 snake_case；常數全大寫。
- 每行不超過 100 字元。
- 函式不超過 30 行，巢狀不超過 3 層（優先使用 guard clause 提前 return）。
- 讀寫檔案一律指定 `encoding="utf-8"`。
- 不寫裸 `except:`，要捕捉具體例外並輸出錯誤訊息。
- 不硬編碼使用者路徑，改用 `pathlib.Path.home()`。
