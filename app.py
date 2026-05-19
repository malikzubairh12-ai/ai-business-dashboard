"""
app.py
------
AI Business Assistant Dashboard — main entry point.

Run with:
    streamlit run app.py

Features:
  1. CSV Upload & Data Preview
  2. Auto-generated statistics & KPI cards
  3. Plotly charts (bar, pie, line, scatter)
  4. AI Business Summary (OpenAI GPT)
  5. AI Email Generator (OpenAI GPT)
"""

import streamlit as st
import pandas as pd

from utils.data_analysis import (
    load_csv,
    detect_date_column,
    detect_numeric_columns,
    get_summary_stats,
    get_monthly_revenue,
    get_category_breakdown,
    get_top_n,
    build_data_summary_text,
)
from utils.charts import bar_chart, pie_chart, line_chart, horizontal_bar, scatter_chart
from utils.ai_client import generate_business_summary, generate_email_reply

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Business Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — dark professional theme
# ──────────────────────────────────────────────
st.markdown("""
<style>
/* Global font & background */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: 1px solid #1e293b;
}
[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}

/* Main area */
.main { background: #0f172a; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1rem;
}

/* Section headers */
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #94a3b8;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin: 1.5rem 0 0.5rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1e293b;
}

/* AI output box */
.ai-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    color: #e2e8f0;
    line-height: 1.7;
    white-space: pre-wrap;
}

/* Dividers */
hr { border-color: #1e293b !important; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.25rem;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# SESSION STATE defaults
# ──────────────────────────────────────────────
for key in ("df", "stats", "date_col", "numeric_cols", "data_text"):
    if key not in st.session_state:
        st.session_state[key] = None


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 AI Business Dashboard")
    st.markdown("---")

    # OpenAI API key input
    st.markdown("### 🔑 OpenAI API Key")
    api_key = st.text_input(
        "Paste your key",
        type="password",
        placeholder="sk-...",
        help="Your key is never stored. Used only for AI features.",
    )
    if api_key:
        st.success("Key loaded ✓", icon="✅")
    else:
        st.info("Add a key to unlock AI features.")

    st.markdown("---")

    # Navigation
    st.markdown("### 🗂 Navigation")
    page = st.radio(
        "Go to",
        ["📁 Upload & Data", "📈 Charts", "🤖 AI Summary", "✉️ Email Generator"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # Load example file shortcut
    st.markdown("### 📂 Quick Start")
    if st.button("Load Example CSV"):
        with open("data/sales.csv", "rb") as f:
            import io
            fake_file = io.BytesIO(f.read())
            fake_file.name = "sales.csv"
            try:
                df = load_csv(fake_file)
                st.session_state.df = df
                st.session_state.stats = get_summary_stats(df)
                st.session_state.date_col = detect_date_column(df)
                st.session_state.numeric_cols = detect_numeric_columns(df)
                st.session_state.data_text = build_data_summary_text(df, st.session_state.stats)
                st.success("Example loaded!")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.caption("Built with Streamlit · Pandas · Plotly · OpenAI")


# ──────────────────────────────────────────────
# HELPER: KPI CARDS
# ──────────────────────────────────────────────
def render_kpi_cards(stats: dict):
    """Display top KPI metrics in a 4-column grid."""
    cols = st.columns(4)
    with cols[0]:
        st.metric("📋 Total Rows", f"{stats['total_rows']:,}")
    with cols[1]:
        st.metric("🗂 Columns", stats["num_columns"])
    with cols[2]:
        if "total_revenue" in stats:
            st.metric("💰 Total Revenue", f"€ {stats['total_revenue']:,.0f}")
        else:
            st.metric("💰 Revenue", "N/A")
    with cols[3]:
        if "avg_order" in stats:
            st.metric("📦 Avg Order Value", f"€ {stats['avg_order']:,.2f}")
        elif "top_product" in stats:
            st.metric("🏆 Top Product", stats["top_product"])
        else:
            st.metric("📊 Avg", "N/A")


# ══════════════════════════════════════════════
# PAGE 1 — UPLOAD & DATA PREVIEW
# ══════════════════════════════════════════════
if page == "📁 Upload & Data":
    st.title("📁 Data Upload & Preview")
    st.caption("Upload a CSV file to analyse your business data.")

    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded:
        try:
            df = load_csv(uploaded)
            st.session_state.df = df
            st.session_state.stats = get_summary_stats(df)
            st.session_state.date_col = detect_date_column(df)
            st.session_state.numeric_cols = detect_numeric_columns(df)
            st.session_state.data_text = build_data_summary_text(df, st.session_state.stats)
            st.success(f"✅ File loaded: **{uploaded.name}**")
        except ValueError as e:
            st.error(str(e))

    # Show data if available
    df = st.session_state.df
    if df is not None:
        stats = st.session_state.stats

        st.markdown('<p class="section-title">📊 KPI Overview</p>', unsafe_allow_html=True)
        render_kpi_cards(stats)

        st.markdown('<p class="section-title">🔍 Data Preview</p>', unsafe_allow_html=True)
        # Pagination: show first N rows
        n_rows = st.slider("Rows to display", 5, min(100, len(df)), 10)
        st.dataframe(df.head(n_rows), use_container_width=True)

        st.markdown('<p class="section-title">📐 Descriptive Statistics</p>', unsafe_allow_html=True)
        st.dataframe(df.describe().round(2), use_container_width=True)

        # Column info
        with st.expander("📋 Column Info"):
            info_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str).values,
                "Non-Null": df.notnull().sum().values,
                "Nulls": df.isnull().sum().values,
                "Unique": df.nunique().values,
            })
            st.dataframe(info_df, use_container_width=True)
    else:
        st.info("👈 Upload a CSV file or click **Load Example CSV** in the sidebar to get started.")


# ══════════════════════════════════════════════
# PAGE 2 — CHARTS
# ══════════════════════════════════════════════
elif page == "📈 Charts":
    st.title("📈 Data Visualisation")

    df = st.session_state.df
    if df is None:
        st.warning("Please upload data first (Page 1).")
        st.stop()

    stats = st.session_state.stats
    date_col = st.session_state.date_col
    numeric_cols = st.session_state.numeric_cols

    render_kpi_cards(stats)
    st.markdown("---")

    revenue_col = stats.get("revenue_col", numeric_cols[0] if numeric_cols else None)

    # ── Row 1: Monthly Revenue + Category Pie ──
    col1, col2 = st.columns(2)

    with col1:
        if date_col and revenue_col:
            monthly = get_monthly_revenue(df, date_col, revenue_col)
            fig = line_chart(monthly, "Month", "Revenue", "Revenue Over Time")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date column detected for time-series chart.")

    with col2:
        # Auto-detect best category column
        cat_col = next(
            (c for c in df.columns if df[c].dtype == "object" and c.lower() not in ("date", "customer")),
            None,
        )
        if cat_col and revenue_col:
            cat_df = get_category_breakdown(df, cat_col, revenue_col)
            fig = pie_chart(cat_df, cat_col, "Revenue", f"Revenue by {cat_col}")
            st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Top Products Bar + Top Customers Bar ──
    col3, col4 = st.columns(2)

    with col3:
        product_col = stats.get("top_product_col")
        if product_col and revenue_col:
            top_products = get_top_n(df, product_col, revenue_col, n=7)
            fig = horizontal_bar(top_products, revenue_col, product_col, f"Top {product_col}s by Revenue")
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        customer_col = stats.get("top_customer_col")
        if customer_col and revenue_col:
            top_customers = get_top_n(df, customer_col, revenue_col, n=7)
            fig = horizontal_bar(top_customers, revenue_col, customer_col, f"Top {customer_col}s by Revenue")
            st.plotly_chart(fig, use_container_width=True)

    # ── Custom Chart Builder ──
    st.markdown('<p class="section-title">🛠 Custom Chart Builder</p>', unsafe_allow_html=True)
    cb_col1, cb_col2, cb_col3, cb_col4 = st.columns(4)
    with cb_col1:
        chart_type = st.selectbox("Chart type", ["Bar", "Line", "Pie", "Scatter"])
    with cb_col2:
        all_cols = df.columns.tolist()
        x_col = st.selectbox("X axis", all_cols)
    with cb_col3:
        y_col = st.selectbox("Y axis", numeric_cols if numeric_cols else all_cols)
    with cb_col4:
        color_col = st.selectbox("Color by (optional)", ["None"] + all_cols)

    if st.button("Generate Chart"):
        color = None if color_col == "None" else color_col
        try:
            if chart_type == "Bar":
                fig = bar_chart(df, x_col, y_col, f"{y_col} by {x_col}")
            elif chart_type == "Line":
                fig = line_chart(df.sort_values(x_col), x_col, y_col, f"{y_col} over {x_col}")
            elif chart_type == "Pie":
                grp = df.groupby(x_col)[y_col].sum().reset_index()
                fig = pie_chart(grp, x_col, y_col, f"{y_col} by {x_col}")
            else:
                fig = scatter_chart(df, x_col, y_col, color, f"{y_col} vs {x_col}")
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Chart error: {e}")


# ══════════════════════════════════════════════
# PAGE 3 — AI BUSINESS SUMMARY
# ══════════════════════════════════════════════
elif page == "🤖 AI Summary":
    st.title("🤖 AI Business Summary")
    st.caption("GPT analyses your data and writes a professional business report.")

    df = st.session_state.df
    if df is None:
        st.warning("Please upload data first (Page 1).")
        st.stop()

    data_text = st.session_state.data_text

    # Show what will be sent to GPT
    with st.expander("🔍 Data context sent to GPT"):
        st.code(data_text, language=None)

    if not api_key:
        st.warning("🔑 Add your OpenAI API key in the sidebar to use this feature.")
    else:
        if st.button("🚀 Generate AI Business Summary"):
            with st.spinner("GPT is analysing your data..."):
                try:
                    summary = generate_business_summary(data_text, api_key)
                    st.session_state["ai_summary"] = summary
                except Exception as e:
                    st.error(f"OpenAI error: {e}")

    if "ai_summary" in st.session_state:
        st.markdown('<p class="section-title">📄 Business Report</p>', unsafe_allow_html=True)
        st.markdown(st.session_state["ai_summary"])

        # Download button
        st.download_button(
            "⬇️ Download Report (Markdown)",
            data=st.session_state["ai_summary"],
            file_name="business_report.md",
            mime="text/markdown",
        )


# ══════════════════════════════════════════════
# PAGE 4 — AI EMAIL GENERATOR
# ══════════════════════════════════════════════
elif page == "✉️ Email Generator":
    st.title("✉️ AI Email Generator")
    st.caption("Describe a business situation and get a professional email instantly.")

    col1, col2 = st.columns([3, 1])
    with col1:
        situation = st.text_area(
            "Describe the situation",
            placeholder="e.g. Customer complaint about a delayed shipment from last week.",
            height=100,
        )
    with col2:
        tone = st.selectbox("Tone", ["professional", "friendly", "formal"])

    # Quick templates
    st.markdown("**Quick templates:**")
    templates = [
        "Customer complaint about delayed shipment",
        "Follow-up after a sales meeting",
        "Apology for incorrect invoice",
        "Request for project deadline extension",
        "Thank-you note after successful deal",
    ]
    cols = st.columns(len(templates))
    for i, tmpl in enumerate(templates):
        if cols[i].button(tmpl, key=f"tmpl_{i}"):
            situation = tmpl  # pre-fill (re-runs the script)
            st.session_state["email_situation"] = tmpl

    # Use session state to keep the selection
    if "email_situation" in st.session_state and not situation:
        situation = st.session_state["email_situation"]

    if not api_key:
        st.warning("🔑 Add your OpenAI API key in the sidebar to use this feature.")
    else:
        if st.button("✉️ Generate Email") and situation.strip():
            with st.spinner("Writing your email..."):
                try:
                    email = generate_email_reply(situation, api_key, tone)
                    st.session_state["generated_email"] = email
                except Exception as e:
                    st.error(f"OpenAI error: {e}")
        elif st.button("✉️ Generate Email"):
            st.warning("Please enter a situation description first.")

    if "generated_email" in st.session_state:
        st.markdown('<p class="section-title">📧 Generated Email</p>', unsafe_allow_html=True)
        email_text = st.session_state["generated_email"]

        # Editable output
        edited = st.text_area("Edit before sending:", value=email_text, height=280)

        c1, c2 = st.columns(2)
        c1.download_button(
            "⬇️ Download (.txt)",
            data=edited,
            file_name="business_email.txt",
            mime="text/plain",
        )
        if c2.button("🗑 Clear"):
            del st.session_state["generated_email"]
            st.rerun()
