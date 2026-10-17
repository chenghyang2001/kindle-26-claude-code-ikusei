"""metrics 模組的測試：正常、邊界、篩選。"""
import pandas as pd
import pytest

from src.load import load_sales
from src.metrics import category_share, filter_sales, kpis, monthly_revenue


@pytest.fixture
def df():
    return load_sales()


def test_shape(df):
    assert len(df) == 36  # 12 個月 × 3 類別


def test_kpis(df):
    k = kpis(df)
    assert k["total_revenue"] == pytest.approx(df["revenue"].sum())
    assert k["avg_price"] == pytest.approx(k["total_revenue"] / k["total_units"])


def test_kpis_empty(df):
    k = kpis(df.iloc[0:0])
    assert k == {"total_revenue": 0.0, "total_units": 0, "avg_price": 0.0}


def test_monthly(df):
    m = monthly_revenue(df)
    assert len(m) == 12
    assert pd.isna(m.loc[0, "mom_pct"])
    assert m["revenue"].sum() == pytest.approx(df["revenue"].sum())


def test_share_sums_100(df):
    assert category_share(df)["share_pct"].sum() == pytest.approx(100)


def test_filter(df):
    out = filter_sales(df, ["食品"], ("2025-03-01", "2025-05-01"))
    assert set(out["category"]) == {"食品"}
    assert len(out) == 3


def test_invalid_months():
    with pytest.raises(ValueError):
        load_sales(months=0)
