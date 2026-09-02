"""
styles.py
ICARE Premium Glassmorphism Design System & Theme Engine for Streamlit.
Supports Dark Mode (#070D1E) & Light Mode (#F8FAFC), Top Navigation,
and Hero Banners for KBCNMU Scopus Dashboard.
"""

import streamlit as st
from config import UNIVERSITY_CONFIG


def get_custom_css(theme: str = "dark") -> str:
    """
    Generate ICARE Glassmorphism CSS tailored for dark or light mode.
    """
    is_dark = theme.lower() == "dark"

    bg_color = "#070D1E" if is_dark else "#F8FAFC"
    card_bg = "rgba(14, 23, 42, 0.75)" if is_dark else "rgba(255, 255, 255, 0.85)"
    card_border = "1px solid rgba(255, 255, 255, 0.08)" if is_dark else "1px solid rgba(15, 23, 42, 0.08)"
    text_color = "#F8FAFC" if is_dark else "#0F172A"
    subtext_color = "#94A3B8" if is_dark else "#64748B"
    primary_color = UNIVERSITY_CONFIG.get("primary_color", "#0284C7")
    accent_color = UNIVERSITY_CONFIG.get("accent_color", "#F59E0B")
    sidebar_bg = "#0B1329" if is_dark else "#FFFFFF"

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
        padding: 0.85rem 1.5rem;
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: {card_border};
        border-radius: 14px;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }}

    .icare-brand {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }}

    .icare-logo-text {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        background: linear-gradient(135deg, #0284C7 0%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .icare-badge {{
        background: rgba(6, 182, 212, 0.15);
        color: #06B6D4;
        border: 1px solid rgba(6, 182, 212, 0.3);
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }}

    .icare-univ-details {{
        text-align: right;
        font-size: 0.88rem;
    }}

    .icare-univ-name {{
        font-weight: 600;
        color: {text_color};
    }}

    .icare-univ-sub {{
        font-weight: 700;
        color: {primary_color};
    }}

    /* Hero Banner Styling */
    .icare-hero {{
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.12) 0%, rgba(14, 23, 42, 0.85) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: {card_border};
        border-radius: 18px;
        padding: 2rem 2.25rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }}

    .icare-hero-badges {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-bottom: 1rem;
    }}

    .hero-pill {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: {text_color};
        padding: 0.3rem 0.75rem;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 600;
    }}

    .hero-pill-gold {{
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid rgba(245, 158, 11, 0.35);
        color: {accent_color};
    }}

    .icare-hero-title {{
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.4rem 0 0.6rem 0;
        line-height: 1.2;
        background: linear-gradient(135deg, #FFFFFF 30%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .icare-hero-desc {{
        color: {subtext_color};
        font-size: 0.98rem;
        max-width: 750px;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }}

    .icare-hero-rankbox {{
        display: flex;
        gap: 1.5rem;
        background: rgba(0, 0, 0, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1rem 1.5rem;
        border-radius: 14px;
        width: fit-content;
    }}

    .rank-stat {{
        display: flex;
        flex-direction: column;
    }}

    .rank-val {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        color: #38BDF8;
    }}

    .rank-lbl {{
        font-size: 0.75rem;
        text-transform: uppercase;
        color: {subtext_color};
        letter-spacing: 0.05em;
        font-weight: 600;
    }}

    /* Metric Cards Styling */
    .metric-card {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: {card_border};
        border-radius: 16px;
        padding: 1.25rem 1.4rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        height: 100%;
    }}

    .metric-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(2, 132, 199, 0.2);
    }}

    .metric-title {{
        font-size: 0.8rem;
        font-weight: 600;
        color: {subtext_color};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
    }}

    .metric-value {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.85rem;
        font-weight: 800;
        color: {text_color};
        margin-bottom: 0.3rem;
    }}

    .metric-subtitle {{
        font-size: 0.78rem;
        color: {primary_color};
        font-weight: 600;
    }}

    /* Streamlit Components Overrides */
    div[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: {card_border};
    }}

    .stButton > button {{
        background: linear-gradient(135deg, {primary_color} 0%, #0284C7 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.25rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(2, 132, 199, 0.45) !important;
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
    Render Top Navigation Bar with ICARE Logo + PORTAL INTELLIGENCE Badge + KBCNMU details.
    """
    css = get_custom_css(theme)
    st.markdown(css, unsafe_allow_html=True)

    full_name = UNIVERSITY_CONFIG.get("full_name", "Kavayitri Bahinabai Chaudhari North Maharashtra University")
    nirf_id = UNIVERSITY_CONFIG.get("nirf_id", "IR-O-U-0320")
    city = UNIVERSITY_CONFIG.get("city", "Jalgaon, Maharashtra")

    topbar_html = f"""
    <div class="icare-topbar">
        <div class="icare-brand">
            <div class="icare-logo-text">⚡ ICARE</div>
            <div class="icare-badge">PORTAL INTELLIGENCE</div>
        </div>
        <div class="icare-univ-details">
            <div class="icare-univ-name">{full_name}</div>
            <div class="icare-univ-sub">{nirf_id} • {city}</div>
        </div>
    </div>
    """
    st.markdown(topbar_html, unsafe_allow_html=True)


def render_icare_hero(total_pubs: int, total_cites: int, theme: str = "dark"):
    """
    Render Hero Banner with badges, title, description, and rank box.
    """
    status_tag = UNIVERSITY_CONFIG.get("status_tag", "🏛️ State Public University (Estd. 1990)")
    naac_badge = UNIVERSITY_CONFIG.get("naac_badge", "⭐ NAAC A (CGPA 3.09)")

    hero_html = f"""
    <div class="icare-hero">
        <div class="icare-hero-badges">
            <span class="hero-pill">🏆 Scopus Research Dossier</span>
            <span class="hero-pill">{status_tag}</span>
            <span class="hero-pill hero-pill-gold">{naac_badge}</span>
            <span class="hero-pill">📜 NIRF Category: University</span>
        </div>
        <div class="icare-hero-title">{UNIVERSITY_CONFIG['app_title']}</div>
        <div class="icare-hero-desc">
            Real-time research analytics, citation impact tracking, institutional collaboration network, 
            and department benchmarking for Kavayitri Bahinabai Chaudhari North Maharashtra University.
        </div>
        <div class="icare-hero-rankbox">
            <div class="rank-stat">
                <span class="rank-val">{total_pubs:,}</span>
                <span class="rank-lbl">Total Scopus Output</span>
            </div>
            <div style="width: 1px; background: rgba(255,255,255,0.15);"></div>
            <div class="rank-stat">
                <span class="rank-val" style="color: #F59E0B;">{total_cites:,}</span>
                <span class="rank-lbl">Total Citations</span>
            </div>
        </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)


if __name__ == "__main__":
    print("styles.py initialized successfully.")
