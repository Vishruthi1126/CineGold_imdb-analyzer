"""Shared CineGold theme styles for dashboard and auth screens."""

import streamlit as st


def apply_theme(mode: str) -> None:
    """Inject premium gold styling; light mode uses crisp black copy."""
    if mode == "Dark":
        bg = "#0d0d0d"
        fg = "#F5E6C8"
        muted = "#C9A227"
        card = "linear-gradient(145deg, #1a1814 0%, #252118 100%)"
        card_border = "1px solid rgba(201, 162, 39, 0.45)"
        sidebar_bg = "#141210"
        accent = "#D4AF37"
    else:
        bg = "#FDF8F0"
        fg = "#000000"
        muted = "#3d3d3d"
        card = "linear-gradient(145deg, #FFFCF5 0%, #F5ECD8 100%)"
        card_border = "1px solid rgba(139, 105, 20, 0.35)"
        sidebar_bg = "#F8F0E3"
        accent = "#8B6914"

    st.markdown(
        _font_import()
        + f"""
        <style>
            html, body, [class*="css"] {{
                font-family: 'Outfit', sans-serif !important;
                color: {fg} !important;
            }}
            .stApp {{
                background: {bg};
                background-image: radial-gradient(ellipse at 20% 0%, rgba(201,162,39,0.08) 0%, transparent 50%),
                                  radial-gradient(ellipse at 80% 100%, rgba(212,175,55,0.06) 0%, transparent 45%);
            }}
            h1, h2, h3, h4, h5, h6,
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
            .stMarkdown h4, .stMarkdown h5 {{
                font-family: 'Cormorant Garamond', serif !important;
                font-weight: 700 !important;
                color: {fg} !important;
                letter-spacing: 0.02em;
            }}
            h1 {{
                background: linear-gradient(135deg, #B8860B 0%, #D4AF37 40%, #C9A227 70%, #8B6914 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.75rem !important;
            }}
            p, label, .stMarkdown, .stCaption, span, li,
            [data-testid="stMarkdownContainer"] p {{
                color: {fg} !important;
            }}
            .stMarkdown a {{
                color: {accent} !important;
                text-decoration: none;
                border-bottom: 1px solid rgba(201, 162, 39, 0.4);
            }}
            section[data-testid="stSidebar"] {{
                background: {sidebar_bg} !important;
                border-right: 1px solid rgba(201, 162, 39, 0.25);
            }}
            section[data-testid="stSidebar"] * {{ color: {fg} !important; }}
            section[data-testid="stSidebar"] h1 {{
                -webkit-text-fill-color: {fg};
                background: none;
                font-size: 1.85rem !important;
            }}
            .metric-card {{
                background: {card};
                border: {card_border};
                padding: 1.15rem 1.35rem;
                border-radius: 14px;
                box-shadow: 0 4px 20px rgba(139, 105, 20, 0.12);
                color: {fg};
            }}
            .metric-card h3 {{
                margin: 0;
                font-family: 'Cormorant Garamond', serif !important;
                font-size: 2rem;
                font-weight: 700;
                color: {fg} !important;
                -webkit-text-fill-color: {fg};
                background: none;
            }}
            .metric-card p {{
                margin: 0.25rem 0 0 0;
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                color: {muted} !important;
            }}
            .gold-divider {{
                height: 2px;
                background: linear-gradient(90deg, transparent, #C9A227, #D4AF37, #C9A227, transparent);
                margin: 1.5rem 0;
                border: none;
            }}
            .hero-tagline {{
                font-family: 'Cormorant Garamond', serif;
                font-size: 1.25rem;
                font-style: italic;
                color: {muted} !important;
                margin-top: -0.5rem;
            }}
            [data-baseweb="tab"][aria-selected="true"] {{
                border-bottom: 2px solid #C9A227 !important;
                color: {accent} !important;
            }}
            .stButton > button {{
                background: linear-gradient(135deg, #8B6914, #C9A227, #D4AF37) !important;
                color: #000 !important;
                font-weight: 600;
                border: none !important;
                border-radius: 8px;
            }}
            .stDownloadButton > button {{
                background: linear-gradient(135deg, #8B6914, #C9A227) !important;
                color: #000 !important;
                font-weight: 600;
            }}
            .stDataFrame, [data-testid="stDataFrame"] {{
                border: 1px solid rgba(201, 162, 39, 0.2);
                border-radius: 10px;
            }}

            /* ── Selectbox / Dropdown: white font ── */
            [data-baseweb="select"] > div,
            [data-baseweb="select"] span,
            [data-baseweb="select"] div[class*="ValueContainer"] *,
            [data-baseweb="select"] div[class*="singleValue"],
            [data-baseweb="select"] input,
            [data-baseweb="select"] div[aria-selected] {{
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
            }}
            /* Dropdown popup list items */
            [data-baseweb="popover"] li,
            [data-baseweb="popover"] [role="option"],
            [data-baseweb="menu"] li,
            [data-baseweb="menu"] [role="option"],
            [data-baseweb="menu"] span {{
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
            }}
            /* Selectbox placeholder */
            [data-baseweb="select"] [class*="placeholder"] {{
                color: rgba(255,255,255,0.5) !important;
                -webkit-text-fill-color: rgba(255,255,255,0.5) !important;
            }}

            /* ── Text input (Search movie): white font ── */
            [data-testid="stTextInput"] input,
            [data-testid="stTextInput"] input::placeholder {{
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
            }}
            [data-testid="stTextInput"] input::placeholder {{
                color: rgba(255,255,255,0.45) !important;
                -webkit-text-fill-color: rgba(255,255,255,0.45) !important;
            }}

            /* ── Number input: white font ── */
            [data-testid="stNumberInput"] input {{
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_auth_styles() -> None:
    """Full-screen cinematic login / sign-up experience."""
    st.markdown(
        _font_import()
        + """
        <style>
            [data-testid="stSidebar"], [data-testid="collapsedControl"] {
                display: none !important;
            }
            header[data-testid="stHeader"] {
                background: transparent !important;
            }
            .stApp {
                background: #080808 !important;
                background-image:
                    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(201,162,39,0.18) 0%, transparent 55%),
                    radial-gradient(ellipse 60% 40% at 100% 100%, rgba(139,105,20,0.12) 0%, transparent 50%),
                    radial-gradient(ellipse 50% 30% at 0% 80%, rgba(212,175,55,0.08) 0%, transparent 45%),
                    linear-gradient(180deg, #0a0a0a 0%, #12100c 50%, #0d0d0d 100%) !important;
            }
            .block-container {
                padding-top: 2rem !important;
                max-width: 1100px !important;
            }
            [data-testid="column"]:nth-child(2) > div > div {
                background: linear-gradient(160deg, rgba(22,20,17,0.98) 0%, rgba(14,13,11,0.99) 100%) !important;
                border-radius: 20px !important;
                padding: 2rem 1.75rem 1.5rem !important;
                border: 1px solid rgba(201,162,39,0.3) !important;
                box-shadow: 0 25px 60px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.05) !important;
            }
            .auth-brand-panel {
                animation: fade-up 0.9s ease-out;
                padding: 2.5rem 2rem 2rem 0;
            }
            @keyframes fade-up {
                from { opacity: 0; transform: translateY(18px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .auth-brand-panel h1 {
                font-family: 'Cormorant Garamond', serif !important;
                font-size: 3.6rem !important;
                font-weight: 700 !important;
                letter-spacing: 0.06em;
                margin: 0 0 0.5rem 0 !important;
                background: linear-gradient(120deg, #F5E6C8 0%, #D4AF37 35%, #C9A227 55%, #8B6914 100%) !important;
                -webkit-background-clip: text !important;
                -webkit-text-fill-color: transparent !important;
                background-clip: text !important;
                line-height: 1.1 !important;
            }
            .auth-brand-panel .tagline {
                font-family: 'Cormorant Garamond', serif;
                font-size: 1.45rem;
                font-style: italic;
                color: rgba(245, 230, 200, 0.75) !important;
                margin: 0 0 2rem 0;
                letter-spacing: 0.03em;
            }
            .auth-brand-panel .features {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            .auth-brand-panel .features li {
                font-family: 'Outfit', sans-serif;
                font-size: 0.92rem;
                color: rgba(245, 230, 200, 0.55) !important;
                padding: 0.55rem 0 0.55rem 1.6rem;
                position: relative;
                letter-spacing: 0.04em;
            }
            .auth-brand-panel .features li::before {
                content: "◆";
                position: absolute;
                left: 0;
                color: #C9A227;
                font-size: 0.55rem;
                top: 0.75rem;
            }
            div[data-testid="stForm"] {
                border: none !important;
                padding: 0 !important;
            }
            div[data-testid="stForm"] label {
                color: rgba(245,230,200,0.7) !important;
                font-size: 0.78rem !important;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                font-weight: 500 !important;
            }
            div[data-testid="stForm"] input {
                background: rgba(255,255,255,0.04) !important;
                border: 1px solid rgba(201,162,39,0.25) !important;
                border-radius: 10px !important;
                color: #F5E6C8 !important;
                padding: 0.65rem 0.9rem !important;
            }
            div[data-testid="stForm"] input:focus {
                border-color: #D4AF37 !important;
                box-shadow: 0 0 0 2px rgba(212,175,55,0.15) !important;
            }
            div[data-testid="stFormSubmitButton"] > button {
                width: 100%;
                padding: 0.75rem 1.5rem !important;
                background: linear-gradient(135deg, #6b5210 0%, #C9A227 45%, #E8D5A3 100%) !important;
                color: #1a1408 !important;
                font-weight: 700 !important;
                border: none !important;
                border-radius: 10px !important;
            }
            [data-testid="column"]:nth-child(2) h2 {
                font-family: 'Cormorant Garamond', serif !important;
                font-size: 2rem !important;
                font-weight: 600 !important;
                color: #F5E6C8 !important;
                -webkit-text-fill-color: #F5E6C8 !important;
                background: none !important;
                text-align: center;
            }
            p.sub {
                text-align: center;
                font-size: 0.82rem;
                color: rgba(245,230,200,0.45) !important;
                margin-bottom: 1.5rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }
            .auth-footer {
                text-align: center;
                margin-top: 1.25rem;
                font-size: 0.75rem;
                color: rgba(245,230,200,0.3) !important;
                letter-spacing: 0.06em;
            }
            div[data-testid="stAlert"] {
                border-radius: 10px;
            }
        </style>
        <div class="auth-particle" style="top:15%;left:10%;animation-delay:0s"></div>
        <div class="auth-particle" style="top:70%;left:85%;animation-delay:2s"></div>
        <div class="auth-particle" style="top:40%;left:92%;animation-delay:4s"></div>
        <div class="auth-particle" style="top:85%;left:25%;animation-delay:1s"></div>
        """,
        unsafe_allow_html=True,
    )


def _font_import() -> str:
    return """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    """
