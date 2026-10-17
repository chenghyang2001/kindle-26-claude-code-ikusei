# Task 004：篩選、計數與清除已完成

- 分支：`task/004-filter-and-count`
- 需求：F5、F6

## 內容
- 篩選按鈕：全部 / 未完成 / 已完成（`data-filter`），目前篩選加 `.active`
- `#todo-count` 顯示「剩下 N 項未完成」
- `#clear-completed` 刪除全部已完成；沒有已完成項目時停用

## 驗收條件
- [ ] 三種篩選結果正確
- [ ] 計數隨新增／勾選／刪除即時更新
- [ ] 清除已完成後只剩未完成項目
- [ ] `node --check app.js` 與 `node scripts/verify.mjs` 通過
