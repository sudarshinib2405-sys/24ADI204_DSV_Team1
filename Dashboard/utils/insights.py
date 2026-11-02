"""Dynamic findings and practical recommendations from observed data."""

import pandas as pd

from utils.metrics import fraud_rate, hourly_summary


INSIGHT_COLUMNS = ["Observed Finding", "Analytical Interpretation", "Suggested Action"]


def build_insights(df: pd.DataFrame, min_sample: int = 30) -> pd.DataFrame:
    """Create non-causal observations, excluding small groups from rate rankings."""
    rows: list[dict[str, str]] = []
    if df.empty or "is_fraud" not in df:
        return pd.DataFrame(columns=INSIGHT_COLUMNS)

    overall_rate = float(df["is_fraud"].mean() * 100)
    for column, label in (("category", "category"), ("state", "state")):
        if column not in df:
            continue
        grouped = fraud_rate(df, column)
        eligible = grouped[grouped["total_count"] >= min_sample]
        if not eligible.empty:
            highest = eligible.sort_values(
                ["fraud_rate_pct", "total_count"], ascending=[False, False]
            ).iloc[0]
            rows.append({
                "Observed Finding": (
                    f"{highest[column]} has the highest observed fraud rate "
                    f"({highest['fraud_rate_pct']:.2f}%; {int(highest['fraud_count']):,} of "
                    f"{int(highest['total_count']):,} transactions)."
                ),
                "Analytical Interpretation": (
                    f"This is {highest['fraud_rate_pct'] - overall_rate:+.2f} percentage points "
                    "relative to the filtered portfolio; the association is descriptive, not causal."
                ),
                "Suggested Action": (
                    "Review this segment with sample size and operational context before changing controls."
                ),
            })

    hourly = hourly_summary(df)
    eligible_hours = hourly[hourly["total"] >= min_sample]
    if not eligible_hours.empty:
        peak = eligible_hours.sort_values(
            ["fraud_rate_pct", "total"], ascending=[False, False]
        ).iloc[0]
        rows.append({
            "Observed Finding": (
                f"Hour {int(peak['transaction_hour']):02d}:00 has the highest observed hourly fraud "
                f"rate ({peak['fraud_rate_pct']:.2f}%; n={int(peak['total']):,})."
            ),
            "Analytical Interpretation": (
                "The rate accounts for hourly transaction volume and may vary with the selected filters."
            ),
            "Suggested Action": (
                "Review staffing and monitoring coverage for this window; validate the pattern over time."
            ),
        })

    if "amt" in df:
        fraud_amount = pd.to_numeric(df.loc[df["is_fraud"] == 1, "amt"], errors="coerce").dropna()
        legitimate_amount = pd.to_numeric(df.loc[df["is_fraud"] == 0, "amt"], errors="coerce").dropna()
        if not fraud_amount.empty and not legitimate_amount.empty:
            fraud_median = float(fraud_amount.median())
            legitimate_median = float(legitimate_amount.median())
            rows.append({
                "Observed Finding": (
                    f"Median transaction amount is ${fraud_median:,.2f} for fraudulent records and "
                    f"${legitimate_median:,.2f} for legitimate records."
                ),
                "Analytical Interpretation": (
                    "This is a retrospective difference in the selected data, not a standalone detection rule."
                ),
                "Suggested Action": (
                    "Review amount thresholds alongside transaction context and avoid treating exposure as confirmed loss."
                ),
            })
    return pd.DataFrame(rows, columns=INSIGHT_COLUMNS)
