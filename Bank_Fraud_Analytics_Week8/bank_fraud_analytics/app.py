import streamlit as st

from utils.data_loader import load_data, prepare_data, find_dataset
from utils.styles import apply_styles, app_banner
from utils.filters import apply_sidebar_filters

st.set_page_config(
    page_title="Bank Fraud Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_styles()
app_banner()

st.sidebar.markdown("# BANK ANALYTICS")
st.sidebar.caption("Credit Card Fraud Intelligence")
st.sidebar.markdown("---")

dataset_path = find_dataset()
if dataset_path is None:
    st.error("Dataset not found. Place fraudTrain_cleaned.csv in the project's data folder.")
    st.code("bank_fraud_analytics/data/fraudTrain_cleaned.csv")
    st.stop()

try:
    with st.spinner("Loading a small transaction sample for faster analysis..."):
        df = prepare_data(load_data(str(dataset_path)))
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

st.sidebar.success(f"Loaded {len(df):,} sampled transactions")
st.sidebar.caption("Fast mode: first 50,000 CSV rows only. All metrics and visuals describe this sample.")
st.sidebar.caption(f"Source: {dataset_path.name}")
st.sidebar.markdown("---")

filtered_df = apply_sidebar_filters(df)
if filtered_df.empty:
    st.warning("No transactions match the selected filters. Adjust the filters in the sidebar.")
    st.stop()

selected = st.sidebar.radio(
    "BANK DASHBOARD",
    ["Executive Overview", "Risk Hotspots", "Transaction Review"],
)
st.sidebar.markdown("---")
st.sidebar.caption("Historical analysis only · Not a live fraud detection or blocking system")

if selected == "Executive Overview":
    from dashboard_pages.overview import show_overview
    show_overview(filtered_df)
elif selected == "Risk Hotspots":
    from dashboard_pages.risk_hotspots import show_risk_hotspots
    show_risk_hotspots(filtered_df)
else:
    from dashboard_pages.transaction_review import show_transaction_review
    show_transaction_review(filtered_df)
