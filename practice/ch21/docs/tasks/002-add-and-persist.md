# Task 002：新增待辦與 localStorage 持久化

- 分支：`task/002-add-and-persist`
- 需求：F1、F4

## 內容
- `loadTodos()`／`saveTodos()`：包 try/catch，損毀或不可用時提示
- 送出表單新增待辦：trim、空白拒絕、截斷 200 字
- `render()`：以 `textContent` 渲染清單

## 驗收條件
- [ ] 輸入文字按 Enter 出現在清單，輸入框清空
- [ ] 全空白不新增，顯示提示
- [ ] 重新整理後資料仍在
- [ ] 輸入 `<b>x</b>` 顯示為純文字
- [ ] `node --check app.js` 通過
