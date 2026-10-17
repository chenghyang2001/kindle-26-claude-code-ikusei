"""服務層測試：add／list／total。"""

from datetime import date
from decimal import Decimal

from ledger.service import add_expense, list_expenses, monthly_total
from ledger.storage import load_expenses


def _seed(data_file):
    add_expense(data_file, "120", "餐飲", note="午餐", date_text="2026-10-01")
    add_expense(data_file, "300", "交通", date_text="2026-10-05")
    add_expense(data_file, "80", "餐飲", date_text="2026-10-03")
    add_expense(data_file, "500", "房租", date_text="2026-09-30")


# --- US1 新增 ---
def test_add_creates_file_and_increments_id(data_file):
    first = add_expense(data_file, "120", "餐飲", note="午餐", date_text="2026-10-01")
    second = add_expense(data_file, "50", "飲料")
    assert (first.id, second.id) == (1, 2)
    assert second.date == date.today()
    assert len(load_expenses(data_file)) == 2


def test_add_strips_category(data_file):
    assert add_expense(data_file, "1", "  交通 ").category == "交通"


def test_add_rejects_blank_category(data_file):
    import pytest

    from ledger.models import LedgerError

    with pytest.raises(LedgerError):
        add_expense(data_file, "1", "   ")
    assert not data_file.exists()


# --- US2 列出 ---
def test_list_sorted_by_date(data_file):
    _seed(data_file)
    dates = [e.date.isoformat() for e in list_expenses(data_file)]
    assert dates == ["2026-09-30", "2026-10-01", "2026-10-03", "2026-10-05"]


def test_list_filter_by_month(data_file):
    _seed(data_file)
    assert len(list_expenses(data_file, month="2026-10")) == 3
    assert list_expenses(data_file, month="2026-08") == []


# --- US3 月合計 ---
def test_monthly_total_with_categories(data_file):
    _seed(data_file)
    total, by_category = monthly_total(data_file, "2026-10")
    assert total == Decimal("500.00")
    assert by_category == {"交通": Decimal("300.00"), "餐飲": Decimal("200.00")}
    assert list(by_category) == ["交通", "餐飲"]  # 依金額由大到小


def test_monthly_total_decimal_exact(data_file):
    add_expense(data_file, "0.1", "零食", date_text="2026-10-01")
    add_expense(data_file, "0.2", "零食", date_text="2026-10-02")
    total, _ = monthly_total(data_file, "2026-10")
    assert total == Decimal("0.30")


def test_monthly_total_empty(data_file):
    assert monthly_total(data_file, "2026-10") == (Decimal("0.00"), {})
