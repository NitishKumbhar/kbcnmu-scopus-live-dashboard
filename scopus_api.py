"""
scopus_api.py
Handles connecting to Elsevier Scopus Search API using cursor pagination,
extracting structured publication metrics for KBCNMU, caching results locally,
and implementing auto-sync / fallback logic.
"""

import json
import os
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

from config import UNIVERSITY_CONFIG
from mock_data import generate_kbcnmu_mock_data

# Load environment variables (.env file)
load_dotenv()

BASE_URL = "https://api.elsevier.com/content/search/scopus"


def get_api_key() -> str:
    """Retrieve cleaned Scopus API Key from environment."""
    key = os.getenv("SCOPUS_API_KEY", "").strip()
    # Strip quotes if present
    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
        key = key[1:-1].strip()
    return key


def infer_department_from_entry(entry: dict) -> str:
    """Infer academic department based on subject area, title, or journal."""
    title = str(entry.get("dc:title", "")).lower()
    journal = str(entry.get("prism:publicationName", "")).lower()

    if any(k in title or k in journal for k in ["chem", "synth", "cataly", "spectro", "molecule", "polymer"]):
        return "School of Chemical Sciences"
    elif any(k in title or k in journal for k in ["bio", "microbiol", "ferment", "enzyme", "genom", "pathog"]):
        return "School of Life Sciences"
    elif any(k in title or k in journal for k in ["phys", "nanopart", "thin film", "optics", "semicond", "actuat"]):
        return "School of Physical Sciences"
    elif any(k in title or k in journal for k in ["math", "statist", "queue", "fuzz", "algebra"]):
        return "School of Mathematical Sciences"
    elif any(k in title or k in journal for k in ["comput", "ieee", "image", "algorithm", "data", "deep learn"]):
        return "School of Computer Sciences"
    elif any(k in title or k in journal for k in ["environ", "water", "pollut", "earth", "geol", "atmos"]):
        return "School of Environmental & Earth Sciences"
    elif any(k in title or k in journal for k in ["engin", "react", "desalin", "process"]):
        return "School of Engineering & Technology"
    elif any(k in title or k in journal for k in ["pharm", "drug", "medic", "delivery"]):
        return "School of Pharmacy"
    elif any(k in title or k in journal for k in ["manag", "business", "econom", "supply chain"]):
        return "School of Management Studies"
    elif any(k in title or k in journal for k in ["social", "politic", "society", "humani"]):
        return "School of Social Sciences"
    return "School of Chemical Sciences"  # Default fallback


def parse_scopus_entry(entry: dict) -> dict:
    """Extract and normalize all required fields from a single Scopus API result entry."""
    scopus_id = str(entry.get("dc:identifier", "")).replace("SCOPUS_ID:", "").strip()
    title = entry.get("dc:title", "Untitled Publication").strip()

    # Extract Authors
    author_list = entry.get("author", [])
    authors = []
    if isinstance(author_list, list) and author_list:
        for a in author_list:
            given = a.get("given-name", "")
            surname = a.get("surname", a.get("authname", ""))
            name = f"{given} {surname}".strip() if given else surname
            if name:
                authors.append(name)
    elif entry.get("dc:creator"):
        authors.append(entry.get("dc:creator"))

    authors_str = ", ".join(authors) if authors else "KBCNMU Researcher"
    primary_author = authors[0] if authors else "KBCNMU Researcher"

    # Journal & Cover Date
    journal = entry.get("prism:publicationName", "Unknown Journal").strip()
    cover_date = entry.get("prism:coverDate", "")
    year = int(cover_date[:4]) if cover_date and len(cover_date) >= 4 and cover_date[:4].isdigit() else datetime.now().year

    # Citations
    cited_count = entry.get("citedby-count", 0)
    try:
        citations = int(cited_count)
    except (ValueError, TypeError):
        citations = 0

    # Affiliations & Collaborations
    affiliations = entry.get("affiliation", [])
    countries = set(["India"])
    is_industry = False

    if isinstance(affiliations, list):
        for aff in affiliations:
            c = aff.get("affiliation-country")
            if c and c.strip().lower() != "india":
                countries.add(c.strip())
            aff_name = str(aff.get("affilname", "")).lower()
            if any(ind in aff_name for ind in ["ltd", "inc", "corp", "pharma", "gmbh", "r&d", "industr"]):
                is_industry = True

    is_international = len(countries) > 1
    doi = entry.get("prism:doi", "")
    dept = infer_department_from_entry(entry)

    # Metrics heuristics (CiteScore, SJR, Quartile)
    citescore = round(max(0.5, (citations / max(1, 2026 - year)) * 1.2), 2)
    sjr = round(max(0.15, citescore * 0.18), 2)

    if citescore >= 6.0 or citations > 35:
        quartile = "Q1"
    elif citescore >= 3.5 or citations > 15:
        quartile = "Q2"
    elif citescore >= 1.8 or citations > 5:
        quartile = "Q3"
    else:
        quartile = "Q4"

    return {
        "scopus_id": scopus_id,
        "title": title,
        "authors": authors_str,
        "primary_author": primary_author,
        "department": dept,
        "journal": journal,
        "year": year,
        "citations": citations,
        "citescore": citescore,
        "sjr": sjr,
        "quartile": quartile,
        "doi": doi,
        "is_international_collab": is_international,
        "is_industry_collab": is_industry,
        "countries": list(countries),
    }


