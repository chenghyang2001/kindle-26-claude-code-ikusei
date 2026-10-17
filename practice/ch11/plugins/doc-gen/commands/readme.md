---
description: 掃描目前專案並產生（或覆寫）README.md
allowed-tools: Read, Glob, Grep, Write, Bash(ls:*), Bash(git log:*)
---

請為目前工作目錄的專案產生 `README.md`，遵循 `readme-style` skill 的格式規範。

步驟：
1. 用 Glob / Read 了解專案結構（略過 .git）。
2. 依 readme-style skill 的章節順序撰寫，內容一律繁體中文。
3. 用 Write 工具寫入專案根目錄的 `README.md`。
4. 完成後只回覆一行：「README.md 已產生」加上章節數。

額外說明（若有）：$ARGUMENTS
