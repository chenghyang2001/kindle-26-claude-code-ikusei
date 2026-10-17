# K26 第 7 章練習筆記：CLAUDE.md 與記憶體管理

## 做了什麼

| 檔案 | 用途 | 進版控 |
| --- | --- | --- |
| `CLAUDE.md` | 保留原有「本專案例外」，追加專案規則（繁中註解、測試放 `tests/`），最後用 `@docs/style.md` 匯入風格指南 | ✅ |
| `docs/style.md` | 程式風格（縮排、命名、行寬、函式長度、編碼、例外處理、路徑） | ✅ |
| `CLAUDE.local.md` | 個人偏好（回覆要簡短、用繁中） | ❌（已加入 `.gitignore`） |
| `.gitignore` | 排除 `CLAUDE.local.md`、`.claude/settings.local.json` 與當機垃圾檔 | ✅ |
| `verify.txt` | `claude -p` 驗證輸出 | ✅ |

## 驗證方式與結果

在 Claude Code session 裡呼叫子 `claude`，先把所有 `CLAUDE` 開頭的環境變數清掉（避免被判定為巢狀 session），stdin 接 `/dev/null`（避免等待輸入）：

```bash
env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT -u CLAUDE_CODE_SESSION_ID ...（其餘 CLAUDE_* 同理） \
  claude -p "列出你目前看到的專案規則，分別說明來自哪個檔案" < /dev/null > verify.txt
```

結果（見 `verify.txt`）：三個來源都被正確辨識——
1. `CLAUDE.md`：本專案例外 + K26 第 7 章規則
2. `docs/style.md`：明確指出「由 `CLAUDE.md` 用 `@docs/style.md` 匯入」
3. `CLAUDE.local.md`：個人偏好，並知道它不進版控

它也自行提到全域 `~/.claude/CLAUDE.md`，並說明衝突時以專案層為準。

## 記憶體階層（書上的概念，本練習只說明不實作）

| 層級 | 位置 | 誰共用 |
| --- | --- | --- |
| 企業政策 | 系統層級目錄（由 IT 統一派發，例如 Windows 的 `C:\ProgramData\ClaudeCode\CLAUDE.md`） | 全公司 |
| 使用者 | `~/.claude/CLAUDE.md` | 自己的所有專案 |
| 專案 | `./CLAUDE.md`（可用 `@路徑` 匯入其他檔） | 團隊（進版控） |
| 專案個人 | `./CLAUDE.local.md` | 只有自己（gitignore） |

越上層越廣、越下層越具體；全部都會載入，內容衝突時通常以較具體的專案層為準。

## 和書上做法的差異

- **全域檔案不動**：書上示範會編輯 `~/.claude/CLAUDE.md`，這裡只在本筆記說明，因為本機的全域檔已有大量既有規則，改動會影響所有專案。
- **用 `claude -p` 非互動驗證**：書上多半在互動模式用 `/memory` 查看載入的檔案；這裡改用一行指令並把回答存成 `verify.txt`，方便留存與比對。
- **巢狀 session 處理**：因為是在 Claude Code 內再呼叫 `claude`，需額外清除 `CLAUDE*` 環境變數並提供 stdin，書上沒有這一步。
- **`CLAUDE.local.md` 手動加 `.gitignore`**：明確寫進 `.gitignore`，不依賴工具自動處理。
