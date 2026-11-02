"""Reusable Plotly charts and visual components for FraudLens."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Brand color palette
FRAUD_COLOR = "#EF4444"
LEGIT_COLOR = "#22C55E"
ACCENT_COLOR = "#3B82F6"
WARN_COLOR = "#F59E0B"
PURPLE_COLOR = "#A855F7"
NEUTRAL_COLOR = "#94A3B8"
DARK_NAVY = "#0B1220"
CARD_BG = "#17243A"
BORDER_COLOR = "#26354D"

COLOR_MAP = {
    "Fraudulent": FRAUD_COLOR,
    "Legitimate": LEGIT_COLOR,
    1: FRAUD_COLOR,
    0: LEGIT_COLOR,
}

LAYOUT_DEFAULTS = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#CBD5E1"),
    margin=dict(l=40, r=20, t=50, b=40),
)


def style_figure(fig: go.Figure, title: str = "", **layout) -> go.Figure:
    """Apply dark navy theme, typography, gridlines and title."""
    title_dict = {"text": title, "font": {"size": 16, "color": "#F1F5F9"}} if title else None
    merged = {**LAYOUT_DEFAULTS, **layout}
    if title_dict:
        merged["title"] = title_dict
    fig.update_layout(**merged)
    fig.update_xaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(148,163,184,0.12)", zeroline=False)
    return fig


def kpi_card(title: str, value: str, subtitle: str = "", color: str = ACCENT_COLOR) -> str:
    """Return a styled HTML KPI card matching design standards."""
    return f"""
<div style="background:linear-gradient(135deg,#17243a,#0b1220);border:1px solid {color}30;border-left:4px solid {color};border-radius:12px;padding:20px;text-align:center;margin-bottom:8px;">
  <p style="color:#64748B;font-size:11px;text-transform:uppercase;letter-spacing:1.5px;margin:0 0 8px 0;">{title}</p>
  <p style="color:{color};font-size:28px;font-weight:800;margin:0 0 4px 0;">{value}</p>
  <p style="color:#475569;font-size:11px;margin:0;">{subtitle}</p>
