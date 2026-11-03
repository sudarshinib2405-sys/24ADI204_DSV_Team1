import streamlit as st

def apply_sidebar_filters(df):
    filtered = df
    st.sidebar.markdown("### ANALYSIS FILTERS")

    if "category" in filtered.columns:
        values = sorted(filtered["category"].dropna().astype(str).unique().tolist())
        selected = st.sidebar.multiselect("Transaction category", values, default=values)
        if len(selected) != len(values):
            filtered = filtered[filtered["category"].isin(selected)]

    if "state" in filtered.columns:
        values = sorted(filtered["state"].dropna().astype(str).unique().tolist())
        selected = st.sidebar.multiselect("State", values, default=values)
        if len(selected) != len(values):
            filtered = filtered[filtered["state"].isin(selected)]

    status = st.sidebar.selectbox(
        "Transaction status",
        ["All transactions", "Fraud only", "Legitimate only"],
    )
    if status == "Fraud only":
        filtered = filtered[filtered["is_fraud"] == 1]
    elif status == "Legitimate only":
        filtered = filtered[filtered["is_fraud"] == 0]

    if not filtered.empty and "amt" in filtered.columns:
        low, high = float(filtered["amt"].min()), float(filtered["amt"].max())
        if low < high:
            amount_range = st.sidebar.slider(
                "Transaction amount ($)", min_value=low, max_value=high,
                value=(low, high),
            )
            if amount_range != (low, high):
                filtered = filtered[filtered["amt"].between(*amount_range)]

    return filtered
