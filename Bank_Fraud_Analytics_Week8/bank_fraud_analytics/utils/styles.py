import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
    :root {
      --bg:#080D19; --panel:#111A2B; --panel2:#17243A;
      --line:#263751; --text:#F2F6FF; --muted:#A7B4C8;
      --blue:#4C8DFF; --cyan:#20C7D9; --purple:#A78BFA;
      --pink:#F472B6; --orange:#F59E0B; --red:#FB7185;
    }
    .stApp { background:var(--bg); color:var(--text); }
    [data-testid="stHeader"] { background:rgba(8,13,25,.96); }
    [data-testid="stSidebar"] { background:#0D1728; border-right:1px solid var(--line); }
    [data-testid="stSidebar"] * { color:var(--text) !important; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:var(--muted) !important; }
    .block-container { padding-top:1.35rem; padding-bottom:2.4rem; max-width:1600px; }
    .brand-banner {
      background:linear-gradient(105deg,#111D35 0%,#173B67 55%,#31245B 100%);
      border:1px solid #304A70; border-radius:16px; padding:22px 26px;
      margin-bottom:22px; box-shadow:0 8px 28px rgba(0,0,0,.25);
    }
    .brand-title { color:#FFFFFF; font-size:27px; font-weight:850; letter-spacing:.6px; }
    .brand-subtitle { color:#C3D5F2; font-size:13px; margin-top:5px; }
    .main-title { color:#F5F7FF; font-size:27px; font-weight:800; margin-bottom:3px; }
    .subtitle { color:#A7B4C8; font-size:14px; margin-bottom:18px; }
    h1,h2,h3,p,label { color:var(--text); }
    h2 { font-size:21px !important; }
    h3 { font-size:17px !important; }
    [data-testid="stMetric"] {
      background:linear-gradient(145deg,#17243A,#101A2B);
      border:1px solid #2A3E5B; border-radius:13px; padding:15px;
      box-shadow:0 5px 18px rgba(0,0,0,.20);
    }
    [data-testid="stMetricLabel"] { color:#AFC0D8 !important; }
    [data-testid="stMetricValue"] { color:#FFFFFF !important; }
    .kpi-card {
      background:linear-gradient(145deg,#17243A,#101A2B); padding:17px 18px;
      border-radius:13px; border:1px solid #2A3E5B; min-height:105px;
      box-shadow:0 5px 18px rgba(0,0,0,.20);
    }
    .kpi-label { color:#AFC0D8; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.6px; }
    .kpi-value { color:#FFFFFF; font-size:25px; font-weight:850; margin-top:10px; }
    div[data-testid="stPlotlyChart"] {
      background:#111A2B; border:1px solid #263751; border-radius:13px; padding:6px;
    }
    div[data-testid="stDataFrame"] { border:1px solid #263751; border-radius:11px; overflow:hidden; }
    .stButton button, .stDownloadButton button {
      background:#3478F6; color:white; border:0; border-radius:8px; font-weight:700;
    }
    .stButton button:hover, .stDownloadButton button:hover { background:#205DCE; color:white; }
    [data-testid="stAlert"] { border-radius:10px; }
    hr { border-color:#263751; }
    </style>
    """, unsafe_allow_html=True)

def app_banner():
    st.markdown("""
    <div class="brand-banner">
      <div class="brand-title">CREDIT CARD FRAUD ANALYTICS</div>
      <div class="brand-subtitle">BANKING INTELLIGENCE · HISTORICAL TRANSACTION ANALYSIS</div>
    </div>
    """, unsafe_allow_html=True)

def page_heading(title: str, subtitle: str = ""):
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)

def kpi_card(label: str, value: str):
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div></div>',
        unsafe_allow_html=True,
    )
