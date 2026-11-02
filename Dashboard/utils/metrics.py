"""Reusable descriptive metric functions for dashboard pages."""

import pandas as pd


def fraud_rate(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Return fraud rate (%) grouped by a given column."""
    if group_col not in df.columns or df.empty:
        return pd.DataFrame(
            columns=[group_col, "fraud_count", "total_count", "fraud_rate_pct", "legit_count"]
        )
    grp = df.groupby(group_col)["is_fraud"].agg(
        fraud_count="sum", total_count="count"
    ).reset_index()
    grp["fraud_rate_pct"] = (
        grp["fraud_count"].div(grp["total_count"].where(grp["total_count"] != 0)).mul(100)
    )
    grp["legit_count"] = grp["total_count"] - grp["fraud_count"]
    return grp


def state_fraud_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "state" not in df.columns:
        return pd.DataFrame(
            columns=["state", "fraud_count", "total_count", "fraud_rate_pct", "legit_count", "fraud_amt"]
        )
    grp = fraud_rate(df, "state")
    amt = (
        df[df["is_fraud"] == 1].groupby("state")["amt"]
        .sum(min_count=1).reset_index(name="fraud_amt")
    )
    return grp.merge(amt, on="state", how="left").fillna({"fraud_amt": 0.0})


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "category" not in df.columns:
        return pd.DataFrame()
    grp = fraud_rate(df, "category")
    avg_amt = df.groupby("category")["amt"].mean().reset_index(name="avg_amt")
    fraud_avg = (
        df[df["is_fraud"] == 1].groupby("category")["amt"]
        .mean().reset_index(name="avg_fraud_amt")
    )
    return grp.merge(avg_amt, on="category").merge(fraud_avg, on="category", how="left")


def hourly_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "transaction_hour" not in df.columns or df.empty:
        return pd.DataFrame(
            columns=["transaction_hour", "total", "fraud_count", "avg_amt", "fraud_rate_pct"]
        )
    grp = df.groupby("transaction_hour").agg(
        total=("is_fraud", "count"),
        fraud_count=("is_fraud", "sum"),
        avg_amt=("amt", "mean"),
    ).reset_index()
    grp["fraud_rate_pct"] = grp["fraud_count"].div(grp["total"].where(grp["total"] != 0)).mul(100)
    return grp


def peak_fraud_hours(df: pd.DataFrame, top_n: int = 3, min_sample: int = 30) -> list:
    """Rank observed hours by rate after excluding very small samples."""
    h = hourly_summary(df)
    h = h[h["total"] >= min_sample]
    h = h.sort_values(["fraud_rate_pct", "total"], ascending=[False, False])
    return h["transaction_hour"].head(top_n).tolist()


def weekday_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "weekday_label" not in df.columns or df.empty:
        return pd.DataFrame(
            columns=["weekday_label", "total", "fraud_count", "fraud_rate_pct"]
        )
    result = df.groupby("weekday_label").agg(
        total=("is_fraud", "count"), fraud_count=("is_fraud", "sum")
    ).reset_index()
    result["fraud_rate_pct"] = result["fraud_count"].div(result["total"]).mul(100)
    return result


def month_summary(df: pd.DataFrame) -> pd.DataFrame:
    if "month_label" not in df.columns or df.empty:
        return pd.DataFrame(
            columns=["month_label", "total", "fraud_count", "fraud_rate_pct"]
        )
    result = df.groupby("month_label").agg(
        total=("is_fraud", "count"), fraud_count=("is_fraud", "sum")
    ).reset_index()
    result["fraud_rate_pct"] = result["fraud_count"].div(result["total"]).mul(100)
    return result


def distance_stats(df: pd.DataFrame) -> dict:
    if "distance_km" not in df.columns:
        return {}
    fraud_dist = df.loc[df["is_fraud"] == 1, "distance_km"].dropna()
    legit_dist = df.loc[df["is_fraud"] == 0, "distance_km"].dropna()
    return {
        "fraud_median_km": round(float(fraud_dist.median()), 2) if not fraud_dist.empty else 0.0,
        "legit_median_km": round(float(legit_dist.median()), 2) if not legit_dist.empty else 0.0,
        "fraud_mean_km": round(float(fraud_dist.mean()), 2) if not fraud_dist.empty else 0.0,
        "legit_mean_km": round(float(legit_dist.mean()), 2) if not legit_dist.empty else 0.0,
    }


def format_currency(value: float) -> str:
    """Format amounts in the source dataset's currency (USD)."""
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"
    return f"${value:,.2f}"


def format_number(value: int) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.2f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:,.1f}K"
    return f"{value:,}"
