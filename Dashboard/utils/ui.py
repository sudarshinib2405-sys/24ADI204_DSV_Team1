"""Shared FraudLens page chrome."""

import streamlit as st


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        .stApp { background:#0b1220; }
        section[data-testid="stSidebar"] { background:#111c2f; border-right:1px solid #26354d; }
        h1,h2,h3,h4 { color:#f1f5f9 !important; letter-spacing:-.02em; }
        p,li,label,[data-testid="stCaptionContainer"] { color:#aab8ca; }
        [data-testid="stMetric"] {
            background:#17243a;border:1px solid #2c3b52;border-radius:10px;padding:14px;
        }
        [data-testid="stMetricLabel"] { color:#aab8ca !important; }
        [data-testid="stMetricValue"] { color:#60a5fa !important; }
        div[data-testid="stDataFrame"] { border:1px solid #26354d;border-radius:8px; }
        .stButton button,.stDownloadButton button {
            border:1px solid #315e9e;border-radius:7px;background:#1d4ed8;color:#fff;
        }
        hr { border-color:#26354d; }
        @media (max-width: 700px) {
            .block-container { padding:1rem 1rem 2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(title: str, subtitle: str, icon: str) -> None:
    st.title(f"{icon}  {title}")
    st.caption(subtitle)
    st.divider()
