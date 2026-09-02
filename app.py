"""
app.py
KBCNMU Live Scopus Intelligence Dashboard - Master Production Application
Features ICARE Glassmorphism design, responsive desktop/mobile layout, real-time Elsevier Scopus API gateway,
10 Core KPIs, and 7 interactive analytical tabs with isolated printing and AI Copilot.
"""

import base64
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import streamlit.components.v1 as components

from ai_copilot import query_scopus_ai_copilot
from config import UNIVERSITY_CONFIG
from data_processor import (
    calculate_top_10_kpis,
    export_to_bibtex,
    filter_publications,
    generate_author_print_html,
    get_author_profile_metrics,
    get_publications_by_month,
    get_publications_by_year,
    get_top_authors_leaderboard,
)
from scopus_api import load_scopus_data
from styles import get_custom_css, render_icare_hero, render_icare_topbar

# 1. Page Configuration
st.set_page_config(
    page_title=UNIVERSITY_CONFIG["app_title"],
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 2. Responsive Sidebar JavaScript Injection
responsive_js = """
<script>
(function() {
    const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;
    function adjustSidebar() {
        const sidebar = parentDoc.querySelector('section[data-testid="stSidebar"]');
        if (!sidebar) return;
        if (window.innerWidth > 768) {
            sidebar.setAttribute('aria-expanded', 'true');
        } else {
            sidebar.setAttribute('aria-expanded', 'false');
        }
    }
    adjustSidebar();
    window.addEventListener('resize', adjustSidebar);
})();
</script>
"""
components.html(responsive_js, height=0)


# 3. Excel Export Helper
def convert_df_to_excel(export_df: pd.DataFrame) -> bytes:
    """Convert publication DataFrame to downloadable Excel bytes buffer."""
    output = io.BytesIO()
    clean_df = export_df.copy()
    if "countries" in clean_df:
        clean_df["countries"] = clean_df["countries"].apply(
            lambda c: ", ".join(c) if isinstance(c, list) else str(c)
        )

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        clean_df.to_excel(writer, index=False, sheet_name="KBCNMU_Publications")
    return output.getvalue()


# 4. Plotly Theme Helper
def apply_plotly_theme(fig, theme: str = "dark"):
    """Format Plotly charts to match dark or light ICARE glassmorphism styling."""
    is_dark = theme.lower() == "dark"

    paper_bg = "#0E172A" if is_dark else "#FFFFFF"
    plot_bg = "rgba(0,0,0,0)"
    font_color = "#F8FAFC" if is_dark else "#0F172A"
    grid_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(15, 23, 42, 0.08)"

    fig.update_layout(
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(family="Inter, sans-serif", color=font_color, size=12),
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=font_color)),
        xaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color, tickfont=dict(color=font_color)),
        yaxis=dict(gridcolor=grid_color, zerolinecolor=grid_color, tickfont=dict(color=font_color)),
    )
    return fig


