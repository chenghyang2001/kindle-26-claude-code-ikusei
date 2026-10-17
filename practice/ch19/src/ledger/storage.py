"""JSON 帳本檔讀寫。"""

import json
import os
import tempfile
from pathlib import Path

from ledger.models import Expense, LedgerError

FORMAT_VERSION = 1
ENV_VAR = "LEDGER_FILE"


def resolve_data_file(explicit: str | None) -> Path:
    """資料檔位置優先序：--file > 環境變數 LEDGER_FILE > ~/.ledger/ledger.json。"""
    if explicit:
        return Path(explicit)
    env_value = os.environ.get(ENV_VAR)
    if env_value:
        return Path(env_value)
    return Path.home() / ".ledger" / "ledger.json"


def load_expenses(path: Path) -> list[Expense]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LedgerError(f"無法讀取資料檔 {path}：{exc}") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("expenses"), list):
        raise LedgerError(f"資料檔格式錯誤（缺少 expenses 清單）：{path}")
    return [Expense.from_dict(item) for item in payload["expenses"]]


def save_expenses(path: Path, expenses: list[Expense]) -> None:
    """先寫同目錄暫存檔再 os.replace，避免寫到一半當機留下壞檔。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": FORMAT_VERSION, "expenses": [e.to_dict() for e in expenses]}
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".ledger-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except OSError as exc:
        Path(tmp_name).unlink(missing_ok=True)
        raise LedgerError(f"無法寫入資料檔 {path}：{exc}") from exc
