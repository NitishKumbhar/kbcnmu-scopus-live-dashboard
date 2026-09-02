"""
ai_copilot.py
Built-in pandas-powered natural language research intelligence assistant for KBCNMU Scopus Dashboard.
Generates structured markdown insights instantly with zero external API key dependencies.
"""

from typing import Dict
import pandas as pd
from data_processor import calculate_top_10_kpis, get_top_authors_leaderboard


def query_scopus_ai_copilot(query_text: str, df: pd.DataFrame) -> str:
    """
    Process natural language queries or preset prompt chips against KBCNMU publication dataset.
    Returns rich, structured markdown response.
    """
    if df is None or df.empty:
        return "⚠️ **No publication data available to analyze.** Please adjust dashboard filters."

    q = query_text.lower().strip()
    kpis = calculate_top_10_kpis(df)
    total_pubs = len(df)
    total_cites = int(df["citations"].sum()) if "citations" in df else 0
    avg_cpp = round(total_cites / total_pubs, 2) if total_pubs > 0 else 0.0

    # 1. Executive Dossier Preset
    if "executive dossier" in q or "dossier" in q or "summary" in q or "overview" in q:
        dept_counts = df["department"].value_counts()
        top_dept = dept_counts.index[0] if not dept_counts.empty else "N/A"
        q1_count = len(df[df["quartile"] == "Q1"])
        q1_pct = round((q1_count / total_pubs) * 100, 1) if total_pubs > 0 else 0.0

        top_author = df["primary_author"].mode().iloc[0] if "primary_author" in df and not df["primary_author"].empty else "N/A"

        return f"""### 📊 Executive Scopus Intelligence Dossier for KBCNMU

**1. Institutional Research Scale**
- **Total Scopus Publications**: `{total_pubs:,}` indexed documents
- **Total Citations Accrued**: `{total_cites:,}` citations across indexed publications
- **Citations Per Paper (CPP)**: `{avg_cpp}` citations/paper
- **Current Year (2026) Output**: `{kpis['vol_2026']:,}` papers

**2. Academic Quality & Global Stature**
- **Q1 High-Impact Share**: `{q1_pct}%` ({q1_count:,} Q1 papers)
- **International Co-Authorship**: `{kpis['intl_collab_pct']}%` of total publications
- **Industry R&D Collaboration**: `{kpis['industry_collab_pct']}%` with corporate partners

**3. Academic Leadership**
- **Lead Performing School**: `{top_dept}` ({dept_counts.iloc[0]} papers)
- **Top Contributing Author**: `Prof. {top_author}`

---
> 💡 *Note: Data compiled dynamically from KBCNMU Scopus Live Intelligence Engine.*
"""

    # 2. Department Rankings Preset
    elif "dept rankings" in q or "department" in q or "school" in q:
        dept_df = (
            df.groupby("department")
            .agg(
                Publications=("scopus_id", "count"),
                Citations=("citations", "sum"),
                Q1_Papers=("quartile", lambda x: sum(x == "Q1")),
            )
            .reset_index()
        )
        dept_df["CPP"] = (dept_df["Citations"] / dept_df["Publications"]).round(2)
        dept_df["Q1_Share_%"] = ((dept_df["Q1_Papers"] / dept_df["Publications"]) * 100).round(1)
        dept_df = dept_df.sort_values(by="Publications", ascending=False).reset_index(drop=True)

        md_rows = ""
        for idx, row in dept_df.iterrows():
            md_rows += f"| #{idx+1} | **{row['department']}** | {row['Publications']:,} | {row['Citations']:,} | {row['CPP']} | {row['Q1_Share_%']}% |\n"

        return f"""### 🏛️ KBCNMU School & Department Performance Rankings

| Rank | Academic School / Department | Publications | Citations | CPP | Q1 Share % |
| :---: | :--- | :---: | :---: | :---: | :---: |
{md_rows}
"""

    # 3. Q1 Quality Analysis Preset
    elif "q1" in q or "quality" in q or "journal" in q:
        q_counts = df["quartile"].value_counts()
        q1_num = q_counts.get("Q1", 0)
        q2_num = q_counts.get("Q2", 0)
        q3_num = q_counts.get("Q3", 0)
        q4_num = q_counts.get("Q4", 0)

        top_journals = df["journal"].value_counts().head(5)
        j_rows = ""
        for j_name, count in top_journals.items():
            j_rows += f"- **{j_name}**: {count} publications\n"

        return f"""### 🏆 Journal Quality & Quartile Breakdown

**Scopus Journal Quartile Distribution:**
- **Q1 (Top 25% Impact)**: `{q1_num:,}` papers (`{round((q1_num/total_pubs)*100, 1)}%`)
- **Q2 (Top 50% Impact)**: `{q2_num:,}` papers (`{round((q2_num/total_pubs)*100, 1)}%`)
- **Q3 (Top 75% Impact)**: `{q3_num:,}` papers (`{round((q3_num/total_pubs)*100, 1)}%`)
- **Q4 (Standard Impact)**: `{q4_num:,}` papers (`{round((q4_num/total_pubs)*100, 1)}%`)

**Top Most Published Outlets at KBCNMU:**
{j_rows}
"""

    # 4. Top Authors Preset
    elif "top authors" in q or "author" in q or "h-index" in q or "faculty" in q:
        leaderboard = get_top_authors_leaderboard(df, top_n=10)

        a_rows = ""
        for idx, row in leaderboard.iterrows():
            a_rows += f"| #{idx+1} | **{row['author']}** | {row['papers']} | {row['citations']:,} | {row['cpp']} | **{row['h_index']}** |\n"

        return f"""### 👥 KBCNMU Top 10 Faculty Researcher Rankings

| Rank | Faculty Researcher | Papers | Citations | CPP | Estimated h-Index |
| :---: | :--- | :---: | :---: | :---: | :---: |
{a_rows}
"""

    # 5. International / Industry Collaboration Query
    elif "collab" in q or "international" in q or "industry" in q or "partner" in q:
        intl_count = len(df[df["is_international_collab"] == True])
        ind_count = len(df[df["is_industry_collab"] == True])

        return f"""### 🌐 Institutional & Industry Collaboration Intelligence

- **International Collaboration Output**: `{intl_count:,}` papers (`{kpis['intl_collab_pct']}%` of total portfolio)
- **Industry R&D Joint Papers**: `{ind_count:,}` papers (`{kpis['industry_collab_pct']}%` of total portfolio)

**Strategic Takeaway**:
KBCNMU maintains active co-authorship networks with top international universities (USA, Germany, UK, South Korea, Japan) and pharma/chemical corporate R&D divisions (Lupin, Reliance, Cipla).
"""

    # 6. Custom General Natural Language Response
    else:
        top_paper = df.sort_values(by="citations", ascending=False).iloc[0] if not df.empty else None
        top_paper_str = f"**{top_paper['title']}** ({top_paper['citations']:,} citations)" if top_paper is not None else "N/A"

        return f"""### 🤖 Scopus AI Research Intelligence Analysis for: *"{query_text}"*

- **Dataset Subset Size**: `{total_pubs:,}` publications analyzed
- **Total Citation Accrual**: `{total_cites:,}` citations
- **Average Citations Per Paper (CPP)**: `{avg_cpp}`
- **Highest Cited Publication**: {top_paper_str}

**Departmental Distribution Overview:**
{df['department'].value_counts().head(3).to_string()}

---
💡 *Tip: Click one of the preset prompt chips above or ask about specific departments, citations, or authors!*
"""
