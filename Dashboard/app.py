"""FraudLens Banking Risk Intelligence Dashboard - Executive Landing Page."""

import os
import sys

# Ensure parent and dashboard imports work smoothly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from data_loader import get_summary_stats, load_data
from utils.charts import (
    ACCENT_COLOR,
    FRAUD_COLOR,
    LEGIT_COLOR,
    PURPLE_COLOR,
    WARN_COLOR,
    kpi_card,
)
from utils.metrics import format_currency, format_number
from utils.ui import apply_theme

# Page Configuration
st.set_page_config(
    page_title="FraudLens | Banking Risk Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply unified dark navy styling
apply_theme()

# Initialize session state for user role
if "role" not in st.session_state:
    st.session_state["role"] = "Bank Management"

# Sidebar Role & Dataset Information
with st.sidebar:
    st.markdown(
        """
        <div style="padding:10px 0 16px; border-bottom:1px solid #26354D; margin-bottom:16px;">
            <div style="font-size:22px;font-weight:800;color:#F8FAFC;letter-spacing:-0.5px;">
                🔍 FraudLens
            </div>
            <div style="font-size:11px;letter-spacing:1.5px;color:#94A3B8;text-transform:uppercase;margin-top:2px;">
                Banking Risk Intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 👤 User Persona")
    current_role = st.selectbox(
        "Active Role",
        ["Bank Management", "Fraud Investigation Analyst"],
        index=0 if st.session_state["role"] == "Bank Management" else 1,
        help="Customizes executive exposure metrics and investigative tooling emphasis.",
        key="app_role_select",
    )
    st.session_state["role"] = current_role

    st.markdown("---")
    st.markdown("### 📋 Platform Info")
    st.caption("• **Project:** B.Tech AI & DS (DSV Team 1)")
    st.caption("• **Dataset:** 1,296,675 Cleaned Txns")
    st.caption("• **Engine:** Streamlit & Plotly")
    st.caption("• **Currency:** USD ($)")

# Load Data
df = load_data()
stats = get_summary_stats(df)

# Header Banner with Gradient Title
role_badge_color = "#3B82F6" if current_role == "Bank Management" else "#A855F7"
st.markdown(
    f"""
    <div style="background:linear-gradient(135deg, #17243A 0%, #0B1220 100%);
                border:1px solid #26354D; border-radius:14px; padding:28px 32px; margin-bottom:24px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
            <div>
                <h1 style="margin:0 0 8px 0; font-size:32px; font-weight:800;
                           background:linear-gradient(90deg, #F8FAFC, #94A3B8);
                           -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                    🔍 FraudLens Risk Intelligence
                </h1>
                <p style="margin:0; color:#94A3B8; font-size:15px; max-width:850px; line-height:1.5;">
                    Next-generation retrospective banking risk surveillance, forensic pattern exploration,
                    and financial exposure diagnostics across 1.29M transaction records.
                </p>
            </div>
            <div style="background:{role_badge_color}20; border:1px solid {role_badge_color}60;
                        border-radius:20px; padding:6px 16px; color:{role_badge_color};
                        font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:1px;">
                Active Persona: {current_role}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 5 Top-Level KPI Cards
st.markdown("### 📊 Portfolio Executive Snapshot")
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(
        kpi_card("Total Transactions", format_number(stats["total_transactions"]), "All recorded transactions", ACCENT_COLOR),
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        kpi_card("Fraud Incidents", format_number(stats["fraud_transactions"]), "Historical fraud labels", FRAUD_COLOR),
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        kpi_card("Legitimate Volume", format_number(stats["legit_transactions"]), "Verified genuine transactions", LEGIT_COLOR),
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        kpi_card("Portfolio Fraud Rate", f"{stats['fraud_pct']:.3f}%", "Historical incident frequency", WARN_COLOR),
        unsafe_allow_html=True,
    )
with c5:
    st.markdown(
        kpi_card("Potential Exposure", format_currency(stats["fraud_associated_amt"]), "Total fraudulent value", PURPLE_COLOR),
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

# Persona Alert Callout
if current_role == "Bank Management":
    st.info(
        "💼 **Bank Management Mode Active:** Prioritizing financial capital preservation, potential exposure "
        f"({format_currency(stats['fraud_associated_amt'])}), category risk distribution, and macro time seasonality.",
        icon="🏦",
    )
else:
    st.info(
        "🔎 **Fraud Analyst Mode Active:** Prioritizing anomaly detection signals, rule-scoring factors, "
        "forensic merchant triaging, and case-level investigation workspace navigation.",
        icon="🕵️",
    )

# 6 Navigation Cards for All Pages
st.markdown("### 🧭 Intelligence Modules")
st.markdown("Navigate to specialized risk discovery and operational modules:")

nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    st.markdown(
        """
        <div style="background:#17243A; border:1px solid #26354D; border-radius:12px; padding:20px; min-height:160px;">
            <div style="font-size:20px; font-weight:700; color:#F1F5F9; margin-bottom:6px;">
                📊 Banking Risk Overview
            </div>
            <p style="color:#94A3B8; font-size:13px; line-height:1.4; margin-bottom:12px;">
                Executive command center featuring total portfolio exposure, category loss rankings,
                and transaction distribution comparisons.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Banking_Risk_Overview.py", label="Open Executive Dashboard", icon="📊")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="background:#17243A; border:1px solid #26354D; border-radius:12px; padding:20px; min-height:160px;">
            <div style="font-size:20px; font-weight:700; color:#F1F5F9; margin-bottom:6px;">
                🛍️ Transaction Behaviour
            </div>
            <p style="color:#94A3B8; font-size:13px; line-height:1.4; margin-bottom:12px;">
                Behavioral profiling across spending categories, high-risk merchant entities,
                customer demographics, and distance anomalies.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/4_Transaction_Behaviour.py", label="Open Behaviour Analytics", icon="🛍️")

with nav_col2:
    st.markdown(
        """
        <div style="background:#17243A; border:1px solid #26354D; border-radius:12px; padding:20px; min-height:160px;">
            <div style="font-size:20px; font-weight:700; color:#F1F5F9; margin-bottom:6px;">
                ⏰ Temporal Risk
            </div>
            <p style="color:#94A3B8; font-size:13px; line-height:1.4; margin-bottom:12px;">
                High-resolution time intelligence: 24-hour diurnal patterns, weekday clustering,
                monthly seasonality, and 2D hour-day heatmaps.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Temporal_Risk.py", label="Open Temporal Intelligence", icon="⏰")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="background:#17243A; border:1px solid #26354D; border-radius:12px; padding:20px; min-height:160px;">
            <div style="font-size:20px; font-weight:700; color:#F1F5F9; margin-bottom:6px;">
                🔎 Investigation Workspace
            </div>
            <p style="color:#94A3B8; font-size:13px; line-height:1.4; margin-bottom:12px;">
                Interactive investigator tool: multi-parameter faceted filtering, transparent
                rule risk scoring (0-100), pagination, and CSV export.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/5_Investigation_Workspace.py", label="Open Investigation Workspace", icon="🔎")

with nav_col3:
    st.markdown(
        """
        <div style="background:#17243A; border:1px solid #26354D; border-radius:12px; padding:20px; min-height:160px;">
            <div style="font-size:20px; font-weight:700; color:#F1F5F9; margin-bottom:6px;">
                🗺️ Geographical Risk
            </div>
            <p style="color:#94A3B8; font-size:13px; line-height:1.4; margin-bottom:12px;">
                Geospatial surveillance across 50 US states, interactive choropleth maps,
                customer-to-merchant haversine distance analysis, and coordinates.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Geographical_Risk.py", label="Open Geographical Intelligence", icon="🗺️")

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="background:#17243A; border:1px solid #26354D; border-radius:12px; padding:20px; min-height:160px;">
            <div style="font-size:20px; font-weight:700; color:#F1F5F9; margin-bottom:6px;">
                💡 Insights & Decision Support
            </div>
            <p style="color:#94A3B8; font-size:13px; line-height:1.4; margin-bottom:12px;">
                Synthesized forensic conclusions, actionable policy recommendations for Bank
                Management and Analysts, and system methodology boundaries.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/6_Insights.py", label="Open Insights & Decision Support", icon="💡")

st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)

# Analytical Disclaimer & Platform Notice
st.caption(
    "⚠️ **Analytical Notice & Governance Disclaimer:** Fraud-associated amounts represent the total historical value "
    "of transactions flagged with confirmed fraud labels in the benchmark dataset, not realized bank chargeback losses. "
    "All observed correlations, temporal peaks, and geographic risk indices are retrospective and descriptive. "
    "The risk scoring system is an interpretable rule-based academic framework intended for analytical decision support."
)
