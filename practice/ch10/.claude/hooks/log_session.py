"""SessionStart hook：把目前時間與啟動來源追加寫進專案根目錄的 hook.log。"""
import datetime
import json
import os
import sys

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    data = {}
root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
now = datetime.datetime.now().isoformat(timespec="seconds")
with open(os.path.join(root, "hook.log"), "a", encoding="utf-8") as f:
    f.write(f"{now} SessionStart source={data.get('source', '?')}\n")
sys.exit(0)
