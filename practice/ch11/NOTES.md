# K26 第 11 章練習筆記：Plugins 外掛系統

## 做了什麼

1. 建立本機 marketplace `.claude-plugin/marketplace.json`（name：`k26-local`），以相對路徑 `./plugins/doc-gen` 指向外掛。
2. 外掛 `plugins/doc-gen/` 內含四種元件：
   - `.claude-plugin/plugin.json`：manifest（名稱、版本、作者）
   - `commands/readme.md`：提供 `/doc-gen:readme` 指令（外掛指令會自動加上 `外掛名:` 命名空間）
   - `skills/readme-style/SKILL.md`：README 格式規範 skill（章節順序、繁中、80 行內）
   - `hooks/hooks.json`：`PostToolUse` + matcher `Write`，寫一行時間戳到 `doc-gen-hook.log`
3. `claude plugin validate .` → 通過。
4. `claude plugin marketplace add ./ --scope project` → 成功（CLI 2.1.302 支援 `--scope`），寫入 **專案** `.claude/settings.json` 的 `extraKnownMarketplaces`（source 類型為 `directory`）。
5. `claude plugin install doc-gen@k26-local --scope project` → 成功，寫入 `.claude/settings.json` 的 `enabledPlugins`；`claude plugin list` 顯示 `Scope: project`、`Read from` 直接指向本專案目錄。
6. 實測：
   ```bash
   env -u CLAUDECODE -u CLAUDE_CODE_ENTRYPOINT claude -p "/doc-gen:readme" \
     --setting-sources project,local --permission-mode acceptEdits \
     --allowedTools "Read,Glob,Grep,Write,Bash(ls:*)" < /dev/null
   ```
   輸出「README.md 已產生（共 5 個章節…）」，`README.md` 章節順序完全符合 skill 規範；`doc-gen-hook.log` 出現一行 hook 紀錄 → **指令、skill、hook 三者皆生效**。
7. 清理：`claude plugin uninstall doc-gen@k26-local --scope project`、`claude plugin marketplace remove k26-local` 皆成功；專案 settings 只剩空物件，已刪除該檔。

## 結果與安全檢查

- `~/.claude/settings.json` 前後 sha256 相同（`a7e97811e3290152…`），未被修改。
- `~/.claude/plugins/known_marketplaces.json`、`installed_plugins.json` 前後 diff 無差異；user 層任何 plugins JSON 都找不到 `k26` 字樣，`marketplaces/` 也沒有殘留。
- **例外**：install 時 CLI 仍會把外掛複製一份到 user 層快取 `~/.claude/plugins/cache/k26-local/doc-gen/0.1.0/`（即使 `--scope project`）；uninstall 後只標記 `.orphaned_at` 而不立刻刪除。這不是設定檔，已手動 `rm -rf` 清掉。
- 結論：user scope 的**設定**完全沒被寫入；唯一碰到 user 目錄的是上述快取副本，已清除。

## 踩到的坑

- `--allowedTools` 是可變長參數，若把 prompt 放在它後面會被當成工具名吃掉，出現
  `Error: Input must be provided either through stdin or as a prompt argument`。解法：prompt 放在 `-p` 後面第一個位置。
- `-p` 非互動模式下 Write 需要權限，用 `--permission-mode acceptEdits` + `--allowedTools` 放行。

## 和書上做法的差異

- 書上多以互動式 `/plugin` 選單（或預設 user scope）加入 marketplace 與安裝；本練習全程用 CLI 子指令並明確指定 `--scope project`，避免汙染全域。
- `marketplace add --scope project` 不會把目錄複製進 `~/.claude/plugins/marketplaces/`，而是在專案 settings 宣告 `directory` 來源、原地讀取外掛，修改外掛檔案即時反映。
- 以 `--setting-sources project,local` 啟動，user 層設定（含使用者原本的外掛）不參與，實驗環境較乾淨。
- 本專案 CLAUDE.md 要求設定寫在 `settings.local.json`，但 `--scope project` 由 CLI 寫進 `.claude/settings.json`（`--scope local` 才會寫 local 檔）；由於練習結束已解除並刪除，未造成長期影響。
