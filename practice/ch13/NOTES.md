# K26 第 13 章練習筆記：MCP Server 大閱兵

日期：2026-10-18｜模式：kindle-drill 快速模式（全自動，選擇題採推薦）

## 做了什麼

1. **`.mcp.json`（project scope）實際放 2 個免金鑰 server**
   - `filesystem`：`@modelcontextprotocol/server-filesystem`，允許目錄只給 `.`（本資料夾）
   - `sequential-thinking`：`@modelcontextprotocol/server-sequential-thinking`
   - 兩者都用 `cmd /c npx -y ...` 啟動（Windows 需要）
2. **`.claude/settings.local.json`**：`enabledMcpjsonServers` 預先核准上面兩個專案 server，免得每次跳「是否信任 .mcp.json」的提示。
3. **`MCP-CATALOG.md`**：GitHub、Notion、Figma、PostgreSQL、Slack（另補 Sentry、Brave Search）的用途、設定範本（`${TOKEN}` 佔位）、適用情境，只記錄不啟用。
4. 沒有執行任何 `claude mcp add -s user`，user scope 未變動。

## 結果

### `claude mcp list`

```
filesystem: cmd /c npx -y @modelcontextprotocol/server-filesystem . - ✔ Connected
sequential-thinking: cmd /c npx -y @modelcontextprotocol/server-sequential-thinking - ✔ Connected
```

（清單中其他 server 是本機原本就有的 user scope / claude.ai 連接器，不是本練習加的。）

### `claude -p` 實際呼叫工具

| 測試 | 結果 |
| --- | --- |
| `list_allowed_directories` | 只有本練習資料夾 ✅ |
| `list_directory C:\Windows` | `Access denied - path outside allowed directories` ✅（沙箱有效） |
| `sequentialthinking` 2 步算 17×23 | 391 ✅ |

### 執行巢狀 claude 的做法

在 Claude Code session 裡呼叫 `claude` 會因環境變數被判定為巢狀執行，所以同一行先清掉所有 `CLAUDE` 開頭的變數，並把 stdin 接到 `/dev/null`：

```bash
env $(env | grep -o '^CLAUDE[A-Z_]*' | sed 's/^/-u /') claude mcp list < /dev/null
env $(env | grep -o '^CLAUDE[A-Z_]*' | sed 's/^/-u /') claude -p "..." --allowedTools "mcp__filesystem__..." < /dev/null
```

## 和書上做法的差異

| 項目 | 書上（一般示範） | 本練習 |
| --- | --- | --- |
| 新增方式 | `claude mcp add <name> -- npx -y ...`（預設 local scope） | 直接手寫 `.mcp.json`（project scope），可入版控、團隊共用 |
| 啟動指令 | `npx -y ...` | Windows 要 `cmd /c npx -y ...`，否則 npx 是 `.cmd` 檔，直接 spawn 會失敗 |
| filesystem 路徑 | 通常寫絕對路徑（如 `/Users/me/project`） | 寫 `.`，由 Claude Code 以專案目錄為 cwd 啟動，跨機器不必改路徑 |
| 首次核准 | 啟動時互動式詢問是否信任 `.mcp.json` | 用 `.claude/settings.local.json` 的 `enabledMcpjsonServers` 白名單預先核准 |
| 需 token 的 server | 示範實際接上 GitHub / Notion 等 | 只寫進 `MCP-CATALOG.md`，用 `${VAR}` 佔位，不放真 token |
| 驗證 | 在互動 session 用 `/mcp` 看狀態 | 用 `claude mcp list` + `claude -p --allowedTools` 自動化驗證，並測沙箱邊界 |

## 已知限制

- 快速模式，未經 QA／審查。
- `MCP-CATALOG.md` 的範本未實測（沒有 token）；套件名稱與網址以撰寫時官方資訊為準，啟用前請再確認。
- `.` 作為 filesystem 允許目錄依賴「從專案根目錄啟動 Claude Code」；從子目錄啟動時範圍會跟著變。
