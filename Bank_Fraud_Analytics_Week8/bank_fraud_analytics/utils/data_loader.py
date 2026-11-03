from pathlib import Path
import pandas as pd
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"
DEFAULT_DATASET = DATA_DIR / "fraudTrain_cleaned.csv"

# Small sample to keep first load and chart rendering responsive.
MAX_ROWS = 50_000

REQUIRED_COLUMNS = ["is_fraud", "amt"]
OPTIONAL_COLUMNS = ["trans_date_trans_time", "category", "state"]

def find_dataset():
    candidates = [
        DEFAULT_DATASET,
        DATA_DIR / "fraudTrain.csv",
        PROJECT_DIR / "fraudTrain_cleaned.csv",
        PROJECT_DIR / "fraudTrain.csv",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None

@st.cache_data(show_spinner="Reading a 50,000-row sample from the CSV...")
def load_data(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset not found: {path}")

    header = pd.read_csv(path, nrows=0)
    available = set(header.columns)
    missing = set(REQUIRED_COLUMNS) - available
    if missing:
        raise ValueError("Missing required CSV column(s): " + ", ".join(sorted(missing)))

    usecols = REQUIRED_COLUMNS + [c for c in OPTIONAL_COLUMNS if c in available]
    dtype_map = {"is_fraud": "int8", "amt": "float32"}
    if "category" in usecols:
        dtype_map["category"] = "category"
    if "state" in usecols:
        dtype_map["state"] = "category"

    return pd.read_csv(
        path, usecols=usecols, dtype=dtype_map,
        nrows=MAX_ROWS, low_memory=False
    )

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_fraud"] = pd.to_numeric(df["is_fraud"], errors="coerce")
    df["amt"] = pd.to_numeric(df["amt"], errors="coerce")
    df = df.dropna(subset=["is_fraud", "amt"])
    df = df[df["is_fraud"].isin([0, 1])].copy()
    df["is_fraud"] = df["is_fraud"].astype("int8")
    df["amt"] = df["amt"].astype("float32")

    if "trans_date_trans_time" in df.columns:
        ts = pd.to_datetime(df["trans_date_trans_time"], errors="coerce")
        df["trans_date_trans_time"] = ts
        df["hour"] = ts.dt.hour

    for col in ("category", "state"):
        if col in df.columns:
            df[col] = df[col].astype("string").fillna("Unknown")
    return df.reset_index(drop=True)
