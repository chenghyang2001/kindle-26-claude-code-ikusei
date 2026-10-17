"""PreToolUse hook：阻擋 Edit/Write 寫入 .env 檔（exit 2 = 拒絕執行該工具）。"""
import json
import os
import sys

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path", "")
name = os.path.basename(path)
if name == ".env" or name.startswith(".env."):
    print(
        f"已阻擋：禁止寫入 {name}（{path}）。.env 存放機密，請改用 .env.example 或手動編輯。",
        file=sys.stderr,
    )
    sys.exit(2)
sys.exit(0)
