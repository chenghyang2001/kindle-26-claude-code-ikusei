# K26 第 10 章練習：Hooks

## 做了什麼

在專案層 `.claude/settings.json` 設定三個 hook，腳本都放在 `.claude/hooks/`，用 Python 從 stdin 讀 JSON：

| 事件 | matcher | 腳本 | 行為 |
| --- | --- | --- | --- |
| PreToolUse | `Edit\|Write` | `block_env.py` | 目標檔名是 `.env`（或 `.env.*`）時 exit 2，stderr 說明原因 → 工具呼叫被拒絕 |
| PostToolUse | `Edit\|Write` | `check_py.py` | 目標是 `.py` 時跑 `python -m py_compile`；失敗則 exit 2 把錯誤回饋給 Claude |
| SessionStart | （無） | `log_session.py` | 把目前時間與 `source` 追加寫入專案根目錄 `hook.log` |

指令統一寫成 `PYTHONUTF8=1 python "$CLAUDE_PROJECT_DIR/.claude/hooks/xxx.py"`，避免 cp950 編碼問題，也不受 hook 執行時的 cwd 影響。

觸發方式（在 Claude session 裡呼叫，需先清掉所有 `CLAUDE*` 環境變數並把 stdin 接到 `/dev/null`）：

```bash
UNSET=$(env | grep -o '^CLAUDE[A-Z_]*' | sed 's/^/-u /' | tr '\n' ' ')
env $UNSET claude -p "<prompt>" --setting-sources project,local --permission-mode acceptEdits < /dev/null
```

## 結果

1. **建立 demo.py**：成功。`demo.py` 建立後出現 `__pycache__/demo.cpython-314.pyc`，證明 PostToolUse 的 py_compile 有執行；`python demo.py` 輸出 `Hello, K26!`。
2. **嘗試寫 .env**：被擋下，`.env` 沒有建立。子 session 回報的原文：
   ```
   PreToolUse:Write hook error: [PYTHONUTF8=1 python "$CLAUDE_PROJECT_DIR/.claude/hooks/block_env.py"]: 已阻擋：禁止寫入 .env（C:\Users\user\workspace\k26-ch10-practice\.env）。.env 存放機密，請改用 .env.example 或手動編輯。
   ```
3. **hook.log 有時間**：每次啟動 `claude -p` 都追加一行（共 4 筆，其中前 2 筆是第一次因參數錯誤而沒執行 prompt 的啟動，也照樣觸發了 SessionStart）：
   ```
   2026-10-18T04:39:35 SessionStart source=startup
   2026-10-18T04:39:42 SessionStart source=startup
   2026-10-18T04:40:00 SessionStart source=startup
   2026-10-18T04:40:33 SessionStart source=startup
   ```

### 踩到的坑

- `--allowedTools "Write Edit" "<prompt>"` 會讓可變長參數把 prompt 吃掉，出現 `Input must be provided either through stdin or as a prompt argument`。解法：prompt 放在 `-p` 後面第一個位置，並改用 `--permission-mode acceptEdits`。
- 只清 `CLAUDECODE`、`CLAUDE_CODE_ENTRYPOINT` 不夠保險，這次的 session 還有 `CLAUDE_CODE_SESSION_ID`、`CLAUDE_CODE_MESSAGING_*` 等 11 個變數，所以用 `env | grep` 動態全清。

## 和書上做法的差異

- **設定位置**：書上的範例多半直接改 `~/.claude/settings.json`（使用者層）；這裡只寫專案層 `.claude/settings.json`，搭配 `--setting-sources project,local` 啟動，完全不載入使用者層設定，避免全域 hook 干擾，也不污染全域環境。（本專案 CLAUDE.md 原本建議放 `settings.local.json`，但這次練習指定 `settings.json`，好處是可以隨 repo 一起 commit 分享。）
- **腳本語言**：書上常用一行 shell + `jq` 解析 stdin；這裡改用 Python 腳本讀 JSON，Windows 上不需要另外裝 `jq`，邏輯也比較好讀好測。
- **路徑**：用 `$CLAUDE_PROJECT_DIR` 組絕對路徑，而不是相對路徑，hook 不管在哪個 cwd 執行都找得到腳本。
- **PostToolUse 失敗時用 exit 2**：讓 py_compile 的錯誤以 stderr 回饋給 Claude 自動修正，而不只是印在終端機上。
- **驗證方式**：用非互動的 `claude -p` 自動觸發，而非在互動 session 裡手動操作，且需處理巢狀 session 的環境變數與 stdin 問題。
