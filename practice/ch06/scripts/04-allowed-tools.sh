#!/bin/bash
# 示範 4：--allowedTools "Read" 只允許讀檔，要求它寫檔，確認被擋
set -euo pipefail
source "$(dirname "$0")/_lib.sh"

forbidden_file="$OUT_DIR/should-not-exist.txt"
rm -f "$forbidden_file"
log_file="$OUT_DIR/04-allowed-tools.txt"

# 明確指定 --permission-mode default：本機全域 defaultMode 是 auto，
# 不指定的話 auto 模式可能自動放行 Write，就測不到 --allowedTools 的效果
cd "$PROJECT_ROOT"
run_claude -p "請用 Write 工具建立檔案 out/should-not-exist.txt，內容寫 hello。完成後回報是否成功。" \
  --allowedTools "Read" \
  --permission-mode default \
  --output-format json < /dev/null > "$OUT_DIR/04-allowed-tools-raw.json" || true

{
  echo "=== claude 的回覆 ==="
  PYTHONUTF8=1 python -c "
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding='utf-8'))
except (OSError, json.JSONDecodeError) as exc:
    sys.exit(f'無法解析 JSON：{exc}')
print(data.get('result'))
print('permission_denials =', json.dumps(data.get('permission_denials', []), ensure_ascii=False))
" "$(win_path "$OUT_DIR/04-allowed-tools-raw.json")"
  echo
  echo "=== 驗證 ==="
  if [ -f "$forbidden_file" ]; then
    echo "失敗：檔案被建立了（Write 沒被擋）"
  else
    echo "成功：out/should-not-exist.txt 不存在，Write 被擋下"
  fi
} | tee "$log_file"

[ ! -f "$forbidden_file" ]
