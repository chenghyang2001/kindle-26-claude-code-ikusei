"""商業邏輯：新增、列出、月合計。"""

from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from ledger.models import CENT, Expense, LedgerError, parse_amount, parse_date, parse_month
from ledger.storage import load_expenses, save_expenses


def add_expense(
    path: Path,
    amount_text: str,
    category: str,
    note: str = "",
    date_text: str | None = None,
) -> Expense:
    # 先驗證全部輸入再讀寫檔案，確保非法輸入不會動到資料（FR-005）
    amount = parse_amount(amount_text)
    spent_on = parse_date(date_text)
    category = category.strip()
    if not category:
        raise LedgerError("類別不可為空")
    expenses = load_expenses(path)
    next_id = max((e.id for e in expenses), default=0) + 1
    expense = Expense(next_id, spent_on, amount, category, note.strip())
    save_expenses(path, [*expenses, expense])
    return expense


def list_expenses(path: Path, month: str | None = None) -> list[Expense]:
    expenses = load_expenses(path)
    if month is not None:
        month = parse_month(month)
        expenses = [e for e in expenses if e.month == month]
    return sorted(expenses, key=lambda e: (e.date, e.id))


def monthly_total(path: Path, month: str) -> tuple[Decimal, dict[str, Decimal]]:
    month_expenses = list_expenses(path, month=month)
    by_category: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for expense in month_expenses:
        by_category[expense.category] += expense.amount
    total = sum(by_category.values(), Decimal("0")).quantize(CENT)
    ordered = dict(sorted(by_category.items(), key=lambda kv: (-kv[1], kv[0])))
    return total, ordered
