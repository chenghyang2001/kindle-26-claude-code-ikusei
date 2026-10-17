#!/bin/bash
# 共用函式：被 01~04 腳本 source 進來
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$PROJECT_ROOT/out"
mkdir -p "$OUT_DIR"

# 在 Claude Code session 裡再呼叫 claude -p 會被當成巢狀 session，
# 所以把所有 CLAUDE 開頭的環境變數用 env -u 清掉（動態列出，不寫死名稱）
run_claude() {
  local unset_args=()
  local var_name
  for var_name in $(compgen -e | grep '^CLAUDE' || true); do
    unset_args+=(-u "$var_name")
  done
  env "${unset_args[@]}" claude "$@"
}

# Windows 版 Python 看不懂 /c/Users/... 這種 Git Bash 路徑，要轉成 C:\...
win_path() {
  if command -v cygpath >/dev/null; then cygpath -w "$1"; else echo "$1"; fi
}

command -v claude >/dev/null || { echo "錯誤：找不到 claude 指令" >&2; exit 1; }
