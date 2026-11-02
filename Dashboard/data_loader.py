"""Load and enrich the original FraudLens transaction dataset."""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


def _find_dataset() -> Path:
    """Find the cleaned CSV in the repository's Week 3 folder or Dashboard/data."""
    dashboard_dir = Path(__file__).resolve().parent
    candidates = (
        dashboard_dir.parent / "Week 3" / "fraudTrain_cleaned.csv",
        dashboard_dir / "data" / "fraudTrain_cleaned.csv",
    )
    for path in candidates:
        if path.is_file():
            return path
    searched = "\n".join(f"- {path}" for path in candidates)
    raise FileNotFoundError(
        "Cannot locate fraudTrain_cleaned.csv. Searched:\n" + searched
    )


@st.cache_data(show_spinner="Loading FraudLens transaction data...")
def load_data() -> pd.DataFrame:
    """Load the original CSV and add derived fields without changing the source."""
    path = _find_dataset()
    df = pd.read_csv(path, low_memory=False)

    required = {"amt", "is_fraud"}
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")

    df["amt"] = pd.to_numeric(df["amt"], errors="coerce")
    fraud = pd.to_numeric(df["is_fraud"], errors="coerce")
    if fraud.isna().any() or not fraud.isin([0, 1]).all():
        raise ValueError("The is_fraud column must contain only non-null 0/1 values.")
    df["is_fraud"] = fraud.astype("int8")

    if "trans_date_trans_time" in df.columns:
        df["trans_datetime"] = pd.to_datetime(
            df["trans_date_trans_time"], errors="coerce"
        )
    elif "unix_time" in df.columns:
        unix_time = pd.to_numeric(df["unix_time"], errors="coerce")
        df["trans_datetime"] = pd.to_datetime(
            unix_time, unit="s", errors="coerce", utc=True
        ).dt.tz_localize(None)
    else:
        df["trans_datetime"] = pd.NaT

    derived_time_fields = {
        "transaction_hour": "hour",
        "transaction_weekday": "dayofweek",
        "transaction_month": "month",
        "transaction_day": "day",
    }
    for column, attribute in derived_time_fields.items():
        if column not in df.columns:
            df[column] = getattr(df["trans_datetime"].dt, attribute)
        else:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    df["transaction_year"] = df["trans_datetime"].dt.year

    coordinates = ("lat", "long", "merch_lat", "merch_long")
    if "distance_km" not in df.columns and all(
        column in df.columns for column in coordinates
    ):
        df["distance_km"] = _haversine_vectorised(
            df["lat"], df["long"], df["merch_lat"], df["merch_long"]
        )

    weekday_names = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    month_names = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
    }
    df["weekday_label"] = df["transaction_weekday"].map(weekday_names)
    df["month_label"] = df["transaction_month"].map(month_names)
    df["fraud_label"] = df["is_fraud"].map({0: "Legitimate", 1: "Fraudulent"})

    if {"first", "last"}.issubset(df.columns):
        df["customer_name"] = (
            df["first"].fillna("").astype(str).str.strip()
            + " "
            + df["last"].fillna("").astype(str).str.strip()
        ).str.strip()
    return df


def _haversine_vectorised(
    lat1: pd.Series,
    lon1: pd.Series,
    lat2: pd.Series,
    lon2: pd.Series,
) -> pd.Series:
    """Calculate customer-to-merchant great-circle distance in kilometres."""
    earth_radius_km = 6371.0
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = (
        np.radians(values.astype(float))
        for values in (lat1, lon1, lat2, lon2)
    )
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    haversine = (
        np.sin(delta_lat / 2) ** 2
        + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon / 2) ** 2
    )
    return pd.Series(
        2 * earth_radius_km * np.arcsin(np.sqrt(haversine)),
        index=lat1.index,
    )


@st.cache_data(show_spinner=False)
def get_summary_stats(_df: pd.DataFrame) -> dict[str, int | float]:
    """Return descriptive transaction and fraud-associated amount metrics."""
    total = len(_df)
    fraud_count = int(_df["is_fraud"].sum()) if total else 0
    legitimate_count = total - fraud_count
    fraud_amounts = _df.loc[_df["is_fraud"] == 1, "amt"].dropna()
    legitimate_amounts = _df.loc[_df["is_fraud"] == 0, "amt"].dropna()
    amounts = _df["amt"].dropna()
    return {
        "total_transactions": total,
        "fraud_transactions": fraud_count,
        "legit_transactions": legitimate_count,
        "fraud_pct": fraud_count / total * 100 if total else 0.0,
        "fraud_associated_amt": float(fraud_amounts.sum()),
        "total_amt": float(amounts.sum()),
        "avg_fraud_amt": float(fraud_amounts.mean()) if not fraud_amounts.empty else 0.0,
        "avg_legit_amt": (
            float(legitimate_amounts.mean()) if not legitimate_amounts.empty else 0.0
        ),
        "median_fraud_amt": (
            float(fraud_amounts.median()) if not fraud_amounts.empty else 0.0
        ),
        "median_legit_amt": (
            float(legitimate_amounts.median()) if not legitimate_amounts.empty else 0.0
        ),
    }
