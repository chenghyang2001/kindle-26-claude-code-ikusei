---

description: "命令列記帳小工具的任務清單"
---

# Tasks: 命令列記帳小工具

**Input**: Design documents from `/specs/001-cli-expense-tracker/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md

**Tests**: 憲章原則 II 要求測試先行，因此每個故事都包含測試任務（先寫、先失敗、再實作）。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 可平行（不同檔案、無相依）
- **[Story]**: 所屬使用者故事（US1／US2／US3）

## Phase 1: Setup

- [X] T001 建立 uv 專案設定 `pyproject.toml`（src layout、`ledger` console script、Python ≥ 3.11）
- [X] T002 以 `uv add --dev pytest` 加入測試依賴並產生 `uv.lock`
- [X] T003 [P] 建立 `.gitignore`（`.venv/`、`__pycache__/`、`.pytest_cache/`、`*.stackdump`）

---

## Phase 2: Foundational

- [X] T004 建立套件骨架 `src/ledger/__init__.py`、`src/ledger/__main__.py`
- [X] T005 [P] 在 `tests/unit/test_models.py` 寫金額／日期／月份解析測試（含非法輸入）
- [X] T006 [P] 在 `tests/unit/test_storage.py` 寫讀寫、檔案不存在、損毀檔測試
- [X] T007 實作 `src/ledger/models.py`：`Expense`、`LedgerError`、`parse_amount`、`parse_date`、`parse_month`
- [X] T008 實作 `src/ledger/storage.py`：`load_expenses`、`save_expenses`（原子寫入）、`resolve_data_file`
- [X] T009 新增共用 fixture `tests/conftest.py`（`data_file` 指向 `tmp_path`）

**Checkpoint**: 模型與儲存層測試通過

---

## Phase 3: User Story 1 - 新增一筆支出 (Priority: P1) 🎯 MVP

**Goal**: `ledger add` 可新增並永久保存紀錄。

**Independent Test**: 執行 add 後讀取資料檔，確認有 1 筆內容正確的紀錄。

- [X] T010 [P] [US1] 在 `tests/unit/test_service.py` 寫 `add_expense` 測試（id 遞增、預設今天）
- [X] T011 [P] [US1] 在 `tests/integration/test_cli.py` 寫 `add` 指令測試（成功輸出、非法金額結束碼 1 且資料不變）
- [X] T012 [US1] 實作 `src/ledger/service.py` 的 `add_expense`
- [X] T013 [US1] 實作 `src/ledger/cli.py` 的 `main`、`--file` 全域選項與 `add` 子指令

**Checkpoint**: US1 可獨立運作

---

## Phase 4: User Story 2 - 列出紀錄 (Priority: P2)

**Goal**: `ledger list [--month]` 依日期排序列出。

**Independent Test**: 預放 3 筆，list 輸出 3 行且順序正確；`--month` 只留該月。

- [X] T014 [P] [US2] 在 `tests/unit/test_service.py` 寫 `list_expenses` 排序與篩選測試
- [X] T015 [P] [US2] 在 `tests/integration/test_cli.py` 寫 `list` 指令測試（含空資料訊息）
- [X] T016 [US2] 實作 `src/ledger/service.py` 的 `list_expenses`
- [X] T017 [US2] 實作 `src/ledger/cli.py` 的 `list` 子指令

---

## Phase 5: User Story 3 - 月合計 (Priority: P3)

**Goal**: `ledger total YYYY-MM` 顯示總計與類別小計。

**Independent Test**: 跨月份資料，10 月總計 500、餐飲 200、交通 300。

- [X] T018 [P] [US3] 在 `tests/unit/test_service.py` 寫 `monthly_total` 測試（含小數 0.1+0.2 精確、空月份 0）
- [X] T019 [P] [US3] 在 `tests/integration/test_cli.py` 寫 `total` 指令測試（含格式錯誤 2026-13）
- [X] T020 [US3] 實作 `src/ledger/service.py` 的 `monthly_total`
- [X] T021 [US3] 實作 `src/ledger/cli.py` 的 `total` 子指令

---

## Phase 6: Polish

- [X] T022 [P] 撰寫 `README.md`（安裝、用法、資料檔位置）
- [X] T023 執行 `uv run pytest` 全部通過，並依 quickstart.md 手動驗證一次

## Dependencies & Execution Order

- Setup → Foundational → US1 → US2 → US3 → Polish。
- US2、US3 只依賴 Foundational 與 `cli.py` 骨架（T013），理論上可在 US1 之後平行進行。
- 每個故事內：測試任務 [P] 可平行，實作任務依序（service → cli）。

## Parallel Example: User Story 1

```text
T010 tests/unit/test_service.py  ∥  T011 tests/integration/test_cli.py
```

## Implementation Strategy

先完成 Phase 1–3 即為 MVP（能記帳）；再逐步加入列出與月合計，每個故事完成後跑一次全部測試。
