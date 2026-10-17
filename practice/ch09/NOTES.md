# K26 第 9 章練習：深度客製化設定檔

## 做了什麼

| 檔案 | 用途 | 進 git？ |
| --- | --- | --- |
| `.claude/settings.json` | 團隊共用：allow `Bash(git status)`、deny `Read(./secrets/**)`、env `DEMO_FLAG=1` | 是 |
| `.claude/settings.local.json` | 個人：allow `Bash(ls:*)`、`Bash(printenv:*)` | 否（已寫入 `.gitignore`） |
| `secrets/key.txt` | 測試用假機密，內容 `dummy-secret` | 是（僅 demo 用，內容是假的） |
| `out/*.txt` | 驗證結果 | 是 |

驗證方式：一律用 `claude -p --setting-sources project,local "..." < /dev/null` 啟動子 session，
執行前先用 `env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT ...` 清掉所有 `CLAUDE*` 環境變數，
避免巢狀 session 的限制，也避免它等待 stdin。

## 結果

1. **deny 生效**（`out/test1-deny-read.txt`）：子 session 回報讀不到 `secrets/key.txt`，
   並指出是 `Read(./secrets/**)` deny 規則擋下的，輸出中沒有出現 `dummy-secret`。
2. **env 生效**（`out/test2b-printenv.txt`）：`printenv DEMO_FLAG` 的輸出是 `1`。
3. **`echo $DEMO_FLAG` 被擋**（`out/test2-env-attempt1-blocked.txt`、`out/test2-env.txt`）：
   Claude Code 的 Bash 權限檢查不允許執行前看不出內容的變數展開
   （"A variable in this command can't be checked before it runs"），
   在 `-p` 非互動模式下也沒辦法跳出核准提示，所以題目指定的這行指令本身無法直接執行。
   第一次測試時連 `printenv` 也需要核准，所以在 `settings.local.json` 加上 `Bash(printenv:*)` 後，
   改用 `printenv` 驗證。
4. 全域 `~/.claude/settings.json` 從頭到尾沒有動過，測試前後 sha256 都是 `a7e97811…ab6a`。

## 設定優先順序（高 → 低）

1. **企業 managed 設定**（managed-settings.json，使用者無法覆寫）
2. **命令列參數**（例如 `--allowedTools`、`--permission-mode`、`--settings`）
3. **local 專案設定** `.claude/settings.local.json`（個人用，不進 git）
4. **project 專案設定** `.claude/settings.json`（團隊共用，進 git）
5. **user 全域設定** `~/.claude/settings.json`

補充：permissions 陣列會跨層「合併」，不是整份覆蓋；判定時 **deny 優先於 allow**，
所以就算 local 加了 allow，也開不了 project 的 deny。

## 和書上做法的差異

- 書上通常直接開互動 session 測試；這裡改用 `claude -p` 搭配 `--setting-sources project,local`，
  排除 user 全域設定的干擾，結果更乾淨、也能存檔。
- 在 Claude Code session 內呼叫 `claude -p` 會碰到巢狀限制，必須先清掉 `CLAUDE*` 環境變數並加 `< /dev/null`。
- 新版 Claude Code 會擋含變數展開的 Bash 指令（`echo $VAR`），所以 env 改用 `printenv` 驗證，
  並在 local 設定加上對應的 allow。
- Windows 環境下子 session 還會嘗試 PowerShell 的 `$env:VAR`，一樣會被權限擋下。