</div>
"""


# ---------------------------------------------------------
# Executive & Overview Charts
# ---------------------------------------------------------

def donut_fraud_distribution(df: pd.DataFrame) -> go.Figure:
    """Donut chart for Fraud vs Legitimate volume distribution."""
    if df.empty or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Transaction Distribution")
    counts = df["is_fraud"].value_counts()
    legit_count = int(counts.get(0, 0))
    fraud_count = int(counts.get(1, 0))
    labels = ["Legitimate", "Fraudulent"]
    values = [legit_count, fraud_count]
    colors = [LEGIT_COLOR, FRAUD_COLOR]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=colors, line=dict(color=DARK_NAVY, width=2)),
                textinfo="percent+label",
                textfont=dict(size=13, color="#F8FAFC"),
                hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )
    return style_figure(fig, "Transaction Distribution (Fraud vs Legitimate)")


def pie_fraud_distribution(df: pd.DataFrame) -> go.Figure:
    """Alias for backwards compatibility."""
    return donut_fraud_distribution(df)


def histogram_amount(df: pd.DataFrame, cap_percentile: float = 0.99) -> go.Figure:
    """Overlapping histogram of transaction amounts capped at 99th percentile."""
    if df.empty or "amt" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Transaction Amount Distribution")

    fig = go.Figure()
    for label, is_fraud_val, color in [("Legitimate", 0, LEGIT_COLOR), ("Fraudulent", 1, FRAUD_COLOR)]:
        sub = df.loc[df["is_fraud"] == is_fraud_val, "amt"].dropna()
        if not sub.empty:
            cap = float(sub.quantile(cap_percentile))
            clipped = sub.clip(upper=cap)
            fig.add_trace(
                go.Histogram(
                    x=clipped,
                    name=label,
                    marker_color=color,
                    opacity=0.7,
                    nbinsx=50,
                    hovertemplate=f"<b>{label}</b><br>Amount: $%{{x:,.2f}}<br>Count: %{{y:,}}<extra></extra>",
                )
            )

    fig.update_layout(barmode="overlay", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(title="Transaction Amount (USD; capped at P99)")
    fig.update_yaxes(title="Transaction Count")
    return style_figure(fig, "Amount Distribution (Fraud vs Legitimate)")


def line_fraud_trend(df: pd.DataFrame) -> go.Figure:
    """Monthly fraud trend with dual axes: Fraud Count (bars) & Fraud Rate % (line)."""
    if df.empty or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Monthly Fraud Trend")

    # Group by period or month_label
    if "trans_datetime" in df.columns and not df["trans_datetime"].isna().all():
        data = df.assign(period=pd.to_datetime(df["trans_datetime"]).dt.to_period("M").astype(str))
        monthly = data.groupby("period").agg(
            total=("is_fraud", "size"),
            fraud=("is_fraud", "sum"),
        ).reset_index()
        monthly = monthly.sort_values("period")
        x_col = "period"
        x_title = "Month"
    elif "month_label" in df.columns:
        order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly = df.groupby("month_label").agg(
            total=("is_fraud", "size"),
            fraud=("is_fraud", "sum"),
        ).reset_index()
        monthly["month_cat"] = pd.Categorical(monthly["month_label"], categories=order, ordered=True)
        monthly = monthly.sort_values("month_cat")
        x_col = "month_label"
        x_title = "Month"
    else:
        return style_figure(go.Figure(), "Monthly Fraud Trend")

    monthly["fraud_rate_pct"] = monthly["fraud"].div(monthly["total"].where(monthly["total"] != 0)).mul(100)

    fig = go.Figure()
    # Fraud count as bar trace on secondary y
    fig.add_trace(
        go.Bar(
            x=monthly[x_col],
            y=monthly["fraud"],
            name="Fraud Count",
            marker_color="rgba(239, 68, 68, 0.35)",
            yaxis="y2",
            hovertemplate="<b>%{x}</b><br>Fraud Count: %{y:,}<extra></extra>",
        )
    )
    # Fraud rate as line trace on primary y
    fig.add_trace(
        go.Scatter(
            x=monthly[x_col],
            y=monthly["fraud_rate_pct"],
            name="Fraud Rate (%)",
            mode="lines+markers",
            line=dict(color=FRAUD_COLOR, width=3),
            marker=dict(size=7, color=FRAUD_COLOR),
            yaxis="y1",
            hovertemplate="<b>%{x}</b><br>Fraud Rate: %{y:.3f}%<extra></extra>",
        )
    )

    fig.update_layout(
        xaxis=dict(title=x_title),
        yaxis=dict(title=dict(text="Fraud Rate (%)", font=dict(color=FRAUD_COLOR)), tickfont=dict(color=FRAUD_COLOR)),
        yaxis2=dict(
            title=dict(text="Fraud Count", font=dict(color=WARN_COLOR)),
            tickfont=dict(color=WARN_COLOR),
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return style_figure(fig, "Monthly Fraud Trend (Dual-Axis)")


def bar_fraud_value_by_category(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Horizontal bar chart of fraud-associated value by category."""
    if df.empty or "category" not in df.columns or "amt" not in df.columns:
        return style_figure(go.Figure(), "Fraud Exposure by Category")

    fraud_df = df[df["is_fraud"] == 1]
    if fraud_df.empty:
        return style_figure(go.Figure(), "Fraud Exposure by Category (No Fraud in Cohort)")

    cat_amt = fraud_df.groupby("category")["amt"].sum().reset_index()
    cat_amt = cat_amt.sort_values("amt", ascending=True).tail(top_n)

    fig = go.Figure(
        go.Bar(
            x=cat_amt["amt"],
            y=cat_amt["category"],
            orientation="h",
            marker=dict(
                color=cat_amt["amt"],
                colorscale=[[0, "#991B1B"], [1, FRAUD_COLOR]],
                showscale=False,
            ),
            hovertemplate="<b>%{y}</b><br>Fraud Exposure: $%{x:,.2f}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Total Fraud Amount (USD)")
    fig.update_yaxes(title="")
    return style_figure(fig, f"Top {top_n} Categories by Fraud-Associated Exposure")


def box_amount_by_fraud(df: pd.DataFrame, sample_n: int = 20000) -> go.Figure:
    """Box plots of transaction amount by fraud status."""
    if df.empty or "amt" not in df.columns or "fraud_label" not in df.columns:
        return style_figure(go.Figure(), "Transaction Amount by Status")

    fig = go.Figure()
    for label, color in [("Legitimate", LEGIT_COLOR), ("Fraudulent", FRAUD_COLOR)]:
        sub = df.loc[df["fraud_label"] == label, "amt"].dropna()
        if not sub.empty:
            sampled = sub.sample(min(sample_n, len(sub)), random_state=42)
            fig.add_trace(
                go.Box(
                    y=sampled,
                    name=label,
                    marker_color=color,
                    boxpoints="outliers",
                    jitter=0.2,
                    boxmean=True,
                    hovertemplate=f"<b>{label}</b><br>Amount: $%{{y:,.2f}}<extra></extra>",
                )
            )

    fig.update_yaxes(title="Transaction Amount (USD)")
    return style_figure(fig, "Transaction Amount Distribution by Status")


def stacked_bar_category_counts(df: pd.DataFrame) -> go.Figure:
    """Stacked bar of transaction volume by category (Legitimate vs Fraudulent)."""
    if df.empty or "category" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Transaction Count by Category")

    counts = df.groupby(["category", "is_fraud"]).size().unstack(fill_value=0).reset_index()
    counts = counts.rename(columns={0: "Legitimate", 1: "Fraudulent"})
    if "Legitimate" not in counts.columns:
        counts["Legitimate"] = 0
    if "Fraudulent" not in counts.columns:
        counts["Fraudulent"] = 0
    counts["Total"] = counts["Legitimate"] + counts["Fraudulent"]
    counts = counts.sort_values("Total", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=counts["category"],
            x=counts["Legitimate"],
            name="Legitimate",
            orientation="h",
            marker_color=LEGIT_COLOR,
            hovertemplate="<b>%{y}</b><br>Legitimate: %{x:,}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=counts["category"],
            x=counts["Fraudulent"],
            name="Fraudulent",
            orientation="h",
            marker_color=FRAUD_COLOR,
            hovertemplate="<b>%{y}</b><br>Fraudulent: %{x:,}<extra></extra>",
        )
    )

    fig.update_layout(barmode="stack", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(title="Transaction Count")
    fig.update_yaxes(title="")
    return style_figure(fig, "Transaction Volume by Category")


# ---------------------------------------------------------
# Temporal Risk Charts
# ---------------------------------------------------------

def bar_fraud_rate_by_hour(df: pd.DataFrame) -> go.Figure:
    """Bar chart of fraud rate by hour (0-23) with gradient highlight on high risk."""
    if df.empty or "transaction_hour" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Fraud Rate by Hour of Day")

    grouped = df.groupby("transaction_hour").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reset_index()
    # Reindex to ensure all 24 hours are present
    all_hours = pd.DataFrame({"transaction_hour": list(range(24))})
    grouped = all_hours.merge(grouped, on="transaction_hour", how="left").fillna(0)
    grouped["rate"] = grouped["fraud"].div(grouped["total"].where(grouped["total"] != 0)).mul(100).fillna(0)

    fig = go.Figure(
        go.Bar(
            x=grouped["transaction_hour"],
            y=grouped["rate"],
            marker=dict(
                color=grouped["rate"],
                colorscale=[[0, ACCENT_COLOR], [0.5, WARN_COLOR], [1, FRAUD_COLOR]],
                colorbar=dict(title="Rate %"),
            ),
            customdata=grouped[["total", "fraud"]],
            hovertemplate="<b>Hour %{x:02d}:00</b><br>Fraud Rate: %{y:.3f}%<br>Total Txns: %{customdata[0]:,}<br>Fraud Txns: %{customdata[1]:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Hour of Day (0–23)", dtick=1)
    fig.update_yaxes(title="Fraud Rate (%)")
    return style_figure(fig, "Fraud Rate by Hour of Day")


def stacked_area_volume_by_hour(df: pd.DataFrame) -> go.Figure:
    """Stacked area / bar chart of legitimate vs fraudulent transaction volume by hour."""
    if df.empty or "transaction_hour" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Hourly Transaction Volume")

    grouped = df.groupby(["transaction_hour", "is_fraud"]).size().unstack(fill_value=0).reset_index()
    all_hours = pd.DataFrame({"transaction_hour": list(range(24))})
    grouped = all_hours.merge(grouped, on="transaction_hour", how="left").fillna(0)
    if 0 not in grouped.columns:
        grouped[0] = 0
    if 1 not in grouped.columns:
        grouped[1] = 0

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=grouped["transaction_hour"],
            y=grouped[0],
            mode="lines",
            name="Legitimate",
            stackgroup="one",
            line=dict(color=LEGIT_COLOR, width=1),
            fillcolor="rgba(34, 197, 94, 0.4)",
            hovertemplate="<b>Hour %{x:02d}:00</b><br>Legitimate: %{y:,}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=grouped["transaction_hour"],
            y=grouped[1],
            mode="lines",
            name="Fraudulent",
            stackgroup="one",
            line=dict(color=FRAUD_COLOR, width=1),
            fillcolor="rgba(239, 68, 68, 0.7)",
            hovertemplate="<b>Hour %{x:02d}:00</b><br>Fraudulent: %{y:,}<extra></extra>",
        )
    )

    fig.update_xaxes(title="Hour of Day", dtick=2)
    fig.update_yaxes(title="Transaction Volume")
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return style_figure(fig, "Hourly Transaction Volume (Legitimate vs Fraudulent)")


