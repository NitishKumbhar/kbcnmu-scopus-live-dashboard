"""
app.py
KBCNMU Live Scopus Intelligence Dashboard
Main Streamlit application featuring ICARE Glassmorphism design, real-time Scopus API integration,
10 Core KPIs, and interactive Plotly visualization Tabs 1 through 4.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as bg
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from config import UNIVERSITY_CONFIG
from data_processor import (
    calculate_top_10_kpis,
    export_to_bibtex,
    filter_publications,
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


# 2. Plotly Theme Helper
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
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=font_color),
        ),
        xaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(color=font_color),
        ),
        yaxis=dict(
            gridcolor=grid_color,
            zerolinecolor=grid_color,
            tickfont=dict(color=font_color),
        ),
    )
    return fig


# 3. Sidebar Controls
with st.sidebar:
    st.image("LOGO/download.png", use_container_width=True) if pd.io.common.file_exists("LOGO/download.png") else st.title("🏛️ KBCNMU")
    st.markdown("### ⚙️ Portal Controls")

    # Theme Toggle
    theme = st.radio("🎨 Dashboard Theme", ["Dark", "Light"], index=0, horizontal=True)
    st.session_state["theme"] = theme.lower()

    # Manual Scopus Sync Button
    st.markdown("---")
    st.markdown("### 🔄 Scopus API Sync")
    force_sync = st.button("⚡ Sync Live Scopus API", use_container_width=True)

    # Load Scopus Data (Cache or Live API or Fallback)
    with st.spinner("Connecting to Scopus Intelligence Portal..."):
        data_res = load_scopus_data(force_refresh=force_sync)

    raw_pubs = data_res.get("publications", [])
    df = pd.DataFrame(raw_pubs)

    # Display Data Source Badge
    if data_res.get("is_live_scopus"):
        st.success("🟢 Live Scopus API Active")
    elif data_res.get("is_from_cache"):
        st.info(f"⚡ Cached (Age: <60m)")
    else:
        st.warning("🟠 Benchmark Offline Dataset")

    st.caption(f"Last Synced: {data_res.get('last_synced_readable', 'N/A')}")
    st.markdown("---")

    # Interactive Filters
    st.markdown("### 🎯 Dataset Filters")

    # Year Filter
    min_yr = int(df["year"].min()) if not df.empty and "year" in df else 1992
    max_yr = int(df["year"].max()) if not df.empty and "year" in df else 2026
    year_range = st.slider("📅 Publication Years", min_value=min_yr, max_value=max_yr, value=(min_yr, max_yr))

    # Department Filter
    all_depts = sorted(df["department"].unique().tolist()) if not df.empty and "department" in df else []
    selected_depts = st.multiselect("🏛️ Departments", options=all_depts, default=[])

    # Quartile Filter
    quartile_opts = ["Q1", "Q2", "Q3", "Q4"]
    selected_quartiles = st.multiselect("⭐ Journal Quartile", options=quartile_opts, default=[])

    # Collaboration Filter
    collab_opts = ["International", "Industry", "National"]
    selected_collabs = st.multiselect("🌐 Collaboration Type", options=collab_opts, default=[])

# Apply Custom CSS
render_icare_topbar(st.session_state.get("theme", "dark"))

# Filter Data
filtered_df = filter_publications(
    df,
    year_range=year_range,
    depts=selected_depts,
    quartiles=selected_quartiles,
    collab_types=selected_collabs,
)

# Compute KPIs
kpis = calculate_top_10_kpis(filtered_df)

# Render Hero Banner
render_icare_hero(kpis["total_output"], kpis["total_citations"], st.session_state.get("theme", "dark"))

# 4. Top 10 Core Metric Cards
m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)

with m_col1:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Total Output</div>
            <div class="metric-value">{kpis['total_output']:,}</div>
            <div class="metric-subtitle">Indexed Papers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col2:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">2026 Volume</div>
            <div class="metric-value">{kpis['vol_2026']:,}</div>
            <div class="metric-subtitle">vs {kpis['vol_2025']:,} in 2025</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col3:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Citations Per Paper</div>
            <div class="metric-value">{kpis['cpp']}</div>
            <div class="metric-subtitle">Total: {kpis['total_citations']:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col4:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Q1 Quality Share</div>
            <div class="metric-value">{kpis['q1_pct']}%</div>
            <div class="metric-subtitle">{kpis['q1_count']:,} Q1 Papers</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with m_col5:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">Intl Collab %</div>
            <div class="metric-value">{kpis['intl_collab_pct']}%</div>
            <div class="metric-subtitle">Industry: {kpis['industry_collab_pct']}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# 5. Dashboard Visualization Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Research Trends",
    "🎯 Citation & Impact",
    "🌐 Global Collaboration",
    "🏆 Quality & Benchmarks",
    "👤 Author Leaderboard",
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

            # Dual-Axis Plotly Chart
            fig_trends = make_subplots(specs=[[{"secondary_y": True}]])

            # Primary Axis: Annual Publications Bar Chart
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

            # Secondary Axis: Cumulative Total Gold Line
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
                title="Annual vs. Cumulative Publication Trajectory (1992 - 2026)",
                hovermode="x unified",
            )
            fig_trends.update_yaxes(title_text="Annual Output", secondary_y=False)
            fig_trends.update_yaxes(title_text="Cumulative Total", secondary_y=True)
            apply_plotly_theme(fig_trends, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_trends, use_container_width=True)
        else:
            st.info("No publication data matching selected filters.")

    with t1_col2:
        # Monthly Velocity Chart
        target_year = max_yr
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

        st.write(
            display_df.to_html(escape=False, index=False),
            unsafe_allow_html=True,
        )


# ----------------------------------------------------
# TAB 3: 🌐 GLOBAL COLLABORATION
# ----------------------------------------------------
with tab3:
    st.markdown("### 🌐 Global Co-Authorship & Industry R&D Network")
    t3_col1, t3_col2 = st.columns([3, 2])

    with t3_col1:
        # Global Map
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
        # Quartile Donut Chart with Exact Required Colors
        if not filtered_df.empty:
            q_counts = filtered_df["quartile"].value_counts().reset_index()
            q_counts.columns = ["quartile", "count"]

            quartile_color_map = {
                "Q1": "#10B981",  # Emerald Green
                "Q2": "#3B82F6",  # Royal Blue
                "Q3": "#F59E0B",  # Amber Gold
                "Q4": "#EF4444",  # Crimson Red
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
        # Quadrant Bubble Chart (Volume vs. CPP with Benchmark Line)
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

            # Gold dashed benchmark line for Average CPP
            fig_bubble.add_hline(
                y=avg_cpp_bench,
                line_dash="dash",
                line_color="#F59E0B",
                annotation_text=f"KBCNMU Average CPP ({avg_cpp_bench})",
                annotation_position="top right",
            )

            apply_plotly_theme(fig_bubble, st.session_state.get("theme", "dark"))
            st.plotly_chart(fig_bubble, use_container_width=True)

    # Department Radar Benchmark Chart
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
        categories = ["Output", "Citations", "Q1_Share", "Intl_Collab"]

        for _, row in radar_df.head(5).iterrows():
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=[row["Output"], row["Citations"] / 10, row["Q1_Share"], row["Intl_Collab"]],
                    theta=["Output Volume", "Citations (/10)", "Q1 Share %", "Intl Collab %"],
                    fill="toself",
                    name=row["department"],
                )
            )

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, showticklabels=True),
            ),
            title="Departmental Comparative Radar Benchmark (Top 5 Schools)",
        )
        apply_plotly_theme(fig_radar, st.session_state.get("theme", "dark"))
        st.plotly_chart(fig_radar, use_container_width=True)


# ----------------------------------------------------
# TAB 5: 👤 AUTHOR LEADERBOARD & BIBTEX EXPORT
# ----------------------------------------------------
with tab5:
    st.markdown("### 👤 Faculty Research Leaderboard & BibTeX Export")
    l_col1, l_col2 = st.columns([2, 1])

    with l_col1:
        leaderboard = get_top_authors_leaderboard(filtered_df, top_n=25)
        st.dataframe(leaderboard, use_container_width=True, height=450)

    with l_col2:
        st.markdown("#### 📥 Export BibTeX")
        st.caption("Generate citation entries for all filtered records.")
        bib_str = export_to_bibtex(filtered_df.head(100))
        st.download_button(
            label="📥 Download BibTeX (.bib)",
            data=bib_str,
            file_name="kbcnmu_scopus_export.bib",
            mime="text/x-bibtex",
            use_container_width=True,
        )