def fetch_from_scopus_api() -> list:
    """
    Fetch all publications from Scopus Search API using cursor pagination (`cursor=*`).
    """
    api_key = get_api_key()
    if not api_key:
        print("[Scopus API] No API Key provided in .env. Falling back to mock data.")
        return []

    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json",
    }

    query = UNIVERSITY_CONFIG["scopus_query"]
    cursor = "*"
    count = 25  # Scopus standard batch size
    all_publications = []

    print(f"[Scopus API] Initiating search query: {query[:80]}...")

    while True:
        params = {
            "query": query,
            "count": count,
            "cursor": cursor,
            "view": "STANDARD",
        }

        try:
            response = requests.get(BASE_URL, headers=headers, params=params, timeout=15)

            if response.status_code != 200:
                print(f"[Scopus API Warning] Cursor fetch returned status {response.status_code}. Retrying with offset pagination...")
                return fetch_from_scopus_api_offset(query, headers)

            data = response.json()
            search_results = data.get("search-results", {})
            entries = search_results.get("entry", [])

            if not entries or (len(entries) == 1 and "error" in entries[0]):
                break

            for entry in entries:
                parsed = parse_scopus_entry(entry)
                all_publications.append(parsed)

            # Cursor pagination next link
            next_cursor = None
            for link in search_results.get("link", []):
                if link.get("@ref") == "next":
                    # Extract cursor parameter from URL or search-results cursor object
                    next_cursor = search_results.get("cursor", {}).get("@next")
                    break

            if not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor

            # Safety cap to avoid infinite loops during initial tests
            if len(all_publications) >= 5000:
                break

            time.sleep(0.2)  # Respect API rate limits

        except Exception as e:
            print(f"[Scopus API Exception] {e}")
            break

    print(f"[Scopus API] Total documents fetched via cursor: {len(all_publications)}")
    return all_publications


def fetch_from_scopus_api_offset(query: str, headers: dict) -> list:
    """Fallback offset-based pagination (`start=0`, `start=25`, ...) when cursor entitlement is restricted."""
    all_publications = []
    start = 0
    count = 25

    print(f"[Scopus API Offset] Fetching with offset pagination...")

    while True:
        params = {
            "query": query,
            "count": count,
            "start": start,
            "view": "STANDARD",
        }

        try:
            response = requests.get(BASE_URL, headers=headers, params=params, timeout=15)

            if response.status_code != 200:
                print(f"[Scopus API Offset Error] Status {response.status_code}: {response.text[:200]}")
                break

            data = response.json()
            search_results = data.get("search-results", {})
            entries = search_results.get("entry", [])

            if not entries or (len(entries) == 1 and "error" in entries[0]):
                break

            for entry in entries:
                parsed = parse_scopus_entry(entry)
                all_publications.append(parsed)

            total_results = int(search_results.get("opensearch:totalResults", 0))
            start += count

            if start >= total_results or start >= 5000 or len(entries) < count:
                break

            time.sleep(0.2)

        except Exception as e:
            print(f"[Scopus API Offset Exception] {e}")
            break

    print(f"[Scopus API Offset] Total documents fetched: {len(all_publications)}")
    return all_publications



def save_cache(publications: list, cache_file: str = None) -> dict:
    """Save publications to JSON cache file with timestamp metadata."""
    if not cache_file:
        cache_file = UNIVERSITY_CONFIG["cache_file"]

    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    cache_data = {
        "last_synced": time.time(),
        "last_synced_readable": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_count": len(publications),
        "publications": publications,
    }

    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2, ensure_ascii=False)

    print(f"[Cache] Saved {len(publications)} records to {cache_file}")
    return cache_data


def load_scopus_data(force_refresh: bool = False) -> dict:
    """
    Auto-Sync Logic: Check cache timestamp; if older than cache_ttl_seconds (3600s)
    or if manual refresh is triggered, perform sync with Scopus API.
    Falls back to mock benchmark data (~2,500 records) if API is unavailable.
    """
    cache_file = UNIVERSITY_CONFIG["cache_file"]
    ttl = UNIVERSITY_CONFIG.get("cache_ttl_seconds", 3600)

    # 1. Check if valid cache exists
    if os.path.exists(cache_file) and not force_refresh:
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache_data = json.load(f)

            last_synced = cache_data.get("last_synced", 0)
            age = time.time() - last_synced

            if age < ttl and cache_data.get("publications"):
                print(f"[Cache] Returning cached data ({len(cache_data['publications'])} items, age {int(age)}s).")
                cache_data["is_live_scopus"] = False
                cache_data["is_from_cache"] = True
                return cache_data
        except Exception as e:
            print(f"[Cache Warning] Error reading cache file: {e}")

    # 2. Attempt live Scopus API fetch
    print("[Sync] Attempting live Scopus API fetch...")
    live_pubs = fetch_from_scopus_api()

    if live_pubs:
        cache_data = save_cache(live_pubs, cache_file)
        cache_data["is_live_scopus"] = True
        cache_data["is_from_cache"] = False
        return cache_data

    # 3. Fallback to mock data generator if API call produced no results
    print("[Fallback] Generating ~2,500 benchmark publications for KBCNMU offline mode...")
    mock_pubs = generate_kbcnmu_mock_data(2500)
    cache_data = save_cache(mock_pubs, cache_file)
    cache_data["is_live_scopus"] = False
    cache_data["is_from_cache"] = False
    cache_data["is_mock_fallback"] = True
    return cache_data


if __name__ == "__main__":
    data = load_scopus_data(force_refresh=True)
    print(f"Loaded {data.get('total_count')} records. Last synced: {data.get('last_synced_readable')}")
