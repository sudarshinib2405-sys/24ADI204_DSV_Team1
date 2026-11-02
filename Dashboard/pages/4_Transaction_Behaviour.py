"""Transaction Behaviour Analytics - Spending Categories, Merchant Risk, Demographics, and Geodistance."""

import os
import sys

# Ensure parent and dashboard imports work smoothly
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import plotly.graph_objects as go
import streamlit as st
from data_loader import load_data
from utils.charts import (
    ACCENT_COLOR,
    FRAUD_COLOR,
    LEGIT_COLOR,
    PURPLE_COLOR,
    WARN_COLOR,
    bar_avg_fraud_amount_by_category,
    bar_fraud_rate_by_category,
    bar_gender_fraud_rate,
    bar_median_distance_by_category,
    bar_merchant_fraud_rate_min_vol,
    bar_top_merchants_fraud,
    box_amount_by_fraud,
    heatmap_gender_category,
    histogram_age_distribution,
    kpi_card,
    scatter_distance_vs_amount,
    stacked_bar_category_counts,
)
from utils.filters import sidebar_filters
from utils.metrics import category_summary, format_currency, format_number
from utils.ui import apply_theme, render_header

# Page Configuration
st.set_page_config(
    page_title="Transaction Behaviour | FraudLens",
    page_icon="🛍️",
    layout="wide",
)

# Apply global dark navy theme
apply_theme()

# Load Data and Apply Portfolio Filters
df = load_data()
filtered = sidebar_filters(df)

# Page Header
render_header(
    "Transaction Behaviour Analytics",
    "Forensic behavioural profiling: category risk distributions, merchant concentration, demographic patterns, and distance correlation.",
    "🛍️",
)

# Empty Cohort Safety Check
if filtered.empty:
    st.info("⚠️ No transactions match the current sidebar filter criteria. Please click **Reset filters** to restore data.")
    st.stop()

# Compute Behavioural KPIs
cat_summary = category_summary(filtered)
eligible_cats = cat_summary[cat_summary["total_count"] >= 30] if not cat_summary.empty else cat_summary

if not eligible_cats.empty:
    top_cat = eligible_cats.sort_values("fraud_rate_pct", ascending=False).iloc[0]
    top_cat_label = f"{top_cat['category']} ({top_cat['fraud_rate_pct']:.2f}%)"
    top_cat_sub = f"{int(top_cat['fraud_count']):,} fraud / {int(top_cat['total_count']):,} txns"
else:
    top_cat_label, top_cat_sub = "N/A", "-"

fraud_amounts = filtered.loc[filtered["is_fraud"] == 1, "amt"].dropna()
med_fraud_amt = format_currency(float(fraud_amounts.median())) if not fraud_amounts.empty else "$0.00"
med_fraud_sub = f"P75: {format_currency(float(fraud_amounts.quantile(0.75)))}" if not fraud_amounts.empty else "-"

fraud_txns = filtered[filtered["is_fraud"] == 1]
if not fraud_txns.empty and "merchant" in fraud_txns.columns:
    top_merch_series = fraud_txns["merchant"].value_counts()
    top_merch_name = str(top_merch_series.index[0]).replace("fraud_", "")
    top_merch_count = f"{top_merch_name} ({top_merch_series.iloc[0]:,} txns)"
    top_merch_sub = "Highest fraud incident volume"
else:
    top_merch_count, top_merch_sub = "N/A", "-"

if "distance_km" in filtered.columns:
    med_dist = f"{float(filtered['distance_km'].dropna().median()):.1f} km"
    med_dist_sub = "All cohort transactions"
else:
    med_dist, med_dist_sub = "N/A", "-"

# 4 KPI Cards
st.markdown("### 🛒 Behavioural Risk Benchmarks")
b1, b2, b3, b4 = st.columns(4)
with b1:
    st.markdown(kpi_card("Highest Risk Category", top_cat_label, top_cat_sub, FRAUD_COLOR), unsafe_allow_html=True)
with b2:
    st.markdown(kpi_card("Median Fraud Amount", med_fraud_amt, med_fraud_sub, PURPLE_COLOR), unsafe_allow_html=True)
with b3:
    st.markdown(kpi_card("Top Fraud Merchant", top_merch_count, top_merch_sub, WARN_COLOR), unsafe_allow_html=True)
with b4:
    st.markdown(kpi_card("Median Transaction Distance", med_dist, med_dist_sub, ACCENT_COLOR), unsafe_allow_html=True)

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# Section 1: Category Fraud Rates and Transaction Volumes
st.markdown("### 🏷️ Category Risk Profiling")
c_col1, c_col2 = st.columns(2)

with c_col1:
    st.plotly_chart(bar_fraud_rate_by_category(filtered), use_container_width=True)
    st.caption("Observed fraud rate percentage across all spending categories with continuous color scaling.")

