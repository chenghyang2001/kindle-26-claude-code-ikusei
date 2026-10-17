"""命令列介面：ledger add／list／total。"""

import argparse
import sys

from ledger.models import Expense, LedgerError
from ledger.service import add_expense, list_expenses, monthly_total
from ledger.storage import resolve_data_file


def _format_expense(expense: Expense) -> str:
    parts = [expense.date.isoformat(), expense.category, f"{expense.amount:.2f}"]
    if expense.note:
        parts.append(expense.note)
    return "  ".join(parts)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ledger", description="命令列記帳小工具")
    parser.add_argument("--file", help="資料檔路徑（預設 $LEDGER_FILE 或 ~/.ledger/ledger.json）")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="新增一筆支出")
    add.add_argument("amount", help="金額，> 0，最多 2 位小數")
    add.add_argument("category", help="類別，例如 餐飲")
    add.add_argument("--note", default="", help="備註")
    add.add_argument("--date", help="日期 YYYY-MM-DD，預設今天")

    lst = sub.add_parser("list", help="列出紀錄")
    lst.add_argument("--month", help="只列出指定月份 YYYY-MM")

    total = sub.add_parser("total", help="月合計")
    total.add_argument("month", help="月份 YYYY-MM")
    return parser


def _run(args: argparse.Namespace) -> None:
    path = resolve_data_file(args.file)
    if args.command == "add":
        expense = add_expense(path, args.amount, args.category, args.note, args.date)
        print(f"已新增 #{expense.id}：{_format_expense(expense)}")
    elif args.command == "list":
        expenses = list_expenses(path, args.month)
        if not expenses:
            print("目前沒有紀錄")
        for expense in expenses:
            print(f"#{expense.id}  {_format_expense(expense)}")
    elif args.command == "total":
        total, by_category = monthly_total(path, args.month)
        print(f"{args.month} 合計：{total:.2f}")
        for category, amount in by_category.items():
            print(f"  {category}  {amount:.2f}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        _run(args)
    except LedgerError as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
