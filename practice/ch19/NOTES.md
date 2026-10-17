# K26 第 19 章練習筆記：Spec Kit 規格驅動開發

日期：2026-10-18｜模式：kindle-drill 快速模式（全自動，選擇題一律採推薦）

## 做了什麼

1. **初始化**：`uvx --from git+https://github.com/github/spec-kit.git specify init ...`
   - 指令照書寫的 `specify init . --ai claude --force` **直接失敗**：`No such option: --ai`。
   - 查 `specify init --help` 後改用新版語法：
     `specify init --here --force --non-interactive --integration claude --script sh --ignore-agent-tools`
   - 安裝的是 specify-cli `1.2.2.dev0`（commit `c6a4c18`）。產生 `.specify/`（範本、bash 腳本、憲章）與
     `.claude/skills/speckit-*/SKILL.md` 共 10 個 skill。
2. **constitution** → `.specify/memory/constitution.md` v1.0.0，五條原則：
   命令列優先、測試先行、簡單 JSON 儲存（原子寫入）、金額精確（Decimal）、YAGNI 只用標準庫。
3. **specify** → `specs/001-cli-expense-tracker/spec.md`：3 個使用者故事（P1 新增／P2 列出／P3 月合計）、
   7 條 FR、4 條 SC、邊界情況；`checklists/requirements.md` 品質清單第 1 輪 16/16 通過，無 NEEDS CLARIFICATION。
4. **plan** → `setup-plan.sh` 複製範本後填寫 `plan.md`（含 Constitution Check 表），並產出
   `research.md`、`data-model.md`、`contracts/cli.md`、`quickstart.md`。
5. **tasks** → `tasks.md` 23 個任務，依 Setup／Foundational／US1／US2／US3／Polish 分階段，標 [P] 與相依關係。
6. **implement** → 依 TDD 先寫測試看紅燈、再實作看綠燈，完成後 23 個任務全部勾成 [X]。

## 成果

```text
src/ledger/  models.py  storage.py  service.py  cli.py  __main__.py
tests/       unit/(models, storage, service)  integration/test_cli.py
```

- `uv run pytest -q` → **42 passed**（約 0.3 秒）。
- 依 quickstart 手動驗證：add／list --month／total 輸出與 `contracts/cli.md` 一致；`add -5` 回 `錯誤：金額必須大於 0` 且結束碼 1。
- 不設 `PYTHONUTF8` 的 cp950 環境下中文輸出也正常。

## 與書上做法的差異

| 項目 | 書上（教學時的 Spec Kit） | 本次實作 |
| --- | --- | --- |
| init 參數 | `--ai claude` | 該參數已移除，改 `--integration claude`，並加 `--non-interactive` 避免互動選單卡住 |
| 指令形式 | `.claude/commands/speckit.*.md`，用 `/speckit.specify` 等斜線指令 | 新版預設裝成 **skills**（`.claude/skills/speckit-*/SKILL.md`），名稱改為 `/speckit-specify`（點號變連字號） |
| 呼叫方式 | 在 Claude Code 中逐一輸入斜線指令 | skills 是本 session 啟動後才產生、未被載入，因此由 Claude **手動照 SKILL.md 內容執行**（含跑 `setup-plan.sh`、`check-prerequisites.sh` 等腳本） |
| 分支 | 書上 specify 會自動開 `001-xxx` git 分支 | 新版分支建立改由 git extension 的 hook 負責，未安裝該 extension → 沒開分支，直接在 `master` 上 commit；改用 `.specify/feature.json` 記錄目前功能目錄 |
| clarify／analyze | 書上建議在 plan 前跑 `/speckit.clarify` | 全自動模式下規格沒有待釐清項，跳過 clarify／analyze／checklist 這些選用步驟 |
| 互動確認 | 各階段會停下來讓人審閱 | 依使用者指示全自動，所有選擇採推薦；`implement` 的 checklist gate 因全部勾選而自動放行 |
| TDD 粒度 | 每個故事各自紅→綠 | Foundational 階段單獨紅→綠；US1～US3 的測試一次寫好後一起紅→綠（快速模式取捨） |

## 踩坑

- `uv add --dev pytest` 在 `src/ledger/` 還是空目錄時就把專案裝進 `.venv`，之後 `uv run ledger` 出現
  `ModuleNotFoundError: No module named 'ledger'`（pytest 沒事，因為設定了 `pythonpath = ["src"]`）。
  用 `uv sync --reinstall-package ledger` 解決。
- `ledger add -5 餐飲`：argparse 會把 `-5` 當成位置參數（因為沒有任何選項長得像負數），所以能正確走到金額驗證。

## 已知未處理（快速模式，未經 QA／審查）

- 沒有編輯／刪除功能（規格明確排除）。
- 未處理多個程序同時寫入同一個資料檔的競態。
