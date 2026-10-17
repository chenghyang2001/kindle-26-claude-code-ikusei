# K26 第 18 章：Claude Code 網頁版（Claude Code on the Web）筆記

> 快速演練：網頁操作要登入 claude.ai，本次**沒有實際操作**，以下是流程整理與對照。

## 1. 整體流程一覽

```
claude.ai/code 登入
   ↓
連 GitHub（安裝 Claude GitHub App，選擇授權的 repo）
   ↓
選 repo + 選「環境」（環境設定：網路等級、環境變數、setup script）
   ↓
輸入任務 → Anthropic 雲端開一個隔離 container，clone repo
   ↓
跑 setup script（裝依賴）→ Claude 在 container 內讀碼、改碼、跑測試
   ↓
產出：推到新分支（claude/xxx）→ 一鍵建立 PR
   ↓
（需要時）teleport 回本機 CLI 接手
```

## 2. 連 GitHub

- 在 claude.ai/code 首次使用時，依指示安裝 **Claude GitHub App**。
- 可以只授權部分 repo（建議最小權限，只開要用的 repo）。
- 雲端只能存取已授權的 repo；私有 repo 也可以，但要在 App 設定中勾選。
- 推送是透過 GitHub proxy 完成，憑證不會直接放進 container。

## 3. 雲端 container

- 每個任務（session）一個**隔離的虛擬環境**，由 Anthropic 管理。
- 預先裝好常見語言與工具（Python、Node.js、Go、Rust、Java 等常用 runtime 與套件管理器）。
- repo 會被 clone 進去，Claude 在裡面自由執行指令、跑測試，不會碰到本機。
- session 結束後環境不保留；要保留的東西必須 commit／push。
- 可以同時開多個任務平行跑，每個都是獨立 container。

## 4. 環境設定與環境變數

- 「環境（Environment）」是一組可重複使用的設定，建立任務時選用。內容包括：
  - 名稱
  - 網路等級（見下節）
  - 環境變數（`KEY=value` 格式，類似 `.env`）
- 環境變數用來放 API endpoint、功能開關、測試用金鑰等。
- 注意：
  - 環境變數對該環境的所有任務都看得到，**不要放正式環境的機密**；能用測試金鑰就用測試金鑰。
  - repo 內的 `CLAUDE.md`、`.claude/settings.json` 一樣會生效，專案規則跟著 repo 走。

## 5. 網路等級

| 等級 | 說明 | 適用情境 |
| --- | --- | --- |
| **Limited**（預設） | 只允許白名單網域：套件來源（npm、PyPI、crates.io…）、GitHub、常見雲端／容器 registry 等 | 大多數開發任務：裝套件、跑測試 |
| **Full** | 不限制對外連線 | 需要呼叫外部 API、抓任意網站資料 |
| **No network** | 完全不能連外（GitHub 推送仍走 proxy） | 高敏感程式碼、確保沒有資料外流、依賴已預裝 |

取捨：網路越開放越方便，但被提示詞注入（例如讀到惡意檔案）後外流資料的風險也越高。預設 Limited 是平衡點。

## 6. Setup script

- 在環境設定中填一段 bash 腳本，**container 啟動、Claude 開工前**自動執行。
- 常見用途：安裝依賴、裝系統套件、準備測試資料庫。

```bash
#!/bin/bash
# 範例：安裝專案依賴
pip install -r requirements.txt
npm ci
```

- 與 SessionStart hook 的差異：setup script 屬於「環境」，只在雲端跑；hook 屬於 repo，本機與雲端都會跑。若 hook 只想在雲端跑，可用環境變數 `CLAUDE_CODE_REMOTE` 判斷。
- setup script 失敗時 session 會無法正常開始，要保持簡單、可重跑。

## 7. 產出分支與 PR

- Claude 完成後把改動 commit 到新分支（通常是 `claude/` 開頭），推到 GitHub。
- 網頁上可以看 diff、直接留言要求修改，再請 Claude 繼續改。
- 滿意後按「Create PR」建立 PR，後續照一般 code review / CI 流程合併。
- 好處：雲端改動一定經過分支 + PR，不會直接動到 main。

## 8. Teleport 回本機 CLI

- 網頁版做到一半，想在本機繼續（例如要用本機工具、看本地 GUI、跑需要硬體的測試）：
  - 網頁上按「Open in CLI」，複製指令；或在本機 repo 目錄執行 `claude --teleport`（可帶 session ID，或互動式選擇）。
- 會把雲端 session 的對話紀錄和分支一起帶到本機，接續工作。
- 前提：本機在同一個 repo、工作樹乾淨、登入同一個 claude.ai 帳號。
- 反方向：本機 CLI 也可以把任務丟到雲端跑（以 `&` 開頭的提示，或 `--remote`）。

## 9. 網頁版 vs CLI 版取捨對照表

| 面向 | 網頁版（雲端） | CLI 版（本機） |
| --- | --- | --- |
| 執行位置 | Anthropic 雲端隔離 container | 自己的電腦 |
| 啟動門檻 | 有瀏覽器就能用，手機也可派任務 | 要安裝 CLI、設定環境 |
| 平行度 | 輕鬆開多個任務同時跑 | 要自己開多個終端或 worktree |
| 本機資源 | 不吃本機 CPU／記憶體，電腦關機也能跑 | 佔用本機，關機就停 |
| 存取範圍 | 只有已授權的 GitHub repo | 本機所有檔案、工具、內網服務 |
| 環境客製 | 環境設定 + setup script，每次重建 | 完全自訂，狀態一直保留 |
| 網路 | Limited／Full／No network 三級可控 | 跟本機網路一樣，沒有內建限制 |
| MCP／本機工具 | 受限（無法用本機 MCP、瀏覽器、GUI） | 全部可用 |
| 安全隔離 | 高：出事只影響 container | 較低：靠權限模式與 hooks 把關 |
| 產出方式 | 一律分支 + PR，方便審查 | 自由：直接 commit、push 或不 commit |
| 互動節奏 | 適合「丟出去、等結果」的非同步任務 | 適合需要密集來回、即時除錯的任務 |
| 適合任務 | 明確的 bug 修復、小功能、測試補齊、文件更新、批次任務 | 探索性開發、需本機環境的工作、跨系統整合 |
| 接續 | 可 teleport 回本機 | 可丟到雲端跑 |

**一句話總結**：任務明確、可以在乾淨環境跑完的，丟網頁版平行處理；需要本機工具或頻繁互動的，留在 CLI。兩者用 teleport 互通。
