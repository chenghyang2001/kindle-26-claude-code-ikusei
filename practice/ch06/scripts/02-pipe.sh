#!/bin/bash
# 示範 2：用管道把 prompt.txt 餵給 claude -p（stdin 就是 prompt）
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

prompt_file="$PROJECT_ROOT/prompt.txt"
[ -f "$prompt_file" ] || { echo "錯誤：找不到 $prompt_file" >&2; exit 1; }

cat "$prompt_file" | run_claude -p | tee "$OUT_DIR/02-pipe.txt"
echo "[02] 已輸出到 out/02-pipe.txt"
