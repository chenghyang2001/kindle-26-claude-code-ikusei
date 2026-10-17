#!/bin/bash
# 示範 1：claude -p 單次分析一個小檔案（把檔案內容放進 prompt，不讓它用工具）
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

target_file="$PROJECT_ROOT/sample.py"
[ -f "$target_file" ] || { echo "錯誤：找不到 $target_file" >&2; exit 1; }

prompt="請用繁體中文分析以下 Python 程式，列出最多 3 個問題與修正建議，精簡回答：

$(cat "$target_file")"

run_claude -p "$prompt" < /dev/null | tee "$OUT_DIR/01-analyze.txt"
echo "[01] 已輸出到 out/01-analyze.txt"
