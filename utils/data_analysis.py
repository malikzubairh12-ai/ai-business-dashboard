"""
utils/data_analysis.py
-----------------------
Helper functions for CSV loading, cleaning, and statistical analysis.
All functions return clean DataFrames or dicts ready for display.
"""

import pandas as pd
import numpy as np
from io import StringIO


def load_csv(uploaded_file) -> pd.DataFrame:
    """Load an uploaded Streamlit file object into a DataFrame."""
    try:
        content = uploaded_file.read().decode("utf-8")
        df = pd.read_csv(StringIO(content))
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        raise ValueError(f"Could not read CSV: {e}")


def detect_numeric_columns(df: pd.DataFrame) -> list[str]:
    """Return a list of numeric column names."""
    return df.select_dtypes(include=[np.number]).columns.tolist()


def detect_date_column(df: pd.DataFrame) -> str | None:
    """Try to detect and parse a date column. Returns column name or None."""
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
                return col
            except Exception:
                pass
    return None


def get_summary_stats(df: pd.DataFrame) -> dict:
    """
    Compute high-level KPIs from the DataFrame.
    Returns a dict with keys: total_revenue, avg_order, top_product,
    top_customer, total_rows, num_columns.
    """
    stats = {
        "total_rows": len(df),
        "num_columns": len(df.columns),
    }

    numeric_cols = detect_numeric_columns(df)

    # Try to find a revenue-like column
    revenue_col = next(
        (c for c in numeric_cols if "revenue" in c.lower() or "total" in c.lower() or "amount" in c.lower()),
        numeric_cols[0] if numeric_cols else None,
    )

    if revenue_col:
        stats["revenue_col"] = revenue_col
        stats["total_revenue"] = df[revenue_col].sum()
        stats["avg_order"] = df[revenue_col].mean()
        stats["max_order"] = df[revenue_col].max()
        stats["min_order"] = df[revenue_col].min()

    # Top product/item
    for col in df.columns:
        if "product" in col.lower() or "item" in col.lower() or "name" in col.lower():
            if revenue_col:
                top = df.groupby(col)[revenue_col].sum().idxmax()
                stats["top_product_col"] = col
                stats["top_product"] = top
            break

    # Top customer
    for col in df.columns:
        if "customer" in col.lower() or "client" in col.lower():
            if revenue_col:
                top_cust = df.groupby(col)[revenue_col].sum().idxmax()
                stats["top_customer_col"] = col
                stats["top_customer"] = top_cust
            break

    return stats


def get_monthly_revenue(df: pd.DataFrame, date_col: str, revenue_col: str) -> pd.DataFrame:
    """Aggregate revenue by month. Returns a DataFrame with Month and Revenue columns."""
    temp = df.copy()
    temp["Month"] = pd.to_datetime(temp[date_col]).dt.to_period("M").astype(str)
    monthly = temp.groupby("Month")[revenue_col].sum().reset_index()
    monthly.columns = ["Month", "Revenue"]
    monthly = monthly.sort_values("Month")
    return monthly


def get_category_breakdown(df: pd.DataFrame, category_col: str, revenue_col: str) -> pd.DataFrame:
    """Group revenue by a category column."""
    breakdown = df.groupby(category_col)[revenue_col].sum().reset_index()
    breakdown.columns = [category_col, "Revenue"]
    breakdown = breakdown.sort_values("Revenue", ascending=False)
    return breakdown


def get_top_n(df: pd.DataFrame, group_col: str, value_col: str, n: int = 5) -> pd.DataFrame:
    """Return top N rows by sum of value_col grouped by group_col."""
    top = df.groupby(group_col)[value_col].sum().nlargest(n).reset_index()
    top.columns = [group_col, value_col]
    return top


def build_data_summary_text(df: pd.DataFrame, stats: dict) -> str:
    """
    Build a compact plain-text summary of the dataset.
    This is passed to the OpenAI API as context.
    """
    lines = [
        f"Dataset: {stats['total_rows']} rows, {stats['num_columns']} columns.",
        f"Columns: {', '.join(df.columns.tolist())}.",
    ]

    if "total_revenue" in stats:
        col = stats["revenue_col"]
        lines.append(
            f"Total {col}: {stats['total_revenue']:,.2f}. "
            f"Average: {stats['avg_order']:,.2f}. "
            f"Max: {stats['max_order']:,.2f}."
        )

    if "top_product" in stats:
        lines.append(f"Top {stats['top_product_col']}: {stats['top_product']}.")

    if "top_customer" in stats:
        lines.append(f"Top {stats['top_customer_col']}: {stats['top_customer']}.")

    # Numeric column stats
    numeric_cols = detect_numeric_columns(df)
    for col in numeric_cols[:4]:
        lines.append(
            f"{col} — mean: {df[col].mean():,.2f}, std: {df[col].std():,.2f}, "
            f"min: {df[col].min():,.2f}, max: {df[col].max():,.2f}."
        )

    return " ".join(lines)
