"""PostToolUse hook：Edit/Write 完成後，若目標是 .py 檔就跑 py_compile 檢查語法。"""
import json
import subprocess
import sys

data = json.load(sys.stdin)
path = (data.get("tool_input") or {}).get("file_path", "")
if not path.endswith(".py"):
    sys.exit(0)

result = subprocess.run(
    [sys.executable, "-m", "py_compile", path],
    capture_output=True, text=True,
)
if result.returncode != 0:
    # exit 2：把 stderr 回饋給 Claude，讓它知道語法有錯
    print(f"[py_compile 失敗] {path}\n{result.stderr}", file=sys.stderr)
    sys.exit(2)
print(f"[py_compile 通過] {path}")
sys.exit(0)
