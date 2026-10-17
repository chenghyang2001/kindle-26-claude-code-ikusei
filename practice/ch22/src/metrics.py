"""指標計算：純函式，不依賴 Streamlit，方便測試。"""
import pandas as pd


def kpis(df: pd.DataFrame) -> dict:
    """總營收、總銷量、平均單價；空資料回傳 0 而不是除以零。"""
    total_revenue = float(df["revenue"].sum())
    total_units = int(df["units"].sum())
    avg_price = total_revenue / total_units if total_units else 0.0
    return {"total_revenue": total_revenue, "total_units": total_units, "avg_price": avg_price}


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """每月營收與月增率（%），依月份排序。"""
    monthly = df.groupby("month", as_index=False)["revenue"].sum().sort_values("month")
    monthly["mom_pct"] = monthly["revenue"].pct_change() * 100
    return monthly.reset_index(drop=True)


def category_share(df: pd.DataFrame) -> pd.DataFrame:
    """各類別營收與占比（%）。"""
    by_cat = df.groupby("category", as_index=False)["revenue"].sum()
    total = by_cat["revenue"].sum()
    by_cat["share_pct"] = by_cat["revenue"] / total * 100 if total else 0.0
    return by_cat.sort_values("revenue", ascending=False).reset_index(drop=True)


def filter_sales(df: pd.DataFrame, categories: list[str] | None = None, month_range=None) -> pd.DataFrame:
    """依類別與月份區間（含頭尾）篩選；參數為 None 代表不篩。"""
    out = df
    if categories is not None:
        out = out[out["category"].isin(categories)]
    if month_range is not None:
        start, end = (pd.Timestamp(x) for x in month_range)
        out = out[(out["month"] >= start) & (out["month"] <= end)]
    return out