def bar_fraud_rate_by_weekday(df: pd.DataFrame) -> go.Figure:
    """Bar chart of fraud rate by weekday ordered Mon-Sun."""
    order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    if df.empty or "weekday_label" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Fraud Rate by Day of Week")

    grouped = df.groupby("weekday_label").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reset_index()
    grouped["rate"] = grouped["fraud"].div(grouped["total"].where(grouped["total"] != 0)).mul(100)
    grouped["weekday_label"] = pd.Categorical(grouped["weekday_label"], categories=order, ordered=True)
    grouped = grouped.sort_values("weekday_label")

    fig = go.Figure(
        go.Bar(
            x=grouped["weekday_label"].astype(str),
            y=grouped["rate"],
            marker=dict(
                color=grouped["rate"],
                colorscale=[[0, ACCENT_COLOR], [1, PURPLE_COLOR]],
            ),
            customdata=grouped[["total", "fraud"]],
            hovertemplate="<b>%{x}</b><br>Fraud Rate: %{y:.3f}%<br>Total Txns: %{customdata[0]:,}<br>Fraud Txns: %{customdata[1]:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Day of Week")
    fig.update_yaxes(title="Fraud Rate (%)")
    return style_figure(fig, "Fraud Rate by Day of Week")


def bar_fraud_rate_by_month(df: pd.DataFrame) -> go.Figure:
    """Bar chart of fraud rate by month ordered Jan-Dec."""
    order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    if df.empty or "month_label" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Fraud Rate by Month")

    grouped = df.groupby("month_label").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reset_index()
    grouped["rate"] = grouped["fraud"].div(grouped["total"].where(grouped["total"] != 0)).mul(100)
    grouped["month_label"] = pd.Categorical(grouped["month_label"], categories=order, ordered=True)
    grouped = grouped.sort_values("month_label")

    fig = go.Figure(
        go.Bar(
            x=grouped["month_label"].astype(str),
            y=grouped["rate"],
            marker=dict(
                color=grouped["rate"],
                colorscale=[[0, ACCENT_COLOR], [1, WARN_COLOR]],
            ),
            customdata=grouped[["total", "fraud"]],
            hovertemplate="<b>%{x}</b><br>Fraud Rate: %{y:.3f}%<br>Total Txns: %{customdata[0]:,}<br>Fraud Txns: %{customdata[1]:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Month")
    fig.update_yaxes(title="Fraud Rate (%)")
    return style_figure(fig, "Fraud Rate by Month of Year")


def heatmap_hour_weekday(df: pd.DataFrame) -> go.Figure:
    """Heatmap of Hour x Weekday fraud rate."""
    order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    if df.empty or "weekday_label" not in df.columns or "transaction_hour" not in df.columns:
        return style_figure(go.Figure(), "Fraud Rate: Hour vs Weekday")

    grouped = df.pivot_table(
        index="weekday_label",
        columns="transaction_hour",
        values="is_fraud",
        aggfunc=["mean", "count"],
        observed=True,
    )
    if grouped.empty:
        return style_figure(go.Figure(), "Fraud Rate: Hour vs Weekday")

    rates = grouped["mean"].reindex(order).mul(100).fillna(0)
    counts = grouped["count"].reindex(order).fillna(0)

    fig = go.Figure(
        go.Heatmap(
            z=rates.to_numpy(),
            x=[f"{h:02d}:00" for h in rates.columns],
            y=rates.index.tolist(),
            customdata=counts.to_numpy(),
            colorscale=[[0, "#0E1A2F"], [0.25, "#1E3A8A"], [0.6, WARN_COLOR], [1, FRAUD_COLOR]],
            colorbar=dict(title="Fraud Rate (%)"),
            hovertemplate="<b>%{y} at %{x}</b><br>Fraud Rate: %{z:.3f}%<br>Transactions: %{customdata:,}<extra></extra>",
            zmin=0,
        )
    )
    fig.update_xaxes(title="Hour of Day", dtick=2)
    fig.update_yaxes(title="Weekday")
    return style_figure(fig, "Temporal Heatmap: Fraud Rate by Hour & Day")


def line_avg_amount_by_hour(df: pd.DataFrame) -> go.Figure:
    """Average transaction amount by hour for Legitimate vs Fraudulent."""
    if df.empty or "transaction_hour" not in df.columns or "amt" not in df.columns:
        return style_figure(go.Figure(), "Average Amount by Hour")

    grouped = df.groupby(["transaction_hour", "is_fraud"])["amt"].mean().unstack(fill_value=0).reset_index()
    all_hours = pd.DataFrame({"transaction_hour": list(range(24))})
    grouped = all_hours.merge(grouped, on="transaction_hour", how="left").fillna(0)
    if 0 not in grouped.columns:
        grouped[0] = 0
    if 1 not in grouped.columns:
        grouped[1] = 0

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=grouped["transaction_hour"],
            y=grouped[0],
            name="Legitimate Mean ($)",
            mode="lines+markers",
            line=dict(color=LEGIT_COLOR, width=2),
            hovertemplate="<b>Hour %{x:02d}:00</b><br>Legitimate Mean: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=grouped["transaction_hour"],
            y=grouped[1],
            name="Fraudulent Mean ($)",
            mode="lines+markers",
            line=dict(color=FRAUD_COLOR, width=2),
            hovertemplate="<b>Hour %{x:02d}:00</b><br>Fraudulent Mean: $%{y:,.2f}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Hour of Day", dtick=2)
    fig.update_yaxes(title="Average Amount (USD)")
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return style_figure(fig, "Average Transaction Amount by Hour (USD)")


# ---------------------------------------------------------
# Geographical Risk Charts
# ---------------------------------------------------------

US_STATE_CODES = set(
    "AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN "
    "MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA "
    "WA WV WI WY DC".split()
)


def choropleth_state_fraud_rate(df: pd.DataFrame) -> go.Figure:
    """Choropleth of US state-level fraud rate."""
    if df.empty or "state" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "State-Level Fraud Rate")

    valid_mask = df["state"].astype(str).str.upper().isin(US_STATE_CODES)
    data = df[valid_mask]
    if data.empty:
        return style_figure(go.Figure(), "State-Level Fraud Rate (No Valid US States)")

    grouped = data.groupby("state").agg(
        fraud_count=("is_fraud", "sum"),
        total=("is_fraud", "count"),
    ).reset_index()
    grouped["fraud_rate"] = grouped["fraud_count"].div(grouped["total"].where(grouped["total"] != 0)).mul(100)

    fig = px.choropleth(
        grouped,
        locations="state",
        locationmode="USA-states",
        color="fraud_rate",
        scope="usa",
        color_continuous_scale=[[0, "#0E1A2F"], [0.4, ACCENT_COLOR], [0.75, WARN_COLOR], [1, FRAUD_COLOR]],
        hover_data={"fraud_count": True, "total": True, "fraud_rate": ":.3f"},
        labels={"fraud_rate": "Fraud Rate (%)", "state": "State", "total": "Total", "fraud_count": "Fraud"},
    )
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)", landcolor="#17243A"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return style_figure(fig, "Geographic Fraud Rate by US State")


