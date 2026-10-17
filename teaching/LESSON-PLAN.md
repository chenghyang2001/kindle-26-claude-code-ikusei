# K26 快速演練課表

依據：NotebookLM 筆記本 `41270591…`（整本書 PDF 為來源）回答的「各章讀者實際動手操作」（2026-10-18 查詢，原文存在 VPS `~/kindle-26/ask/`）。
書上沒有隨書程式碼；第 4 章範例 repo（fingerprints）網址未取得，改用本書先前實驗留下的 `epic-flashcard-review` 專案當「現有專案」。

每段提示詞前面都要加：「全自動執行：不要問我任何問題、不要用選擇題，所有選擇一律採用你的推薦，直接做完並回報」。

## 共通限制（每章都適用）

- **絕不執行** `/logout`、`/login`、`/upgrade`、`/install-github-app`、`/statusline`、`/doctor`，也不要修改全域 `~/.claude/` 底下任何檔案（`settings.json`、`CLAUDE.md`、`agents/`、`skills/`、`output-styles/`）。書上寫到全域的地方，一律改成專案層（`./.claude/`、`./CLAUDE.md`、`.mcp.json`）。
- `claude mcp add`、`claude plugin install` 一律加 `--scope project`（或 `local`）；不要加 user scope。
- 不建立 GitHub repo、不 push 到任何遠端、不部署到 Vercel／Streamlit Cloud。
- 不需要 API key 的才實際執行；需要第三方 token 的只寫設定範本（值用 `${ENV_VAR}` 佔位）。
- 每章產出一份 `NOTES.md`：做了什麼、結果、和書上做法的差異。

## 第 1 章 Claude Code 必備的基礎知識（k26-ch01-practice）

> 寫 `CONCEPTS.md`：用 Vibe Coding、LLM 運作原理、Spec Driven Development 三段整理本章觀念，每段最後附一個「在 Claude Code 裡怎麼體現」的具體例子。不要安裝任何東西。

## 第 2 章 Claude Code 這麼強大的原因（k26-ch02-practice）

> 寫 `ARCHITECTURE.md`：說明 LLM 工具呼叫、Agent 協作迴圈、沙箱執行、五大開發階段。再用一段 ASCII 圖畫出「使用者提示 → 模型 → 工具呼叫 → 結果回填 → 下一輪」的迴圈。

## 第 3 章 安裝及基本使用（k26-ch03-practice）

1. 檢查 `claude --version`、`node --version`、`git --version`、`gh --version`，寫 `ENV-CHECK.md`（列出書上的三種安裝方式，標註本機實際用哪一種）。
2. 建 `claude-test/`，在裡面用 `claude -p "這個資料夾是做什麼的？請用一句話回答"` 跑一次單次指令，把回答存成 `claude-test/answer.txt`。
3. 不要執行 `/login`、`/logout`（會把目前登入弄掉）。

## 第 4 章 從現有的專案開始玩起（k26-ch04-practice）

1. 教練先把 `%USERPROFILE%\workspace\kindle-26-claude-code-育成手冊\epic-flashcard-review` 複製到本章資料夾（排除 `.git`、`node_modules`、`.claude.backup-*`、`.claude-spec-workflow-bak`），`git init` 後 commit 一次當起點，再 `git checkout -b feature/demo`。
2. 依序問練習視窗（一次一段）：「這個專案是做什麼的？」→「追蹤一個使用者操作從前端到後端的完整流程」→「畫一張 ASCII 圖說明這個流程」→「如何執行這個應用程式？請實際啟動並用 curl 驗證首頁」。
3. 送 `/init` 產生 `CLAUDE.md`，再請它在 `CLAUDE.md` 加一條記憶「總是用 npm run 指令啟動，不要直接 node」，最後在 feature/demo 分支 commit。

## 第 5 章 斜線指令系統（k26-ch05-practice）

1. 建一個小專案（一支 `hello.py` 即可），送 `/init`。
2. 教練依序對練習視窗送這些斜線指令並記錄畫面重點：`/help`、`/status`、`/context`、`/cost`、`/model`（只看不切）、`/memory`（只看）、`/compact`、`/export ch05-export.md`、`/todos`、`/agents`（只看）、`/hooks`（只看）、`/clear`。
3. 寫 `SLASH-CHEATSHEET.md`：書上提到的指令分「對話維護／帳號／審查／偏好／進階」五類，標註本次實測過哪些、哪些因共通限制略過。

## 第 6 章 CLI 深度應用與自動化（k26-ch06-practice）

