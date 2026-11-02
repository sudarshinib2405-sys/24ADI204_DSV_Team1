"""Shared sidebar filters used by every FraudLens page."""

import pandas as pd
import streamlit as st


def reset_filters() -> None:
    """Clear shared filter values before Streamlit reruns the current page."""
    for key in ("filter_dates", "filter_categories", "filter_states", "filter_status", "filter_amount"):
        st.session_state.pop(key, None)


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render common filters and return a filtered view of the input frame."""
    with st.sidebar:
        st.markdown(
            "<div style='padding:8px 0 16px'><div style='font-size:23px;font-weight:750;color:#f8fafc'>"
            "◈ FraudLens</div><div style='font-size:10px;letter-spacing:1px;color:#94a3b8'>"
            "BANKING RISK INTELLIGENCE</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("#### Portfolio filters")
        st.button("Reset filters", use_container_width=True, on_click=reset_filters)

        result = df
        dates = pd.to_datetime(df.get("trans_datetime"), errors="coerce").dropna()
        if not dates.empty:
            min_date = dates.min().date()
            max_date = dates.max().date()
            selected_dates = st.date_input(
                "Transaction date",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="filter_dates",
            )
            if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
                start_date, end_date = selected_dates
                transaction_dates = pd.to_datetime(result["trans_datetime"], errors="coerce")
                result = result[
                    transaction_dates.dt.date.between(start_date, end_date)
                ]

        categories = sorted(df["category"].dropna().astype(str).unique()) if "category" in df else []
        if categories:
            selected_categories = st.multiselect(
                "Transaction category",
                categories,
                default=categories,
                key="filter_categories",
            )
            if selected_categories:
                result = result[result["category"].astype(str).isin(selected_categories)]
            else:
                result = result.iloc[0:0]

        states = sorted(df["state"].dropna().astype(str).unique()) if "state" in df else []
        if states:
            selected_states = st.multiselect(
                "State",
                states,
                default=states,
                key="filter_states",
            )
            if selected_states:
                result = result[result["state"].astype(str).isin(selected_states)]
            else:
                result = result.iloc[0:0]

        if "is_fraud" in df:
            selected_status = st.selectbox(
                "Fraud status",
                ["All", "Fraudulent", "Legitimate"],
                key="filter_status",
            )
            if selected_status != "All":
                fraud_value = 1 if selected_status == "Fraudulent" else 0
                result = result[result["is_fraud"] == fraud_value]
                st.caption(
                    "Single-label selection makes fraud-rate comparisons non-comparable."
                )

        if "amt" in df:
            amounts = pd.to_numeric(df["amt"], errors="coerce").dropna()
            if not amounts.empty and amounts.min() < amounts.max():
                amount_bounds = (float(amounts.min()), float(amounts.max()))
                amount_range = st.slider(
                    "Transaction amount (USD)",
                    min_value=amount_bounds[0],
                    max_value=amount_bounds[1],
                    value=amount_bounds,
                    key="filter_amount",
                )
                result = result[
                    result["amt"].between(amount_range[0], amount_range[1], inclusive="both")
                ]

        st.caption(f"{len(result):,} of {len(df):,} transactions")
    return result
