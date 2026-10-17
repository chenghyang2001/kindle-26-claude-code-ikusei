# K26 第 16 章練習筆記：GitHub Actions 與 CI/CD

> 快速 demo 模式：只驗證 YAML 語法與關鍵欄位，未實際在 GitHub 上執行。

## 做了什麼

| 檔案 | 用途 | 觸發時機 |
| --- | --- | --- |
| `.github/workflows/claude.yml` | 互動模式：留言叫 `@claude` 就由 Claude 回應／改程式 | `issue_comment`、`pull_request_review_comment`、`pull_request_review`、`issues`（opened／assigned），且內容含 `@claude` |
| `.github/workflows/review.yml` | 自動模式：PR 自動審查，用繁體中文留言 | `pull_request` 的 `opened`、`synchronize` |

兩支都用 `anthropics/claude-code-action@v1`，API key 一律讀 `${{ secrets.ANTHROPIC_API_KEY }}`，不寫死在檔案裡。

### permissions 設計

| 權限 | claude.yml | review.yml | 原因 |
| --- | --- | --- | --- |
| `contents` | write | read | 互動模式可能要推分支；審查只需要讀 |
| `pull-requests` | write | write | 在 PR 留言 |
| `issues` | write | read | 互動模式要回 issue |
| `id-token` | write | write | action 用 OIDC 換 GitHub token |
| `actions` | read | — | 讓 Claude 讀 CI 結果 |

原則：最小權限，審查用的 workflow 不給寫入程式碼的權限。

### 其他細節

- `claude.yml` 的 `if` 先過濾 `@claude`，避免每則留言都啟動 runner、浪費額度。
- `review.yml` 加 `concurrency` + `cancel-in-progress`：同一個 PR 連推多次只留最新一次審查。
- `review.yml` 用 `claude_args --allowedTools` 只開放 `gh pr comment／diff／view` 和 inline comment，限制 Claude 在 CI 裡能做的事。
- 兩支都設 `timeout-minutes`，避免卡住時一直計費。

## 驗證結果

指令：`uv run --with pyyaml python -c "...yaml.safe_load..."`

```text
OK .github/workflows/claude.yml: name=Claude Code triggers=['issue_comment', 'pull_request_review_comment', 'issues', 'pull_request_review'] job=claude perms={...5 項...}
OK .github/workflows/review.yml: name=Claude PR Review triggers=['pull_request'] job=review perms={...4 項...}
```

除了語法，也檢查了：觸發事件、action 版本是 `@v1`、key 來自 secrets。

踩到的小坑：PyYAML 依 YAML 1.1 規則，會把 `on:` 解析成布林值 `True`，所以驗證程式要用 `d.get(True)` 取觸發條件。GitHub Actions 本身不受影響。

## 和書上做法的差異

| 項目 | 書上（一般做法） | 本次練習 |
| --- | --- | --- |
| 安裝方式 | 在 Claude Code 跑 `/install-github-app`，自動裝 GitHub App、設 secret、開 PR 放 workflow | 手寫 workflow 檔；**沒裝 App、沒設 secret、沒建 repo、沒 push** |
| 實際執行 | 在 GitHub 上留言 `@claude` 看它回應 | 只做離線 YAML 驗證，沒跑過真正的 Actions |
| Action 版本／參數 | 較早期範例可能用 `@beta` 與 `direct_prompt` 等參數 | 用 `@v1`，自動審查改用 `prompt` + `claude_args` |
| 審查語言 | 預設英文 | prompt 明確要求繁體中文留言 |

## 要真正跑起來還缺

1. 建 GitHub repo 並 push。
2. 安裝 Claude GitHub App（或在 Claude Code 跑 `/install-github-app`）。
3. 在 repo Settings → Secrets 加 `ANTHROPIC_API_KEY`。
4. 開一個 PR 或在 issue 留言 `@claude` 測試。
