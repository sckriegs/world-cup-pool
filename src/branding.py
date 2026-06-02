"""IQVIA Digital brand tokens (from IQVIA-Digital-Brand-Guidelines.html)."""

import streamlit as st

INDIGO = "#140B42"
CHARCOAL_5 = "#F4F4F4"
BRIGHT_TEAL = "#0CEFC3"
TEXT_MUTED = "#5a5a6e"
WHITE = "#FFFFFF"

BRAND_CSS = f"""
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
<style>
    html, body, [class*="css"] {{
        font-family: "Noto Sans", Arial, sans-serif !important;
    }}
    .stApp {{
        background-color: {WHITE};
    }}
    [data-testid="stSidebar"] {{
        background-color: {CHARCOAL_5};
        border-right: 1px solid #e0e0e8;
    }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {{
        color: {INDIGO};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {INDIGO} !important;
        font-weight: 700 !important;
    }}
    p, label, .stMarkdown, span {{
        color: {INDIGO};
    }}
    [data-testid="stCaptionContainer"] {{
        color: {TEXT_MUTED} !important;
    }}
    div[data-testid="stMetric"] {{
        background-color: {CHARCOAL_5};
        border-radius: 12px;
        padding: 0.75rem 1rem;
        border: 1px solid #e8e8ee;
    }}
    div[data-testid="stMetric"] label {{
        color: {TEXT_MUTED} !important;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {INDIGO} !important;
    }}
    .stButton > button[kind="primary"] {{
        background-color: {INDIGO} !important;
        color: {WHITE} !important;
        border: none !important;
        font-weight: 600 !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background-color: #1f1458 !important;
        border-left: 3px solid {BRIGHT_TEAL} !important;
    }}
    .stButton > button[kind="secondary"] {{
        color: {INDIGO} !important;
        border-color: {INDIGO} !important;
    }}
    [data-baseweb="tab-highlight"] {{
        background-color: {BRIGHT_TEAL} !important;
    }}
    a {{
        color: {INDIGO} !important;
    }}
    a:hover {{
        color: {BRIGHT_TEAL} !important;
    }}
    .iqvia-header {{
        background: {INDIGO};
        color: {WHITE};
        padding: 1.25rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }}
    .iqvia-header .eyebrow {{
        color: {BRIGHT_TEAL};
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0 0 0.35rem;
    }}
    .iqvia-header h1 {{
        color: {WHITE} !important;
        margin: 0;
        font-size: 1.75rem;
        line-height: 1.2;
    }}
    .iqvia-header p {{
        color: rgba(255, 255, 255, 0.92);
        margin: 0.5rem 0 0;
        font-weight: 300;
        font-size: 0.95rem;
    }}
</style>
"""


def apply_branding() -> None:
    st.markdown(BRAND_CSS, unsafe_allow_html=True)


def brand_header(title: str, subtitle: str = "") -> None:
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"""
        <div class="iqvia-header">
            <p class="eyebrow">IQVIA Digital</p>
            <h1>{title}</h1>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
