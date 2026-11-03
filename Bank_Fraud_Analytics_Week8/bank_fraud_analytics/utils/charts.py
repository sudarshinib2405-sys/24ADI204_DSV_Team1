import pandas as pd
import plotly.express as px

NAVY = "#EAF1FF"
BLUE = "#4C8DFF"
TEAL = "#20C7D9"
RED = "#FB7185"
PURPLE = "#A78BFA"
ORANGE = "#F59E0B"
PINK = "#F472B6"

def style_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#111A2B",
        paper_bgcolor="#111A2B",
        font=dict(color="#EAF1FF", family="Arial, sans-serif", size=12),
        margin=dict(l=25, r=22, t=48, b=30),
        legend_title_text="",
        title_font=dict(size=15, color="#F4F7FF"),
        hoverlabel=dict(bgcolor="#17243A", font_color="white"),
        colorway=[BLUE, TEAL, PURPLE, RED, ORANGE, PINK],
    )
    fig.update_xaxes(showgrid=False, linecolor="#34445E", zeroline=False)
    fig.update_yaxes(gridcolor="#263751", zeroline=False)
    return fig

def fraud_split_chart(normal_count, fraud_count):
    data = pd.DataFrame({
        "Transaction status": ["Legitimate", "Fraudulent"],
        "Transactions": [normal_count, fraud_count],
    })
    fig = px.pie(
        data, names="Transaction status", values="Transactions", hole=0.64,
        color="Transaction status",
        color_discrete_map={"Legitimate": BLUE, "Fraudulent": RED},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return style_chart(fig)
