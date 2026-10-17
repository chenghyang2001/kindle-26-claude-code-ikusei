# K26 第 3 章練習筆記：安裝及基本使用

## 做了什麼

1. **環境檢查**：執行 `claude/node/git/gh --version` 與 `where claude`，結果寫在 [ENV-CHECK.md](ENV-CHECK.md)。
2. **單次指令測試**：建立 `claude-test/README.md`，在該資料夾執行：

   ```bash
   env -u CLAUDECODE <其他 CLAUDE 開頭變數也 -u 掉> \
     claude -p "這個資料夾是做什麼的？請用一句話回答" > answer.txt
   ```

3. **沒有執行** `/login`、`/logout`（沿用既有登入狀態）。

## 結果

- 四個工具都正常，Claude Code 版本 2.1.302，安裝方式為 **npm 全域安裝**。
- `claude -p` 結束碼 0，回答（存於 `claude-test/answer.txt`）：

  > 這是 K26 第 3 章「安裝及基本使用」的練習資料夾，用來測試 Claude Code 的單次指令模式（`claude -p`）能不能讀懂資料夾內容並回答問題。

  幾乎是 README 內容的改寫，表示它有讀到資料夾裡的檔案。

## 和書上做法的差異

| 項目 | 書上 | 本次實作 | 原因 |
| --- | --- | --- | --- |
| 安裝方式 | 推薦原生安裝腳本 | 沿用既有的 npm 全域安裝 | 本機早已用 npm 裝好，不重裝 |
| 登入 | 首次啟動跑 `/login` 用瀏覽器登入 | 跳過 | 已登入；練習規定不得 `/login`、`/logout` |
| 執行 `claude -p` | 直接在終端機輸入 | 先 `unset` `CLAUDECODE` 等 `CLAUDE*` 變數 | 本次是在 Claude Code session 裡再呼叫 `claude`，要避免巢狀執行限制 |
| 互動模式 | 書上會示範進入互動模式聊天 | 只做單次指令 `-p` | 全自動執行，無法人工互動 |

## 小觀察

- 在非互動 shell 裡跑 `claude -p` 會出現警告 `no stdin data received in 3s`，加上 `< /dev/null` 就能避免，不影響結果。
