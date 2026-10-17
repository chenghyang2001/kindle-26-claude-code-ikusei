"""資料模型與輸入解析／驗證。"""

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation

CENT = Decimal("0.01")
_MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class LedgerError(Exception):
    """使用者可理解的錯誤（CLI 會轉成 stderr 訊息與結束碼 1）。"""


@dataclass(frozen=True)
class Expense:
    id: int
    date: date
    amount: Decimal
    category: str
    note: str = ""

    @property
    def month(self) -> str:
        return self.date.strftime("%Y-%m")

    def to_dict(self) -> dict:
        # 金額存字串，避免 JSON number 讀回時變成 float（憲章原則 IV）
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "amount": f"{self.amount:.2f}",
            "category": self.category,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, raw: dict) -> "Expense":
        try:
            return cls(
                id=int(raw["id"]),
                date=date.fromisoformat(raw["date"]),
                amount=parse_amount(str(raw["amount"])),
                category=str(raw["category"]),
                note=str(raw.get("note", "")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise LedgerError(f"資料檔紀錄格式錯誤：{raw!r}") from exc


def parse_amount(raw: str) -> Decimal:
    """解析金額：必須 > 0 且至多 2 位小數。"""
    try:
        value = Decimal(raw.strip())
    except (InvalidOperation, AttributeError):
        raise LedgerError(f"金額必須是數字：{raw!r}") from None
    if not value.is_finite():
        raise LedgerError(f"金額必須是數字：{raw!r}")
    if value <= 0:
        raise LedgerError(f"金額必須大於 0：{raw}")
    if value != value.quantize(CENT):
        raise LedgerError(f"金額最多 2 位小數：{raw}")
    return value.quantize(CENT)


def parse_date(raw: str | None) -> date:
    """解析 YYYY-MM-DD；未提供時回傳今天。"""
    if raw is None:
        return date.today()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise LedgerError(f"日期格式須為 YYYY-MM-DD：{raw}")
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise LedgerError(f"日期不存在：{raw}") from None


def parse_month(raw: str) -> str:
    """驗證 YYYY-MM 月份格式。"""
    if not _MONTH_RE.fullmatch(raw):
        raise LedgerError(f"月份格式須為 YYYY-MM：{raw}")
    return raw
