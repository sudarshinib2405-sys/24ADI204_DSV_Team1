"""Fraud Investigation Workspace - Faceted Filtering, Risk Scoring Engine, and Case Review."""

import math
import os
import sys

# Ensure parent and dashboard imports work smoothly
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from data_loader import load_data
from utils.charts import (
    ACCENT_COLOR,
    FRAUD_COLOR,
    LEGIT_COLOR,
    PURPLE_COLOR,
    WARN_COLOR,
    bar_fraud_rate_by_category,
    bar_fraud_rate_by_hour,
    bar_top_states_fraud_rate,
    histogram_amount,
    kpi_card,
)
from utils.metrics import format_currency, format_number
from utils.risk_scoring import score_transactions
from utils.ui import apply_theme, render_header

# Page Configuration
st.set_page_config(
    page_title="Investigation Workspace | FraudLens",
    page_icon="🔎",
    layout="wide",
)

# Apply global dark navy theme
apply_theme()

# Load Reference Dataset
df = load_data()

# Page Header
render_header(
    "Fraud Investigation Workspace",
    "Analyst forensic console: faceted multi-criteria filters, heuristic rule scoring (0-100), case pagination, and audit data export.",
    "🔎",
)

# Sidebar Faceted Filters
with st.sidebar:
    st.markdown("### 🔍 Investigation Filters")
    if st.button("Reset All Filters", use_container_width=True):
        for k in [
            "inv_status",
            "inv_cats",
            "inv_states",
            "inv_genders",
            "inv_amt",
            "inv_hours",
            "inv_months",
            "inv_search",
            "inv_page",
        ]:
            st.session_state.pop(k, None)
        st.rerun()

    # 1. Fraud Status Filter (multiselect)
    status_options = ["Fraudulent", "Legitimate"]
    selected_status = st.multiselect(
        "Transaction Status",
        options=status_options,
        default=status_options,
        key="inv_status",
    )

    # 2. Category Filter (multiselect)
    all_categories = sorted(df["category"].dropna().unique()) if "category" in df.columns else []
    selected_cats = st.multiselect(
        "Spending Category",
        options=all_categories,
        default=all_categories,
        key="inv_cats",
    )

    # 3. State Filter (multiselect)
    all_states = sorted(df["state"].dropna().unique()) if "state" in df.columns else []
    selected_states = st.multiselect(
        "US State",
        options=all_states,
        default=all_states,
        key="inv_states",
    )

    # 4. Gender Filter (multiselect)
    all_genders = sorted(df["gender"].dropna().unique()) if "gender" in df.columns else []
    selected_genders = st.multiselect(
        "Cardholder Gender",
        options=all_genders,
        default=all_genders,
        key="inv_genders",
    )

    # 5. Amount Range Slider
    amt_min = float(df["amt"].min()) if "amt" in df.columns else 0.0
    amt_max = float(df["amt"].max()) if "amt" in df.columns else 10000.0
    selected_amt_range = st.slider(
        "Transaction Amount ($)",
        min_value=0.0,
        max_value=amt_max,
        value=(0.0, amt_max),
        step=50.0,
        key="inv_amt",
    )

    # 6. Hour Range Slider (0-23)
    selected_hour_range = st.slider(
        "Hour of Day (0–23)",
        min_value=0,
        max_value=23,
        value=(0, 23),
        step=1,
        key="inv_hours",
    )

    # 7. Month Filter (multiselect)
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    available_months = [m for m in month_order if m in df["month_label"].values] if "month_label" in df.columns else []
    selected_months = st.multiselect(
        "Transaction Month",
        options=available_months,
        default=available_months,
        key="inv_months",
    )

# Apply Filtering Logic Vectorially
filtered = df.copy()

# Status filter
if len(selected_status) == 1:
    target_fraud_val = 1 if selected_status[0] == "Fraudulent" else 0
    filtered = filtered[filtered["is_fraud"] == target_fraud_val]
elif len(selected_status) == 0:
    filtered = filtered.iloc[0:0]

# Category filter
if selected_cats:
    filtered = filtered[filtered["category"].isin(selected_cats)]
else:
    filtered = filtered.iloc[0:0]

# State filter
if selected_states:
    filtered = filtered[filtered["state"].isin(selected_states)]
