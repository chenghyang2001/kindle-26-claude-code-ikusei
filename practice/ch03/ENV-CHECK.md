# 環境檢查（K26 第 3 章）

檢查日期：2026-10-18　機器：Windows 10 Home 19045（Git Bash）

## 工具版本

| 工具 | 指令 | 結果 |
| --- | --- | --- |
| Claude Code | `claude --version` | 2.1.302 (Claude Code) |
| Node.js | `node --version` | v24.13.1 |
| Git | `git --version` | 2.50.1.windows.1 |
| GitHub CLI | `gh --version` | 2.86.0 (2026-01-21) |

## 書上的三種安裝方式

| # | 方式 | 典型指令 | 本機？ |
| --- | --- | --- | --- |
| 1 | 原生安裝腳本 | macOS/Linux：`curl -fsSL https://claude.ai/install.sh \| bash`；Windows：`irm https://claude.ai/install.ps1 \| iex` | ❌ 未使用（`~/.local/bin` 沒有 `claude.exe`） |
| 2 | npm 全域安裝 | `npm install -g @anthropic-ai/claude-code` | ✅ **本機實際使用這種** |
| 3 | 套件管理器 | Windows：`winget install Anthropic.ClaudeCode`；macOS：`brew install --cask claude-code` | ❌ 未使用 |

## 判斷依據

```text
$ where claude
%APPDATA%\npm\claude
%APPDATA%\npm\claude.cmd

$ npm ls -g --depth=0 | grep claude
+-- @anthropic-ai/claude-code@2.1.302
```

- `claude` 位於 npm 全域目錄 `%APPDATA%\npm\`，且 `npm ls -g` 列出 `@anthropic-ai/claude-code`，可確定是 npm 安裝。
- `winget list` 有一筆 `Anthropic.Claude`（2.42304.0.0），那是 **Claude 桌面 App**，不是 Claude Code CLI，不影響判斷。
