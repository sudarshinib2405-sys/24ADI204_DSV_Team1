"""Executive Command Center - Portfolio-Level Banking Risk Intelligence."""

import os
import sys

# Ensure parent and dashboard imports work smoothly
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import plotly.graph_objects as go
import streamlit as st
from data_loader import get_summary_stats, load_data
from utils.charts import (
    ACCENT_COLOR,
    FRAUD_COLOR,
    LEGIT_COLOR,
    PURPLE_COLOR,
    WARN_COLOR,
    bar_fraud_value_by_category,
    box_amount_by_fraud,
    donut_fraud_distribution,
    histogram_amount,
    kpi_card,
    line_fraud_trend,
    stacked_bar_category_counts,
)
from utils.filters import sidebar_filters
from utils.metrics import category_summary, format_currency, format_number
from utils.ui import apply_theme, render_header

# Page Configuration
st.set_page_config(
    page_title="Executive Risk Overview | FraudLens",
    page_icon="📊",
    layout="wide",
)

# Apply global dark navy theme
apply_theme()

# Load Data and Apply Portfolio Filters
df = load_data()
filtered = sidebar_filters(df)

# Page Header
render_header(
    "Banking Risk Overview",
    "Executive portfolio surveillance: transaction volumes, financial exposure, category risk, and monthly trends.",
    "📊",
)

# Empty Cohort Safety Check
if filtered.empty:
    st.info("⚠️ No transactions match the current sidebar filter criteria. Please click **Reset filters** to restore data.")
    st.stop()

# Role Context
current_role = st.session_state.get("role", "Bank Management")

# Compute Summary Statistics
stats = get_summary_stats(filtered)

# 6 Executive KPI Cards
st.markdown("### 🏛️ Executive Key Performance Indicators")
k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(
        kpi_card("Total Volume", format_number(stats["total_transactions"]), "Selected cohort", ACCENT_COLOR),
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        kpi_card("Fraud Incidents", format_number(stats["fraud_transactions"]), "Confirmed historical fraud", FRAUD_COLOR),
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        kpi_card("Legitimate Volume", format_number(stats["legit_transactions"]), "Verified genuine", LEGIT_COLOR),
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        kpi_card("Fraud Rate", f"{stats['fraud_pct']:.3f}%", "Cohort incident %", WARN_COLOR),
        unsafe_allow_html=True,
    )
with k5:
    st.markdown(
        kpi_card("Potential Exposure", format_currency(stats["fraud_associated_amt"]), "Total fraud value", PURPLE_COLOR),
        unsafe_allow_html=True,
    )