# 5. Sidebar Controls & Scopus Gateway
with st.sidebar:
    # Top Brand Box
    st.markdown(
        """
        <div style="background: #0A1428; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 1rem 1.1rem; margin-bottom: 0.85rem; text-align: left;">
            <div style="font-weight: 800; font-size: 1.1rem; color: #FFFFFF; letter-spacing: 0.04em;">🏛️ KBCNMU PORTAL</div>
            <div style="font-size: 0.72rem; font-weight: 700; color: #0284C7; letter-spacing: 0.05em; margin-top: 0.25rem;">LIVE SCOPUS INTELLIGENCE [IR-O-U-0320]</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Reset Dashboard Button
    if st.button("🔄 Reset Dashboard", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)

    # Scopus Gateway Panel & Feed Status Indicator
    with st.spinner("Connecting to Scopus Intelligence..."):
        data_res = load_scopus_data(force_refresh=False)

    raw_pubs = data_res.get("publications", [])
    df = pd.DataFrame(raw_pubs)

    if data_res.get("is_live_scopus"):
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 0.45rem; text-align: center; font-size: 0.78rem; font-weight: 700; color: #10B981; margin-bottom: 0.85rem;">
                🟢 Live Scopus Feed • Auto-synced every 60m
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif data_res.get("is_from_cache"):
        st.markdown(
            """
            <div style="background: rgba(2, 132, 199, 0.15); border: 1px solid rgba(2, 132, 199, 0.3); border-radius: 8px; padding: 0.45rem; text-align: center; font-size: 0.78rem; font-weight: 700; color: #38BDF8; margin-bottom: 0.85rem;">
                ⚡ Live Scopus Feed • Auto-synced every 60m
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 0.45rem; text-align: center; font-size: 0.78rem; font-weight: 700; color: #F59E0B; margin-bottom: 0.85rem;">
                🟠 Offline Benchmark Dataset
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Theme Toggle Buttons (Dark Mode | Light Mode)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        if st.button("🌙 Dark Mode", use_container_width=True):
            st.session_state["theme"] = "dark"
            st.rerun()
    with col_t2:
        if st.button("☀️ Light Mode", use_container_width=True):
            st.session_state["theme"] = "light"
            st.rerun()

    st.markdown("---")

    # Section: NAVIGATE & FILTER
    st.markdown("<div style='font-size: 0.8rem; font-weight: 800; color: #38BDF8; letter-spacing: 0.06em; margin-bottom: 0.5rem;'>🔍 NAVIGATE & FILTER</div>", unsafe_allow_html=True)
    st.markdown("**📅 Evaluation Period**")

    # Year Slider 1950 - 2026
    year_range_val = st.slider("Evaluation Period", min_value=1950, max_value=2026, value=(1950, 2026), label_visibility="collapsed")

    # Start Year / End Year Box Inputs
    col_yr1, col_yr2 = st.columns(2)
    with col_yr1:
        start_yr = st.number_input("Start Year", min_value=1950, max_value=2026, value=year_range_val[0])
    with col_yr2:
        end_yr = st.number_input("End Year", min_value=1950, max_value=2026, value=year_range_val[1])

    if st.button("🔄 Apply Year Range", use_container_width=True):
        st.session_state["applied_yr_range"] = (start_yr, end_yr)

    eval_yr_range = st.session_state.get("applied_yr_range", (start_yr, end_yr))

    st.markdown("<br>", unsafe_allow_html=True)

    # Department Filter
    all_depts = sorted(df["department"].unique().tolist()) if not df.empty and "department" in df else []
    selected_depts = st.multiselect("🏛️ Department / School", options=all_depts, default=[], placeholder="Choose options")

    # Quartile Filter
    quartile_opts = ["Q1", "Q2", "Q3", "Q4"]
    selected_quartiles = st.multiselect("🏆 Journal Quartile (Q1-Q4)", options=quartile_opts, default=[], placeholder="Choose options")

    # Collaboration Filter
    collab_opts = ["International", "Industry", "National"]
    selected_collabs = st.multiselect("🌐 Collaboration Scope", options=collab_opts, default=[], placeholder="Choose options")

    st.markdown("<br>", unsafe_allow_html=True)

    # Scopus Gateway & Sync Expander (Matching Screenshot)
    with st.expander("⚙️ Scopus Gateway & API Sync", expanded=False):
        if st.button("🔄 Sync Scopus Now", use_container_width=True):
            with st.spinner("Connecting to Elsevier Scopus API..."):
                load_scopus_data(force_refresh=True)
            st.rerun()
        st.caption(f"Last Synced: {data_res.get('last_synced_readable', 'N/A')}")

    st.markdown("<div style='font-size: 0.75rem; color: #64748B; margin-top: 1rem;'>⚡ ICARE Portal Intelligence | KBCNMU</div>", unsafe_allow_html=True)


# Apply Custom CSS Topbar & Theme
render_icare_topbar(st.session_state.get("theme", "dark"))

# Filter Data
filtered_df = filter_publications(
    df,
    year_range=eval_yr_range,
    depts=selected_depts,
    quartiles=selected_quartiles,
    collab_types=selected_collabs,
)

# Compute 10 Core KPIs
kpis = calculate_top_10_kpis(filtered_df)

# Render Hero Banner
render_icare_hero(kpis["total_output"], kpis["total_citations"], st.session_state.get("theme", "dark"))

# 6. Report Overview Bar (Matching Friend's Dashboard Screenshot)
rep_col1, rep_col2 = st.columns([2, 1.8])

with rep_col1:
    st.markdown(
        """
        <div style="font-weight: 700; font-size: 0.95rem; color: #FFFFFF; padding-top: 0.4rem;">
            📄 REPORT: KBCNMU Live Scopus Intelligence Dashboard Overview
        </div>
        """,
        unsafe_allow_html=True,
    )

with rep_col2:
    b_ex1, b_ex2, b_print = st.columns(3)
    with b_ex1:
        excel_data = convert_df_to_excel(filtered_df)
        st.download_button("📊 Export Excel", data=excel_data, file_name="kbcnmu_scopus.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with b_ex2:
        bib_data = export_to_bibtex(filtered_df)
        st.download_button("📑 Export BibTeX", data=bib_data, file_name="kbcnmu_scopus.bib", mime="text/x-bibtex", use_container_width=True)
    with b_print:
        if st.button("🖨️ Print Dashboard", use_container_width=True):
            components.html("<script>window.parent.print();</script>", height=0)

st.markdown("<br>", unsafe_allow_html=True)

# 7. Top 5 Metric Cards Row (Matching Friend's Dashboard Screenshot)
m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

with m_col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">TOTAL SCOPUS OUTPUT <span>🏆</span></div>
            <div class="metric-value">{kpis['total_output']:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">PUBLICATIONS - 2026 <span>🌴</span></div>
            <div class="metric-value">{kpis['vol_2026']:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">PUBLICATIONS - 2025 <span>📅</span></div>
            <div class="metric-value">{kpis['vol_2025']:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">TOTAL CITATIONS <span>⭐</span></div>
            <div class="metric-value">{kpis['total_citations']:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col5:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">CITATIONS PER PUB (CPP) <span>📈</span></div>
            <div class="metric-value">{kpis['cpp']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# 8. Dashboard 7 Analytical Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 Research Trends",
    "🎯 Citation & Impact",
    "🌐 Global Collaboration",
    "🏆 Quality & Benchmarks",
    "👥 Faculty Authors",
    "📡 Live Feed & Export",
    "🤖 AI Copilot",
])

# ----------------------------------------------------
# TAB 1: 📈 RESEARCH TRENDS
# ----------------------------------------------------
with tab1:
    st.markdown("### 📈 Publication Growth & Monthly Velocity")
    t1_col1, t1_col2 = st.columns([2, 1])

    with t1_col1:
        yearly_data = get_publications_by_year(filtered_df)
        if not yearly_data.empty:
            yearly_data["cumulative_pubs"] = yearly_data["publications"].cumsum()

            fig_trends = make_subplots(specs=[[{"secondary_y": True}]])
            fig_trends.add_trace(
                go.Bar(
                    x=yearly_data["year"],
                    y=yearly_data["publications"],
                    name="Annual Publications",
                    marker_color="#0284C7",
                    opacity=0.85,
                ),
                secondary_y=False,
            )
            fig_trends.add_trace(
                go.Scatter(
                    x=yearly_data["year"],
                    y=yearly_data["cumulative_pubs"],
                    name="Cumulative Output",
                    line=dict(color="#F59E0B", width=3.5),
                    mode="lines+markers",
                ),
                secondary_y=True,
            )
            fig_trends.update_layout(
                title="Annual vs. Cumulative Publication Trajectory",
                hovermode="x unified",
            )
            fig_trends.update_yaxes(title_text="Annual Output", secondary_y=False)
            fig_trends.update_yaxes(title_text="Cumulative Total", secondary_y=True)
            apply_plotly_theme(fig_trends, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_trends, use_container_width=True)
        else:
            st.info("No publication data matching selected filters.")

    with t1_col2:
        target_year = 2026
        monthly_df = get_publications_by_month(filtered_df, target_year)

        fig_month = px.bar(
            monthly_df,
            x="month",
            y="publications",
            title=f"📅 {target_year} Monthly Velocity",
            color_discrete_sequence=["#06B6D4"],
            text="publications",
        )
        fig_month.update_traces(textposition="outside")
        apply_plotly_theme(fig_month, st.session_state.get("theme", "dark"))
        st.plotly_chart(fig_month, use_container_width=True)

    # Departmental Research Output Breakdown Chart (Matching Friend's Screenshot)
    st.markdown("<br>", unsafe_allow_html=True)
    if not filtered_df.empty and "department" in filtered_df:
        dept_output = (
            filtered_df["department"]
            .value_counts()
            .reset_index()
        )
        dept_output.columns = ["department", "publications"]
        dept_output = dept_output.sort_values("publications", ascending=True)

        fig_dept_breakdown = px.bar(
            dept_output,
            x="publications",
            y="department",
            orientation="h",
            title="Departmental Research Output Breakdown",
            text="publications",
            color="publications",
            color_continuous_scale="Emerald",
        )
        fig_dept_breakdown.update_traces(textposition="outside")
        fig_dept_breakdown.update_layout(
            xaxis_title="Publications",
            yaxis_title="Department",
            coloraxis_showscale=False,
            height=450,
        )
        apply_plotly_theme(fig_dept_breakdown, st.session_state.get("theme", "dark"))
        st.plotly_chart(fig_dept_breakdown, use_container_width=True)



# ----------------------------------------------------
# TAB 2: 🎯 CITATION & IMPACT
# ----------------------------------------------------
with tab2:
    st.markdown("### 🎯 Citation Accrual & High Impact Publications")
    t2_col1, t2_col2 = st.columns(2)

    with t2_col1:
        yearly_data = get_publications_by_year(filtered_df)
        if not yearly_data.empty:
            fig_cites = px.line(
                yearly_data,
                x="year",
                y="citations",
                title="📈 Annual Citation Accrual Curve",
                markers=True,
                color_discrete_sequence=["#10B981"],
            )
            apply_plotly_theme(fig_cites, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_cites, use_container_width=True)

    with t2_col2:
        if not filtered_df.empty:
            dept_cites = (
                filtered_df.groupby("department")["citations"]
                .sum()
                .reset_index()
                .sort_values("citations", ascending=True)
            )
            fig_dept_cites = px.bar(
                dept_cites,
                x="citations",
                y="department",
                orientation="h",
                title="🏛️ Departmental Citation Impact",
                color="citations",
                color_continuous_scale="Blues",
            )
            apply_plotly_theme(fig_dept_cites, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_dept_cites, use_container_width=True)

    st.markdown("#### 📜 Landmark Publications (Top Cited)")
    if not filtered_df.empty:
        top_cited = filtered_df.sort_values(by="citations", ascending=False).head(10).copy()
        top_cited["DOI Link"] = top_cited["doi"].apply(
            lambda d: f'<a href="https://doi.org/{d}" target="_blank">DOI ↗</a>' if d else "N/A"
        )
        display_df = top_cited[["title", "primary_author", "journal", "year", "citations", "quartile", "DOI Link"]]
        st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)


# ----------------------------------------------------
# TAB 3: 🌐 GLOBAL COLLABORATION
# ----------------------------------------------------
with tab3:
    st.markdown("### 🌐 Global Co-Authorship & Industry R&D Network")
    t3_col1, t3_col2 = st.columns([3, 2])

    with t3_col1:
        country_counts = {}
        if not filtered_df.empty and "countries" in filtered_df:
            for countries_list in filtered_df["countries"].dropna():
                for c in countries_list:
                    country_counts[c] = country_counts.get(c, 0) + 1

        country_df = pd.DataFrame(list(country_counts.items()), columns=["country", "count"])
        if not country_df.empty:
            fig_map = px.choropleth(
                country_df,
                locations="country",
                locationmode="country names",
                color="count",
                title="🗺️ Global Co-Authorship Footprint",
                color_continuous_scale="Viridis",
            )
            apply_plotly_theme(fig_map, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_map, use_container_width=True)

    with t3_col2:
        if not country_df.empty:
            top_countries = (
                country_df[country_df["country"] != "India"]
                .sort_values("count", ascending=False)
                .head(10)
            )
            fig_top_countries = px.bar(
                top_countries,
                x="count",
                y="country",
                orientation="h",
                title="🤝 Top 10 Partner Countries",
                color_discrete_sequence=["#38BDF8"],
            )
            apply_plotly_theme(fig_top_countries, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_top_countries, use_container_width=True)

    t3_b1, t3_b2 = st.columns(2)
    with t3_b1:
        if not filtered_df.empty:
            fig_tree = px.treemap(
                filtered_df,
                path=["department", "journal"],
                title="🌳 Department & Journal Treemap Distribution",
                color_discrete_sequence=px.colors.qualitative.Prism,
            )
            apply_plotly_theme(fig_tree, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_tree, use_container_width=True)

    with t3_b2:
        if not filtered_df.empty:
            collab_summary = pd.DataFrame({
                "Type": ["International", "Industry R&D", "Domestic Only"],
                "Count": [
                    len(filtered_df[filtered_df["is_international_collab"] == True]),
                    len(filtered_df[filtered_df["is_industry_collab"] == True]),
                    len(filtered_df[(filtered_df["is_international_collab"] == False) & (filtered_df["is_industry_collab"] == False)]),
                ],
            })
            fig_collab_pie = px.pie(
                collab_summary,
                values="Count",
                names="Type",
                title="🏢 Industry R&D vs International Collaboration",
                hole=0.4,
                color_discrete_sequence=["#0284C7", "#F59E0B", "#64748B"],
            )
            apply_plotly_theme(fig_collab_pie, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_collab_pie, use_container_width=True)


# ----------------------------------------------------
# TAB 4: 🏆 QUALITY & BENCHMARKS
# ----------------------------------------------------
with tab4:
    st.markdown("### 🏆 Journal Quality & Institutional Benchmarking")
    t4_col1, t4_col2 = st.columns(2)

    with t4_col1:
        if not filtered_df.empty:
            q_counts = filtered_df["quartile"].value_counts().reset_index()
            q_counts.columns = ["quartile", "count"]

            quartile_color_map = {
                "Q1": "#10B981",
                "Q2": "#3B82F6",
                "Q3": "#F59E0B",
                "Q4": "#EF4444",
            }

            fig_donut = px.pie(
                q_counts,
                values="count",
                names="quartile",
                title="🍩 Scopus Journal Quartile Breakdown",
                hole=0.5,
                color="quartile",
                color_discrete_map=quartile_color_map,
            )
            apply_plotly_theme(fig_donut, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_donut, use_container_width=True)

    with t4_col2:
        if not filtered_df.empty:
            dept_summary = (
                filtered_df.groupby("department")
                .agg(
                    publications=("scopus_id", "count"),
                    total_citations=("citations", "sum"),
                    avg_citescore=("citescore", "mean"),
                )
                .reset_index()
            )
            dept_summary["cpp"] = (dept_summary["total_citations"] / dept_summary["publications"]).round(2)
            avg_cpp_bench = round(dept_summary["cpp"].mean(), 2) if not dept_summary.empty else 0

            fig_bubble = px.scatter(
                dept_summary,
                x="publications",
                y="cpp",
                size="total_citations",
                color="department",
                text="department",
                title="📍 Department Impact vs. Volume Quadrant",
                hover_data=["avg_citescore"],
            )
            fig_bubble.add_hline(
                y=avg_cpp_bench,
                line_dash="dash",
                line_color="#F59E0B",
                annotation_text=f"Average CPP ({avg_cpp_bench})",
                annotation_position="top right",
            )
            apply_plotly_theme(fig_bubble, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("#### 🎯 Department Multi-Dimensional Radar Benchmark")
    if not filtered_df.empty:
        radar_df = (
            filtered_df.groupby("department")
            .agg(
                Output=("scopus_id", "count"),
                Citations=("citations", "sum"),
                Q1_Share=("quartile", lambda x: (sum(x == "Q1") / len(x)) * 100 if len(x) > 0 else 0),
                Intl_Collab=("is_international_collab", lambda x: (sum(x) / len(x)) * 100 if len(x) > 0 else 0),
            )
            .reset_index()
        )
        fig_radar = go.Figure()
        for _, row in radar_df.head(5).iterrows():
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=[row["Output"], row["Citations"] / 10, row["Q1_Share"], row["Intl_Collab"]],
                    theta=["Output Volume", "Citations (/10)", "Q1 Share %", "Intl Collab %"],
                    fill="toself",
                    name=row["department"],
                )
            )
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, showticklabels=True)), title="Departmental Comparative Radar Benchmark")
        apply_plotly_theme(fig_radar, st.session_state.get("theme", "dark"))
        st.plotly_chart(fig_radar, use_container_width=True)


