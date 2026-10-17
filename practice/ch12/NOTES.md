# K26 第 12 章練習：MCP Server（chrome-devtools）

> 快速 demo 模式，未經 QA／審查。

## 做了什麼

1. **加入 MCP（project scope）**

   ```bash
   env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT ...（清掉所有 CLAUDE* 變數） \
     claude mcp add --scope project chrome-devtools -- npx chrome-devtools-mcp@latest --headless < /dev/null
   ```

   產生 `.mcp.json`（`type: stdio`，指令 `npx chrome-devtools-mcp@latest --headless`）。沒有動到 user scope（已確認 `~/.claude.json` 的 `mcpServers` 裡沒有 chrome-devtools）。
2. **建立 `form.html`**：註冊表單（姓名／Email／密碼），送出時用 JS 驗證，成功就在頁面顯示「註冊成功！歡迎 姓名」，失敗顯示錯誤提示。訊息用 `textContent` 寫入，避免 XSS。
3. **背景起服務**：`python -m http.server 8765 --bind 127.0.0.1`，`curl` 確認回 200。
4. **用 `claude -p` 操作瀏覽器**

   ```bash
   env -u CLAUDE... claude -p "<步驟說明>" \
     --mcp-config .mcp.json --strict-mcp-config --dangerously-skip-permissions < /dev/null
   ```

   子 Claude 使用的 chrome-devtools 工具：

   | 步驟 | 工具 | 結果 |
   | --- | --- | --- |
   | 開頁面 | `new_page` | 開啟 form.html |
   | 改樣式 | `evaluate_script` | 按鈕背景與 h1 改成藍色 `#1e66f5` |
   | 填表 | `take_snapshot` → `fill_form` | 王小明／<xiaoming@example.com>／secret123 |
   | 送出 | `click` → `evaluate_script` 讀 `#message` | 「註冊成功！歡迎 王小明」 |
   | 截圖 | `take_screenshot`（整頁） | `screenshot.png`（31 KB） |

5. **`claude mcp list`**：chrome-devtools 顯示 `⏸ Pending approval (run claude to approve)`。
6. **關閉 http.server**：停止背景工作，確認 8765 已無人監聽。

## 結果

- `screenshot.png` 已目視確認：標題和送出按鈕是藍色、三欄已填、下方綠框顯示成功訊息。
- `claude mcp list` 的「Pending approval」是正常的：project scope 的 `.mcp.json` 會進版控，所以 Claude Code 要求在互動式 `claude` 裡手動信任一次。`claude -p` 搭配 `--mcp-config .mcp.json --strict-mcp-config` 是直接指定設定檔載入，所以不受這個核准限制。

## 和書上做法的差異

| 項目 | 書上（一般做法） | 本次 |
| --- | --- | --- |
| 操作方式 | 互動式 `claude` 裡用自然語言叫它開瀏覽器 | `claude -p` 非互動一次跑完，方便自動化 |
| 瀏覽器 | 預設會彈出 Chrome 視窗 | 加 `--headless`，不開視窗 |
| MCP 載入 | 啟動後自動讀 `.mcp.json`，第一次需核准 | `--mcp-config` + `--strict-mcp-config` 只載入這一個 server，不混入使用者其他 MCP |
| 權限 | 每次工具呼叫詢問 | `--dangerously-skip-permissions`（只在本機練習用） |
| 巢狀執行 | 不需要 | 在 Claude Code session 裡呼叫 `claude`，要先清掉 `CLAUDE*` 環境變數、加 `< /dev/null`，否則會被判定為巢狀 session 或卡在等 stdin |
| 改樣式 | 可能請 Claude 修改 HTML 原始檔 | 用 `evaluate_script` 在瀏覽器即時改 DOM，原始檔不變 |

## 三種傳輸方式（transport）

| 傳輸 | 運作方式 | 適合 | 加入範例 |
| --- | --- | --- | --- |
| **stdio** | Claude Code 在本機啟動子程序，透過標準輸入／輸出交換 JSON-RPC | 本機工具（瀏覽器、檔案系統、CLI 包裝）；本次 chrome-devtools 就是 stdio | `claude mcp add name -- npx some-mcp` |
| **SSE**（Server-Sent Events） | 連到遠端 HTTP 伺服器，伺服器用 SSE 串流推回訊息；舊版遠端傳輸，**已被標為過時** | 還沒升級的舊遠端 server | `claude mcp add --transport sse name https://example.com/sse` |
| **HTTP**（Streamable HTTP） | 一般 HTTP POST 請求，必要時回應可串流；目前推薦的遠端傳輸，支援 OAuth | 雲端服務（如 GitHub、Notion、Google 的 MCP） | `claude mcp add --transport http name https://example.com/mcp` |

## `claude mcp serve`

反過來把 **Claude Code 自己當成 MCP server**（stdio）。其他 MCP client（例如 Claude Desktop、另一個 agent）可以呼叫 Claude Code 的工具，如讀檔、編輯、執行 Bash。設定範例：

```json
{
  "mcpServers": {
    "claude-code": { "type": "stdio", "command": "claude", "args": ["mcp", "serve"] }
  }
}
```

注意：被呼叫端會直接在本機執行工具，權限確認由呼叫端負責，要小心開放的範圍。

## 檔案

- `.mcp.json`：project scope MCP 設定
- `form.html`：註冊表單
- `screenshot.png`：自動填表送出後的截圖
- `NOTES.md`：本說明
