# 🔍 FraudLens: Banking Risk Intelligence Platform

[![B.Tech AI & DS](https://img.shields.io/badge/B.Tech-AI_%26_DS-blue.svg)](#)
[![DSV Team 1](https://img.shields.io/badge/DSV-Team_1-purple.svg)](#)
[![Week 8](https://img.shields.io/badge/Milestone-Week_8_Dashboard-emerald.svg)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)](#)
[![Plotly](https://img.shields.io/badge/Plotly-5.15%2B-cyan.svg)](#)

FraudLens is an enterprise-grade banking risk surveillance and fraud forensic dashboard engineered to analyze transaction exposure, temporal anomalies, geospatial patterns, and behavioral risk factors across **1,296,675 credit card transactions**.

---

## 🏛️ Platform Architecture & Features

The platform provides a dual-persona interface supporting both **Bank Management** (financial exposure, contingency reserves, policy governance) and **Fraud Investigation Analysts** (incident triage, anomaly isolation, heuristic risk scoring).

### 📑 Dashboard Modules

| Page | Name | Core Capabilities |
| :--- | :--- | :--- |
| **Landing Page** | `app.py` | Command center with 5 high-level portfolio KPIs, role toggle (`Bank Management` vs `Fraud Investigation Analyst`), dynamic persona briefings, and module quick-launch cards. |
| **Page 1** | `1_Banking_Risk_Overview.py` | 6 executive KPI cards, donut transaction mix chart, overlapping amount histogram (capped at P99), monthly dual-axis fraud volume/rate trend, category exposure bars, quartile box plots, stacked category volumes, and dynamic management alerts. |
| **Page 2** | `2_Temporal_Risk.py` | 4 temporal benchmark KPIs (primary/secondary peak hours, peak day, peak month), 24-hour diurnal fraud rate gradient, hourly stacked transaction volume curve, day-of-week and month-of-year seasonality, annotated 2D hour × weekday heatmap, and average hourly ticket size lines. |
| **Page 3** | `3_Geographical_Risk.py` | 4 state benchmark KPIs, interactive US state choropleth map, top 20 state fraud rates bar, continental US customer and merchant coordinate scatter geo maps, 4 haversine distance KPIs, distance distribution histograms, and state surveillance table. |
| **Page 4** | `4_Transaction_Behaviour.py` | 4 behavioral benchmark KPIs, category fraud rate gradient, grouped volume bars, amount dispersion box plots, average fraud amount bars, gender fraud comparisons, category × gender heatmaps, customer age distributions, top 15 fraud merchants, dynamic merchant minimum volume threshold filter, and distance vs. amount scatter. |
| **Page 5** | `5_Investigation_Workspace.py` | Faceted multi-parameter sidebar filters (fraud status, category, state, gender, amount slider, hour slider, month multiselect), free-text search (Txn ID, Merchant, Cardholder), 5 dynamically updating filtered KPI cards, 4 inline cohort diagnostic charts, transparent rule-based risk scoring engine (0-100), paginated case table (25/50/100/250 rows/page) with reddish fraud highlighting, and CSV export. |
| **Page 6** | `6_Insights.py` | Full portfolio governance KPI banner, 6 expandable empirical deep dives with synchronized charts (Category, Temporal, Geospatial, Amount, Distance, Demographic Compliance), tabbed strategic playbooks (Bank Management vs. Fraud Analyst), and platform limitations table. |

---

## 🛠️ Tech Stack

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Frontend & UI** | Streamlit | `>= 1.28.0` | Reactive multi-page web application & dashboard chrome |
| **Data Visualization** | Plotly & Plotly Express | `>= 5.15.0` | Dark navy themed interactive charts, heatmaps, choropleths |
| **Data Processing** | Pandas | `>= 1.5.0` | Vectorized aggregations, pivot tables, and transformations |
| **Numerical Computing** | NumPy | `>= 1.24.0` | Haversine distance calculations and array operations |
| **Styling & CSS** | Custom CSS3 | Modern | Dark navy `#0B1220` palette, responsive cards, typography |

---

## 📂 Project Structure

```text
DSV_Project/
├── Week 3/
│   └── fraudTrain_cleaned.csv            # Cleaned benchmark dataset (1.29M rows)
└── Dashboard/
    ├── app.py                            # Landing page & navigation hub
    ├── data_loader.py                    # Cached data loader & haversine distance
    ├── requirements.txt                  # Python dependencies
    ├── README.md                         # Documentation
    ├── .gitignore                        # Git ignore rules
    ├── pages/
    │   ├── 1_Banking_Risk_Overview.py    # Executive overview
    │   ├── 2_Temporal_Risk.py            # Chronological analytics
    │   ├── 3_Geographical_Risk.py        # Spatial intelligence
    │   ├── 4_Transaction_Behaviour.py    # Behavioral profiling
    │   ├── 5_Investigation_Workspace.py  # Analyst tool & rule scoring
    │   └── 6_Insights.py                 # Strategic playbooks & findings
    └── utils/
        ├── __init__.py                   # Package initializer
        ├── charts.py                     # Rich Plotly charts library
        ├── filters.py                    # Sidebar filter components
        ├── insights.py                   # Automated findings generator
        ├── metrics.py                    # Mathematical aggregations & formatters
        ├── risk_scoring.py               # Transparent heuristic scoring engine
        └── ui.py                         # Shared dark navy theme & header
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.10** or higher installed.

### 2. Install Dependencies
Open PowerShell or Terminal, navigate to the `Dashboard` directory, and install the required packages:

```bash
cd C:\Users\Sudarshini\Certificates_Resume\SEM_3_shrim\DSV_Project\Dashboard
pip install -r requirements.txt
```

### 3. Verify Dataset
Confirm that `fraudTrain_cleaned.csv` is present at:
- `../Week 3/fraudTrain_cleaned.csv` (relative to `Dashboard/`), or
- `Dashboard/data/fraudTrain_cleaned.csv`

---

## 🚀 Running the Dashboard

Launch the application with Streamlit:

```bash
cd C:\Users\Sudarshini\Certificates_Resume\SEM_3_shrim\DSV_Project\Dashboard
streamlit run app.py
```

Streamlit will start local server hosting, typically accessible at:
👉 **`http://localhost:8501`**

---

## 🔬 Risk Scoring Engine Methodology

The transparent rule-scoring engine in `utils/risk_scoring.py` evaluates transactions without inspecting the historical fraud label (`is_fraud`), assigning points up to a maximum score of 100:

| Rule Factor | Criteria | Weight |
| :--- | :--- | :--- |
| **High Ticket Size** | Amount $\ge$ Reference 95th Percentile | **+30 pts** |
| **Extreme Ticket Size** | Amount $\ge$ Reference 99th Percentile | **+15 pts** |
| **Median Multiplier** | Amount $\ge$ 3 $\times$ Reference Median | **+10 pts** |
| **Off-Peak Low Volume Hour** | Transaction hour in lowest volume quartile | **+20 pts** |
| **Anomalous Distance** | Customer-merchant distance $\ge$ 95th Percentile | **+25 pts** |

**Risk Tiers:**
- `0 – 19`: **Low Risk**
- `20 – 44`: **Medium Risk**
- `45 – 69`: **High Risk**
- `70 – 100`: **Critical Risk**

---

## ⚠️ Limitations & Governance Notice

1. **Non-Causal Associations:** All observed metrics, correlations, and peak windows are retrospective and descriptive. They do not prove causality.
2. **Exposure vs. Loss:** "Potential Exposure" reflects the authorized value of flagged transactions, not net realized financial loss (does not include chargeback recoveries, merchant liability shifts, or pre-authorization declines).
3. **Data Scope:** The dataset is an academic simulation benchmark. Real-world systems require device identifiers, IP geolocation, proxy/VPN detection, and chip cryptographic verification.
4. **Demographic Fair Lending Compliance:** Customer demographic attributes (such as gender and age) are included for exploratory auditing only and must **never** be used as blocking criteria under ECOA and Fair Lending laws.

---

**Developed for Data Science & Visualization (DSV) Course — Week 8 Milestone.**
