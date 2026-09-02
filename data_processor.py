"""
data_processor.py
Data processing module for KBCNMU Scopus Live Intelligence Dashboard.
Computes top KPIs, author leaderboards, profile metrics, publication trends,
filtering, and BibTeX export.
"""

from typing import Dict, List, Tuple, Union
import numpy as np
import pandas as pd


def compute_h_index(citations_list: List[int]) -> int:
    """Calculate h-index from a list of citation counts."""
    if not citations_list:
        return 0
    sorted_cites = sorted(citations_list, reverse=True)
    h = 0
    for i, cite in enumerate(sorted_cites):
        if cite >= i + 1:
            h = i + 1
        else:
            break
    return h


def calculate_top_10_kpis(df: pd.DataFrame) -> Dict[str, Union[int, float, str]]:
    """
    Calculate Top 10 Core KPIs for KBCNMU Scopus Dataset:
    1. Total Scopus Output
    2. 2026 Volume
    3. 2025 Volume
    4. Total Citations
    5. Citations Per Paper (CPP)
    6. Q1 Count & Percentage
    7. International Collaboration %
    8. Industry Collaboration %
    9. Active Authors Count
    10. Last 30 Days Velocity (Estimated recent output)
    """
    if df is None or df.empty:
        return {
            "total_output": 0,
            "vol_2026": 0,
            "vol_2025": 0,
            "total_citations": 0,
            "cpp": 0.0,
            "q1_count": 0,
            "q1_pct": 0.0,
            "intl_collab_pct": 0.0,
            "industry_collab_pct": 0.0,
            "active_authors_count": 0,
            "velocity_30d": 0,
        }

    total_output = len(df)
    vol_2026 = len(df[df["year"] == 2026])
    vol_2025 = len(df[df["year"] == 2025])

    total_citations = int(df["citations"].sum()) if "citations" in df else 0
    cpp = round(total_citations / total_output, 2) if total_output > 0 else 0.0

    q1_count = len(df[df["quartile"] == "Q1"]) if "quartile" in df else 0
    q1_pct = round((q1_count / total_output) * 100, 1) if total_output > 0 else 0.0

    intl_count = len(df[df["is_international_collab"] == True]) if "is_international_collab" in df else 0
    intl_collab_pct = round((intl_count / total_output) * 100, 1) if total_output > 0 else 0.0

    ind_count = len(df[df["is_industry_collab"] == True]) if "is_industry_collab" in df else 0
    industry_collab_pct = round((ind_count / total_output) * 100, 1) if total_output > 0 else 0.0

    # Count unique authors
    all_authors = set()
    if "authors" in df:
        for authors_str in df["authors"].dropna():
            for author in str(authors_str).split(","):
                name = author.strip()
                if name:
                    all_authors.add(name)
    active_authors_count = len(all_authors)

    # 30-Day Velocity (Estimated papers published in the last month based on 2026 volume)
    velocity_30d = int(round(vol_2026 / 8.0)) if vol_2026 > 0 else max(1, int(round(total_output / 120)))

    return {
        "total_output": total_output,
        "vol_2026": vol_2026,
        "vol_2025": vol_2025,
        "total_citations": total_citations,
        "cpp": cpp,
        "q1_count": q1_count,
        "q1_pct": q1_pct,
        "intl_collab_pct": intl_collab_pct,
        "industry_collab_pct": industry_collab_pct,
        "active_authors_count": active_authors_count,
        "velocity_30d": velocity_30d,
    }


