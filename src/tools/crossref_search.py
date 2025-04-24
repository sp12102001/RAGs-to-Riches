"""
Academic search tool using the CrossRef API
"""

import requests
from typing import List, Dict, Optional
from agents import function_tool  # type: ignore

from src.utils.cache import load_from_cache, save_to_cache
from src.utils.formatting import safe_str

@function_tool
def crossref_search(query: str, filter_type: Optional[str], rows: int) -> List[Dict]:
    """
    Search for academic publications using the CrossRef API.

    Args:
        query: Search term or phrase
        filter_type: Filter by type (journal-article, book, conference-paper, etc.)
        rows: Maximum number of results to return

    Returns a list of publications with title, DOI, author, and publication details.
    """
    # Check cache first
    cache_key = f"{query}_{filter_type}_{rows}"
    cached_results = load_from_cache("crossref", cache_key)
    if cached_results:
        return cached_results

    # Base URL for CrossRef API
    base_url = "https://api.crossref.org/works"

    # Build parameters
    params = {
        "query": query,
        "rows": rows,
        "sort": "relevance",
        "order": "desc",
    }

    # Add filter if specified
    if filter_type:
        params["filter"] = f"type:{filter_type}"

    # Make the request
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("message", {}).get("items", []):
            # Extract authors
            authors = []
            for author in item.get("author", []):
                name_parts = []
                if "given" in author:
                    name_parts.append(safe_str(author["given"]))
                if "family" in author:
                    name_parts.append(safe_str(author["family"]))
                if name_parts:
                    authors.append(" ".join(name_parts))

            authors_str = ", ".join(authors[:3])
            if len(authors) > 3:
                authors_str += f" and {len(authors) - 3} more"

            # Extract publication details
            pub_date = ""
            date_parts = []
            if "published-print" in item and item["published-print"].get("date-parts"):
                date_parts = item["published-print"]["date-parts"][0]
            elif "published-online" in item and item["published-online"].get("date-parts"):
                date_parts = item["published-online"]["date-parts"][0]

            if date_parts:
                pub_date = "-".join([safe_str(part) for part in date_parts])

            # Extract journal/publisher
            container = ""
            if item.get("container-title") and item["container-title"]:
                container = safe_str(item["container-title"][0])

            publisher = safe_str(item.get("publisher"))

            # Get title
            title = ""
            if item.get("title") and item["title"]:
                title = safe_str(item["title"][0])

            # Get DOI URL
            url = ""
            if "DOI" in item:
                url = f"https://doi.org/{item['DOI']}"

            # Format snippet from abstract or title
            snippet = safe_str(item.get("abstract"))
            if not snippet:
                if container:
                    snippet = f"Published in {container}"
                elif publisher:
                    snippet = f"Published by {publisher}"
                else:
                    snippet = ""

            result = {
                "title": title,
                "url": url,
                "snippet": snippet,
                "authors": authors_str,
                "publication_date": pub_date,
                "journal": container,
                "publisher": publisher,
                "source": "CrossRef"
            }

            results.append(result)

        # Save to cache
        save_to_cache("crossref", cache_key, results)
        return results

    except Exception as e:
        return [{"title": "Search Error", "url": "", "snippet": f"Error performing CrossRef search: {str(e)}", "source": "Error"}]