> 寫 `scripts/` 底下 4 支示範腳本並逐一實際執行、把輸出存到 `out/`：(1) `claude -p` 單次分析一個小檔案；(2) `cat prompt.txt | claude -p` 管道輸入；(3) `--output-format json` 後用 python 取出 `result` 欄位；(4) `--allowedTools "Read"` 限制工具後要求它寫檔，確認被擋。最後在 `NOTES.md` 說明 `-r`／`--resume` 的用法（不必實跑）。

## 第 7 章 CLAUDE.md 與記憶體管理（k26-ch07-practice）

> 建 `./CLAUDE.md`（專案規則）、`./CLAUDE.local.md`（個人偏好，加進 .gitignore）、`docs/style.md`，在 CLAUDE.md 用 `@docs/style.md` 匯入。再用 `claude -p "列出你目前看到的專案規則"` 驗證三份都被讀到。書上的全域 `~/.claude/CLAUDE.md` 只在 NOTES.md 說明，不要改。

最後教練送 `/memory`（只看）與 `/compact 保留記憶檔討論`。

## 第 8 章 可能取代 MCP 的 Agent Skills（k26-ch08-practice）

> 在 `.claude/skills/pdf-text/` 建 `SKILL.md`（YAML frontmatter 含 name、description）和 `pdf_to_text.py`（用 pypdf，裝在專案的 .venv）。自己產生一份含文字的測試 PDF，然後在對話中說「幫我把 sample.pdf 轉成文字」，確認 skill 被觸發、輸出 `sample.txt`。

## 第 9 章 深度客製化設定檔（k26-ch09-practice，isolated）

> 建 `.claude/settings.json`（團隊共用：permissions allow `Bash(git status)`、deny `Read(./secrets/**)`、env 加 `DEMO_FLAG=1`）和 `.claude/settings.local.json`（個人：加一條 allow），`settings.local.json` 加進 .gitignore。建 `secrets/key.txt`，用 `claude -p "讀 secrets/key.txt 的內容"` 驗證被擋；用 `claude -p "執行 echo %DEMO_FLAG%"`（或 `$DEMO_FLAG`）驗證 env 生效。NOTES.md 寫優先順序（企業 > 命令列 > local > project > user）。

## 第 10 章 Hooks 自動化機制（k26-ch10-practice，isolated）

> 只在 `.claude/settings.json` 設三個 hook：PostToolUse（Edit|Write 後對 .py 跑格式化，用 python 內建 `python -m py_compile` 或 ruff/black 擇一已安裝者）、PreToolUse（禁止寫入 `.env`，exit 2 並說明原因）、SessionStart（把時間寫進 `hook.log`）。用 `claude -p` 觸發三種情境並把結果寫進 NOTES.md。

## 第 11 章 Plugins 外掛系統（k26-ch11-practice，isolated）

> 建一個本機 marketplace（`.claude-plugin/marketplace.json`）和外掛 `doc-gen/`（`.claude-plugin/plugin.json`、一個 `/doc-gen:readme` 指令、一個 skill、一個 hook）。用 `claude plugin marketplace add ./` 加入、`claude plugin install doc-gen@<marketplace> --scope project` 安裝，實測指令產生 README。結束前 `claude plugin uninstall` 並確認全域 settings.json 沒被改。

## 第 12 章 MCP Server（k26-ch12-practice）

> 用 `claude mcp add --scope project chrome-devtools -- npx chrome-devtools-mcp@latest --headless` 加入（寫進 `.mcp.json`）。建一個本機 `form.html`（註冊表單），用 python `http.server` 在 127.0.0.1 起服務，讓 Claude 透過 MCP 打開頁面、調整樣式、自動填表送出並截圖存檔。最後用 `claude mcp list` 列出，並在 NOTES.md 說明 stdio／SSE／HTTP 三種傳輸與 `claude mcp serve`。

## 第 13 章 MCP Server 大閱兵（k26-ch13-practice）

> 寫 `.mcp.json`，實際放 2–3 個不需金鑰的 server（例：filesystem 限本資料夾、sequential-thinking），用 `claude mcp list` 驗證連線。需要 token 的（GitHub、Notion、Figma、PostgreSQL 等）只寫進 `MCP-CATALOG.md`：用途、設定範本（`${TOKEN}` 佔位）、適用情境。

## 第 14 章 Subagent 子代理（k26-ch14-practice）

> 在 `.claude/agents/` 建 `code-reviewer.md`、`debugger.md`（YAML frontmatter），寫一支有 bug 的小程式，分別請兩個子代理審查與修正。再用 `git worktree add` 開兩個工作區平行做兩個小功能（各由一個子代理負責），完成後合併回 main 並 `git worktree remove` 清理。

## 第 15 章 輸出樣式 Output Style（k26-ch15-practice）

