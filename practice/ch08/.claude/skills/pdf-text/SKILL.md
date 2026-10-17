---
name: pdf-text
description: 把 PDF 檔的文字抽出來，存成同名 .txt。使用時機：使用者要讀取、抽取、轉換 PDF 內的文字（例如「把這個 PDF 轉成文字」「抽出 PDF 文字」「讀這份 PDF 的內容」「pdf to text」「extract text from PDF」），或需要先拿到 PDF 純文字才能做摘要、搜尋、翻譯時。不適用：掃描影像型 PDF 的 OCR、編輯或合併 PDF、產生 PDF。
---

# pdf-text：PDF 轉純文字

用 `pypdf` 讀取 PDF 每一頁的文字，輸出到與 PDF 同目錄、同檔名的 `.txt`（例如 `report.pdf` → `report.txt`）。

## 使用步驟

1. 確認專案 `.venv` 已安裝 pypdf（沒有就執行 `uv venv .venv` 與 `uv pip install --python .venv/Scripts/python.exe pypdf`）。
2. 執行腳本（可一次給多個 PDF）：

   ```bash
   PYTHONUTF8=1 .venv/Scripts/python.exe .claude/skills/pdf-text/pdf_to_text.py <檔案.pdf> [更多檔案.pdf ...]
   ```

3. 讀取產生的 `.txt` 回報內容或繼續後續處理（摘要、搜尋等）。

## 輸出格式

- 每頁之間以 `--- Page N ---` 分隔。
- 編碼一律 UTF-8。

## 結束碼

| 碼 | 意義 |
| --- | --- |
| 0 | 全部成功 |
| 1 | 至少一個檔案失敗（不存在、不是 PDF、加密、損毀） |
| 2 | 沒有給參數 |

## 限制

- 掃描影像型 PDF 沒有文字層，會得到空白內容（腳本會提示），需要另外做 OCR。
- 有密碼的 PDF 會嘗試用空密碼開啟，失敗就報錯。
