# K26 第 18 章練習紀錄（Claude Code 網頁版）

## 做了什麼

- 以快速 demo 模式完成，全自動執行、不提問。
- 寫了 `WEB-NOTES.md`，整理網頁版流程：
  1. 連 GitHub（Claude GitHub App）
  2. 雲端 container
  3. 環境設定與環境變數
  4. 網路等級 Limited／Full／No network
  5. setup script
  6. 產出分支與 PR
  7. teleport 回本機 CLI
  8. 網頁版 vs CLI 版取捨對照表
- 把 `CLAUDE.md`、`WEB-NOTES.md`、`NOTES.md` 加入 git 並在本機 commit（沒有 push）。

## 結果

- 兩份筆記完成，已在本機 commit。
- 沒有寫任何程式碼，也沒有建立 GitHub repo。

## 和書上做法的差異

| 書上做法 | 本次做法 | 原因 |
| --- | --- | --- |
| 實際登入 claude.ai/code、安裝 GitHub App | 略過，只整理流程 | 需要登入網頁，快速演練不做實際操作 |
| 實際建立環境、設網路等級與環境變數、寫 setup script | 只在筆記中說明設定方式與範例 | 同上 |
| 實際派任務、看雲端產生分支並開 PR | 未執行，僅描述流程 | 沒有遠端 repo，也不 push |
| 實際用 `claude --teleport` 把 session 拉回本機 | 未執行，僅記錄指令與前提 | 沒有雲端 session 可拉 |

## 已知限制

- 筆記內容依本人對 Claude Code 網頁版的了解整理，未經實機操作驗證；介面按鈕名稱、白名單網域等細節可能隨版本變動，實際使用時以官方文件為準。
