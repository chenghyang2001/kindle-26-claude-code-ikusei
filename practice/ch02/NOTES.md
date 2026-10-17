# NOTES.md — 第 2 章練習紀錄

日期：2026-10-18

## 做了什麼

1. 寫 `ARCHITECTURE.md`，涵蓋四個主題：
   - LLM 工具呼叫（tool_use → 客戶端執行 → tool_result）
   - Agent 協作迴圈（含 sub-agent 分工）
   - 沙箱執行（權限、沙箱、hooks、工作目錄範圍）
   - 五大開發階段（探索 → 規劃 → 實作 → 驗證 → 提交）
2. 用 ASCII 圖畫出「使用者提示 → 模型 → 工具呼叫 → 結果回填 → 下一輪」迴圈，另附五階段流程小圖。
3. 寫本檔 `NOTES.md`。
4. `git add` CLAUDE.md、ARCHITECTURE.md、NOTES.md 並 commit（未 push）。

## 結果

- 三個檔案已建立並 commit 到本機 `master` 分支。
- 純文件練習，沒有程式碼，所以沒有測試要跑。

## 和書上做法的差異

- **全自動執行**：書上通常是一步一步和 Claude 對話、看它問問題再回答；這次依使用者指示全程不提問，所有選擇採用預設建議。
- **快速 demo 模式**：依專案 CLAUDE.md，沒有走 writer → QA → reviewer 的多 agent 流程，主 Claude 直接寫檔（而且全部是 `.md`，本來就不受程式碼鐵律限制）。
- **五大階段的命名**：書上的階段名稱可能略有不同；這裡用 Claude Code 官方常見的「探索、規劃、實作、驗證、提交」說法整理。
- **沙箱說明**：書上可能以示範指令為主；這裡改用表格整理各防護層，沒有實際開啟沙箱模式測試。
- **不 push**：只在本機 commit，沒有建立 GitHub repo。
