"""Transparent, label-independent rule scoring for retrospective investigation."""

import numpy as np
import pandas as pd


def score_transactions(
    transactions: pd.DataFrame,
    reference: pd.DataFrame,
) -> pd.DataFrame:
    """Score records using amount, hour frequency and distance only.

    Amount at/above reference P95 adds 30 points (P99 adds 15 more), an
    amount at least three times the reference median adds 10, an hour in the
    lowest-volume quartile adds 20, and distance at/above reference P95 adds
    25. A score of 0-19 is Low, 20-44 Medium, 45-69 High, and 70-100 Critical.
    The fraud label is never read by this engine.
    """
    scored = transactions.copy()
    if scored.empty:
        scored["risk_score"] = pd.Series(dtype="int64")
        scored["risk_level"] = pd.Series(dtype="object")
        scored["risk_factors"] = pd.Series(dtype="object")
        return scored

    reference_amounts = pd.to_numeric(reference.get("amt", pd.Series(dtype=float)), errors="coerce").dropna()
    amount_p95 = float(reference_amounts.quantile(0.95)) if not reference_amounts.empty else float("inf")
    amount_p99 = float(reference_amounts.quantile(0.99)) if not reference_amounts.empty else float("inf")
    amount_median = float(reference_amounts.median()) if not reference_amounts.empty else float("inf")

    amount = pd.to_numeric(scored.get("amt", 0), errors="coerce")
    high_amount = amount.ge(amount_p95).fillna(False)
    very_high_amount = amount.ge(amount_p99).fillna(False)
    multiple_of_median = amount.ge(3 * amount_median).fillna(False)

    low_volume_hours: set[int] = set()
    if "transaction_hour" in reference:
        hour_counts = reference["transaction_hour"].value_counts()
        if not hour_counts.empty:
            low_volume_hours = set(
                hour_counts[hour_counts <= hour_counts.quantile(0.25)].index.dropna().astype(int)
            )
    hours = pd.to_numeric(scored.get("transaction_hour", pd.Series(index=scored.index)), errors="coerce")
    unusual_hour = hours.isin(low_volume_hours)

    distance_available = (
        "distance_km" in scored.columns and "distance_km" in reference.columns
    )
    if distance_available:
        reference_distance = pd.to_numeric(reference["distance_km"], errors="coerce").dropna()
        distance_p95 = (
            float(reference_distance.quantile(0.95))
            if not reference_distance.empty else float("inf")
        )
        unusual_distance = pd.to_numeric(
            scored["distance_km"], errors="coerce"
        ).ge(distance_p95).fillna(False)
    else:
        unusual_distance = pd.Series(False, index=scored.index)

    score = (
        high_amount.astype(int) * 30
        + very_high_amount.astype(int) * 15
        + multiple_of_median.astype(int) * 10
        + unusual_hour.astype(int) * 20
        + unusual_distance.astype(int) * 25
    ).clip(upper=100)

    factors = []
    for is_high_amount, is_very_high, is_multiple_median, is_unusual_hour, is_unusual_distance in zip(
        high_amount, very_high_amount, multiple_of_median, unusual_hour, unusual_distance
    ):
        triggered = []
        if is_high_amount:
            triggered.append("Amount at or above reference 95th percentile")
        if is_very_high:
            triggered.append("Amount at or above reference 99th percentile")
        if is_multiple_median:
            triggered.append("Amount at least three times the reference median")
        if is_unusual_hour:
            triggered.append("Transaction hour is in the lowest-volume quartile")
        if is_unusual_distance:
            triggered.append("Customer-to-merchant distance at or above reference 95th percentile")
        factors.append("; ".join(triggered) if triggered else "No configured rules triggered")

    scored["risk_score"] = score.astype("int8")
    scored["risk_level"] = pd.cut(
        scored["risk_score"],
        bins=[-1, 19, 44, 69, 100],
        labels=["Low Risk", "Medium Risk", "High Risk", "Critical Risk"],
    ).astype(str)
    scored["risk_factors"] = factors
    return scored
