"""用 nbformat 產生練習用的 sales.ipynb（模擬「重構前」的 notebook）。"""
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

CELL_LOAD = '''import numpy as np
import pandas as pd

# 固定亂數種子，讓每次產生的資料一樣
rng = np.random.default_rng(42)
months = pd.date_range("2025-01-01", periods=12, freq="MS")
categories = ["電子產品", "服飾", "食品"]
base = {"電子產品": 120000, "服飾": 80000, "食品": 60000}
rows = []
for m in months:
    for c in categories:
        units = int(rng.integers(200, 600))
        revenue = base[c] * (1 + 0.03 * m.month) * rng.uniform(0.85, 1.15)
        rows.append({"month": m, "category": c, "units": units, "revenue": round(revenue, 2)})
df = pd.DataFrame(rows)
df.head()'''

CELL_METRICS = '''total_revenue = df["revenue"].sum()
total_units = df["units"].sum()
avg_price = total_revenue / total_units
monthly = df.groupby("month", as_index=False)["revenue"].sum()
monthly["mom_pct"] = monthly["revenue"].pct_change() * 100
share = df.groupby("category")["revenue"].sum() / total_revenue * 100
print(f"總營收 {total_revenue:,.0f}，總銷量 {total_units:,}，平均單價 {avg_price:,.1f}")
monthly'''

CELL_CHARTS = '''import plotly.express as px

fig1 = px.line(monthly, x="month", y="revenue", markers=True, title="月營收趨勢")
fig1.show()
fig2 = px.pie(share.reset_index(name="share"), names="category", values="share", title="類別營收占比")
fig2.show()'''


def build_notebook() -> nbformat.NotebookNode:
    """組出三段式 notebook：載入、指標、圖表。"""
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell("# 銷售分析（重構前的 Notebook）"),
        new_markdown_cell("## 1. 載入資料"),
        new_code_cell(CELL_LOAD),
        new_markdown_cell("## 2. 指標計算"),
        new_code_cell(CELL_METRICS),
        new_markdown_cell("## 3. 圖表"),
        new_code_cell(CELL_CHARTS),
    ]
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    return nb


def main() -> None:
    try:
        out = Path(__file__).parent / "sales.ipynb"
        nb = build_notebook()
        nbformat.validate(nb)
        nbformat.write(nb, out)
        print(f"已產生 {out}（{len(nb.cells)} 個 cell）")
    except (OSError, nbformat.ValidationError) as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