else:
    filtered = filtered.iloc[0:0]

# Gender filter
if selected_genders:
    filtered = filtered[filtered["gender"].isin(selected_genders)]
else:
    filtered = filtered.iloc[0:0]

# Amount range filter
filtered = filtered[
    filtered["amt"].between(selected_amt_range[0], selected_amt_range[1], inclusive="both")
]

# Hour range filter
if "transaction_hour" in filtered.columns:
    filtered = filtered[
        filtered["transaction_hour"].between(selected_hour_range[0], selected_hour_range[1], inclusive="both")
    ]

# Month filter
if selected_months and "month_label" in filtered.columns:
    filtered = filtered[filtered["month_label"].isin(selected_months)]
elif not selected_months and "month_label" in filtered.columns:
    filtered = filtered.iloc[0:0]

# Search Bar for Free-Text Matching
st.markdown("### 🔎 Forensic Search")
search_term = st.text_input(
    "Search Transaction ID, Merchant, or Cardholder Name",
    placeholder="e.g., 0b242abb623, fraud_Rippin, Jennifer Banks...",
    key="inv_search",
)

if search_term.strip():
    term = search_term.strip().lower()
    search_mask = pd.Series(False, index=filtered.index)
    if "trans_num" in filtered.columns:
        search_mask = search_mask | filtered["trans_num"].astype(str).str.lower().str.contains(term, na=False)
    if "merchant" in filtered.columns:
        search_mask = search_mask | filtered["merchant"].astype(str).str.lower().str.contains(term, na=False)
    if "customer_name" in filtered.columns:
        search_mask = search_mask | filtered["customer_name"].astype(str).str.lower().str.contains(term, na=False)
    filtered = filtered[search_mask]

# Empty Cohort Safety Check
if filtered.empty:
    st.info("⚠️ No transactions match your active filter and search combination. Please broaden your selection.")
    st.stop()

# Compute Filtered Cohort Metrics
total_filtered = len(filtered)
fraud_filtered = int(filtered["is_fraud"].sum())
legit_filtered = total_filtered - fraud_filtered
rate_filtered = (fraud_filtered / total_filtered * 100) if total_filtered else 0.0
exp_filtered = float(filtered.loc[filtered["is_fraud"] == 1, "amt"].sum())

# 5 Filtered KPI Cards
st.markdown("### 📊 Active Filtered Cohort Snapshot")
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(kpi_card("Filtered Records", format_number(total_filtered), f"of {len(df):,} total", ACCENT_COLOR), unsafe_allow_html=True)
with k2:
    st.markdown(kpi_card("Fraud Count", format_number(fraud_filtered), "Flagged incidents", FRAUD_COLOR), unsafe_allow_html=True)
with k3:
    st.markdown(kpi_card("Legitimate Count", format_number(legit_filtered), "Genuine volume", LEGIT_COLOR), unsafe_allow_html=True)
with k4:
    st.markdown(kpi_card("Cohort Fraud Rate", f"{rate_filtered:.3f}%", "Selected sample", WARN_COLOR), unsafe_allow_html=True)
with k5:
    st.markdown(kpi_card("Cohort Exposure", format_currency(exp_filtered), "Fraud amount sum", PURPLE_COLOR), unsafe_allow_html=True)

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# 4 Inline Analysis Charts on Filtered Data
st.markdown("### 📈 Real-Time Cohort Diagnostics")
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(bar_fraud_rate_by_category(filtered), use_container_width=True)
    st.caption("Category fraud rate (%) across active cohort filters.")
with c2:
    st.plotly_chart(bar_fraud_rate_by_hour(filtered), use_container_width=True)
    st.caption("Hourly fraud rate (%) across active cohort filters.")

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(histogram_amount(filtered), use_container_width=True)
    st.caption("Amount distribution (capped at P99) across active cohort filters.")
with c4:
    st.plotly_chart(bar_top_states_fraud_rate(filtered, top_n=15, min_transactions=10), use_container_width=True)
    st.caption("Top states by fraud rate (%) across active cohort filters.")

st.markdown("---")

