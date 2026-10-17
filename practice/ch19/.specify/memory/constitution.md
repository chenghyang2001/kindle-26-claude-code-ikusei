# 記帳小工具（ledger）Constitution

## Core Principles

### I. 命令列優先（CLI-First）

所有功能 MUST 透過命令列子指令提供（`add`／`list`／`total`）。
正常輸出寫到 stdout，錯誤訊息寫到 stderr，且錯誤時結束碼 MUST 非 0。
理由：命令列工具最容易被腳本串接與自動化測試。

### II. 測試先行（NON-NEGOTIABLE）

每個使用者故事 MUST 先寫 pytest 測試、確認失敗，再寫實作讓它通過。
所有測試 MUST 能以 `uv run pytest` 一個指令跑完，且不碰使用者真實資料檔
（測試一律使用暫存目錄）。

### III. 簡單資料儲存

資料 MUST 以單一 UTF-8 JSON 檔保存，格式人類可讀（縮排、`ensure_ascii=False`）。
寫入 MUST 採「寫暫存檔再取代」以避免寫到一半損毀。
資料檔路徑可由環境變數或參數覆寫，不得硬編碼使用者路徑。

### IV. 金額精確

金額 MUST 以整數（新台幣元）或 `Decimal` 處理，禁止使用浮點數累加，
避免 0.1 + 0.2 類誤差。輸入驗證 MUST 拒絕非數字、0 與負數。

### V. 保持簡單（YAGNI）

只使用 Python 標準函式庫實作功能（測試依賴 pytest 除外）。
不加入未被規格要求的功能（例如編輯、刪除、雲端同步）。

## 技術限制

- 語言：Python 3.11 以上。
- 專案與依賴管理：uv（`pyproject.toml` + `uv.lock`）。
- 測試框架：pytest。
- 文件、註解與 docstring 使用繁體中文。

## 開發流程

- 依 Spec Kit 流程：constitution → specify → plan → tasks → implement。
- 每個任務完成後在 `tasks.md` 勾選。
- 合併前 MUST 全部測試通過。

## Governance

本憲章優先於其他開發慣例。修訂需更新本檔、說明理由並依語意化版本遞增：
移除或重新定義原則為 MAJOR，新增原則或章節為 MINOR，文字澄清為 PATCH。
每次 plan 階段 MUST 執行「Constitution Check」確認設計符合上述原則。

**Version**: 1.0.0 | **Ratified**: 2026-10-18 | **Last Amended**: 2026-10-18