def bar_top_states_fraud_rate(df: pd.DataFrame, top_n: int = 20, min_transactions: int = 50) -> go.Figure:
    """Horizontal bar chart of top states by fraud rate with minimum volume filter."""
    if df.empty or "state" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Top States by Fraud Rate")

    grouped = df.groupby("state").agg(
        fraud=("is_fraud", "sum"),
        total=("is_fraud", "count"),
    ).reset_index()
    grouped = grouped[grouped["total"] >= min_transactions]
    if grouped.empty:
        return style_figure(go.Figure(), "Top States by Fraud Rate (Insufficient Data)")

    grouped["rate"] = grouped["fraud"].div(grouped["total"]).mul(100)
    grouped = grouped.sort_values("rate", ascending=True).tail(top_n)

    fig = go.Figure(
        go.Bar(
            x=grouped["rate"],
            y=grouped["state"],
            orientation="h",
            marker=dict(
                color=grouped["rate"],
                colorscale=[[0, ACCENT_COLOR], [1, FRAUD_COLOR]],
            ),
            customdata=grouped[["total", "fraud"]],
            hovertemplate="<b>State: %{y}</b><br>Fraud Rate: %{x:.3f}%<br>Total Txns: %{customdata[0]:,}<br>Fraud Txns: %{customdata[1]:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Fraud Rate (%)")
    fig.update_yaxes(title="")
    return style_figure(fig, f"Top {top_n} States by Observed Fraud Rate (min {min_transactions} txns)")


def scatter_geo_locations(
    df: pd.DataFrame,
    lat_col: str = "lat",
    lon_col: str = "long",
    title: str = "Customer Geographic Locations",
    sample_n: int = 20000,
) -> go.Figure:
    """Scatter geo map of customer or merchant locations, sampled safely."""
    required = {lat_col, lon_col, "is_fraud"}
    if df.empty or not required.issubset(df.columns):
        return style_figure(go.Figure(), title)

    # Safe coordinate filtering for US continental bounds
    sub = df[
        df[lat_col].between(20, 55) & df[lon_col].between(-130, -65)
    ].copy()

    if sub.empty:
        return style_figure(go.Figure(), f"{title} (No coordinates in range)")

    # Sample safely: prioritize all fraud cases + sample legit cases
    fraud_pts = sub[sub["is_fraud"] == 1]
    legit_pts = sub[sub["is_fraud"] == 0]
    n_legit = max(0, sample_n - len(fraud_pts))
    legit_sample = legit_pts.sample(min(n_legit, len(legit_pts)), random_state=42)
    sample_data = pd.concat([fraud_pts, legit_sample]).sample(frac=1, random_state=42)

    sample_data["status"] = sample_data["is_fraud"].map({0: "Legitimate", 1: "Fraudulent"})

    fig = px.scatter_geo(
        sample_data,
        lat=lat_col,
        lon=lon_col,
        color="status",
        color_discrete_map={"Legitimate": "rgba(34, 197, 94, 0.4)", "Fraudulent": FRAUD_COLOR},
        scope="usa",
        opacity=0.7,
        hover_data={"status": True, lat_col: False, lon_col: False},
    )
    fig.update_traces(marker=dict(size=3))
    fig.update_layout(
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)", landcolor="#17243A"),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return style_figure(fig, title)


def histogram_distance(df: pd.DataFrame, cap_percentile: float = 0.99) -> go.Figure:
    """Histogram of customer-to-merchant distance (km) by fraud status."""
    if df.empty or "distance_km" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Customer-Merchant Distance Distribution")

    fig = go.Figure()
    for label, val, color in [("Legitimate", 0, LEGIT_COLOR), ("Fraudulent", 1, FRAUD_COLOR)]:
        sub = df.loc[df["is_fraud"] == val, "distance_km"].dropna()
        if not sub.empty:
            cap = float(sub.quantile(cap_percentile))
            clipped = sub.clip(upper=cap)
            fig.add_trace(
                go.Histogram(
                    x=clipped,
                    name=label,
                    marker_color=color,
                    opacity=0.7,
                    nbinsx=40,
                    hovertemplate=f"<b>{label}</b><br>Distance: %{{x:,.1f}} km<br>Count: %{{y:,}}<extra></extra>",
                )
            )

    fig.update_layout(barmode="overlay", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(title="Customer-Merchant Distance (km; capped at P99)")
    fig.update_yaxes(title="Transaction Count")
    return style_figure(fig, "Customer-to-Merchant Distance Distribution")


def box_distance_by_fraud(df: pd.DataFrame, sample_n: int = 20000) -> go.Figure:
    """Box plot of customer-to-merchant distance by fraud status."""
    if df.empty or "distance_km" not in df.columns or "fraud_label" not in df.columns:
        return style_figure(go.Figure(), "Distance Distribution by Status")

    fig = go.Figure()
    for label, color in [("Legitimate", LEGIT_COLOR), ("Fraudulent", FRAUD_COLOR)]:
        sub = df.loc[df["fraud_label"] == label, "distance_km"].dropna()
        if not sub.empty:
            sampled = sub.sample(min(sample_n, len(sub)), random_state=42)
            fig.add_trace(
                go.Box(
                    y=sampled,
                    name=label,
                    marker_color=color,
                    boxpoints="outliers",
                    jitter=0.2,
                    boxmean=True,
                    hovertemplate=f"<b>{label}</b><br>Distance: %{{y:,.1f}} km<extra></extra>",
                )
            )

    fig.update_yaxes(title="Distance (km)")
    return style_figure(fig, "Customer-Merchant Distance by Status")


# ---------------------------------------------------------
# Behaviour Intelligence Charts
# ---------------------------------------------------------

def bar_fraud_rate_by_category(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of fraud rate by category sorted ascending."""
    if df.empty or "category" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Category Fraud Rate")

    grouped = df.groupby("category").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reset_index()
    grouped["rate"] = grouped["fraud"].div(grouped["total"].where(grouped["total"] != 0)).mul(100)
    grouped = grouped.sort_values("rate", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=grouped["rate"],
            y=grouped["category"],
            orientation="h",
            marker=dict(
                color=grouped["rate"],
                colorscale=[[0, ACCENT_COLOR], [0.5, WARN_COLOR], [1, FRAUD_COLOR]],
            ),
            customdata=grouped[["total", "fraud"]],
            hovertemplate="<b>%{y}</b><br>Fraud Rate: %{x:.3f}%<br>Total Txns: %{customdata[0]:,}<br>Fraud Txns: %{customdata[1]:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Fraud Rate (%)")
    fig.update_yaxes(title="")
    return style_figure(fig, "Fraud Rate by Transaction Category")


def bar_avg_fraud_amount_by_category(df: pd.DataFrame) -> go.Figure:
    """Bar chart of average fraud amount per category."""
    if df.empty or "category" not in df.columns or "amt" not in df.columns:
        return style_figure(go.Figure(), "Average Fraud Amount by Category")

    fraud_df = df[df["is_fraud"] == 1]
    if fraud_df.empty:
        return style_figure(go.Figure(), "Average Fraud Amount by Category (No Fraud Data)")

    grouped = fraud_df.groupby("category")["amt"].agg(mean="mean", count="count").reset_index()
    grouped = grouped.sort_values("mean", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=grouped["mean"],
            y=grouped["category"],
            orientation="h",
            marker=dict(color=PURPLE_COLOR),
            customdata=grouped["count"],
            hovertemplate="<b>%{y}</b><br>Avg Fraud Amt: $%{x:,.2f}<br>Fraud Txns: %{customdata:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Mean Fraud Amount (USD)")
    fig.update_yaxes(title="")
    return style_figure(fig, "Average Fraud Amount by Category")


def bar_gender_fraud_rate(df: pd.DataFrame) -> go.Figure:
    """Bar chart of fraud rate by gender."""
    if df.empty or "gender" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Fraud Rate by Gender")

    grouped = df.groupby("gender").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reset_index()
    grouped["rate"] = grouped["fraud"].div(grouped["total"].where(grouped["total"] != 0)).mul(100)

    fig = go.Figure(
        go.Bar(
            x=grouped["gender"],
            y=grouped["rate"],
            marker_color=[ACCENT_COLOR, WARN_COLOR][: len(grouped)],
            customdata=grouped[["total", "fraud"]],
            hovertemplate="<b>Gender %{x}</b><br>Fraud Rate: %{y:.3f}%<br>Total Txns: %{customdata[0]:,}<br>Fraud Txns: %{customdata[1]:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Gender")
    fig.update_yaxes(title="Fraud Rate (%)")
    return style_figure(fig, "Observed Fraud Rate by Gender")


def heatmap_gender_category(df: pd.DataFrame) -> go.Figure:
    """Heatmap of Gender x Category fraud rate."""
    if df.empty or "gender" not in df.columns or "category" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Gender × Category Fraud Rate")

    grouped = df.pivot_table(
        index="category",
        columns="gender",
        values="is_fraud",
        aggfunc="mean",
        observed=True,
    ).mul(100).fillna(0)

    fig = go.Figure(
        go.Heatmap(
            z=grouped.to_numpy(),
            x=grouped.columns.tolist(),
            y=grouped.index.tolist(),
            colorscale=[[0, "#0E1A2F"], [0.5, WARN_COLOR], [1, FRAUD_COLOR]],
            colorbar=dict(title="Rate %"),
            hovertemplate="<b>%{y} (Gender: %{x})</b><br>Fraud Rate: %{z:.3f}%<extra></extra>",
        )
    )
    fig.update_xaxes(title="Gender")
    fig.update_yaxes(title="Category")
    return style_figure(fig, "Gender × Category Fraud Rate (%)")


def bar_top_merchants_fraud(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Bar chart of top merchants by fraud count."""
    if df.empty or "merchant" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Top Merchants by Fraud Count")

    fraud_df = df[df["is_fraud"] == 1]
    if fraud_df.empty:
        return style_figure(go.Figure(), "Top Merchants by Fraud Count (No Fraud)")

    grouped = fraud_df.groupby("merchant").agg(
        fraud_count=("is_fraud", "count"),
        fraud_exposure=("amt", "sum"),
    ).reset_index()
    grouped = grouped.sort_values("fraud_count", ascending=True).tail(top_n)

    # Clean merchant display name
    clean_names = grouped["merchant"].astype(str).str.replace("^fraud_", "", regex=True)

    fig = go.Figure(
        go.Bar(
            x=grouped["fraud_count"],
            y=clean_names,
            orientation="h",
            marker=dict(color=FRAUD_COLOR),
            customdata=grouped["fraud_exposure"],
            hovertemplate="<b>%{y}</b><br>Fraud Count: %{x:,}<br>Total Exposure: $%{customdata:,.2f}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Fraudulent Transaction Count")
    fig.update_yaxes(title="")
    return style_figure(fig, f"Top {top_n} Merchants by Fraud Incident Count")


def bar_merchant_fraud_rate_min_vol(df: pd.DataFrame, min_volume: int = 100, top_n: int = 15) -> go.Figure:
    """Top merchants by fraud rate with minimum transaction volume threshold."""
    if df.empty or "merchant" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Merchant Fraud Rate")

    grouped = df.groupby("merchant").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reset_index()
    grouped = grouped[grouped["total"] >= min_volume]
    if grouped.empty:
        return style_figure(go.Figure(), f"Merchant Fraud Rate (No merchants with >= {min_volume} txns)")

    grouped["rate"] = grouped["fraud"].div(grouped["total"]).mul(100)
    grouped = grouped.sort_values("rate", ascending=True).tail(top_n)
    clean_names = grouped["merchant"].astype(str).str.replace("^fraud_", "", regex=True)

    fig = go.Figure(
        go.Bar(
            x=grouped["rate"],
            y=clean_names,
            orientation="h",
            marker=dict(
                color=grouped["rate"],
                colorscale=[[0, WARN_COLOR], [1, FRAUD_COLOR]],
            ),
            customdata=grouped[["total", "fraud"]],
            hovertemplate="<b>%{y}</b><br>Fraud Rate: %{x:.3f}%<br>Total Txns: %{customdata[0]:,}<br>Fraud Txns: %{customdata[1]:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Fraud Rate (%)")
    fig.update_yaxes(title="")
    return style_figure(fig, f"Top {top_n} Merchants by Fraud Rate (min {min_volume} txns)")


def scatter_distance_vs_amount(df: pd.DataFrame, sample_n: int = 20000) -> go.Figure:
    """Scatter plot of Distance vs Amount colored by fraud status."""
    required = {"distance_km", "amt", "is_fraud"}
    if df.empty or not required.issubset(df.columns):
        return style_figure(go.Figure(), "Distance vs Amount")

    # Sample safely: keep all fraud + sample legit
    fraud_pts = df[df["is_fraud"] == 1]
    legit_pts = df[df["is_fraud"] == 0]
    n_legit = max(0, sample_n - len(fraud_pts))
    legit_sample = legit_pts.sample(min(n_legit, len(legit_pts)), random_state=42)
    sample_data = pd.concat([fraud_pts, legit_sample]).sample(frac=1, random_state=42)

    sample_data["label"] = sample_data["is_fraud"].map({0: "Legitimate", 1: "Fraudulent"})

    fig = px.scatter(
        sample_data,
        x="distance_km",
        y="amt",
        color="label",
        color_discrete_map={"Legitimate": "rgba(34, 197, 94, 0.35)", "Fraudulent": FRAUD_COLOR},
        opacity=0.6,
        labels={"distance_km": "Customer-Merchant Distance (km)", "amt": "Amount (USD)", "label": "Status"},
        hover_data={"distance_km": ":.1f", "amt": ":$,.2f", "label": True},
    )
    fig.update_traces(marker=dict(size=4))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return style_figure(fig, "Distance vs Amount (Sampled View)")


def bar_median_distance_by_category(df: pd.DataFrame) -> go.Figure:
    """Median distance comparison by category for Legitimate vs Fraudulent."""
    if df.empty or "category" not in df.columns or "distance_km" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Median Distance by Category")

    grouped = df.groupby(["category", "is_fraud"])["distance_km"].median().unstack(fill_value=0).reset_index()
    grouped = grouped.rename(columns={0: "Legitimate", 1: "Fraudulent"})
    if "Legitimate" not in grouped.columns:
        grouped["Legitimate"] = 0
    if "Fraudulent" not in grouped.columns:
        grouped["Fraudulent"] = 0
    grouped = grouped.sort_values("Fraudulent", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=grouped["category"],
            x=grouped["Legitimate"],
            name="Legitimate Median (km)",
            orientation="h",
            marker_color=LEGIT_COLOR,
            hovertemplate="<b>%{y}</b><br>Legit Median: %{x:,.1f} km<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            y=grouped["category"],
            x=grouped["Fraudulent"],
            name="Fraudulent Median (km)",
            orientation="h",
            marker_color=FRAUD_COLOR,
            hovertemplate="<b>%{y}</b><br>Fraud Median: %{x:,.1f} km<extra></extra>",
        )
    )
    fig.update_layout(barmode="group", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(title="Median Distance (km)")
    fig.update_yaxes(title="")
    return style_figure(fig, "Median Distance by Category (km)")


def histogram_age_distribution(df: pd.DataFrame) -> go.Figure:
    """Customer age distribution by fraud status."""
    if df.empty or "customer_age" not in df.columns or "is_fraud" not in df.columns:
        return style_figure(go.Figure(), "Customer Age Distribution")

    fig = go.Figure()
    for label, val, color in [("Legitimate", 0, LEGIT_COLOR), ("Fraudulent", 1, FRAUD_COLOR)]:
        sub = df.loc[df["is_fraud"] == val, "customer_age"].dropna()
        if not sub.empty:
            fig.add_trace(
                go.Histogram(
                    x=sub,
                    name=label,
                    marker_color=color,
                    opacity=0.7,
                    nbinsx=35,
                    hovertemplate=f"<b>{label}</b><br>Age: %{{x}}<br>Count: %{{y:,}}<extra></extra>",
                )
            )

    fig.update_layout(barmode="overlay", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_xaxes(title="Customer Age (Years)", dtick=10)
    fig.update_yaxes(title="Transaction Count")
    return style_figure(fig, "Customer Age Distribution by Status")
