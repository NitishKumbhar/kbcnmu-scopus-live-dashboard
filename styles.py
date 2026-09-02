import base64
import os
import streamlit as st
from config import UNIVERSITY_CONFIG


def get_image_b64(file_path: str) -> str:
    """Read local image file and return Base64 string."""
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""


def get_custom_css(theme: str = "dark") -> str:
    """
    Generate ICARE Glassmorphism CSS tailored for dark or light mode.
    """
    is_dark = theme.lower() == "dark"

    bg_color = "#070D1E" if is_dark else "#F8FAFC"
    card_bg = "rgba(14, 23, 42, 0.85)" if is_dark else "rgba(255, 255, 255, 0.9)"
    card_border = "1px solid rgba(255, 255, 255, 0.1)" if is_dark else "1px solid rgba(15, 23, 42, 0.08)"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    subtext_color = "#94A3B8" if is_dark else "#64748B"
    primary_color = UNIVERSITY_CONFIG.get("primary_color", "#0284C7")
    accent_color = UNIVERSITY_CONFIG.get("accent_color", "#F59E0B")
    sidebar_bg = "#0A1224" if is_dark else "#FFFFFF"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap');

    /* Base Page Settings */
    .stApp {{
        background-color: {bg_color} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: {text_color} !important;
    }}

    /* Global Typography */
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Outfit', sans-serif !important;
        color: {text_color} !important;
    }}

    /* Top Bar Styling */
    .icare-topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1.25rem;
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: {card_border};
        border-radius: 14px;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }}

    .icare-topbar-left {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}

    .icare-logo-box {{
        background: #FFFFFF;
        padding: 4px 10px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 32px;
    }}

    .icare-logo-img {{
        height: 24px;
        object-fit: contain;
    }}

    .icare-badge-pill {{
        background: #0284C7;
        color: #FFFFFF;
        font-weight: 800;
        padding: 0.35rem 0.75rem;
        border-radius: 8px;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }}

    .icare-title-tag {{
        font-weight: 700;
        color: {subtext_color};
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}

    .icare-topbar-right {{
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }}

    .univ-details-text {{
        text-align: right;
    }}

    .univ-title-bold {{
        font-weight: 800;
        font-size: 0.95rem;
        color: {text_color};
    }}

    .univ-sub-cyan {{
        font-weight: 700;
        font-size: 0.8rem;
        color: #38BDF8;
    }}

    .univ-logo-box {{
        background: #FFFFFF;
        padding: 3px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 38px;
        height: 38px;
    }}

    .univ-logo-img {{
        width: 34px;
        height: 34px;
        object-fit: cover;
        border-radius: 6px;
    }}

    /* Hero Banner Styling */
    .icare-hero {{
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.15) 0%, rgba(14, 23, 42, 0.9) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: {card_border};
        border-radius: 18px;
        padding: 1.8rem 2.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }}

    .icare-hero-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-bottom: 0.85rem;
    }}

    .hero-pill {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: {text_color};
        padding: 0.3rem 0.8rem;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
    }}

    .hero-pill-gold {{
        background: rgba(245, 158, 11, 0.18);
        border: 1px solid rgba(245, 158, 11, 0.4);
        color: #F59E0B;
    }}

    .icare-hero-title {{
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0.3rem 0 0.4rem 0;
        line-height: 1.2;
        color: #FFFFFF;
    }}

    .icare-hero-subtitle {{
        color: {subtext_color};
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 1.25rem;
    }}

    .hero-stat-block {{
        margin-top: 0.5rem;
    }}

    .hero-stat-label {{
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #94A3B8;
        letter-spacing: 0.06em;
    }}

    .hero-stat-val {{
        font-family: 'Outfit', sans-serif;
        font-size: 2.8rem;
        font-weight: 800;
        color: #38BDF8;
        line-height: 1;
        margin: 0.2rem 0;
    }}

    .hero-stat-sub {{
        font-size: 0.88rem;
        color: #CBD5E1;
        font-weight: 600;
    }}

    /* Report Overview Bar */
    .report-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: {card_bg};
        border: {card_border};
        border-radius: 12px;
        padding: 0.75rem 1.25rem;
        margin-bottom: 1.5rem;
    }}

    .report-title {{
        font-size: 0.92rem;
        font-weight: 700;
        color: {text_color};
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    /* Metric Cards Styling */
    .metric-card {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: {card_border};
        border-radius: 16px;
        padding: 1.2rem 1.3rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        height: 100%;
    }}

    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(2, 132, 199, 0.2);
    }}

    .metric-title {{
        font-size: 0.75rem;
        font-weight: 700;
        color: {subtext_color};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .metric-value {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.9rem;
        font-weight: 800;
        color: {text_color};
        margin-bottom: 0.2rem;
    }}

    /* Streamlit Components Overrides */
    div[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: {card_border};
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.45rem 1rem !important;
        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
    }}

    /* Hide Default Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """
    return css


def render_icare_topbar(theme: str = "dark"):
    """
    Render Top Navigation Bar with both ICARE Logo and KBCNMU Logo.
    """
    css = get_custom_css(theme)
    st.markdown(css, unsafe_allow_html=True)

    icare_b64 = get_image_b64("LOGO/download.png")
    kbcnmu_b64 = get_image_b64("LOGO/WhatsApp Image 2026-07-06 at 4.05.20 PM.jpeg")

    full_name = UNIVERSITY_CONFIG.get("full_name", "Kavayitri Bahinabai Chaudhari North Maharashtra University")
    nirf_id = UNIVERSITY_CONFIG.get("nirf_id", "IR-O-U-0320")
    city = UNIVERSITY_CONFIG.get("city", "Jalgaon, Maharashtra")
    app_title = UNIVERSITY_CONFIG.get("app_title", "KBCNMU Live Scopus Intelligence Dashboard")

    topbar_html = f"""
    <div class="icare-topbar">
        <div class="icare-topbar-left">
            <div class="icare-logo-box">
                <img src="data:image/png;base64,{icare_b64}" class="icare-logo-img" alt="ICARE Logo">
            </div>
            <div class="icare-badge-pill">PORTAL INTELLIGENCE</div>
            <div class="icare-title-tag">
                <span>☑️</span> {app_title}
            </div>
        </div>
        <div class="icare-topbar-right">
            <div class="univ-details-text">
                <div class="univ-title-bold">{full_name}</div>
                <div class="univ-sub-cyan">{nirf_id} • {city}</div>
            </div>
            <div class="univ-logo-box">
                <img src="data:image/jpeg;base64,{kbcnmu_b64}" class="univ-logo-img" alt="KBCNMU Logo">
            </div>
        </div>
    </div>
    """
    st.markdown(topbar_html, unsafe_allow_html=True)


def render_icare_hero(total_pubs: int, total_cites: int, theme: str = "dark"):
    """
    Render Hero Banner matching exact format of COEP reference dashboard.
    """
    status_tag = UNIVERSITY_CONFIG.get("status_tag", "🏛️ State Public University (Estd. 1990)")
    naac_badge = UNIVERSITY_CONFIG.get("naac_badge", "⭐ NAAC A (CGPA 3.09)")

    hero_html = f"""
    <div class="icare-hero">
        <div class="icare-hero-badges">
            <span class="hero-pill hero-pill-gold">🏆 Scopus Research Dossier</span>
            <span class="hero-pill">{status_tag}</span>
            <span class="hero-pill hero-pill-gold">{naac_badge}</span>
            <span class="hero-pill">📜 NIRF Category: University</span>
        </div>
        <div class="icare-hero-title">{UNIVERSITY_CONFIG['app_title']}</div>
        <div class="icare-hero-subtitle">
            Kavayitri Bahinabai Chaudhari North Maharashtra University, Jalgaon • Elsevier Scopus Bibliometrics & Global Research Impact
        </div>
        <div class="hero-stat-block">
            <div class="hero-stat-label">TOTAL SCOPUS OUTPUT</div>
            <div class="hero-stat-val">#{total_pubs:,}</div>
            <div class="hero-stat-sub">{total_cites:,} Citations Accrued</div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)



if __name__ == "__main__":
    print("styles.py initialized successfully.")
