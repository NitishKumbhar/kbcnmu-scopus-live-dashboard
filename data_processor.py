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
    top_journal = author_df["journal"].mode().iloc[0] if not author_df["journal"].empty else "N/A"

    recent_papers = author_df.sort_values(by=["year", "citations"], ascending=False).head(10)

    return {
        "author_name": author_name,
        "total_papers": total_papers,
        "total_citations": total_citations,
        "h_index": h_idx,
        "cpp": cpp,
        "q1_papers": q1_papers,
        "top_journal": top_journal,
        "recent_papers": recent_papers,
    }


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
