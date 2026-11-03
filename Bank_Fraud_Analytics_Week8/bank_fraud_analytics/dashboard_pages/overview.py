import pandas as pd
import plotly.express as px
import streamlit as st
from utils.styles import page_heading

def _style(fig):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=40, b=15), legend_title_text=""
    )
    return fig

def show_overview(df: pd.DataFrame):
    page_heading("Executive Overview", "A concise view of transaction activity and fraud exposure for bank monitoring teams.")
    st.info("This dashboard analyses the first 50,000 rows of the CSV only. Figures below are sample-level indicators, not full-portfolio totals.")

    total = len(df)
    fraud_df = df[df["is_fraud"] == 1]
    fraud_count = len(fraud_df)
    legitimate = total - fraud_count
    fraud_rate = (fraud_count / total * 100) if total else 0
    fraud_value = float(fraud_df["amt"].sum()) if fraud_count else 0
    avg_fraud = float(fraud_df["amt"].mean()) if fraud_count else 0

    a, b, c = st.columns(3)
    a.metric("Transactions reviewed", f"{total:,}")
    b.metric("Fraud-labelled transactions", f"{fraud_count:,}")
    c.metric("Legitimate transactions", f"{legitimate:,}")
    d, e, f = st.columns(3)
    d.metric("Fraud rate in sample", f"{fraud_rate:.2f}%")
    e.metric("Fraud transaction value", f"${fraud_value:,.2f}")
    f.metric("Average fraud transaction", f"${avg_fraud:,.2f}")

    st.caption("Fraud transaction value is the sum of amounts labelled as fraud; it is not confirmed net bank loss. Recovery and chargeback data are not included.")
    st.markdown("### Transaction mix and amount profile")
    left, right = st.columns(2)
    with left:
        split = pd.DataFrame({"Status": ["Legitimate", "Fraud-labelled"], "Count": [legitimate, fraud_count]})
        fig = px.pie(split, names="Status", values="Count", hole=.6,
                     color="Status", color_discrete_map={"Legitimate":"#4C8DFF","Fraud-labelled":"#F472B6"})
        st.plotly_chart(_style(fig), use_container_width=True)
    with right:
        plot_df = df.copy()
        plot_df["Status"] = plot_df["is_fraud"].map({0:"Legitimate", 1:"Fraud-labelled"})
        # Clip only the chart axis to the 99th percentile so extreme values do not flatten the distribution.
        cap = float(plot_df["amt"].quantile(.99))
        plot_df["Amount shown (up to 99th percentile)"] = plot_df["amt"].clip(upper=cap)
        fig = px.histogram(plot_df, x="Amount shown (up to 99th percentile)", color="Status",
                           nbins=35, barmode="overlay", opacity=.72,
                           color_discrete_map={"Legitimate":"#4C8DFF","Fraud-labelled":"#F472B6"})
        st.plotly_chart(_style(fig), use_container_width=True)

    st.markdown("### Bank monitoring interpretation")
    if fraud_count:
        st.write(f"In this sample, **{fraud_rate:.2f}%** of reviewed transactions are labelled fraudulent. The average fraud-labelled transaction is **${avg_fraud:,.2f}**.")
    else:
        st.write("No fraud-labelled transactions appear in this sample.")
    st.warning("Use the hotspot and record-review pages to prioritise further investigation. A high count is not, by itself, proof of a high-risk customer or location.")
