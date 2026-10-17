# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/002-countdown-timer/plan.md
<!-- SPECKIT END -->

> 上面 SPECKIT 區塊由 `.specify/extensions/agent-context/` 的腳本自動維護，不要手動改。

## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。

## 記憶

- 總是用 npm run 指令啟動，不要直接 node。（主 App 和兩個子專案都有 `start`／`test` script；`npm start`、`npm test` 是 `npm run start`、`npm run test` 的簡寫，可以照用。）

## 專案組成

一個 repo 裡有**三個互相獨立的 Node.js 應用**，各自有自己的啟動方式與資料庫，彼此不共用程式碼：

| 目錄 | 內容 | 技術 | Port | 資料庫 |
| --- | --- | --- | --- | --- |
| 根目錄 | 法語單字學習 App（測驗＋閃卡複習） | CommonJS + Express | `PORT` 或 3000 | `data/french-quiz.db`（gitignored） |
| `countdown-timer/` | 倒數計時器 | ESM + `node:http`，無 Express | 3000（寫死） | `countdown-timer/countdown.db` |
| `user-comments/` | 文章留言／回覆 | ESM + `node:http`，無 Express | 3001（寫死） | `user-comments/comments.db`（已進版控） |

三者都用 Node 內建的 `node:sqlite`（`DatabaseSync`，同步 API），需要 Node ≥ 22.5；本機是 Node 24，啟動時的 `ExperimentalWarning` 可以忽略。`countdown-timer` 和主 App 預設都用 3000，同時跑主 App 要設 `PORT`。

## 常用指令

主 App（在根目錄）：

```bash
npm install --omit=dev      # 只裝 express；puppeteer 只有 test-scenario-g.mjs 會用到
npm run init                # 建 data/french-quiz.db（schema + fallback_words），首次必跑
npm run seed                # 灌測試單字（會先 DELETE FROM words 清空！）
PORT=3456 npm start         # 啟動 → http://localhost:3456

npm test                                                    # 全部測試（node:test）
node --no-warnings --test tests/srs.test.js                 # 單一檔案
node --no-warnings --test --test-name-pattern="T025a" tests/srs.test.js   # 單一測試
```

子專案（一定要先 `cd` 進目錄，資料庫檔名是相對於執行目錄建立的）：

```bash
npm start    # 啟動
npm test     # 測試
```

注意：`specs/002-countdown-timer/plan.md` 寫的 `node --test tests/` 在 Node 24 會失敗（會把資料夾當成模組載入），一定要用 `tests/*.test.js`（子專案的 `npm test` 已照這樣寫）。

沒有 build、lint 步驟，前端是純靜態檔。

## 主 App 架構

- `server.js` 掛兩個 router：`/api/quiz` → `api/quiz.js`、`/api/words` → `api/words.js`，其餘由 `public/` 提供靜態檔；未知路由回 JSON 404，錯誤統一回 JSON 500。
- `api/db.js` 的 `getDb()` 是**單例**連線，路徑讀 `DB_PATH` 環境變數（預設 `data/french-quiz.db`），檔案不存在會直接 throw。但 `db/init.js` 和 `db/seed-test.js` **寫死**路徑、不讀 `DB_PATH`。
- 資料表見 `db/schema.sql`：`words`（含 SRS 欄位 `srs_interval`、`next_review_at`）、`fallback_words`（測驗干擾選項的備用字庫）、`quiz_sessions` / `quiz_questions`。

### 兩條使用者流程都會改 `words` 的 SRS 欄位

| 流程 | 前端 | 後端 | 何時寫回 SRS |
| --- | --- | --- | --- |
| 單字測驗（4 選 1） | `public/index.html` + `js/quiz.js`，透過 `js/api.js` 的 `window.QuizAPI` 呼叫 | `api/quiz.js` | 一場測驗作答完畢時 `updateSrsForSession()` 批次更新 |
| 閃卡複習 | `public/flashcard.html` + `js/flashcard.js`（ESM，直接用 `fetch`，**沒有**走 `QuizAPI`） | `GET /api/words?due=true` 取佇列；`PATCH /api/words/:id/review` 逐張寫回 | 每按一次「認識／不認識」 |

**SRS 規則寫了兩份**：`api/quiz.js` 的 `computeNewInterval()`，以及 `api/words.js` 的 PATCH handler 內聯同一個公式（答對 ×2、上限 30 天，答錯重設為 1）。改規則時兩處要一起改。

其他非顯而易見的行為：

- 測驗至少要 10 個單字才能開始（`/readiness`、`POST /sessions` 都會檢查）；干擾選項分三層取：同 CEFR 的 `words` → 同 CEFR 的 `fallback_words` → 任意 `fallback_words`。
- 所有日期都用 SQLite 的 `date('now')`，也就是 **UTC**。台灣時間早上 8 點前的「今天」會落在前一天。
- `computeNewInterval` 是掛在 router 物件上匯出的（`router.computeNewInterval`），`tests/srs.test.js` 靠這個直接測純函式。
- `tests/quiz.test.js` 在 `require` 路由**之前**先把 `DB_PATH` 設成暫存檔，再自己起 HTTP server 測試，不會碰到 `data/` 的正式資料。新增整合測試要沿用這個順序，否則 `getDb()` 單例會連到正式資料庫。
- `test-scenario-g.mjs` 是 Puppeteer 端對端煙霧測試，裡面寫死了另一個專案的 scratchpad 路徑和 `localhost:3000`，在這個 repo 不能直接跑。

## 規格與需求文件

這個 repo 同時留著三套規格驅動開發工具的產出，找需求或設計時依功能對應：

- `specs/NNN-*/`（spec-kit，`.specify/`）：`spec.md` → `plan.md` → `tasks.md`，加上 `contracts/api.md`、`data-model.md`。`001-vocab-quiz` 對應主 App 的測驗，`002-countdown-timer` 對應 `countdown-timer/`。
- `.claude/prds/` + `.claude/epics/`（ccpm skill）：閃卡複習功能的 PRD 與拆解任務。PRD 規劃另建 `flashcard_reviews` 表，實作卻是直接把欄位放在 `words` 上，以程式碼為準。
- `.claude/specs/user-comments/`（spec-workflow）：`user-comments/` 的 requirements／design／tasks，配合 `.claude/commands/user-comments/task-N.md`。
