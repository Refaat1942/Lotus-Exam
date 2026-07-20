import os
import base64
import streamlit as st

# ======================================================
# BRAND CONSTANTS
# ======================================================
BRAND_NAME = "Lotus Evaluation Platform"
BRAND_TAGLINE = "Talent Assessment & Recruitment System"

PRIMARY = "#1f7a4d"      # Lotus green
PRIMARY_DARK = "#145c39"
PRIMARY_LIGHT = "#e6f4ec"
ACCENT = "#d4af37"       # subtle gold accent
BG = "#f6f8f7"
TEXT = "#1f2a24"

# Logo lookup: put your file in the project folder (or /assets) with one of these names.
LOGO_CANDIDATES = [
    "assets/logo.png",
    "assets/logo.jpg",
    "assets/logo.jpeg",
    "assets/logo.svg",
    "logo.png",
    "logo.jpg",
    "logo.jpeg",
    "logo.svg",
]


# ======================================================
# HELPERS
# ======================================================
def _find_logo():
    base = os.path.dirname(os.path.abspath(__file__))
    for rel in LOGO_CANDIDATES:
        path = os.path.join(base, rel)
        if os.path.exists(path):
            return path
    return None


def _logo_data_uri():
    path = _find_logo()
    if not path:
        return None
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = "image/svg+xml" if ext == "svg" else f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:{mime};base64,{data}"
    except Exception:
        return None


# ======================================================
# GLOBAL STYLES
# ======================================================
def inject_global_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

        :root {{
            --primary: {PRIMARY};
            --primary-dark: {PRIMARY_DARK};
            --primary-light: {PRIMARY_LIGHT};
            --accent: {ACCENT};
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', 'Segoe UI', sans-serif;
            color: {TEXT};
        }}

        .stApp {{
            background:
                radial-gradient(1200px 600px at 10% -10%, {PRIMARY_LIGHT} 0%, rgba(230,244,236,0) 55%),
                radial-gradient(1000px 500px at 110% 0%, #eef6ff 0%, rgba(238,246,255,0) 50%),
                {BG};
        }}

        /* Hide default streamlit chrome for a cleaner look */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header[data-testid="stHeader"] {{background: transparent;}}

        .block-container {{
            max-width: 900px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Poppins', sans-serif;
            color: {PRIMARY_DARK};
            letter-spacing: -0.01em;
        }}

        /* ---------- Brand header ---------- */
        .brand-header {{
            display: flex;
            align-items: center;
            gap: 18px;
            padding: 20px 26px;
            margin-bottom: 22px;
            background: rgba(255,255,255,0.75);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(31,122,77,0.12);
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(20,92,57,0.08);
        }}
        .brand-header img {{
            height: 58px;
            width: auto;
            border-radius: 10px;
        }}
        .brand-logo-fallback {{
            height: 58px; width: 58px;
            display: flex; align-items: center; justify-content: center;
            border-radius: 14px;
            background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_DARK} 100%);
            color: #fff; font-size: 30px; font-family: 'Poppins';
            box-shadow: 0 6px 16px rgba(20,92,57,0.35);
        }}
        .brand-text .name {{
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 1.35rem;
            color: {PRIMARY_DARK};
            line-height: 1.1;
        }}
        .brand-text .tag {{
            font-size: 0.86rem;
            color: #5b6b63;
            font-weight: 500;
        }}

        /* ---------- Card ---------- */
        .lx-card {{
            background: #ffffff;
            border: 1px solid rgba(31,122,77,0.10);
            border-radius: 18px;
            padding: 26px 28px;
            box-shadow: 0 12px 34px rgba(20,92,57,0.07);
            margin-bottom: 18px;
        }}
        .lx-card h3 {{ margin-top: 0; }}

        /* ---------- Buttons ---------- */
        .stButton > button, .stLinkButton > a, .stDownloadButton > button {{
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-family: 'Poppins', sans-serif !important;
            padding: 0.55rem 1.2rem !important;
            border: none !important;
            transition: transform .08s ease, box-shadow .2s ease !important;
        }}
        .stButton > button[kind="primary"], .stFormSubmitButton > button {{
            background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_DARK} 100%) !important;
            color: #fff !important;
            box-shadow: 0 8px 20px rgba(20,92,57,0.28) !important;
        }}
        .stButton > button:hover, .stLinkButton > a:hover, .stFormSubmitButton > button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 12px 26px rgba(20,92,57,0.32) !important;
        }}

        /* ---------- Inputs ---------- */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {{
            border-radius: 12px !important;
        }}
        .stTextInput input:focus, .stNumberInput input:focus {{
            border-color: {PRIMARY} !important;
            box-shadow: 0 0 0 2px {PRIMARY_LIGHT} !important;
        }}

        /* ---------- Metrics ---------- */
        [data-testid="stMetric"] {{
            background: #fff;
            border: 1px solid rgba(31,122,77,0.10);
            border-radius: 16px;
            padding: 16px 18px;
            box-shadow: 0 8px 22px rgba(20,92,57,0.06);
        }}
        [data-testid="stMetricValue"] {{
            color: {PRIMARY_DARK};
            font-family: 'Poppins', sans-serif;
        }}

        /* ---------- Radio (exam options) ---------- */
        div[role="radiogroup"] label {{
            background: #fff;
            border: 1.5px solid rgba(31,122,77,0.15);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 10px !important;
            transition: all .15s ease;
            cursor: pointer;
        }}
        div[role="radiogroup"] label:hover {{
            border-color: {PRIMARY};
            background: {PRIMARY_LIGHT};
        }}

        /* ---------- Timer chip ---------- */
        .lx-timer {{
            display: inline-block;
            padding: 8px 18px;
            border-radius: 999px;
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 0.95rem;
        }}
        .lx-timer.ok {{ background: {PRIMARY_LIGHT}; color: {PRIMARY_DARK}; }}
        .lx-timer.warn {{ background: #fff3cd; color: #8a6d00; }}
        .lx-timer.danger {{ background: #fdecec; color: #b3261e; }}

        /* progress bar accent */
        .stProgress > div > div > div > div {{
            background: linear-gradient(90deg, {PRIMARY} 0%, {ACCENT} 100%);
        }}

        .lx-footer {{
            text-align: center;
            color: #8a978f;
            font-size: 0.8rem;
            margin-top: 28px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ======================================================
# BRAND HEADER
# ======================================================
def render_header(subtitle: str = None):
    logo = _logo_data_uri()
    if logo:
        logo_html = f'<img src="{logo}" alt="logo" />'
    else:
        logo_html = '<div class="brand-logo-fallback">&#10047;</div>'

    tag = subtitle or BRAND_TAGLINE
    st.markdown(
        f"""
        <div class="brand-header">
            {logo_html}
            <div class="brand-text">
                <div class="name">{BRAND_NAME}</div>
                <div class="tag">{tag}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        f'<div class="lx-footer">© {BRAND_NAME} · Powered by Lotus Pharmacies</div>',
        unsafe_allow_html=True,
    )


def page_setup(subtitle: str = None, show_header: bool = True):
    inject_global_css()
    if show_header:
        render_header(subtitle)
