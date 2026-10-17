"""資料載入：產生 12 個月 × 3 類別的模擬銷售資料。"""
import numpy as np
import pandas as pd

CATEGORIES = ["電子產品", "服飾", "食品"]
BASE_REVENUE = {"電子產品": 120000, "服飾": 80000, "食品": 60000}


def load_sales(seed: int = 42, start: str = "2025-01-01", months: int = 12) -> pd.DataFrame:
    """回傳欄位為 month / category / units / revenue 的 DataFrame。"""
    if months <= 0:
        raise ValueError("months 必須大於 0")
    rng = np.random.default_rng(seed)
    rows = []
    for m in pd.date_range(start, periods=months, freq="MS"):
        for c in CATEGORIES:
            units = int(rng.integers(200, 600))
            revenue = BASE_REVENUE[c] * (1 + 0.03 * m.month) * rng.uniform(0.85, 1.15)
            rows.append({"month": m, "category": c, "units": units, "revenue": round(revenue, 2)})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print(load_sales().head())
