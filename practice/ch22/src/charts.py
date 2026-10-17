"""圖表：只負責把指標結果畫成 Plotly Figure。"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def trend_chart(monthly: pd.DataFrame) -> go.Figure:
    """月營收趨勢折線圖。"""
    fig = px.line(monthly, x="month", y="revenue", markers=True, title="月營收趨勢")
    fig.update_layout(xaxis_title="月份", yaxis_title="營收")
    return fig


def share_chart(share: pd.DataFrame) -> go.Figure:
    """類別營收占比甜甜圈圖。"""
    return px.pie(share, names="category", values="revenue", hole=0.45, title="類別營收占比")
