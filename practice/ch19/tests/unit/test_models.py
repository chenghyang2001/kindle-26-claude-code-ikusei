"""金額／日期／月份解析測試。"""

from datetime import date
from decimal import Decimal

import pytest

from ledger.models import LedgerError, parse_amount, parse_date, parse_month


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("120", Decimal("120.00")), ("12.5", Decimal("12.50")), ("0.01", Decimal("0.01"))],
)
def test_parse_amount_ok(raw, expected):
    assert parse_amount(raw) == expected


@pytest.mark.parametrize("raw", ["abc", "0", "-5", "1.234", "", "NaN", "Infinity"])
def test_parse_amount_rejects_invalid(raw):
    with pytest.raises(LedgerError):
        parse_amount(raw)


def test_parse_date_default_today():
    assert parse_date(None) == date.today()


def test_parse_date_ok():
    assert parse_date("2026-10-01") == date(2026, 10, 1)


@pytest.mark.parametrize("raw", ["2026-02-30", "2026/10/01", "昨天"])
def test_parse_date_rejects_invalid(raw):
    with pytest.raises(LedgerError):
        parse_date(raw)


def test_parse_month_ok():
    assert parse_month("2026-10") == "2026-10"


@pytest.mark.parametrize("raw", ["2026-13", "10月", "2026-1", "2026-10-01"])
def test_parse_month_rejects_invalid(raw):
    with pytest.raises(LedgerError):
        parse_month(raw)
