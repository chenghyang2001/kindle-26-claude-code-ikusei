# MCP Server 型錄（需要金鑰／連線字串，只記錄、不啟用）

> K26 第 13 章「MCP Server 大閱兵」練習。以下 server 都需要 token 或帳密，**本專案沒有實際放進 `.mcp.json`**。
> 範本中的 `${TOKEN}` 類佔位會由 Claude Code 從**環境變數**展開（支援 `${VAR}` 與 `${VAR:-預設值}`），
> 真正的值請放在系統環境變數或不入版控的地方，**絕對不要把 token 直接寫進 `.mcp.json` 再 commit**。
>
> Windows 注意：本機執行 `npx` 型 server 時，`command` 要寫成 `"cmd"`、`args` 前面加 `"/c", "npx"`（本專案 `.mcp.json` 就是這樣寫）。下面範本為了易讀寫成跨平台的 `npx`，Windows 上請自行包一層。

## 總覽

| Server | 類型 | 需要的金鑰 | 一句話用途 |
| --- | --- | --- | --- |
| GitHub | 遠端 HTTP | GitHub PAT | 讀寫 issue / PR / 程式碼搜尋 |
| Notion | 遠端 HTTP（OAuth） | 瀏覽器登入授權 | 讀寫 Notion 頁面與資料庫 |
| Figma | 遠端 HTTP／本機 Dev Mode | Figma 帳號授權或 API token | 讀設計稿、取得元件與樣式轉程式碼 |
| PostgreSQL | 本機 stdio | 資料庫連線字串 | 讓 Claude 查 schema、跑 SQL |
| Slack | 本機 stdio | Bot token + Team ID | 讀頻道訊息、發訊息 |
| Sentry | 遠端 HTTP（OAuth） | 瀏覽器登入授權 | 查錯誤事件、堆疊追蹤 |
| Brave Search | 本機 stdio | Brave API key | 網頁搜尋 |

---

## 1. GitHub

- **用途**：查 / 開 issue、讀 PR diff、留 review、搜尋程式碼、建分支。
- **設定範本**（官方遠端 server）：

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

- **適用情境**：PR 審查流程自動化、從 issue 直接開工、跨 repo 搜尋範例程式碼。
- **安全提醒**：PAT 給最小權限（fine-grained token、只勾需要的 repo）。

## 2. Notion

- **用途**：搜尋、讀取、建立、更新 Notion 頁面與資料庫。
- **設定範本**（官方遠端 server，OAuth，不用貼 token）：

```json
{
  "mcpServers": {
    "notion": {
      "type": "http",
      "url": "https://mcp.notion.com/mcp"
    }
  }
}
```

  加入後在 Claude Code 裡執行 `/mcp` → 選 notion → 瀏覽器登入授權。
  若要用 Integration token（自架版）：

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": { "NOTION_TOKEN": "${NOTION_TOKEN}" }
    }
  }
}
```

- **適用情境**：把會議紀錄 / 規格書寫進 Notion、從 Notion 任務資料庫讀需求後開工。

## 3. Figma

- **用途**：讀取設計稿的 frame、元件、變數（色彩 / 字級），讓 Claude 依設計稿產生前端程式碼。
- **設定範本**（官方遠端 server，OAuth）：

```json
{
  "mcpServers": {
    "figma": {
      "type": "http",
      "url": "https://mcp.figma.com/mcp"
    }
  }
}
```

  或 Figma 桌面版 Dev Mode 本機 server：`"type": "http", "url": "http://127.0.0.1:3845/mcp"`。
  社群版（需 API token）：

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--stdio"],
      "env": { "FIGMA_API_KEY": "${FIGMA_API_KEY}" }
    }
  }
}
```

- **適用情境**：設計稿轉 React/Tailwind 元件、檢查實作與設計稿是否一致。

## 4. PostgreSQL

- **用途**：列出資料表 / schema、執行 SQL 查詢、協助寫 migration。
- **設定範本**：

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"]
    }
  }
}
```

  `DATABASE_URL` 範例格式：`postgresql://<user>:<password>@<host>:5432/<db>`（放環境變數）。

- **適用情境**：資料分析、除錯「為什麼這筆資料不見」、設計 schema 時對照現況。
- **安全提醒**：連線帳號給**唯讀權限**；官方參考實作已被標為 archived，正式使用可考慮社群維護版或 Neon / Supabase 官方 MCP。

## 5. Slack

- **用途**：列頻道、讀歷史訊息與討論串、發訊息、加表情回應。
- **設定範本**：

```json
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
        "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
      }
    }
  }
}
```

- **適用情境**：彙整頻道討論成摘要、部署完成自動通知、從客訴頻道整理 bug 清單。
- **安全提醒**：Bot 只加入需要的頻道；發訊息屬「對外動作」，先確認再送。

## 6. Sentry（補充）

- **用途**：查詢錯誤事件、堆疊追蹤、影響使用者數。
- **設定範本**：`{"mcpServers":{"sentry":{"type":"http","url":"https://mcp.sentry.dev/mcp"}}}`（OAuth）
- **適用情境**：「這個錯誤從什麼時候開始？」→ 直接對照程式碼修 bug。

## 7. Brave Search（補充）

- **用途**：網頁搜尋，補 Claude 知識截止日之後的資訊。
- **設定範本**：

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    }
  }
}
```

- **適用情境**：查最新套件版本、錯誤訊息搜尋。注意 rate limit（約 3 req/s）。

---

## 啟用時的三個 scope 怎麼選

| scope | 存放位置 | 適合 |
| --- | --- | --- |
| local（預設） | `~/.claude.json` 中該專案區塊 | 只有自己、只在這個專案用，含個人 token |
| project | 專案根目錄 `.mcp.json`（入版控） | 團隊共用；token 一律用 `${VAR}` |
| user | `~/.claude.json` 全域 | 自己所有專案都要用 |

本練習只用 **project scope**（`.mcp.json`），沒有動 user scope。
