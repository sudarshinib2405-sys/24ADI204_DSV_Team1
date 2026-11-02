"""Temporal Risk Intelligence - Time-Series, Diurnal, and Day-of-Week Risk Patterns."""

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
    PURPLE_COLOR,
    WARN_COLOR,
    bar_fraud_rate_by_hour,
    bar_fraud_rate_by_month,
    bar_fraud_rate_by_weekday,
    heatmap_hour_weekday,
    kpi_card,
    line_avg_amount_by_hour,
    line_fraud_trend,
    stacked_area_volume_by_hour,
)
from utils.filters import sidebar_filters
from utils.metrics import hourly_summary, month_summary, weekday_summary
from utils.ui import apply_theme, render_header

# Page Configuration
st.set_page_config(
    page_title="Temporal Risk Intelligence | FraudLens",
    page_icon="⏰",
    layout="wide",
)

# Apply global dark navy theme
apply_theme()

# Load Data and Apply Portfolio Filters
df = load_data()
filtered = sidebar_filters(df)

# Page Header
render_header(
    "Temporal Risk Intelligence",
    "Chronological risk forensics: 24-hour diurnal patterns, weekday clustering, monthly cycles, and hourly ticket values.",
    "⏰",
)

# Empty Cohort Safety Check
if filtered.empty:
    st.info("⚠️ No transactions match the current sidebar filter criteria. Please click **Reset filters** to restore data.")
    st.stop()

# Compute Temporal Aggregations
hourly = hourly_summary(filtered)
weekdays = weekday_summary(filtered)
months = month_summary(filtered)

# 4 Key Temporal KPI Cards
eligible_h = hourly[hourly["total"] >= 30] if not hourly.empty else hourly
if not eligible_h.empty:
    h_sorted = eligible_h.sort_values("fraud_rate_pct", ascending=False)
    peak_h = f"Hour {int(h_sorted.iloc[0]['transaction_hour']):02d}:00"
    peak_h_sub = f"Fraud Rate: {h_sorted.iloc[0]['fraud_rate_pct']:.2f}%"
    if len(h_sorted) > 1:
        peak_h2 = f"Hour {int(h_sorted.iloc[1]['transaction_hour']):02d}:00"
        peak_h2_sub = f"Fraud Rate: {h_sorted.iloc[1]['fraud_rate_pct']:.2f}%"
    else:
        peak_h2, peak_h2_sub = "N/A", "-"
else:
    peak_h, peak_h_sub, peak_h2, peak_h2_sub = "N/A", "-", "N/A", "-"

eligible_wd = weekdays[weekdays["total"] >= 30] if not weekdays.empty else weekdays
if not eligible_wd.empty:
    wd_sorted = eligible_wd.sort_values("fraud_rate_pct", ascending=False)
    peak_wd = str(wd_sorted.iloc[0]["weekday_label"])
    peak_wd_sub = f"Fraud Rate: {wd_sorted.iloc[0]['fraud_rate_pct']:.2f}%"
else:
    peak_wd, peak_wd_sub = "N/A", "-"

eligible_mo = months[months["total"] >= 30] if not months.empty else months
if not eligible_mo.empty:
    mo_sorted = eligible_mo.sort_values("fraud_rate_pct", ascending=False)
    peak_mo = str(mo_sorted.iloc[0]["month_label"])
    peak_mo_sub = f"Fraud Rate: {mo_sorted.iloc[0]['fraud_rate_pct']:.2f}%"
else:
    peak_mo, peak_mo_sub = "N/A", "-"

st.markdown("### ⏱️ Temporal Risk Benchmarks")
t1, t2, t3, t4 = st.columns(4)
with t1:
    st.markdown(kpi_card("Primary Peak Hour", peak_h, peak_h_sub, FRAUD_COLOR), unsafe_allow_html=True)
with t2:
    st.markdown(kpi_card("Secondary Peak Hour", peak_h2, peak_h2_sub, WARN_COLOR), unsafe_allow_html=True)
with t3:
    st.markdown(kpi_card("Highest Risk Day", peak_wd, peak_wd_sub, ACCENT_COLOR), unsafe_allow_html=True)
with t4:
    st.markdown(kpi_card("Highest Risk Month", peak_mo, peak_mo_sub, PURPLE_COLOR), unsafe_allow_html=True)

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# Section 1: Diurnal Hourly Breakdown
st.markdown("### 🕐 24-Hour Diurnal Dynamics")
col_h1, col_h2 = st.columns(2)

with col_h1:
    st.plotly_chart(bar_fraud_rate_by_hour(filtered), use_container_width=True)
    st.caption("Normalized fraud rate by hour of the day (0:00 to 23:00). High rates frequently peak late evening/night hours.")

with col_h2:
    st.plotly_chart(stacked_area_volume_by_hour(filtered), use_container_width=True)
    st.caption("Stacked transaction volume showing the total volume curve (genuine vs fraudulent transactions) over 24 hours.")

st.markdown("---")

# Section 2: Day of Week & Monthly Seasonality
st.markdown("### 📅 Day of Week & Monthly Seasonality")
col_d1, col_d2 = st.columns(2)

with col_d1:
    st.plotly_chart(bar_fraud_rate_by_weekday(filtered), use_container_width=True)
    st.caption("Fraud rate percentage across Monday through Sunday. Uncovers whether weekends or mid-week have higher fraud concentration.")

with col_d2:
    st.plotly_chart(bar_fraud_rate_by_month(filtered), use_container_width=True)
    st.caption("Monthly seasonality tracking fraud rate from January through December. Identifies seasonal shopping and holiday risk spikes.")

st.markdown("---")

# Section 3: 2D Hour x Weekday Risk Matrix
st.markdown("### 🗓️ Hour × Weekday Risk Heatmap")
st.plotly_chart(heatmap_hour_weekday(filtered), use_container_width=True)
st.caption(
    "Two-dimensional interaction heatmap crossing day of week with hour of day. Bright amber and red cells indicate "
    "critical time windows where fraud concentration is exceptionally elevated relative to transaction volume."
)

st.markdown("---")

# Section 4: Trend and Average Hourly Ticket Amount
st.markdown("### 📊 Macro Trend & Hourly Ticket Sizes")
col_trend, col_amt = st.columns(2)

with col_trend:
    st.plotly_chart(line_fraud_trend(filtered), use_container_width=True)
    st.caption("Long-term monthly timeline comparing total fraud incidents (bars) with the monthly fraud rate (line).")

with col_amt:
    st.plotly_chart(line_avg_amount_by_hour(filtered), use_container_width=True)
    st.caption(
        "Average transaction amount ($) by hour of the day for legitimate vs fraudulent transactions. "
        "Fraud attempts during nocturnal hours often carry higher ticket values."
    )
