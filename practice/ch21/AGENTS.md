# AGENTS.md — 團隊與 AI 代理協作規範

本檔是所有人類開發者與 AI 代理（Claude Code、Codex 等）在本 repo 工作時都必須遵守的規範。

## 1. 工作流程

1. 腦力激盪 `docs/brainstorm.md` → PRD `docs/prd.md` → Epic `docs/epic.md` → Tasks `docs/tasks/NNN-*.md`
2. 規劃文件先在 `master` commit，之後才開始實作。
3. 一個 task 對應一個分支，做完後以 `git merge --no-ff` 合併回 `master`，保留分支歷史。
4. 不可在沒有對應 task 檔的情況下直接改程式。

## 2. 分支命名

| 類型 | 格式 | 範例 |
| --- | --- | --- |
| 任務 | `task/NNN-簡短英文描述` | `task/001-html-skeleton` |
| 修 bug | `fix/NNN-描述` | `fix/005-empty-title` |
| 文件 | `docs/描述` | `docs/update-prd` |

- 編號 `NNN` 必須對應 `docs/tasks/NNN-*.md`。
- 全小寫、單字以連字號分隔。

## 3. Commit 格式

```
<類型>(<範圍>): <繁體中文簡述>

<可選：說明為什麼這樣改>

Refs: docs/tasks/NNN-*.md
```

- 類型：`feat` 新功能、`fix` 修復、`docs` 文件、`refactor` 重構、`test` 測試、`chore` 雜項
- 範例：`feat(todo): 新增待辦項目並存入 localStorage`
- 合併 commit：`merge: 合併 task/NNN-xxx`
- 一個 commit 只做一件事；不使用 `--no-verify`；不 force push。

## 4. 測試要求

每個 task 合併前必須通過：

1. `node --check app.js`（語法檢查）
2. `node scripts/verify.mjs`（檢查 `index.html` 結構與必要元素 id）
3. 手動冒煙：瀏覽器打開 `index.html`，跑過該 task 的驗收條件

task 檔中的「驗收條件」全部打勾才可合併。

## 5. 程式碼規範

- 純 HTML + 原生 JavaScript，不引入框架與建置工具。
- 使用者輸入一律用 `textContent` 顯示，禁止 `innerHTML` 插入使用者資料（防 XSS）。
- `localStorage` 讀寫一律包 `try/catch`，資料壞掉時重設為空陣列並提示使用者。
- 註解用繁體中文，寫「為什麼」而非「做什麼」。
- 縮排 2 空格，變數 camelCase。
