# K26 第 5 章練習筆記：斜線指令系統

- 日期：2026-10-18
- 環境：Claude Code v2.1.302、Claude Max、Opus 5.5、Windows 10（Git Bash）
- 模式：kindle-drill 快速 demo 模式（教練視窗代操作練習視窗）

## 做了什麼

1. 建立極小練習 repo，只有 `hello.py`（印出 `Hello, Claude Code`）。
2. 用 `/init` 產生 `CLAUDE.md`。
3. 依序實測書上提到的斜線指令：`/help`、`/status`、`/context`、`/cost`、`/model`、`/memory`、`/compact`、`/export`、`/todos`、`/agents`、`/hooks`、`/clear`。
4. 把結果整理成 `SLASH-CHEATSHEET.md`（五類分組＋狀態標記）。

## 結果

| 指令 | 結果 |
| --- | --- |
| `/init` | 產生 `CLAUDE.md` |
| `/help` | General／Commands／Custom commands 三頁，附快捷鍵 |
| `/status` | Settings／Status／Config／Usage／Stats 五個分頁 |
| `/context` | 分項列出系統提示、工具、記憶檔、skills 的 token 用量 |
| `/cost` | 導向 `/usage`，顯示用量來源分析 |
| `/model` | 開出選單，只看不切 |
| `/memory` | 列出 Auto-memory 與 User／Project 記憶檔，取消未編輯 |
| `/compact` | 壓縮成功 |
| `/export ch05-export.md` | 匯出約 29 KB 的 Markdown |
| `/todos` | Unknown command |
| `/agents` | 「The /agents wizard has been removed」 |
| `/hooks` | 唯讀清單，31 hooks／7 events |
| `/clear` | 清空對話 |

統計：實測 12、已移除 2、因限制略過 7、未測 9（明細見 `SLASH-CHEATSHEET.md`）。

## 和書上的差異

| 項目 | 書上 | v2.1.302 實測 |
| --- | --- | --- |
| `/cost` | 顯示本次 session 花費 | 導向 `/usage`，改成用量與來源分析（訂閱制下看的是額度，不是金額） |
| `/status` | 單頁狀態資訊 | 擴充成 Settings／Status／Config／Usage／Stats 分頁，`/config`、`/usage` 的內容也能在這裡看 |
| `/todos` | 列出待辦清單 | 已移除，回 Unknown command |
| `/agents` | 互動式精靈建立／管理 subagent | 精靈已移除；subagent 改由 `.claude/agents/*.md` 檔案管理 |
| `/hooks` | 互動式新增／編輯 hook | 變成唯讀清單；新增或修改 hook 要直接改 `settings.json` |
| `/memory` | 開啟 CLAUDE.md 編輯 | 多了 Auto-memory 項目（自動記憶），並分 User／Project 層 |
| `/help` | 指令列表 | 分三頁，多了 Custom commands（自訂指令與 skills） |

## 心得

- 版本更新很快，書上的指令有些已改名、合併或移除，實測比照抄書可靠。
- 整體方向是「互動式精靈 → 檔案設定」：`/agents`、`/hooks` 都改成直接編輯檔案。
- `/context` 很適合判斷什麼時候該 `/compact` 或 `/clear`。

## 已知限制

- 快速模式，沒有跑 QA／審查。
- 帳號、付費、全域設定相關指令（`/login`、`/logout`、`/upgrade`、`/config` 修改、`/statusline`、`/doctor`、`/install-github-app`）刻意不執行。
- 審查類指令（`/review`、`/security-review`、`/pr-comments`）需要 GitHub remote 和 PR，本 repo 沒有，所以未測。
