import pandas as pd
import streamlit as st
from utils.styles import page_heading

def show_transaction_review(df: pd.DataFrame):
    page_heading("Transaction Review", "A small, privacy-conscious sample of historical fraud-labelled records for analyst review.")
    st.caption("This is not a live case-management tool. Customer names, card numbers, merchant names and personal identifiers are intentionally excluded.")

    fraud = df[df["is_fraud"] == 1].copy()
    if fraud.empty:
        st.warning("No fraud-labelled records in the current selection. Set Transaction status to All transactions or Fraud only.")
        return

    st.metric("Fraud-labelled records available in this sample", f"{len(fraud):,}")
    display_cols = [c for c in ["trans_date_trans_time", "category", "state", "hour", "amt"] if c in fraud.columns]
    if not display_cols:
        display_cols = ["amt"]

    max_rows = st.selectbox("Records to display", [25, 50, 100, 200], index=1)
    sort_choice = st.selectbox("Sort records by", ["Highest amount", "Lowest amount", "Earliest in sample"])
    if sort_choice == "Highest amount":
        shown = fraud.sort_values("amt", ascending=False).head(max_rows)
    elif sort_choice == "Lowest amount":
        shown = fraud.sort_values("amt", ascending=True).head(max_rows)
    else:
        shown = fraud.head(max_rows)

    st.dataframe(shown[display_cols], use_container_width=True, hide_index=True)
    csv_bytes = shown[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download displayed sample (CSV)",
        data=csv_bytes,
        file_name="sample_fraud_records_for_review.csv",
        mime="text/csv"
    )
    st.caption("Transaction amounts are shown in the dataset's currency units. Confirm currency and case status before operational use.")