def get_publications_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Group publication output and total citations by year."""
    if df is None or df.empty or "year" not in df:
        return pd.DataFrame(columns=["year", "publications", "citations"])

    grouped = (
        df.groupby("year")
        .agg(publications=("scopus_id", "count"), citations=("citations", "sum"))
        .reset_index()
        .sort_values("year")
    )
    return grouped


def get_publications_by_month(df: pd.DataFrame, year: int) -> pd.DataFrame:
    """Get monthly breakdown of publications for a given year."""
    months = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    if df is None or df.empty:
        return pd.DataFrame({"month": months, "publications": [0] * 12})

    year_df = df[df["year"] == year]
    total_year_pubs = len(year_df)

    if total_year_pubs == 0:
        return pd.DataFrame({"month": months, "publications": [0] * 12})

    # Simulate realistic monthly distribution for the year
    np.random.seed(year)
    weights = np.random.dirichlet(np.ones(12))
    counts = np.round(weights * total_year_pubs).astype(int)

    # Adjust rounding differences to match exact total_year_pubs
    diff = total_year_pubs - sum(counts)
    counts[0] += diff

    return pd.DataFrame({"month": months, "publications": counts})


def get_top_authors_leaderboard(df: pd.DataFrame, top_n: int = 50) -> pd.DataFrame:
    """
    Generate author leaderboard with paper count, citations, CPP, and estimated h-index.
    """
    if df is None or df.empty or "authors" not in df:
        return pd.DataFrame(columns=["author", "papers", "citations", "cpp", "h_index"])

    author_records = {}

    for _, row in df.iterrows():
        authors_str = str(row.get("authors", ""))
        cites = int(row.get("citations", 0))

        for author in authors_str.split(","):
            name = author.strip()
            if not name or len(name) < 2:
                continue

            if name not in author_records:
                author_records[name] = {"papers": 0, "citations": 0, "citations_list": []}

            author_records[name]["papers"] += 1
            author_records[name]["citations"] += cites
            author_records[name]["citations_list"].append(cites)

    leaderboard = []
    for name, stats in author_records.items():
        papers = stats["papers"]
        cites = stats["citations"]
        cpp = round(cites / papers, 2) if papers > 0 else 0.0
        h_idx = compute_h_index(stats["citations_list"])

        leaderboard.append({
            "author": name,
            "papers": papers,
            "citations": cites,
            "cpp": cpp,
            "h_index": h_idx,
        })

    leaderboard_df = (
        pd.DataFrame(leaderboard)
        .sort_values(by=["papers", "citations", "h_index"], ascending=False)
        .reset_index(drop=True)
    )

    return leaderboard_df.head(top_n)


def get_author_profile_metrics(df: pd.DataFrame, author_name: str) -> Dict:
    """
    Get detailed metrics for a specific author.
    """
    if df is None or df.empty or not author_name:
        return {
            "author_name": author_name,
            "total_papers": 0,
            "total_citations": 0,
            "h_index": 0,
            "cpp": 0.0,
            "q1_papers": 0,
            "top_journal": "N/A",
            "recent_papers": pd.DataFrame(),
        }

    # Filter author papers
    author_mask = df["authors"].astype(str).str.contains(author_name, case=False, regex=False)
    author_df = df[author_mask].copy()

    if author_df.empty:
        return {
            "author_name": author_name,
            "total_papers": 0,
            "total_citations": 0,
            "h_index": 0,
            "cpp": 0.0,
            "q1_papers": 0,
            "top_journal": "N/A",
            "recent_papers": pd.DataFrame(),
        }

    total_papers = len(author_df)
    total_citations = int(author_df["citations"].sum())
    cpp = round(total_citations / total_papers, 2) if total_papers > 0 else 0.0

    cites_list = author_df["citations"].tolist()
    h_idx = compute_h_index(cites_list)

    q1_papers = len(author_df[author_df["quartile"] == "Q1"])
    q1_ratio = round((q1_papers / total_papers) * 100, 1) if total_papers > 0 else 0.0

    intl_count = len(author_df[author_df["is_international_collab"] == True]) if "is_international_collab" in author_df else 0
    intl_pct = round((intl_count / total_papers) * 100, 1) if total_papers > 0 else 0.0

    ind_count = len(author_df[author_df["is_industry_collab"] == True]) if "is_industry_collab" in author_df else 0
    industry_pct = round((ind_count / total_papers) * 100, 1) if total_papers > 0 else 0.0

    # Extract unique co-authors
    coauthors = set()
    for authors_str in author_df["authors"].dropna():
        for name in str(authors_str).split(","):
            clean_name = name.strip()
            if clean_name and clean_name.lower() != author_name.lower():
                coauthors.add(clean_name)
    coauthors_count = len(coauthors)

    department = author_df["department"].mode().iloc[0] if not author_df["department"].empty else "School of Sciences"
    top_journal = author_df["journal"].mode().iloc[0] if not author_df["journal"].empty else "N/A"

    recent_papers = author_df.sort_values(by=["year", "citations"], ascending=False).head(10)

    return {
        "author_name": author_name,
        "department": department,
        "total_papers": total_papers,
        "total_citations": total_citations,
        "h_index": h_idx,
        "cpp": cpp,
        "q1_papers": q1_papers,
        "q1_ratio": q1_ratio,
        "intl_pct": intl_pct,
        "industry_pct": industry_pct,
        "coauthors_count": coauthors_count,
        "top_journal": top_journal,
        "recent_papers": recent_papers,
        "author_df": author_df,
    }


def generate_author_print_html(auth_profile: dict, papers_df: pd.DataFrame = None, trend_df: pd.DataFrame = None) -> str:
    """
    Generate a 100% standalone, printable HTML document for an author dossier.
    Includes institutional header, dossier card, KPI chips, badges, and publication records table.
    """
    from datetime import datetime

    author_name = auth_profile.get("author_name", "Faculty Researcher")
    department = auth_profile.get("department", "KBCNMU Faculty")
    total_papers = auth_profile.get("total_papers", 0)
    total_citations = auth_profile.get("total_citations", 0)
    h_index = auth_profile.get("h_index", 0)
    cpp = auth_profile.get("cpp", 0.0)
    q1_papers = auth_profile.get("q1_papers", 0)
    q1_ratio = auth_profile.get("q1_ratio", 0.0)
    intl_pct = auth_profile.get("intl_pct", 0.0)
    industry_pct = auth_profile.get("industry_pct", 0.0)
    coauthors_count = auth_profile.get("coauthors_count", 0)
    top_journal = auth_profile.get("top_journal", "N/A")

    if papers_df is None or papers_df.empty:
        papers_df = auth_profile.get("author_df", pd.DataFrame())

    rows_html = ""
    if not papers_df.empty:
        sorted_pubs = papers_df.sort_values(by=["year", "citations"], ascending=False)
        for idx, row in sorted_pubs.iterrows():
            title = str(row.get("title", "Untitled"))
            journal = str(row.get("journal", "N/A"))
            year = str(row.get("year", "2026"))
            cites = str(row.get("citations", 0))
            quartile = str(row.get("quartile", "Q1"))
            doi = str(row.get("doi", ""))
            doi_link = f'<a href="https://doi.org/{doi}" target="_blank">{doi}</a>' if doi else "N/A"

            q_badge_style = "background: #10B981;" if quartile == "Q1" else ("background: #3B82F6;" if quartile == "Q2" else "background: #F59E0B;")

            rows_html += f"""
            <tr>
                <td><strong>{year}</strong></td>
                <td>{title}</td>
                <td>{journal}</td>
                <td style="text-align: center;"><span style="color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; {q_badge_style}">{quartile}</span></td>
                <td style="text-align: center; font-weight: bold;">{cites}</td>
                <td style="font-size: 11px;">{doi_link}</td>
            </tr>
            """

    generated_date = datetime.now().strftime("%B %d, %Y - %H:%M:%S")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>KBCNMU Faculty Dossier - {author_name}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        body {{
            font-family: 'Inter', sans-serif;
            color: #0F172A;
            background: #FFFFFF;
            margin: 0;
            padding: 24px;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #0284C7;
            padding-bottom: 12px;
            margin-bottom: 20px;
        }}
        .univ-title {{
            font-size: 18px;
            font-weight: 800;
            color: #0284C7;
            text-transform: uppercase;
        }}
        .dossier-tag {{
            font-size: 12px;
            font-weight: 700;
            color: #64748B;
        }}
        .author-box {{
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 20px;
        }}
        .author-name {{
            font-size: 24px;
            font-weight: 800;
            color: #0F172A;
            margin: 0 0 4px 0;
        }}
        .author-dept {{
            font-size: 14px;
            color: #0284C7;
            font-weight: 600;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            margin-bottom: 20px;
        }}
        .kpi-chip {{
            background: #F1F5F9;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        .kpi-val {{
            font-size: 20px;
            font-weight: 800;
            color: #0284C7;
        }}
        .kpi-lbl {{
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            color: #475569;
            margin-top: 2px;
        }}
        .badges-row {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        .badge {{
            background: #E0F2FE;
            color: #0369A1;
            border: 1px solid #BAE6FD;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
            margin-top: 10px;
        }}
        th, td {{
            padding: 8px 10px;
            border: 1px solid #E2E8F0;
            text-align: left;
        }}
        th {{
            background: #0284C7;
            color: #FFFFFF;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 11px;
        }}
        tr:nth-child(even) {{
            background: #F8FAFC;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 10px;
            border-top: 1px solid #E2E8F0;
            font-size: 11px;
            color: #94A3B8;
            display: flex;
            justify-content: space-between;
        }}
        @media print {{
            body {{ padding: 0; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <div class="univ-title">Kavayitri Bahinabai Chaudhari North Maharashtra University</div>
            <div class="dossier-tag">ICARE Live Scopus Intelligence Dossier • IR-O-U-0320</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 14px; font-weight: 800; color: #0284C7;">SCOPUS PROFILE</div>
            <div style="font-size: 10px; color: #64748B;">Generated: {generated_date}</div>
        </div>
    </div>

    <div class="author-box">
        <h1 class="author-name">👨‍🏫 {author_name}</h1>
        <div class="author-dept">🏛️ {department} &nbsp;|&nbsp; 📖 Top Journal: {top_journal}</div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-chip">
            <div class="kpi-val">{total_papers}</div>
            <div class="kpi-lbl">Publications</div>
        </div>
        <div class="kpi-chip">
            <div class="kpi-val">{total_citations:,}</div>
            <div class="kpi-lbl">Citations</div>
        </div>
        <div class="kpi-chip">
            <div class="kpi-val">{cpp}</div>
            <div class="kpi-lbl">CPP</div>
        </div>
        <div class="kpi-chip">
            <div class="kpi-val">{h_index}</div>
            <div class="kpi-lbl">h-Index</div>
        </div>
        <div class="kpi-chip">
            <div class="kpi-val">{q1_ratio}%</div>
            <div class="kpi-lbl">Q1 Ratio</div>
        </div>
    </div>

    <div class="badges-row">
        <span class="badge">⭐ Q1 Papers: {q1_papers}</span>
        <span class="badge">🌐 International Collab: {intl_pct}%</span>
        <span class="badge">🏢 Industry Collab: {industry_pct}%</span>
        <span class="badge">👥 Unique Co-Authors: {coauthors_count}</span>
    </div>

    <h3>📜 Complete Scopus Indexed Publications ({total_papers})</h3>
    <table>
        <thead>
            <tr>
                <th style="width: 55px;">Year</th>
                <th>Publication Title</th>
                <th>Journal</th>
                <th style="width: 50px; text-align: center;">Quartile</th>
                <th style="width: 55px; text-align: center;">Cites</th>
                <th style="width: 140px;">DOI</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <div class="footer">
        <span>KBCNMU Scopus Intelligence Portal • Jalgaon, Maharashtra</span>
        <span>Official Verification Record</span>
    </div>
</body>
</html>
"""
    return html



