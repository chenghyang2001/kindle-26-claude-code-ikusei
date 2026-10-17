# 第 1 章練習筆記

日期：2026-10-18

## 做了什麼

1. 確認專案目錄現況：只有 `CLAUDE.md`（快速 demo 模式設定），git repo 尚無任何 commit。
2. 撰寫 `CONCEPTS.md`，分三段整理本章觀念：
   - Vibe Coding：定義、優點、風險，例子為「一句話做番茄鐘 HTML」。
   - LLM 運作原理：token 預測、context window、無狀態、隨機性、知識截止、tool use，例子為 `CLAUDE.md` 自動載入、`/compact`、透過 Bash 取得真實結果。
   - Spec Driven Development：流程、規格內容、與 Vibe Coding 對照表，例子為「先寫 `docs/spec.md` → Plan Mode → 依規格實作＋測試」。
3. 撰寫本檔 `NOTES.md`。
4. `git add CLAUDE.md CONCEPTS.md NOTES.md` 並 commit（依指示不 push）。

## 結果

- 產出 `CONCEPTS.md`、`NOTES.md` 兩份文件，與 `CLAUDE.md` 一起成為本 repo 的第一個 commit。
- 沒有安裝任何套件，也沒有寫任何程式碼檔。

## 和書上做法的差異

- **沒有書本原文可對照**：練習目錄裡沒有第 1 章的內容檔，`CONCEPTS.md` 是依本章三個主題的通用觀念整理，章節用語、例子細節可能與書中不同，之後可拿原書比對補正。
- **例子為自行設計**：每段的「在 Claude Code 裡怎麼體現」是用 Claude Code 實際功能（`CLAUDE.md`、`/compact`、Plan Mode、工具呼叫）舉例，不一定是書上的範例。
- **全自動執行**：依使用者指示不中途提問，所有選擇採預設推薦；書中若有「與 AI 來回討論需求」的步驟，本次省略。
- **不 push**：依指示只做本機 commit，未建立 GitHub repo。
