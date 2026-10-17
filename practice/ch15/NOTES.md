# K26 第 15 章練習筆記：輸出樣式（Output Style）

## 做了什麼

1. 建立專案層級輸出樣式 `.claude/output-styles/prd-writer.md`
   - frontmatter：`name: PRD Writer`、`description`、`keep-coding-instructions: false`
   - 內文規定固定六段：背景、目標、使用者故事、功能需求、非功能需求、驗收條件，並附寫作規則（可量化、無開場白、資訊不足時列假設、不寫程式碼）。
2. 在 `.claude/settings.local.json` 設 `"outputStyle": "PRD Writer"`（只影響本專案、本機，不動全域 `~/.claude/`）。
3. 在 session 內執行巢狀 `claude -p`：
   ```bash
   env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT ...（所有 CLAUDE* 變數） \
     claude -p "為一個番茄鐘小工具寫 PRD" < /dev/null > prd-pomodoro.md
   ```
   - 用迴圈抓出 `env` 中所有 `CLAUDE` 開頭變數逐一 `-u`，共 13 個。
   - `< /dev/null` 避免 `-p` 等 stdin。
4. 產出 `prd-pomodoro.md`（112 行）。

## 結果

- 六個章節標題與順序完全照樣式：`## 1. 背景` … `## 6. 驗收條件`。
- 規則有被遵守：背景末尾有「假設」小節、目標有可量化指標與「非目標」、使用者故事 9 則標 P0/P1/P2、FR-01～14、NFR-01～11（含驗證方式）、AC-01～23 用 Given/When/Then 並對應 FR/NFR 編號。
- 沒有開場白或結尾客套話 → 證明 output style 確實換掉了預設的 system prompt 行為。
- 小插曲：Windows 下 `claude -p` 輸出到檔案時，結尾多了一行不完整的重複位元組（UTF-8 解碼失敗），已用 Python 移除該殘段行。

## 和內建樣式的差異

| 項目 | Default | Explanatory（內建） | Learning（內建） | PRD Writer（本練習自訂） |
| --- | --- | --- | --- | --- |
| 目的 | 有效率完成軟體工程任務 | 完成任務的同時解釋「為什麼這樣做」 | 協作式教學，讓使用者自己動手 | 把任何需求轉成結構化 PRD |
| 輸出特徵 | 精簡回報 | 穿插「★ Insight」區塊說明實作選擇與程式碼模式 | 除了 Insight，還會留 `TODO(human)` 要使用者自己寫關鍵程式碼 | 固定六段標題、表格、編號、Given/When/Then |
| 是否保留寫程式指令 | 是 | 是（加上說明） | 是（加上教學互動） | 否（`keep-coding-instructions: false`，專注文件） |
| 適合情境 | 日常開發 | 想理解 codebase 或學新技術時 | 想練手、邊做邊學 | PM／規格撰寫、需求先行 |
| 互動性 | 低 | 低（單向解說） | 高（會停下來等你寫） | 無（一次輸出完整文件） |

重點：Explanatory／Learning 是「在原本工程行為上**加料**」，PRD Writer 是「**換掉**主要行為，改成固定文件格式」。

## 和書上做法的差異

- **樣式放專案層而非全域**：書上常示範放 `~/.claude/output-styles/`；本練習照要求放 `.claude/output-styles/`，避免影響其他專案。
- **用設定檔而不是 `/output-style` 指令切換**：書上多半在互動模式用 `/output-style` 選單切換；這裡直接寫 `settings.local.json` 的 `outputStyle`，讓非互動的 `claude -p` 也套用。
- **巢狀呼叫的環境處理**：書上是在一般終端機執行 `claude -p`；本練習是在 Claude Code session 裡呼叫，所以要先清掉所有 `CLAUDE*` 環境變數並把 stdin 接 `/dev/null`。
- **輸出後處理**：書上不會遇到；Windows 管線造成結尾殘段，需要額外清理。
- 快速 demo 模式：未經 QA／審查流程。

## 版控說明

`.claude/settings.local.json` 被全域 `.gitignore` 排除（本機設定慣例），因此沒有 commit。內容只有一行：

```json
{ "outputStyle": "PRD Writer" }
```

若要讓團隊共用，可改寫到 `.claude/settings.json`。
