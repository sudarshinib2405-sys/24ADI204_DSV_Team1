"""Geographical Risk Intelligence - US State Choropleth, Scatter Geo, and Distance Metrics."""

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
    bar_top_states_fraud_rate,
    box_distance_by_fraud,
    choropleth_state_fraud_rate,
    histogram_distance,
    kpi_card,
    scatter_geo_locations,
)
from utils.filters import sidebar_filters
from utils.metrics import distance_stats, format_currency, format_number, state_fraud_summary
from utils.ui import apply_theme, render_header

# Page Configuration
st.set_page_config(
    page_title="Geographical Risk | FraudLens",
    page_icon="🗺️",
    layout="wide",
)

# Apply global dark navy theme
apply_theme()

# Load Data and Apply Portfolio Filters
df = load_data()
filtered = sidebar_filters(df)

# Page Header
render_header(
    "Geographical Risk Intelligence",
    "Spatial surveillance across the United States: state-level risk choropleths, geolocation scatter, and haversine distance forensics.",
    "🗺️",
)

# Empty Cohort Safety Check
if filtered.empty:
    st.info("⚠️ No transactions match the current sidebar filter criteria. Please click **Reset filters** to restore data.")
    st.stop()

if "state" not in filtered.columns:
    st.warning("⚠️ State field is not present in the current dataset.")
    st.stop()

# State Summary Aggregations
state_summary_df = state_fraud_summary(filtered)

# 4 Key Geographical KPIs
eligible_states = state_summary_df[state_summary_df["total_count"] >= 30] if not state_summary_df.empty else state_summary_df

if not eligible_states.empty:
    top_rate_state = eligible_states.sort_values("fraud_rate_pct", ascending=False).iloc[0]
    top_rate_label = f"{top_rate_state['state']} ({top_rate_state['fraud_rate_pct']:.2f}%)"
    top_rate_sub = f"{int(top_rate_state['fraud_count']):,} fraud / {int(top_rate_state['total_count']):,} total"

    top_exp_state = state_summary_df.sort_values("fraud_amt", ascending=False).iloc[0]
    top_exp_label = f"{top_exp_state['state']} ({format_currency(top_exp_state['fraud_amt'])})"
    top_exp_sub = f"{int(top_exp_state['fraud_count']):,} fraud incidents"

    active_state_count = f"{len(state_summary_df):,} States"
    active_state_sub = "Represented in cohort"

    avg_state_rate = f"{state_summary_df['fraud_rate_pct'].mean():.2f}%"
    avg_state_sub = "Unweighted state mean"
else:
    top_rate_label, top_rate_sub = "N/A", "-"
    top_exp_label, top_exp_sub = "N/A", "-"
    active_state_count, active_state_sub = "0", "-"
    avg_state_rate, avg_state_sub = "0.00%", "-"

st.markdown("### 🌐 State Risk Benchmarks")
g1, g2, g3, g4 = st.columns(4)
with g1:
    st.markdown(kpi_card("Highest Fraud Rate State", top_rate_label, top_rate_sub, FRAUD_COLOR), unsafe_allow_html=True)
with g2:
    st.markdown(kpi_card("Highest Exposure State", top_exp_label, top_exp_sub, WARN_COLOR), unsafe_allow_html=True)
with g3:
    st.markdown(kpi_card("Monitored US States", active_state_count, active_state_sub, ACCENT_COLOR), unsafe_allow_html=True)
with g4:
    st.markdown(kpi_card("Average State Fraud Rate", avg_state_rate, avg_state_sub, PURPLE_COLOR), unsafe_allow_html=True)

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# Section 1: USA Choropleth Map & Top States Ranking
st.markdown("### 🗺️ State-Level Fraud Rate Surveillance")
col_map, col_bar = st.columns([1.2, 0.8])

with col_map:
    st.plotly_chart(choropleth_state_fraud_rate(filtered), use_container_width=True)
    st.caption("Interactive US Choropleth map illustrating observed fraud percentage across jurisdictions.")

