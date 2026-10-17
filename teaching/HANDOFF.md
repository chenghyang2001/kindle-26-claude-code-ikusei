# K26 演練交接

## 原機器結果

本書沒有在其他機器演練過，沒有可比對的原機器結果。每章的差異以「和書上原做法的差異」記錄。

## 快速模式進度表

| 章 | 完成日 | 實際耗時 | 和書上做法的差異 |
| --- | --- | --- | --- |
| 01 | 2026-10-18 | 2 分 | 只寫 CONCEPTS.md；手邊無書原文，觀念與例子由 Claude 依一般知識整理 |
| 02 | 2026-10-18 | 1 分 | 只寫 ARCHITECTURE.md＋ASCII 迴圈圖；五大階段名稱沿用官方常見說法，沙箱未實測 |
| 03 | 2026-10-18 | 3 分 | ENV-CHECK.md＋claude -p 單次指令；需先清 CLAUDE* 環境變數避開巢狀限制，未進互動模式、未碰 /login |
| 04 | 2026-10-18 | 10 分 | 書上 fingerprints repo 改用 epic-flashcard-review；4 問＋實際啟動 curl 200＋/init＋npm run 記憶，Claude 另幫子專案補 start/test script；/init 建議的 /import 略過 |
| 05 | 2026-10-18 | 8 分 | 實測 13 個斜線指令＋五類速查表；2.1.302 已移除 /todos 與 /agents 精靈、/cost 改導 /usage；帳號與 /doctor /statusline 依限制略過 |
| 06 | 2026-10-18 | 5 分 | 4 支腳本實跑（單次／管道／JSON 取 result／--allowedTools Read 寫檔被擋）；需清 CLAUDE* 變數＋提供 stdin，--resume 只寫說明 |

## 環境備註（2026-10-18 Yama-Desktop）

- Claude Code 2.1.302（看門狗驗證版 2.1.295，開跑後確認 log 有「錨點校準通過」）