with c_col2:
    st.plotly_chart(stacked_bar_category_counts(filtered), use_container_width=True)
    st.caption("Total volume per category segmented into genuine and fraudulent transactions.")

st.markdown("---")

# Section 2: Amounts by Category and Fraud Status
st.markdown("### 💵 Transaction Amount Characteristics")
amt_col1, amt_col2 = st.columns(2)

with amt_col1:
    st.plotly_chart(box_amount_by_fraud(filtered, sample_n=20000), use_container_width=True)
    st.caption("Distribution box plot illustrating IQR and outliers for legitimate vs fraudulent transactions.")

with amt_col2:
    st.plotly_chart(bar_avg_fraud_amount_by_category(filtered), use_container_width=True)
    st.caption("Average ticket size for fraudulent transactions across each spending category.")

st.markdown("---")

# Section 3: Demographic & Gender Profiling
st.markdown("### 👥 Demographic Risk Observations")
st.caption("Descriptive retrospective associations. These metrics reflect empirical sample properties and do not establish causal vulnerability.")

demo_col1, demo_col2 = st.columns(2)

with demo_col1:
    st.plotly_chart(bar_gender_fraud_rate(filtered), use_container_width=True)
    st.caption("Empirical fraud rate percentage across gender groups in the filtered transaction sample.")

with demo_col2:
    st.plotly_chart(heatmap_gender_category(filtered), use_container_width=True)
    st.caption("Two-dimensional cross-tabulation of fraud rate (%) across categories and cardholder gender.")

if "customer_age" in filtered.columns:
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.plotly_chart(histogram_age_distribution(filtered), use_container_width=True)
    st.caption("Customer age distribution comparison between legitimate and fraudulent transactions.")

st.markdown("---")

# Section 4: Merchant Risk Intelligence
st.markdown("### 🏪 Merchant Risk Analytics")

merch_col1, merch_col2 = st.columns(2)

with merch_col1:
    st.plotly_chart(bar_top_merchants_fraud(filtered, top_n=15), use_container_width=True)
    st.caption("Top 15 merchant outlets ranked by gross fraudulent transaction count.")

with merch_col2:
    min_vol = st.slider(
        "Minimum Merchant Transaction Volume Filter",
        min_value=50,
        max_value=500,
        value=100,
        step=25,
        help="Filters out low-volume merchant accounts to reveal sustained high fraud rate percentages.",
    )
    st.plotly_chart(bar_merchant_fraud_rate_min_vol(filtered, min_volume=min_vol, top_n=15), use_container_width=True)
    st.caption(f"Top 15 merchants ranked by fraud rate (%) among entities with at least {min_vol} transactions.")

st.markdown("---")

# Section 5: Distance vs Amount & Distance by Category
st.markdown("### 📐 Geodistance vs Transaction Ticket Size")
dist_col1, dist_col2 = st.columns(2)

with dist_col1:
    st.plotly_chart(scatter_distance_vs_amount(filtered, sample_n=20000), use_container_width=True)
    st.caption("Bivariate scatter plot comparing customer-to-merchant distance against transaction amount (USD).")

with dist_col2:
    st.plotly_chart(bar_median_distance_by_category(filtered), use_container_width=True)
    st.caption("Median distance (km) by category comparing legitimate vs fraudulent transactions.")

st.markdown("---")

# Section 6: Comprehensive Category Detail Table
st.markdown("### 📋 Category Behaviour Detail Table")
if not cat_summary.empty:
    detail_df = cat_summary.sort_values("fraud_rate_pct", ascending=False).copy()
    detail_df = detail_df.rename(
        columns={
            "category": "Category",
            "total_count": "Total Volume",
            "fraud_count": "Fraud Incidents",
            "legit_count": "Legitimate Volume",
            "fraud_rate_pct": "Fraud Rate (%)",
            "avg_amt": "Average Ticket ($)",
            "avg_fraud_amt": "Avg Fraud Ticket ($)",
        }
    )
    detail_df["Fraud Rate (%)"] = detail_df["Fraud Rate (%)"].map("{:.3f}%".format)
    detail_df["Average Ticket ($)"] = detail_df["Average Ticket ($)"].map("${:,.2f}".format)
    detail_df["Avg Fraud Ticket ($)"] = detail_df["Avg Fraud Ticket ($)"].fillna(0).map("${:,.2f}".format)
    detail_df["Total Volume"] = detail_df["Total Volume"].map("{:,}".format)
    detail_df["Fraud Incidents"] = detail_df["Fraud Incidents"].map("{:,}".format)
    detail_df["Legitimate Volume"] = detail_df["Legitimate Volume"].map("{:,}".format)

    st.dataframe(detail_df, use_container_width=True, hide_index=True)
