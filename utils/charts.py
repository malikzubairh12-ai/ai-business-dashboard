"""
utils/charts.py
---------------
Plotly chart factory functions.
Each function returns a go.Figure ready for st.plotly_chart().
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Consistent color palette
COLORS = [
    "#6366f1", "#06b6d4", "#f59e0b", "#10b981",
    "#f43f5e", "#8b5cf6", "#14b8a6", "#f97316",
]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=12, color="#e2e8f0"),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


def bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> go.Figure:
    """Vertical bar chart."""
    fig = px.bar(
        df, x=x_col, y=y_col,
        title=title,
        color_discrete_sequence=COLORS,
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_traces(marker_line_width=0)
    return fig


def pie_chart(df: pd.DataFrame, names_col: str, values_col: str, title: str) -> go.Figure:
    """Donut pie chart."""
    fig = px.pie(
        df, names=names_col, values=values_col,
        title=title,
        color_discrete_sequence=COLORS,
        hole=0.4,
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> go.Figure:
    """Smooth area line chart for time series."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x_col], y=df[y_col],
        mode="lines+markers",
        line=dict(color=COLORS[0], width=2.5, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.15)",
        marker=dict(size=6, color=COLORS[0]),
        name=y_col,
    ))
    fig.update_layout(title=title, xaxis_title=x_col, yaxis_title=y_col, **LAYOUT_DEFAULTS)
    return fig


def horizontal_bar(df: pd.DataFrame, x_col: str, y_col: str, title: str) -> go.Figure:
    """Horizontal bar chart — ideal for top-N rankings."""
    fig = px.bar(
        df.sort_values(x_col), x=x_col, y=y_col,
        orientation="h",
        title=title,
        color_discrete_sequence=COLORS,
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_traces(marker_line_width=0)
    return fig


def scatter_chart(df: pd.DataFrame, x_col: str, y_col: str, color_col: str | None, title: str) -> go.Figure:
    """Scatter plot with optional color grouping."""
    fig = px.scatter(
        df, x=x_col, y=y_col,
        color=color_col,
        title=title,
        color_discrete_sequence=COLORS,
        opacity=0.8,
    )
    fig.update_layout(**LAYOUT_DEFAULTS)
    return fig
