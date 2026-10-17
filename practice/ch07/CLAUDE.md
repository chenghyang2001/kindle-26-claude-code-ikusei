
## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。

## 專案規則（K26 第 7 章練習）

- 程式碼註解、docstring 一律使用繁體中文。
- 測試檔一律放在 `tests/` 目錄，檔名格式 `test_*.py`。
- 新增功能時，同一次產出要附上對應的測試。
- 程式風格詳見下方匯入的風格指南。

## 匯入

@docs/style.md
