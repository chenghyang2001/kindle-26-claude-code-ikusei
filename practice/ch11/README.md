# k26-ch11-practice

K26 第 11 章練習用的本機 Claude Code plugin marketplace，內含一個產生專案 `README.md` 的 `doc-gen` 外掛。

## 目錄結構

```
k26-ch11-practice/
├── .claude-plugin/
│   └── marketplace.json          # 本機 marketplace 定義（k26-local）
├── .claude/
│   └── settings.json             # 專案層設定：登錄 marketplace 並啟用外掛
├── plugins/
│   └── doc-gen/
│       ├── .claude-plugin/
│       │   └── plugin.json       # 外掛 manifest
│       ├── commands/
│       │   └── readme.md         # /doc-gen:readme 斜線指令
│       ├── skills/
│       │   └── readme-style/
│       │       └── SKILL.md      # README 格式規範 skill
│       └── hooks/
│           └── hooks.json        # PostToolUse hook（Write 後寫 log）
└── CLAUDE.md                     # 專案說明與例外規則
```

## 使用方式

1. 在本專案目錄啟動 Claude Code，`.claude/settings.json` 會自動登錄 `k26-local` marketplace 並啟用 `doc-gen@k26-local`。
2. 執行斜線指令產生 README：

   ```
   /doc-gen:readme [額外說明]
   ```

3. Claude 會掃描專案結構，依 `readme-style` 規範寫入根目錄的 `README.md`。
4. 每次 Write 工具執行後，hook 會在專案根目錄的 `doc-gen-hook.log` 追加一行時間戳記錄。

## 元件說明

| 元件 | 類型 | 說明 |
| --- | --- | --- |
| `marketplace.json` | Marketplace | 名稱 `k26-local`，列出 `doc-gen` 外掛（版本 0.1.0） |
| `plugin.json` | Manifest | 外掛名稱、版本與作者資訊 |
| `commands/readme.md` | Command | 掃描專案並產生（或覆寫）`README.md`，限定可用工具為 Read、Glob、Grep、Write 及部分 Bash |
| `skills/readme-style` | Skill | README 格式規範：繁體中文、固定章節順序、80 行以內、不捏造功能 |
| `hooks/hooks.json` | Hook | `PostToolUse` 比對 `Write`，將執行時間寫入 `doc-gen-hook.log` |
| `.claude/settings.json` | 設定 | `extraKnownMarketplaces` 與 `enabledPlugins` |

## 授權

未指定
