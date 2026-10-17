# K26 第 20 章練習筆記：更了解你的 Claude Code

日期：2026-10-18（快速 demo 模式，未經 QA／審查）

## 做了什麼

1. 執行 `npx -y ccusage@latest daily --since 20261011 --json`，把 JSON 暫存到系統暫存資料夾。
2. 用一段 Python 只擷取「日期、Total Tokens、Cost」三欄，加上總計列，存成 `usage.txt`。
3. 寫 `COST-NOTES.md`：ccusage 子指令、GLM 第三方 Base URL 接法、Ollama＋LiteLLM 本地模型接法（只寫步驟）。
4. 寫本檔 `NOTES.md`，最後 git commit（不 push）。

## 結果

- ccusage 版本：20.0.35
- 2026-10-11 ～ 2026-10-18 共 8 天：約 **9.99 億 tokens**，等值 API 費用約 **US$478.83**
- 最高的一天是 10/17（1.85 億 tokens、US$90.28）
- token 絕大部分是 **cache read**（快取讀取），單價低；實際輸入／輸出 token 只占一小部分
- 用的是 Max 訂閱，這個金額是「如果走 API 要付多少」的估算，不是實際帳單

## 和書上做法的差異

| 項目 | 書上 | 本次 |
| --- | --- | --- |
| 輸出格式 | 直接看 ccusage 的彩色表格 | 用 `--json` + Python 只留日期／Tokens／Cost，表格較窄、好存檔 |
| ccusage 版本 | 書出版時的舊版，只算 Claude Code | 20.x 新版，`daily` 會彙總多種 coding agent（Codex、Gemini CLI 等），另多了 `weekly`、`statusline` 子指令 |
| 模型 | 書中例子多為 Sonnet／Opus 4 系列 | 實際用到 claude-opus-5-5／sonnet-5-5／haiku-5-5 |
| GLM／Ollama | 書上實際設定並切換 | 只寫步驟、沒改環境變數，避免影響訂閱計費與其他 session |

## 已知未處理

- usage.txt 是當下快照，今天（10/18）的數字還會增加。
- COST-NOTES.md 中 GLM 端點網址與模型名稱以廠商當時文件為準，未實測。