with k6:
    st.markdown(
        kpi_card("Avg Fraud Amount", format_currency(stats["avg_fraud_amt"]), "Per fraud event", FRAUD_COLOR),
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# Role-Aware Executive Banner
if current_role == "Bank Management":
    st.markdown(
        f"""
        <div style="background:#1E293B; border-left:4px solid #3B82F6; border-radius:8px; padding:16px 20px; margin-bottom:20px;">
            <div style="font-size:14px; font-weight:700; color:#60A5FA; margin-bottom:4px;">
                💼 Management Executive Summary & Financial Exposure
            </div>
            <div style="font-size:13px; color:#CBD5E1; line-height:1.5;">
                Total monitored financial value in this active cohort is <b>{format_currency(stats['total_amt'])}</b>, of which 
                <b>{format_currency(stats['fraud_associated_amt'])}</b> ({stats['fraud_associated_amt'] / stats['total_amt'] * 100 if stats['total_amt'] else 0:.2f}%) 
                is tied to fraudulent transactions. Recommended contingency reserve buffer: 
                <b>{format_currency(stats['fraud_associated_amt'] * 1.15)}</b> (factoring operational dispute & recovery overhead).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
        <div style="background:#1E293B; border-left:4px solid #A855F7; border-radius:8px; padding:16px 20px; margin-bottom:20px;">
            <div style="font-size:14px; font-weight:700; color:#C084FC; margin-bottom:4px;">
                🔍 Investigation Lead Briefing & Incident Triage
            </div>
            <div style="font-size:13px; color:#CBD5E1; line-height:1.5;">
                Cohort contains <b>{format_number(stats['fraud_transactions'])}</b> confirmed fraud transactions requiring retrospective triage.
                Mean fraud amount (<b>{format_currency(stats['avg_fraud_amt'])}</b>) is significantly higher than legitimate transactions 
                (<b>{format_currency(stats['avg_legit_amt'])}</b>). Use the Category Breakdown below to prioritize high-yield investigations.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Section 1: Transaction Mix and Amount Distribution
st.markdown("### 🥧 Transaction Distribution & Amount Profiles")
row1_left, row1_right = st.columns(2)

with row1_left:
    st.plotly_chart(donut_fraud_distribution(filtered), use_container_width=True)
    st.caption("Distribution of transactions by historical label. Extreme class imbalance is characteristic of banking risk data.")

with row1_right:
    st.plotly_chart(histogram_amount(filtered), use_container_width=True)
    st.caption("Overlapping frequency distribution of transaction values, capped at the 99th percentile to reveal density peaks.")

st.markdown("---")

# Section 2: Macro Temporal Trend
st.markdown("### 📈 Monthly Portfolio Trend (Dual-Axis)")
st.plotly_chart(line_fraud_trend(filtered), use_container_width=True)
st.caption(
    "Dual-axis analysis tracking monthly incident count (bars, right axis) alongside the portfolio fraud rate percentage (line, left axis). "
    "Allows distinguishing volume-driven surges from actual risk concentration spikes."
)

st.markdown("---")

# Section 3: Category Risk & Exposure
st.markdown("### 🏷️ Category Risk & Exposure Analysis")
cat_col1, cat_col2 = st.columns(2)

with cat_col1:
    st.plotly_chart(bar_fraud_value_by_category(filtered, top_n=10), use_container_width=True)
    st.caption("Top spending categories ranked by total dollar exposure associated with fraudulent transactions.")

with cat_col2:
    st.plotly_chart(stacked_bar_category_counts(filtered), use_container_width=True)
    st.caption("Total transaction volume per merchant category segmented into legitimate and fraudulent subsets.")

st.markdown("---")

# Section 4: Box Plot Amount Dispersion
st.markdown("### 📦 Amount Dispersion & Outlier Comparison")
st.plotly_chart(box_amount_by_fraud(filtered), use_container_width=True)
st.caption(
    "Box plot comparing the quartile distribution, medians, and outliers of legitimate vs fraudulent amounts. "
    "Fraudulent events typically exhibit higher median values and tight clustering in specific fraud threshold bands."
)

st.markdown("---")

# Section 5: Dynamic Management Alert
category_df = category_summary(filtered)
st.markdown("### 🚨 Dynamic Risk Alerts")

if not category_df.empty:
    eligible_cats = category_df[category_df["total_count"] >= 30]
    if not eligible_cats.empty:
        highest_risk_cat = eligible_cats.sort_values("fraud_rate_pct", ascending=False).iloc[0]
        cat_name = highest_risk_cat["category"]
        cat_rate = highest_risk_cat["fraud_rate_pct"]
        cat_fraud_count = int(highest_risk_cat["fraud_count"])
        cat_total = int(highest_risk_cat["total_count"])
        cat_avg_fraud = highest_risk_cat["avg_fraud_amt"]

        if cat_rate > stats["fraud_pct"]:
            st.warning(
                f"⚠️ **High-Risk Segment Alert:** Category **{cat_name.upper()}** demonstrates an observed fraud rate of "
                f"**{cat_rate:.2f}%** ({cat_fraud_count:,} fraud events out of {cat_total:,} txns), which is "
                f"**{cat_rate - stats['fraud_pct']:+.2f} percentage points above the portfolio benchmark** ({stats['fraud_pct']:.2f}%). "
                f"Average fraud ticket size: **${cat_avg_fraud:,.2f}**. Enhanced 3-D Secure authentication is recommended.",
                icon="⚠️",
            )
        else:
            st.success(
                f"✅ **Balanced Risk Distribution:** No merchant category with at least 30 transactions exceeds the portfolio fraud rate of {stats['fraud_pct']:.2f}%.",
                icon="✅",
            )
    else:
        st.info("ℹ️ Insufficient category transaction volume (minimum 30 transactions required) to trigger risk alerts.")
else:
    st.info("ℹ️ Category summary unavailable for the active filter selection.")

# Section 6: Comprehensive Category Summary Table
st.markdown("### 📋 Category Financial & Risk Breakdown")
if not category_df.empty:
    display_df = category_df.sort_values("fraud_rate_pct", ascending=False).copy()
    display_df = display_df.rename(
        columns={
            "category": "Category",
            "total_count": "Total Transactions",
            "fraud_count": "Fraud Incidents",
            "legit_count": "Legitimate Transactions",
            "fraud_rate_pct": "Fraud Rate (%)",
            "avg_amt": "Average Overall Amount ($)",
            "avg_fraud_amt": "Average Fraud Amount ($)",
        }
    )
    # Format currency and percentages for display
    display_df["Fraud Rate (%)"] = display_df["Fraud Rate (%)"].map("{:.3f}%".format)
    display_df["Average Overall Amount ($)"] = display_df["Average Overall Amount ($)"].map("${:,.2f}".format)
    display_df["Average Fraud Amount ($)"] = display_df["Average Fraud Amount ($)"].fillna(0).map("${:,.2f}".format)
    display_df["Total Transactions"] = display_df["Total Transactions"].map("{:,}".format)
    display_df["Fraud Incidents"] = display_df["Fraud Incidents"].map("{:,}".format)
    display_df["Legitimate Transactions"] = display_df["Legitimate Transactions"].map("{:,}".format)

    st.dataframe(display_df, use_container_width=True, hide_index=True)
