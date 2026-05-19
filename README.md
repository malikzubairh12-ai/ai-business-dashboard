# 📊 AI Business Assistant Dashboard

A professional Streamlit web app that lets you upload CSV business data, explore it visually, and generate AI-powered summaries and professional email replies using the OpenAI API.

---

## ✨ Features

| Feature | Description |
|---|---|
| **CSV Upload** | Upload any CSV file; automatic type detection |
| **KPI Cards** | Instant metrics: revenue, average order, top product |
| **Interactive Charts** | Bar, line, pie, scatter via Plotly |
| **Custom Chart Builder** | Choose axes and chart type freely |
| **AI Business Summary** | GPT-4o-mini writes a structured business report |
| **AI Email Generator** | Describe a situation → get a ready-to-send email |
| **Download Results** | Export reports (.md) and emails (.txt) |

---

## 🚀 Quick Start

### 1. Clone / unzip the project

```bash
cd ai_business_dashboard
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate.bat     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## 🔑 OpenAI API Key

Paste your key in the sidebar when the app is running. The key is **never stored** — it lives only in the current session.

Alternatively, create a `.streamlit/secrets.toml` file:

```toml
OPENAI_API_KEY = "sk-..."
```

And update `app.py` to use `st.secrets["OPENAI_API_KEY"]` instead of the sidebar input.

---

## 📁 Folder Structure

```
ai_business_dashboard/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── data/
│   └── sales.csv           # Example dataset (40 rows, 8 columns)
└── utils/
    ├── __init__.py
    ├── data_analysis.py    # CSV loading, stats, KPIs
    ├── charts.py           # Plotly chart factories
    └── ai_client.py        # OpenAI API wrapper
```

---

## 📂 Example CSV Format

The included `data/sales.csv` file has these columns:

```
Date, Product, Category, Units_Sold, Unit_Price, Revenue, Customer, Region
```

The app auto-detects date columns, numeric columns, and tries to identify revenue, product, and customer columns — so it works with many CSV structures out of the box.

---


