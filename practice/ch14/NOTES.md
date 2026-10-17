# K26 第 14 章練習筆記：Subagent 子代理

## 做了什麼

1. **建立專案層級子代理**（只放在 `.claude/agents/`，沒動全域 `~/.claude/agents/`）
   - `code-reviewer.md`：tools 只給 `Read, Grep, Glob`（唯讀），model `sonnet`
   - `debugger.md`：tools 給 `Read, Edit, Bash, Grep, Glob`，model `sonnet`
2. **寫有 bug 的 `calc.py` 並 commit 當起點**（`3c04e47`）
   - `average([])` 除以零 → `ZeroDivisionError`
   - `last_n(xs, n)` 切片起點多減 1（off-by-one），會多回傳一個元素
   - 起點測試：3 個測試裡 1 個失敗、1 個錯誤
3. **code-reviewer 審查**：找出 2 個 🔴 必改（就是上面兩個 bug），另外提出 🟡 `n<=0`、`n` 大於長度的邊界問題，以及 🟢 過時註解、缺少邊界測試
4. **debugger 修正**：先重現 → 說明根因 → 最小修正 → 補 2 個邊界測試 → 5 個測試全過（`1704c9e`）
5. **git worktree 平行開發**
   - `git worktree add ../k26-ch14-wt-a -b feat-a`：子代理 A 新增 `median()` 與 4 個測試（`7cd513a`）
   - `git worktree add ../k26-ch14-wt-b -b feat-b`：子代理 B 新增 argparse CLI（`avg` / `last` 子命令）與 `test_cli.py`（`78d29ef`）
   - 兩個子代理**同時**派出，各自在自己的 worktree commit
6. **合併與清理**：`git merge --no-ff` 依序合併 feat-a、feat-b，沒有衝突；12 個測試全過；`git worktree remove` 兩個工作區，`git branch -d` 刪除分支

## 結果

```
$ python calc.py avg 1 2 3 4
2.5
$ python calc.py last 2 1 2 3 4 5
[4.0, 5.0]
$ python -m unittest test_calc test_cli
Ran 12 tests ... OK
```

commit 圖：

```
*   492e110 合併 feat-b：CLI 參數介面
|\
| * 78d29ef 新增 calc.py 命令列參數介面
* |   e81efef 合併 feat-a：median 函式
|\ \
| * | 7cd513a 新增 median 中位數函式
|/ /
* 1704c9e 修復 average 除以零與 last_n off-by-one（debugger 子代理）
* 3c04e47 新增有 bug 的 calc.py 與專案子代理定義（起點）
```

## 和書上做法的差異

| 項目 | 書上做法 | 本次做法 | 原因 |
| --- | --- | --- | --- |
| 建立子代理 | 用 `/agents` 互動選單建立 | 直接寫 `.claude/agents/*.md` | 全自動執行，不走互動 UI；結果一樣是帶 YAML frontmatter 的 md 檔 |
| 呼叫子代理 | 用名稱呼叫（如「用 code-reviewer 審查」） | 用 general-purpose 代理，提示裡要它先讀 agent 定義檔、照其 system prompt 與工具限制執行 | agent 檔在 session 中途才建立，本 session 不會重新載入；而且全域已有同名的 `code-reviewer`，直接呼叫會用到全域版本。重開 session 後專案版本會優先 |
| 工具限制 | 由 frontmatter 的 `tools` 強制 | 靠提示要求遵守（軟限制） | 同上；正式使用時請重開 session，讓 frontmatter 真正生效 |
| worktree 平行開發 | 開兩個終端機，各跑一個 Claude session | 一個主 session 平行派兩個子代理，各自 `cd` 到自己的 worktree | 示範「主代理指揮、子代理分工」；效果相同，都靠 worktree 隔離工作目錄 |
| 避免合併衝突 | 書上沒特別處理 | 派工時指定改動位置（A 只動函式區、B 只動 `__main__` 區並另開測試檔） | 兩個功能都改 `calc.py`，事先劃分範圍就能自動合併 |
| 測試框架 | 常見 pytest | `unittest` | 免安裝 |

## 已知限制（快速模式，未經 QA／審查）

- 合併 commit 是主代理用 `git merge` 產生，未附 Co-Authored-By 尾註
- CLI 數字一律用 float 解析，`last` 輸出會是 `[4.0, 5.0]` 而不是 `[4, 5]`
- 未 push（依指示）
