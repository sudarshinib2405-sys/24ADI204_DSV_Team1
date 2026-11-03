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

def show_risk_hotspots(df: pd.DataFrame):
    page_heading("Risk Hotspots", "Identify where fraud-labelled activity is concentrated across merchant categories, time and geography.")
    st.info("All results describe the 50,000-row sample after sidebar filters. Compare counts with rates and transaction volumes before drawing conclusions.")

    fraud = df[df["is_fraud"] == 1].copy()
    if fraud.empty:
        st.warning("No fraud-labelled transactions in the current selection. Change the status filter to All transactions.")
        return

    if "category" in df.columns:
        st.markdown("### Category risk profile")
        cat = df.groupby("category", dropna=False).agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum")
        ).reset_index()
        cat["fraud_rate_pct"] = 100 * cat["fraud_transactions"] / cat["total_transactions"].clip(lower=1)
        cat = cat.sort_values("fraud_transactions", ascending=False)
        fig = px.bar(cat, x="category", y="fraud_transactions", color="fraud_rate_pct",
                     color_continuous_scale="Plasma",
                     hover_data=["total_transactions", "fraud_rate_pct"],
                     labels={"category":"Transaction category","fraud_transactions":"Fraud-labelled transactions","fraud_rate_pct":"Fraud rate (%)"})
        st.plotly_chart(_style(fig), use_container_width=True)
        st.dataframe(cat.rename(columns={
            "category":"Category", "total_transactions":"Transactions",
            "fraud_transactions":"Fraud transactions", "fraud_rate_pct":"Fraud rate (%)"
        }).round(2), use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        if "hour" in fraud.columns and fraud["hour"].notna().any():
            st.markdown("### Fraud-labelled activity by hour")
            hourly = fraud.groupby("hour").size().reindex(range(24), fill_value=0).rename("Fraud transactions").reset_index()
            fig = px.bar(hourly, x="hour", y="Fraud transactions",
                         labels={"hour":"Hour of day"})
            st.plotly_chart(_style(fig), use_container_width=True)
        else:
            st.caption("Time analysis unavailable: transaction timestamp column not found.")
    with right:
        if "state" in fraud.columns:
            st.markdown("### States with most fraud-labelled records")
            states = fraud.groupby("state").size().nlargest(10).rename("Fraud transactions").reset_index()
            fig = px.bar(states.sort_values("Fraud transactions"), x="Fraud transactions", y="state", orientation="h")
            st.plotly_chart(_style(fig), use_container_width=True)
        else:
            st.caption("Geographic analysis unavailable: state column not found.")


    if "state" in df.columns:
        st.markdown("### Geographical review")
        st.caption("Compare fraud counts with transaction volume. A state with more transactions may naturally have more fraud records.")

        geo = df.groupby("state", dropna=False).agg(
            total_transactions=("is_fraud", "size"),
            fraud_transactions=("is_fraud", "sum"),
            fraud_amount=("amt", lambda values: float(values[df.loc[values.index, "is_fraud"].eq(1)].sum()))
        ).reset_index()
        geo["fraud_rate_pct"] = (
            100 * geo["fraud_transactions"] / geo["total_transactions"].clip(lower=1)
        )
        geo = geo.sort_values("fraud_rate_pct", ascending=False)

        # Avoid highlighting tiny groups as if they were reliable risk signals.
        min_volume = st.slider(
            "Minimum transactions per state for rate comparison",
            min_value=1, max_value=max(1, int(geo["total_transactions"].max())),
            value=min(100, max(1, int(geo["total_transactions"].max()))),
            help="States below this transaction count are excluded from the rate chart, but remain in the table."
        )
        geo_chart = geo[geo["total_transactions"] >= min_volume].copy()

        if not geo_chart.empty:
            top_geo = geo_chart.sort_values("fraud_rate_pct", ascending=False).head(12)
            fig = px.bar(
                top_geo.sort_values("fraud_rate_pct"),
                x="fraud_rate_pct", y="state", orientation="h",
                color="fraud_rate_pct", color_continuous_scale="Plasma",
                hover_data=["total_transactions", "fraud_transactions", "fraud_amount"],
                labels={
                    "state": "State",
                    "fraud_rate_pct": "Fraud rate (%)",
                    "total_transactions": "Transactions",
                    "fraud_transactions": "Fraud transactions",
                    "fraud_amount": "Fraud-labelled transaction value"
                }
            )
            st.plotly_chart(_style(fig), use_container_width=True)
        else:
            st.info("No states meet the selected minimum transaction volume.")

        st.markdown("#### State-level summary")
        geo_table = geo.rename(columns={
            "state": "State",
            "total_transactions": "Total transactions",
            "fraud_transactions": "Fraud transactions",
            "fraud_rate_pct": "Fraud rate (%)",
            "fraud_amount": "Fraud-labelled transaction value"
        }).copy()
        geo_table["Fraud rate (%)"] = geo_table["Fraud rate (%)"].round(2)
        geo_table["Fraud-labelled transaction value"] = geo_table["Fraud-labelled transaction value"].round(2)
        st.dataframe(geo_table, use_container_width=True, hide_index=True)
    else:
        st.info("Geographical review unavailable: the dataset does not contain a state column.")

    st.caption("These are descriptive patterns in a sample. A bank should validate against exposure, customer base, merchant volume and confirmed investigation outcomes.")