# ----------------------------------------------------
# TAB 5: 👥 FACULTY AUTHORS & PROFILE DOSSIER
# ----------------------------------------------------
with tab5:
    st.markdown("### 👥 Faculty Research Leaderboard & Deep-Dive Profile Inspection")

    top3_leaderboard = get_top_authors_leaderboard(filtered_df, top_n=3)
    if not top3_leaderboard.empty:
        p_col1, p_col2, p_col3 = st.columns(3)
        podium_styles = [
            ("🥇 GOLD PODIUM", "#F59E0B", "rgba(245, 158, 11, 0.15)", "1px solid rgba(245, 158, 11, 0.4)"),
            ("🥈 SILVER PODIUM", "#94A3B8", "rgba(148, 163, 184, 0.15)", "1px solid rgba(148, 163, 184, 0.4)"),
            ("🥉 BRONZE PODIUM", "#D97706", "rgba(217, 119, 6, 0.15)", "1px solid rgba(217, 119, 6, 0.4)"),
        ]
        cols = [p_col1, p_col2, p_col3]
        for idx, row in top3_leaderboard.iterrows():
            if idx < 3:
                label, color, bg_c, border_c = podium_styles[idx]
                with cols[idx]:
                    st.markdown(
                        f"""
                        <div style="background: {bg_c}; border: {border_c}; border-radius: 16px; padding: 1.25rem; text-align: center;">
                            <div style="font-size: 0.75rem; font-weight: 800; color: {color}; letter-spacing: 0.08em; margin-bottom: 0.4rem;">{label}</div>
                            <div style="font-size: 1.35rem; font-weight: 800; color: #FFFFFF; margin-bottom: 0.5rem;">👨‍🏫 {row['author']}</div>
                            <div style="display: flex; justify-content: space-around; background: rgba(0,0,0,0.25); border-radius: 10px; padding: 0.6rem; font-size: 0.85rem;">
                                <div><div style="font-weight: 800; color: #38BDF8;">{row['papers']}</div><div style="font-size: 0.7rem; color: #94A3B8;">Papers</div></div>
                                <div><div style="font-weight: 800; color: #F59E0B;">{row['citations']:,}</div><div style="font-size: 0.7rem; color: #94A3B8;">Cites</div></div>
                                <div><div style="font-weight: 800; color: #10B981;">{row['cpp']}</div><div style="font-size: 0.7rem; color: #94A3B8;">CPP</div></div>
                                <div><div style="font-weight: 800; color: #EC4899;">{row['h_index']}</div><div style="font-size: 0.7rem; color: #94A3B8;">h-Index</div></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with st.expander("📋 Full Faculty Leaderboard Table & BibTeX Export", expanded=False):
        full_lb_col1, full_lb_col2 = st.columns([3, 1])
        with full_lb_col1:
            full_leaderboard = get_top_authors_leaderboard(filtered_df, top_n=500)
            st.dataframe(full_leaderboard, use_container_width=True, height=350)
        with full_lb_col2:
            st.markdown("#### 📥 Export BibTeX")
            bib_str = export_to_bibtex(filtered_df.head(100))
            st.download_button(
                label="📥 Download BibTeX (.bib)",
                data=bib_str,
                file_name="kbcnmu_scopus_export.bib",
                mime="text/x-bibtex",
                use_container_width=True,
            )

    st.markdown("---")

    all_authors_df = get_top_authors_leaderboard(filtered_df, top_n=1000)
    all_author_names = all_authors_df["author"].tolist() if not all_authors_df.empty else []

    sel_col, btn_col = st.columns([3, 1])
    with sel_col:
        selected_author = st.selectbox(
            "👨‍🏫 Select Faculty Researcher for Deep-Dive Inspection",
            options=all_author_names,
            index=0 if all_author_names else 0,
        )

    auth_prof = get_author_profile_metrics(filtered_df, selected_author) if selected_author else {}

    with btn_col:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        do_print = st.button("🖨️ Print Profile", use_container_width=True)

    if do_print and auth_prof:
        print_html = generate_author_print_html(auth_prof)
        b64_html = base64.b64encode(print_html.encode("utf-8")).decode("utf-8")

        iframe_js = f"""
        <script>
        (function() {{
        const b64 = "{b64_html}";
        const html = decodeURIComponent(escape(window.atob(b64)));
        const parentDoc = (window.parent && window.parent.document) ? window.parent.document : document;
        let frame = parentDoc.getElementById('author-print-isolated-frame');
        if (frame) frame.remove();
        frame = parentDoc.createElement('iframe');
        frame.id = 'author-print-isolated-frame';
        frame.style.position = 'fixed'; frame.style.right = '0'; frame.style.bottom = '0';
        frame.style.width = '0'; frame.style.height = '0'; frame.style.border = '0';
        parentDoc.body.appendChild(frame);
        const doc = frame.contentWindow.document;
        doc.open(); doc.write(html); doc.close();
        setTimeout(() => {{ frame.contentWindow.focus(); frame.contentWindow.print(); }}, 350);
        }})();
        </script>
        """
        components.html(iframe_js, height=0)
        st.toast(f"🖨️ Isolated print job launched for Prof. {selected_author}!", icon="🖨️")

    if auth_prof and selected_author:
        st.markdown(
            f"""
            <div style="background: rgba(2, 132, 199, 0.1); border: 1px solid rgba(2, 132, 199, 0.3); border-radius: 16px; padding: 1.5rem; margin-top: 1rem; margin-bottom: 1.5rem;">
                <div style="font-size: 1.8rem; font-weight: 800; color: #FFFFFF;">👨‍🏫 {auth_prof['author_name']}</div>
                <div style="font-size: 0.95rem; color: #38BDF8; font-weight: 600; margin-top: 0.2rem;">
                    🏛️ {auth_prof['department']} &nbsp;|&nbsp; 📖 Primary Journal: {auth_prof['top_journal']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Publications</div>
                    <div class="metric-value">{auth_prof['total_papers']}</div>
                    <div class="metric-subtitle">Scopus Indexed</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Citations</div>
                    <div class="metric-value">{auth_prof['total_citations']:,}</div>
                    <div class="metric-subtitle">Total Accrued</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">CPP</div>
                    <div class="metric-value">{auth_prof['cpp']}</div>
                    <div class="metric-subtitle">Cites Per Paper</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">h-Index</div>
                    <div class="metric-value">{auth_prof['h_index']}</div>
                    <div class="metric-subtitle">Estimated Metric</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with k5:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Q1 Ratio</div>
                    <div class="metric-value">{auth_prof['q1_ratio']}%</div>
                    <div class="metric-subtitle">{auth_prof['q1_papers']} Q1 Papers</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
                <span class="hero-pill hero-pill-gold">⭐ Q1 Papers: {auth_prof['q1_papers']}</span>
                <span class="hero-pill">🌐 International Collab: {auth_prof['intl_pct']}%</span>
                <span class="hero-pill">🏢 Industry Collab: {auth_prof['industry_pct']}%</span>
                <span class="hero-pill">👥 Co-Authors Count: {auth_prof['coauthors_count']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        author_df = auth_prof.get("author_df", pd.DataFrame())
        if not author_df.empty:
            ac_col1, ac_col2 = st.columns(2)
            with ac_col1:
                author_yearly = (
                    author_df.groupby("year")
                    .agg(publications=("scopus_id", "count"), citations=("citations", "sum"))
                    .reset_index()
                    .sort_values("year")
                )
                fig_auth_trend = make_subplots(specs=[[{"secondary_y": True}]])
                fig_auth_trend.add_trace(
                    go.Bar(
                        x=author_yearly["year"],
                        y=author_yearly["publications"],
                        name="Annual Output",
                        marker_color="#0284C7",
                    ),
                    secondary_y=False,
                )
                fig_auth_trend.add_trace(
                    go.Scatter(
                        x=author_yearly["year"],
                        y=author_yearly["citations"],
                        name="Citations Accrued",
                        line=dict(color="#F59E0B", width=3),
                        mode="lines+markers",
                    ),
                    secondary_y=True,
                )
                fig_auth_trend.update_layout(title=f"📈 {selected_author} Output & Citation Trajectory")
                fig_auth_trend.update_yaxes(title_text="Publications", secondary_y=False)
                fig_auth_trend.update_yaxes(title_text="Citations", secondary_y=True)
                apply_plotly_theme(fig_auth_trend, st.session_state.get("theme", "dark"))
                st.plotly_chart(fig_auth_trend, use_container_width=True)

            with ac_col2:
                auth_q_counts = author_df["quartile"].value_counts().reset_index()
                auth_q_counts.columns = ["quartile", "count"]
                fig_auth_q = px.pie(
                    auth_q_counts,
                    values="count",
                    names="quartile",
                    title=f"🍩 {selected_author} Journal Quartile Breakdown",
                    hole=0.45,
                    color="quartile",
                    color_discrete_map={
                        "Q1": "#10B981",
                        "Q2": "#3B82F6",
                        "Q3": "#F59E0B",
                        "Q4": "#EF4444",
                    },
                )
                apply_plotly_theme(fig_auth_q, st.session_state.get("theme", "dark"))
                st.plotly_chart(fig_auth_q, use_container_width=True)

            st.markdown(f"#### 📜 Top 5 Landmark Contributions - {selected_author}")
            top5_auth_papers = author_df.sort_values(by="citations", ascending=False).head(5).copy()
            top5_auth_papers["DOI Link"] = top5_auth_papers["doi"].apply(
                lambda d: f'<a href="https://doi.org/{d}" target="_blank">DOI ↗</a>' if d else "N/A"
            )
            st.write(
                top5_auth_papers[["title", "journal", "year", "citations", "quartile", "DOI Link"]].to_html(
                    escape=False, index=False
                ),
                unsafe_allow_html=True,
            )

            st.markdown(f"#### 📚 Complete Indexed Publications ({len(author_df)})")
            st.dataframe(
                author_df[["year", "title", "journal", "quartile", "citations", "doi"]].sort_values(
                    by="year", ascending=False
                ),
                use_container_width=True,
                height=350,
            )


# ----------------------------------------------------
# TAB 6: 📡 LIVE FEED & EXPORT
# ----------------------------------------------------
with tab6:
    st.markdown("### 📡 Live Feed & Data Export Center")

    search_kw = st.text_input(
        "🔍 Search Publications by Keyword, Title, Author, Journal, or DOI",
        placeholder="Type to filter... (e.g., Chemistry, Nanoparticles, Mahulikar, 2026)",
    )

    search_df = filtered_df.copy()
    if search_kw.strip():
        kw = search_kw.strip().lower()
        mask = (
            search_df["title"].astype(str).str.lower().str.contains(kw)
            | search_df["authors"].astype(str).str.lower().str.contains(kw)
            | search_df["journal"].astype(str).str.lower().str.contains(kw)
            | search_df["department"].astype(str).str.lower().str.contains(kw)
            | search_df["doi"].astype(str).str.lower().str.contains(kw)
        )
        search_df = search_df[mask]

    ex_col1, ex_col2, ex_info = st.columns([1, 1, 2])

    with ex_col1:
        excel_bytes = convert_df_to_excel(search_df)
        st.download_button(
            label="📊 Export Excel (.xlsx)",
            data=excel_bytes,
            file_name="kbcnmu_scopus_filtered.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with ex_col2:
        bib_bytes = export_to_bibtex(search_df)
        st.download_button(
            label="📑 Export BibTeX (.bib)",
            data=bib_bytes,
            file_name="kbcnmu_scopus_filtered.bib",
            mime="text/x-bibtex",
            use_container_width=True,
        )

    with ex_info:
        st.markdown(
            f"""
            <div style="background: rgba(2, 132, 199, 0.1); border: 1px solid rgba(2, 132, 199, 0.2); padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.9rem; color: #38BDF8;">
                Showing {len(search_df):,} matching publication records
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.dataframe(
        search_df[
            ["year", "title", "primary_author", "department", "journal", "quartile", "citations", "doi"]
        ].sort_values(by="year", ascending=False),
        use_container_width=True,
        height=520,
    )


# ----------------------------------------------------
# TAB 7: 🤖 AI COPILOT
# ----------------------------------------------------
with tab7:
    st.markdown("### 🤖 Scopus AI Research Intelligence Assistant")
    st.caption("Fast built-in Pandas/Python natural language research assistant. Zero external API dependencies.")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    hdr_c1, hdr_c2 = st.columns([3, 1])
    with hdr_c2:
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()

    st.markdown("##### 💡 Preset Prompt Chips")
    chip_c1, chip_c2, chip_c3, chip_c4 = st.columns(4)

    prompt_trigger = None

    with chip_c1:
        if st.button("📊 Executive Dossier", use_container_width=True):
            prompt_trigger = "Executive Dossier"
    with chip_c2:
        if st.button("🏛️ Dept Rankings", use_container_width=True):
            prompt_trigger = "Dept Rankings"
    with chip_c3:
        if st.button("🏆 Q1 Quality Analysis", use_container_width=True):
            prompt_trigger = "Q1 Quality Analysis"
    with chip_c4:
        if st.button("👥 Top Authors", use_container_width=True):
            prompt_trigger = "Top Authors"

    st.markdown("---")

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("💬 Ask AI Copilot anything about KBCNMU research data...")

    active_prompt = prompt_trigger or user_input

    if active_prompt:
        st.session_state["chat_history"].append({"role": "user", "content": active_prompt})
        with st.chat_message("user"):
            st.markdown(active_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing KBCNMU dataset..."):
                response_md = query_scopus_ai_copilot(active_prompt, filtered_df)
                st.markdown(response_md)

        st.session_state["chat_history"].append({"role": "assistant", "content": response_md})