# Section: Risk Scoring Engine & Case Review Table
st.markdown("### 🛡️ Transparent Rule-Based Risk Scoring & Case Review")
st.info(
    "🔬 **Rule-Based Scoring Engine Notice:** Transactions are scored on a scale of 0 to 100 using observable "
    "characteristics (P95/P99 amount thresholds, lowest-volume hour quartiles, and customer-merchant distance) "
    "benchmarked against the baseline portfolio. The engine **never** observes the `is_fraud` label.",
    icon="ℹ️",
)

# Limit candidate set for fast interactive scoring and review
MAX_DISPLAY_CANDIDATES = 25000
if total_filtered > MAX_DISPLAY_CANDIDATES:
    st.caption(f"Displaying top {MAX_DISPLAY_CANDIDATES:,} most recent transactions out of {total_filtered:,} filtered matches for performance.")
    candidate_df = filtered.head(MAX_DISPLAY_CANDIDATES).copy()
else:
    candidate_df = filtered.copy()

# Score Candidate Transactions
with st.spinner("Scoring transactions with heuristic risk rules..."):
    scored_df = score_transactions(candidate_df, df)

# Pagination Controls
st.markdown("#### 📄 Paginated Case Review")
page_control_col1, page_control_col2, page_control_col3 = st.columns([1, 1, 2])

with page_control_col1:
    page_size = st.selectbox("Rows per page", options=[25, 50, 100, 250], index=1, key="inv_page_size")

total_pages = max(1, math.ceil(len(scored_df) / page_size))

if "inv_page" not in st.session_state:
    st.session_state["inv_page"] = 1

# Bound current page
st.session_state["inv_page"] = min(max(1, st.session_state["inv_page"]), total_pages)

with page_control_col2:
    current_page = st.number_input(
        f"Page (1 to {total_pages})",
        min_value=1,
        max_value=total_pages,
        value=st.session_state["inv_page"],
        step=1,
        key="inv_page_num_input",
    )
    st.session_state["inv_page"] = current_page

start_idx = (st.session_state["inv_page"] - 1) * page_size
end_idx = min(start_idx + page_size, len(scored_df))

page_slice = scored_df.iloc[start_idx:end_idx].copy()

# Prepare Display Columns
display_columns = [
    "trans_num",
    "trans_datetime",
    "amt",
    "category",
    "merchant",
    "customer_name",
    "state",
    "city",
    "distance_km",
    "risk_score",
    "risk_level",
    "risk_factors",
    "fraud_label",
    "is_fraud",
]
available_cols = [col for col in display_columns if col in page_slice.columns]
display_slice = page_slice[available_cols].copy()

# Clean Merchant Name
if "merchant" in display_slice.columns:
    display_slice["merchant"] = display_slice["merchant"].astype(str).str.replace("^fraud_", "", regex=True)

# Highlight Fraud Rows in Reddish Hue
def highlight_fraud_rows(row):
    is_fraud = row.get("is_fraud", 0)
    if is_fraud == 1 or row.get("fraud_label") == "Fraudulent":
        return ["background-color: rgba(239, 68, 68, 0.22); color: #FCA5A5;"] * len(row)
    return [""] * len(row)

styled_table = (
    display_slice.style.apply(highlight_fraud_rows, axis=1)
    .format(
        {
            "amt": "${:,.2f}",
            "distance_km": "{:,.1f} km",
            "risk_score": "{:d}",
        },
        na_rep="N/A",
    )
)

st.dataframe(styled_table, use_container_width=True, hide_index=True)
st.caption(f"Showing rows {start_idx + 1:,} to {end_idx:,} of {len(scored_df):,} matching cases. Red-tinted rows represent confirmed historical fraud incidents.")

# Export Controls
st.markdown("---")
export_col1, export_col2 = st.columns([1, 2])

with export_col1:
    # Prepare download CSV
    csv_bytes = page_slice.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Current Page as CSV",
        data=csv_bytes,
        file_name=f"fraudlens_investigation_page_{st.session_state['inv_page']}.csv",
        mime="text/csv",
        use_container_width=True,
    )

with export_col2:
    st.caption(
        "💡 **Analyst Tip:** Filtered case files contain enriched geospatial distance, "
        "calculated rule scores (0-100), factor descriptions, and validated customer demographics for audit compliance."
    )
