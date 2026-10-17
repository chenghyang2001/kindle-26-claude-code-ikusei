# K26 第 4 章練習筆記：從現有專案開始玩起

日期：2026-10-18　分支：`feature/demo`

## 做了什麼

1. **了解專案**：讓 Claude 讀程式碼，回答「這個專案是做什麼的」。
   這個 repo 主要是一個法語單字學習 App（Express + SQLite，有單字測驗和閃卡複習兩個功能），另外附了 `countdown-timer/` 和 `user-comments/` 兩個獨立小專案。
2. **追蹤完整流程**：挑「翻牌複習」這個操作，從前端追到資料庫：
   `flashcard.html` → `js/flashcard.js`（`init` / `showCard` / `handleReview`）→ `PATCH /api/words/:id/review` → `api/words.js` → SQLite 的 `words` 表。
   另外用暫存資料庫實際打 API，確認「認識」會讓複習間隔加倍、「不認識」會重設為 1 天。
3. **畫 ASCII 流程圖**：把上面的流程畫成一張前端 → 後端 → 資料庫的圖，另附一張卡片複習間隔變化圖。
4. **實際啟動 App**：`npm install --omit=dev` → `npm run init` → `PORT=3456 npm start`，用 curl 驗證首頁回傳 200，驗證完關掉伺服器。
5. **`/init` 產生 CLAUDE.md**：保留原本的內容，補上常用指令、三個應用的組成、主 App 架構重點、規格文件導覽。
6. **加一條記憶**：在 CLAUDE.md 加上「總是用 npm run 指令啟動，不要直接 node」。
   為了讓這條規則也適用於子專案，替 `countdown-timer/`、`user-comments/` 的 `package.json` 補上 `start`、`test` script。
7. **收尾**：確認 `.gitignore` 已排除 `node_modules/`，寫這份筆記，在 `feature/demo` 分支 commit（沒有 push）。

## 結果

| 項目 | 結果 |
| --- | --- |
| 主 App 測試 `npm test` | 19 / 19 通過 |
| `countdown-timer` 測試 | 17 / 17 通過 |
| `user-comments` 測試 | 29 / 29 通過 |
| 主 App 首頁 `GET /` | HTTP 200 |
| `countdown-timer` 用 `npm start` 啟動 | 首頁 HTTP 200 |

追蹤流程時發現、但這次**沒有修**的問題：

- 日期用 SQLite 的 `date('now')`，是 UTC 時間；台灣早上 8 點前的「今天」會算成前一天。
- 閃卡正面的「詞性」欄位其實顯示的是 CEFR 等級（A1/A2…），資料表沒有詞性欄位。
- 複習間隔的計算公式在 `api/quiz.js` 和 `api/words.js` 各寫了一份。
- 閃卡頁直接呼叫 `fetch`，沒有使用測驗頁共用的 `js/api.js`。
- 閃卡功能的 PRD 規劃另建 `flashcard_reviews` 表，實作卻是把欄位直接放在 `words` 表。
- `specs/002-countdown-timer/plan.md` 寫的 `node --test tests/` 在 Node 24 會失敗，要用 `tests/*.test.js`。

## 和書上做法的差異

| 項目 | 書上 | 這次練習 |
| --- | --- | --- |
| 練習用的現有專案 | 作者提供的 **fingerprints** 範例 repo | 改用自己前幾章做出來的 **epic-flashcard-review**（法語單字 App），複製一份當起點（commit `77c8ba0`） |
| 原因 | — | 用自己做過的專案，比較容易判斷 Claude 的說明對不對；而且這個專案本身就有規格文件、測試和多個子專案，夠「現有」 |
| 啟動前準備 | 依 fingerprints 的 README | 這個專案沒有 README；改用 `npm install --omit=dev` 跳過 puppeteer，並多跑一次 `npm run init` 建立資料庫 |
| CLAUDE.md | `/init` 從零產生 | 專案原本就有 CLAUDE.md（spec-kit 區塊＋本專案例外），所以是保留原內容再補充 |
| 執行方式 | 逐步手動操作 | 全自動模式：所有選擇採用 Claude 的建議，不中途詢問 |
