"""Streamlit 銷售儀表板：KPI 卡、月趨勢、類別占比、篩選器。"""
import streamlit as st

from src.charts import share_chart, trend_chart
from src.load import CATEGORIES, load_sales
from src.metrics import category_share, filter_sales, kpis, monthly_revenue

st.set_page_config(page_title="銷售儀表板", layout="wide")


@st.cache_data
def get_data():
    return load_sales()


st.title("銷售儀表板")
df = get_data()

with st.sidebar:
    st.header("篩選器")
    picked = st.multiselect("產品類別", CATEGORIES, default=CATEGORIES)
    months = sorted(df["month"].dt.date.unique())
    start, end = st.select_slider("月份區間", options=months, value=(months[0], months[-1]))

view = filter_sales(df, picked, (start, end))
if view.empty:
    st.warning("目前篩選條件沒有資料，請至少選一個類別。")
    st.stop()

k = kpis(view)
c1, c2, c3 = st.columns(3)
c1.metric("總營收", f"{k['total_revenue']:,.0f}")
c2.metric("總銷量", f"{k['total_units']:,}")
c3.metric("平均單價", f"{k['avg_price']:,.1f}")

left, right = st.columns([2, 1])
left.plotly_chart(trend_chart(monthly_revenue(view)), width="stretch")
right.plotly_chart(share_chart(category_share(view)), width="stretch")

with st.expander("明細資料"):
    st.dataframe(view, width="stretch")
