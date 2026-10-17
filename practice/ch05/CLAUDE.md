# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

K26 第 5 章（斜線指令系統）的練習 repo。內容刻意保持極小：目前只有 `hello.py`（印出 `Hello, Claude Code`），用來演練各種斜線指令，不是正式專案。

## 常用指令

```bash
# 執行（Windows 須加 PYTHONUTF8=1）
PYTHONUTF8=1 python hello.py
```

沒有建置步驟、相依套件、lint 設定或測試套件；冒煙測試就是執行 `hello.py` 並確認輸出。

## 慣例

- 本機分支為 `master`，尚未設定 remote，只在本機 commit，不 push。
- `.claude/session-state.md` 由 hook 自動產生，不要 commit。

## 本專案例外

本專案是 Kindle 書籍教學 demo（kindle-drill 快速模式），豁免全域「程式碼三 agent 鐵律」：主 Claude 直接寫檔，不派 code-writer／code-qa／code-reviewer；不需詢問複雜度，也不需詢問是否使用快速模式（已選快速模式）。
所有選擇題一律採用推薦選項、不要停下來問使用者；不可修改全域 `~/.claude/settings.json`，設定一律寫在本專案的 `.claude/settings.local.json`。