def filter_publications(
    df: pd.DataFrame,
    year_range: Tuple[int, int] = None,
    depts: List[str] = None,
    quartiles: List[str] = None,
    collab_types: List[str] = None,
) -> pd.DataFrame:
    """
    Multi-dimensional filtering helper for KBCNMU publication dataset.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    filtered = df.copy()

    # 1. Year Range Filter
    if year_range and len(year_range) == 2:
        filtered = filtered[(filtered["year"] >= year_range[0]) & (filtered["year"] <= year_range[1])]

    # 2. Department Filter
    if depts:
        filtered = filtered[filtered["department"].isin(depts)]

    # 3. Quartile Filter
    if quartiles:
        filtered = filtered[filtered["quartile"].isin(quartiles)]

    # 4. Collaboration Filter
    if collab_types:
        conditions = []
        if "International" in collab_types:
            conditions.append(filtered["is_international_collab"] == True)
        if "Industry" in collab_types:
            conditions.append(filtered["is_industry_collab"] == True)
        if "National" in collab_types:
            conditions.append(
                (filtered["is_international_collab"] == False) & (filtered["is_industry_collab"] == False)
            )

        if conditions:
            combined_mask = pd.concat(conditions, axis=1).any(axis=1)
            filtered = filtered[combined_mask]

    return filtered


def export_to_bibtex(df: pd.DataFrame) -> str:
    """
    Generate valid BibTeX entries formatted string for all papers in DataFrame.
    """
    if df is None or df.empty:
        return "% No publications available to export."

    bibtex_entries = []

    for idx, row in df.iterrows():
        scopus_id = str(row.get("scopus_id", f"paper_{idx}"))
        title = str(row.get("title", "Untitled")).replace("{", "").replace("}", "")
        authors = str(row.get("authors", "Author, A."))
        journal = str(row.get("journal", "Journal"))
        year = str(row.get("year", "2026"))
        doi = str(row.get("doi", ""))

        bib_entry = f"""@article{{kbcnmu_{scopus_id},
  author    = {{{authors}}},
  title     = {{{title}}},
  journal   = {{{journal}}},
  year      = {{{year}}},
  doi       = {{{doi}}}
}}"""
        bibtex_entries.append(bib_entry)

    return "\n\n".join(bibtex_entries)


if __name__ == "__main__":
    from mock_data import generate_kbcnmu_mock_data

    raw_data = generate_kbcnmu_mock_data(100)
    df_sample = pd.DataFrame(raw_data)

    kpis = calculate_top_10_kpis(df_sample)
    print("Calculated KPIs Sample:", kpis)

    leaderboard = get_top_authors_leaderboard(df_sample, top_n=5)
    print("Top 5 Authors Leaderboard:\n", leaderboard)

    bib_sample = export_to_bibtex(df_sample.head(2))
    print("BibTeX Sample:\n", bib_sample)
