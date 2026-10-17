#!/bin/bash
# 示範 3：--output-format json，再用 Python 取出 result 欄位
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

raw_json="$OUT_DIR/03-json-raw.json"
run_claude -p "用一句繁體中文說明什麼是 JSON。" --output-format json < /dev/null > "$raw_json"

PYTHONUTF8=1 python - "$(win_path "$raw_json")" <<'PY' | tee "$OUT_DIR/03-json-result.txt"
import json
import sys

try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        payload = json.load(fh)
except (OSError, json.JSONDecodeError) as exc:
    print(f"錯誤：無法解析 JSON：{exc}", file=sys.stderr)
    sys.exit(1)

if payload.get("is_error"):
    print(f"錯誤：claude 回報失敗：{payload}", file=sys.stderr)
    sys.exit(1)

print("result =", payload.get("result"))
print("session_id =", payload.get("session_id"))
print("num_turns =", payload.get("num_turns"))
print("total_cost_usd =", payload.get("total_cost_usd"))
PY
echo "[03] 原始 JSON：out/03-json-raw.json；取出結果：out/03-json-result.txt"
