"""JSON 儲存層測試。"""

import json
from datetime import date
from decimal import Decimal

import pytest

from ledger.models import Expense, LedgerError
from ledger.storage import load_expenses, resolve_data_file, save_expenses


def _sample():
    return [Expense(1, date(2026, 10, 1), Decimal("120.00"), "餐飲", "午餐")]


def test_missing_file_is_empty(data_file):
    assert load_expenses(data_file) == []


def test_round_trip_keeps_chinese_and_decimal(data_file):
    save_expenses(data_file, _sample())
    assert load_expenses(data_file) == _sample()
    raw = data_file.read_text(encoding="utf-8")
    assert "餐飲" in raw  # ensure_ascii=False，人類可讀
    assert json.loads(raw)["expenses"][0]["amount"] == "120.00"


def test_save_creates_parent_dir(tmp_path):
    target = tmp_path / "nested" / "ledger.json"
    save_expenses(target, _sample())
    assert target.exists()


@pytest.mark.parametrize("content", ["{not json", '{"version": 1}', '{"expenses": [{"id": 1}]}'])
def test_corrupted_file_raises_and_keeps_file(data_file, content):
    data_file.write_text(content, encoding="utf-8")
    with pytest.raises(LedgerError):
        load_expenses(data_file)
    assert data_file.read_text(encoding="utf-8") == content


def test_resolve_data_file_priority(tmp_path, monkeypatch):
    explicit = tmp_path / "a.json"
    env_file = tmp_path / "b.json"
    monkeypatch.setenv("LEDGER_FILE", str(env_file))
    assert resolve_data_file(str(explicit)) == explicit
    assert resolve_data_file(None) == env_file
    monkeypatch.delenv("LEDGER_FILE")
    assert resolve_data_file(None).name == "ledger.json"
