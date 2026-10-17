# NOTES：K26 第 21 章練習——工業化流程開發 AI 專案

## 做了什麼

1. **AGENTS.md**：定下團隊規範——分支命名（`task/NNN-xxx`、`fix/NNN-xxx`）、commit 格式（`類型(範圍): 繁中簡述` + `Refs:`）、合併前測試要求（`node --check`、`scripts/verify.mjs`、手動冒煙）、安全規則（只用 `textContent`、localStorage 包 try/catch）。
2. **規劃文件鏈**（先在 master 單獨 commit）：
   - `docs/brainstorm.md`：發散 10 個點子 → 收斂 MVP 6 項，列出風險
   - `docs/prd.md`：需求 F1～F6、資料模型、非功能需求、邊界案例表
   - `docs/epic.md`：拆成 4 個 task、依賴關係、完成定義
   - `docs/tasks/001～004-*.md`：每個 task 的內容與驗收條件
3. **依 task 實作**，每個 task 一個分支，完成後 `git merge --no-ff` 回 master：
   - `task/001-html-skeleton`：`index.html`、`style.css`、空的 `app.js`、`scripts/verify.mjs`
   - `task/002-add-and-persist`：新增待辦、localStorage 讀寫與容錯
   - `task/003-toggle-and-delete`：勾選完成、刪除（事件委派）
   - `task/004-filter-and-count`：篩選、未完成計數、清除已完成
   - 另有兩個修正分支：`fix/003-duplicate-listener`、`fix/005-storage-warning-cleared`

## 結果

- master 歷史：1 個規劃 commit + 6 個 `--no-ff` 合併（4 task + 2 fix），`git log --graph` 可清楚看到每個分支。
- 驗證：
  - `node --check app.js` ✅
  - `node scripts/verify.mjs`（檢查 7 個必要元素 id、3 個篩選按鈕、資源載入、`lang`）✅
  - 額外冒煙測試（極簡假 DOM 用 `vm` 執行 app.js，10 項）✅：新增／trim／XSS、空白拒絕、勾選、計數、三種篩選、刪除、重新載入持久化、清除已完成、損毀資料容錯、localStorage 停用提示。測試腳本放在 session 暫存區，沒有進 repo。
- 使用方式：直接用瀏覽器開 `index.html`。

### 過程中抓到的兩個 bug

| bug | 原因 | 怎麼發現 |
| --- | --- | --- |
| 每新增一筆就多綁一次清單點擊監聽器，勾選觸發偶數次而抵銷 | task 003 用字串替換插入程式碼，`render();` 錨點同時命中了表單處理器內縮排的那一行 | 做 task 004 時替換斷言數量不對（預期 1，實得 6）才察覺 |
| localStorage 停用時「無法儲存」警告立刻被清掉 | `addTodo` 在 `saveTodos()` 之後才 `showMessage('')` | 冒煙測試第 10 項失敗 |

兩者 `node --check` 與 HTML 結構檢查都抓不到——**語法檢查不等於功能驗證**，這是本次最大的收穫。依 AGENTS.md 開 `fix/` 分支修正，而不是改寫已合併的歷史。

## GitHub Issues 同步步驟（只記錄，未實際執行）

書上流程會把 Epic 與 Tasks 同步成 GitHub Issues，讓團隊在 Issues 上追蹤。若要做，步驟如下：

```bash
# 1. 建立遠端 repo 並推送
gh repo create chenghyang2001/k26-ch21-practice --public --source . --push

# 2. 建立標籤
gh label create epic --color 5319e7
gh label create task --color 0e8a16

# 3. Epic 開成一個 issue
gh issue create --title "Epic：Todo MVP" --body-file docs/epic.md --label epic

# 4. 每個 task 開一個 issue，內文用 task 檔（記下回傳的 issue 編號）
for f in docs/tasks/*.md; do
  gh issue create --title "$(head -1 "$f" | sed 's/^# //')" --body-file "$f" --label task
done

# 5. 在 Epic issue 內文加上 task 清單（- [ ] #2 ...）建立父子關聯
# 6. 之後 commit 的 Refs: 改寫成 "Refs: #N"，PR 內文寫 "Closes #N"，合併時自動關閉 issue
```

## 和書上做法的差異

| 項目 | 書上（工業化流程） | 本練習 |
| --- | --- | --- |
| 規劃產生方式 | 用專用指令／agent 逐步產生 brainstorm → PRD → epic → tasks，每步讓人審閱 | 一次手寫全部規劃文件，沒有逐步停下審閱（全自動快速模式） |
| Issues 同步 | 把 epic／tasks 推成 GitHub Issues，以 issue 編號追蹤 | 只把步驟寫在本檔，未建 repo、未同步 |
| 合併方式 | 通常走 PR + code review 再合併 | 本機 `git merge --no-ff`，沒有 PR 與審查 |
| 平行開發 | 獨立 task 可用 worktree 或多個 agent 平行做 | 4 個 task 線性依賴，依序在同一工作目錄做 |
| 測試 | 通常有正式測試框架與 CI | `node --check` + 自製結構檢查 + 一次性冒煙測試，無 CI |
| 推送 | push 到遠端 | 依指示不 push |