> 在專案 `.claude/output-styles/` 建 `prd-writer.md`（自訂樣式），在 `.claude/settings.local.json` 設定使用它，用 `claude -p` 讓它產生一份小功能的 PRD。再對照內建 Explanatory／Learning 的差異寫進 NOTES.md。不要寫到全域 `~/.claude/output-styles/`。

## 第 16 章 GitHub Actions 與 CI/CD（k26-ch16-practice）

> 寫 `.github/workflows/claude.yml`（issue／PR 留言 `@claude` 觸發，使用 `anthropics/claude-code-action`，key 用 `${{ secrets.ANTHROPIC_API_KEY }}`）和 `.github/workflows/review.yml`（PR 自動審查）。用 python `yaml.safe_load` 驗證語法。不安裝 GitHub App、不設 secret、不 push。

## 第 17 章 接上自訂模型（k26-ch17-practice）

> 只寫設定範本：`litellm-config.yaml`（Gemini／Vertex AI／Ollama 三種 model_list，key 用環境變數佔位）、`run-proxy.md`（啟動步驟與要設的 `ANTHROPIC_BASE_URL`）。不安裝 LiteLLM、不改任何環境變數、不實際連線。

## 第 18 章 Claude Code 網頁版（k26-ch18-practice）

> 只寫 `WEB-NOTES.md`：網頁版的流程（連 GitHub、雲端 container、環境變數、網路等級 Limited／No network、產出 PR），以及和 CLI 版的取捨。（網頁操作需要登入 claude.ai，快速演練略過。）

## 第 19 章 Spec Kit 規格驅動開發（k26-ch19-practice）

> 用 `uvx --from git+https://github.com/github/spec-kit.git specify init . --ai claude --force` 初始化，依序跑 constitution → specify → plan → tasks → implement，做一個「命令列記帳小工具」（新增／列出／月合計，資料存 JSON）。完成後跑一次測試。

## 第 20 章 更了解你的 Claude Code（k26-ch20-practice）

> 執行 `npx ccusage@latest daily --since <7 天前>`，把輸出存成 `usage.txt`（只留日期與合計欄）。寫 `COST-NOTES.md`：ccusage 用法、GLM 第三方 Base URL 與 Ollama＋LiteLLM 本地模型的接法（只寫步驟，不實際設定）。

## 第 21 章 工業化流程開發 AI 專案（k26-ch21-practice）

> 寫 `AGENTS.md`（團隊規範）。用「腦力激盪 → PRD（docs/prd.md）→ Epic（docs/epic.md）→ Tasks（docs/tasks/*.md）」流程規劃一個待辦事項網頁應用，再依 tasks 實作（純 HTML＋JS 或 Node 擇一）、每個 task 一個分支、做完合併回 main。GitHub Issues 同步步驟只寫在 NOTES.md，不實際同步。

## 第 22 章 Notebook → .py → Streamlit（k26-ch22-practice）

> 自己產生一份 `sales.ipynb`（用模擬銷售資料做載入、指標、圖表三段）。把它重構成 `src/load.py`、`src/metrics.py`、`src/charts.py`，再寫 `app.py`（Streamlit 儀表板）。用 uv 建 .venv 安裝依賴，`streamlit run app.py --server.headless true` 啟動後 curl 首頁確認 200 再關掉。不部署雲端。

## 第 23 章 Claude 與 Xcode（k26-ch23-practice）

> 本機不是 Mac，只寫程式不建置：產生 SwiftUI 天氣 App 的原始檔（主題切換、環境資訊、逐時預報、城市選擇），放 `WeatherApp/`，附 `README.md` 說明在 Xcode 怎麼開與怎麼接 Claude。

## 第 24 章 純雲端部署的電商網站（k26-ch24-practice）

> 先寫 `CLAUDE.md`（架構規範）。做一個手機電商網站的本機版：商品列表、購物車、結帳、訂單查詢（技術自選，資料用 SQLite 或 JSON）。在 127.0.0.1 啟動並用 curl 跑一輪「加入購物車 → 結帳 → 查訂單」。Vercel／Neon 部署只寫在 `DEPLOY.md`，不實際部署。

## 第 25 章 Claude Code＋Unsloth 訓練推理模型（k26-ch25-practice）

> 本機沒有 GPU，只寫程式不訓練：用 Spec Kit 精簡流程寫 `spec.md`（constitution／specify／plan／tasks 四段）、`train.py`（Unsloth GRPO 微調腳本）、`infer.py`、`README.md`（Colab 執行步驟）。只用 `python -m py_compile` 檢查語法，不安裝 torch／unsloth。
