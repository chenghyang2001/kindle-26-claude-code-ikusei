# Epic：Todo MVP

對應 PRD：`docs/prd.md`（F1～F6）

## 目標
交付可在瀏覽器直接開啟、資料存於 localStorage 的待辦清單 MVP。

## 任務拆解
| Task | 分支 | 內容 | 對應需求 | 依賴 |
| --- | --- | --- | --- | --- |
| [001](tasks/001-html-skeleton.md) | `task/001-html-skeleton` | HTML 骨架、樣式、驗證腳本 | 非功能 | — |
| [002](tasks/002-add-and-persist.md) | `task/002-add-and-persist` | 新增、渲染、localStorage 存取 | F1, F4 | 001 |
| [003](tasks/003-toggle-and-delete.md) | `task/003-toggle-and-delete` | 切換完成、刪除 | F2, F3 | 002 |
| [004](tasks/004-filter-and-count.md) | `task/004-filter-and-count` | 篩選、計數、清除已完成 | F5, F6 | 003 |

依賴為線性，依序執行（不平行）。

## 完成定義（DoD）
- 4 個 task 都合併回 master（`--no-ff`）
- `node --check app.js` 與 `node scripts/verify.mjs` 通過
- PRD 邊界案例表全部處理
