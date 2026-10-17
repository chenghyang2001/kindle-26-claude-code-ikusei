# K26 第 8 章練習：Agent Skills（pdf-text）

## 做了什麼

1. 用 `uv venv .venv` 建專案虛擬環境，`uv pip install pypdf` 只裝在 `.venv`（pypdf 6.21.1），沒有裝到全域。
2. 建 `.claude/skills/pdf-text/`：
   - `SKILL.md`：YAML frontmatter 含 `name: pdf-text`，`description` 寫明何時觸發（轉文字、抽出 PDF 文字、pdf to text、摘要／搜尋前先取純文字）與不適用情況（OCR、編輯或產生 PDF），內文寫使用步驟、輸出格式、結束碼與限制。
   - `pdf_to_text.py`：用 pypdf 逐頁抽文字，輸出同目錄同名 `.txt`（UTF-8，每頁以 `--- Page N ---` 分隔），可一次轉多個檔。
3. 用手寫的最小 PDF（自己算 xref 偏移）產生兩頁英文的 `sample.pdf`。
4. `.gitignore` 排除 `.venv/`；`.gitattributes` 把 `*.pdf` 標成二進位，避免 Git 換行轉換弄壞 PDF。
5. 在對話中說「幫我把 sample.pdf 轉成文字」，驗證 skill 觸發與輸出。

## 結果

- `sample.txt` 內容正確，與 PDF 寫入的文字逐字相同：

  ```
  --- Page 1 ---
  Hello from K26 Chapter 8.
  Agent Skills make Claude reusable.

  --- Page 2 ---
  Page two: pypdf extracts this text.
  ```

- 冒煙測試：正常轉檔回傳 0；檔案不存在、損毀 PDF 回傳 1 並印中文錯誤；沒給參數回傳 2。
- **關於「skill 是否被觸發」的實話**：
  - 第一次說「幫我把 sample.pdf 轉成文字」時，pdf-text **還沒出現在 Claude 的可用 skill 清單**（skill 是在同一個 session 中途建立的），所以 Claude 是看到檔案後**直接執行腳本**，並不是經由 Skill 機制觸發。
  - 下一輪訊息起 pdf-text 已出現在清單裡，用 Skill 工具正式呼叫（`Launching skill: pdf-text`），照 SKILL.md 的步驟重新產生 `sample.txt`，內容與先前完全相同（git 無差異）。
  - 心得：在同一個 session 中途新增的 skill，要到下一輪對話才會被載入；最保險的驗證方式是開新 session 再說觸發語句。

## 和書上做法的差異

對照來源：第 8 章投影片（`~/workspace/kindle-26-slides/png/08-*`，由書整理而成，不是原書全文）與教案 `kindle-26-claude-code-ikusei/teaching/LESSON-PLAN.md`。

| 項目 | 書上（投影片） | 本次練習 |
| --- | --- | --- |
| skill 資料夾名稱 | `pdf-extractor/` | `pdf-text/`（依教案指定） |
| 腳本檔名 | `script.py` | `pdf_to_text.py` |
| 底層套件 | PyPDF2 | pypdf（PyPDF2 的後繼版本，PyPDF2 已停止維護） |
| 輸出格式 | PDF → md（轉成 AI 可讀的文字串流） | PDF → 同名 `.txt` |
| 相依套件宣告 | 資料夾內放 `package.json` | 不放宣告檔，改用專案 `.venv` + uv 安裝 |
| SKILL.md 寫法 | 範例用 `Name:` / `Description:` / `Run: python run_linter.py {{target_dir}}` | 用官方 YAML frontmatter（`name`、`description`），執行指令寫在內文步驟，沒有 `Run:` 欄位或 `{{參數}}` 樣板 |
| 安全邊界（檢驗步驟） | 強調 SKILL.md 要宣告作用目錄範圍與權限邊界 | 沒有額外宣告權限；只靠腳本自己檢查檔案是否存在、是否為 `.pdf` |
| 測試資料 | 未說明 | 自己手寫最小 PDF 產生 `sample.pdf` |

相同之處：都是「SKILL.md（大腦／介面層）+ 本地腳本（肌肉／邏輯層）+ 套件（執行層）」三層結構，放在專案 `.claude/skills/` 下跟著版本控制；靠 `description` 讓 Claude 依對話內容自動判斷要不要載入（漸進式載入）。

## 已知限制

- 這是快速 demo 模式，未經 QA／程式碼審查。
- 掃描影像型 PDF 沒有文字層，抽不到字（腳本會警告），需要 OCR。
- 損毀的 PDF 會先出現 pypdf 自己的英文警告，然後才印中文錯誤。