with col_bar:
    st.plotly_chart(bar_top_states_fraud_rate(filtered, top_n=20, min_transactions=30), use_container_width=True)
    st.caption("Top 20 US states ranked by fraud rate percentage (minimum sample threshold of 30 transactions).")

st.markdown("---")

# Section 2: Spatial Scatter Geo Maps (Customer vs Merchant)
st.markdown("### 📍 Geolocation Scatter Intelligence (Sampled Continental US)")
st.caption("Visualizing spatial coordinates bounded within continental US latitudes (20°N to 55°N) and longitudes (-130°W to -65°W).")

geo_col1, geo_col2 = st.columns(2)

with geo_col1:
    st.plotly_chart(
        scatter_geo_locations(filtered, lat_col="lat", lon_col="long", title="Customer Geolocation Distribution", sample_n=20000),
        use_container_width=True,
    )
    st.caption("Sampled customer residential coordinate distribution with highlighted fraudulent transaction origins.")

with geo_col2:
    st.plotly_chart(
        scatter_geo_locations(filtered, lat_col="merch_lat", lon_col="merch_long", title="Merchant Geolocation Distribution", sample_n=20000),
        use_container_width=True,
    )
    st.caption("Sampled merchant processing terminal locations across the United States.")

st.markdown("---")

# Section 3: Haversine Distance Diagnostics
st.markdown("### 📏 Customer-to-Merchant Distance Forensics")

dist_kpis = distance_stats(filtered)
d_c1, d_c2, d_c3, d_c4 = st.columns(4)

with d_c1:
    st.markdown(
        kpi_card("Fraud Median Distance", f"{dist_kpis.get('fraud_median_km', 0):.1f} km", "Customer to merchant", FRAUD_COLOR),
        unsafe_allow_html=True,
    )
with d_c2:
    st.markdown(
        kpi_card("Legit Median Distance", f"{dist_kpis.get('legit_median_km', 0):.1f} km", "Customer to merchant", LEGIT_COLOR),
        unsafe_allow_html=True,
    )
with d_c3:
    st.markdown(
        kpi_card("Fraud Mean Distance", f"{dist_kpis.get('fraud_mean_km', 0):.1f} km", "Average great-circle km", WARN_COLOR),
        unsafe_allow_html=True,
    )
with d_c4:
    st.markdown(
        kpi_card("Legit Mean Distance", f"{dist_kpis.get('legit_mean_km', 0):.1f} km", "Average great-circle km", ACCENT_COLOR),
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

dist_hist_col, dist_box_col = st.columns(2)

with dist_hist_col:
    st.plotly_chart(histogram_distance(filtered), use_container_width=True)
    st.caption("Overlapping customer-to-merchant distance distribution (km) capped at the 99th percentile.")

with dist_box_col:
    st.plotly_chart(box_distance_by_fraud(filtered, sample_n=20000), use_container_width=True)
    st.caption("Comparative box plot highlighting distance dispersion and extreme outliers between legitimate and fraud events.")

st.markdown("---")

# Section 4: Detailed State Summary Table
st.markdown("### 📋 State Surveillance Summary Table")
if not state_summary_df.empty:
    state_table = state_summary_df.sort_values("fraud_rate_pct", ascending=False).copy()
    state_table = state_table.rename(
        columns={
            "state": "State",
            "total_count": "Total Transactions",
            "fraud_count": "Fraud Incidents",
            "legit_count": "Legitimate Transactions",
            "fraud_rate_pct": "Fraud Rate (%)",
            "fraud_amt": "Total Fraud Exposure ($)",
        }
    )
    state_table["Fraud Rate (%)"] = state_table["Fraud Rate (%)"].map("{:.3f}%".format)
    state_table["Total Fraud Exposure ($)"] = state_table["Total Fraud Exposure ($)"].map("${:,.2f}".format)
    state_table["Total Transactions"] = state_table["Total Transactions"].map("{:,}".format)
    state_table["Fraud Incidents"] = state_table["Fraud Incidents"].map("{:,}".format)
    state_table["Legitimate Transactions"] = state_table["Legitimate Transactions"].map("{:,}".format)

    st.dataframe(state_table, use_container_width=True, hide_index=True)
