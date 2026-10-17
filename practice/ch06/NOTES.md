# K26 第 6 章練習：CLI 深度應用與自動化

> 快速 demo 模式（未經 QA／code review），執行日期 2026-10-18，Claude Code CLI 2.1.302，Windows 10 + Git Bash。

## 做了什麼

| 檔案 | 示範重點 | 輸出 |
| --- | --- | --- |
| `scripts/_lib.sh` | 共用函式：`run_claude` 動態清掉所有 `CLAUDE*` 環境變數再呼叫 `claude`；`win_path` 轉換路徑 | — |
| `scripts/01-analyze.sh` | `claude -p "<prompt + sample.py 內容>" < /dev/null` 單次分析 | `out/01-analyze.txt` |
| `scripts/02-pipe.sh` | `cat prompt.txt \| claude -p` 管道輸入 | `out/02-pipe.txt` |
| `scripts/03-json.sh` | `--output-format json`，Python 取出 `result` 欄位 | `out/03-json-raw.json`、`out/03-json-result.txt` |
| `scripts/04-allowed-tools.sh` | `--allowedTools "Read"` 後要求寫檔，驗證檔案沒產生 | `out/04-allowed-tools.txt`、`out/04-allowed-tools-raw.json` |
| `sample.py` | 被分析的小檔案（故意留空清單除以零、沒關檔、沒指定 encoding） | — |
| `prompt.txt` | 02 管道用的 prompt | — |

執行方式：`bash scripts/01-analyze.sh`（其餘同理）。

## 結果

1. **01-analyze**：成功。找出 3 個問題（空清單 `ZeroDivisionError`、`open()` 未關閉、未指定 `encoding`），並附修正程式碼。
2. **02-pipe**：成功。stdin 的內容直接被當成 prompt，回了 3 點管道概念說明。
3. **03-json**：成功。JSON 內含 `result`、`session_id`、`num_turns`、`total_cost_usd` 等欄位；這次 `num_turns=1`、`total_cost_usd≈0.0208`。
4. **04-allowed-tools**：成功擋下。`permission_denials` 記錄了被拒的 `Write` 呼叫，`out/should-not-exist.txt` 確認不存在，腳本以 exit 0 結束。

## 和書上做法的差異

| 項目 | 書上（一般終端機） | 本練習 |
| --- | --- | --- |
| 呼叫方式 | 直接 `claude -p ...` | 在 Claude Code session 裡執行，必須先清掉 `CLAUDECODE`、`CLAUDE_CODE_ENTRYPOINT` 等 13 個 `CLAUDE*` 變數（避免被當成巢狀 session），用 `compgen -e` 動態列出後 `env -u` 清除 |
| stdin | 互動終端機不用處理 | 沒有管道時加 `< /dev/null`，避免 `claude -p` 等待 stdin |
| 解析 JSON | 書上常用 `jq` | 用 Python（本機沒預設 jq）；Windows 版 Python 看不懂 `/c/Users/...`，要先 `cygpath -w` 轉換（第一次執行 03 就踩到這個坑） |
| `--allowedTools` 測試 | 只加 `--allowedTools "Read"` | 另加 `--permission-mode default`：本機全域 `defaultMode` 是 `auto`，不指定的話 auto 模式可能自己放行 Write，就測不到 `--allowedTools` 的效果 |
| 01 分析方式 | 可能讓 Claude 自己用 Read 讀檔 | 直接把檔案內容放進 prompt，一次呼叫就完成，不需授權任何工具 |

## `-r`／`--resume` 與 `-c`／`--continue`（未實跑）

| 選項 | 作用 | 例子 |
| --- | --- | --- |
| `-c`, `--continue` | 接續**目前目錄最近一次**的對話 | `claude -c`（互動）或 `claude -c -p "再補一個測試案例"`（非互動接著問） |
| `-r`, `--resume [id]` | 接續**指定 session**；不給 id 時跳出清單讓你選 | `claude -r` 選單；`claude -r 913467ef-... -p "延續剛才的回答，再舉一個例子"` |

- session id 從哪來：`--output-format json` 回傳的 `session_id`（例如 03 這次的 `913467ef-71eb-4c62-996f-36e7b5fac439`）。腳本可以先存下來，下一步用 `-r` 接續，做成多步驟自動化。
- 差別：`-c` 只看「最近一次」，適合手動連續追問；`-r <id>` 指定確切對話，適合腳本，因為別的對話不會插隊。
- 在腳本裡要接續，一樣得加 `-p` 才是非互動模式；在 Claude Code session 裡呼叫時，同樣要清掉 `CLAUDE*` 環境變數。

## 已知限制

- 快速模式：沒有完整測試套件，只各跑一次實際呼叫。
- `claude -p` 的回覆每次都不同，`out/` 裡的內容只代表這次執行的結果。
- 每次執行都會消耗用量（03 這次約 0.02 美元等值）。
