# Task 001：HTML 骨架與驗證腳本

- 分支：`task/001-html-skeleton`
- Epic：`docs/epic.md`

## 內容
- 建立 `index.html`：標題、輸入表單（`#new-todo-form`、`#new-todo-input`）、清單（`#todo-list`）、狀態列（`#todo-count`、篩選 `#filters`、`#clear-completed`）、提示區（`#message`）
- 建立 `style.css`（RWD）
- 建立空的 `app.js`（以 `defer` 載入）
- 建立 `scripts/verify.mjs`：檢查 index.html 有上述元素 id、有載入 app.js 與 style.css

## 驗收條件
- [ ] `node scripts/verify.mjs` 通過
- [ ] 瀏覽器打開可看到輸入框與空清單
