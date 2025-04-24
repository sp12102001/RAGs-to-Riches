"""
Web search tool using DuckDuckGo
"""

from typing import List, Dict
from duckduckgo_search import DDGS  # type: ignore
from agents import function_tool  # type: ignore

from src.utils.cache import load_from_cache, save_to_cache
from src.utils.formatting import safe_str

@function_tool
def web_search(query: str, max_results: int) -> List[Dict]:
    """
    Search the web for the given query using DuckDuckGo and return a list of results.
    Each result is a dict with 'title', 'url', and 'snippet'.

    Args:
        query: Search term or phrase
        max_results: Maximum number of results to return
    """
    # Check cache first
    cached_results = load_from_cache("web_search", query)
    if cached_results:
        return cached_results

    # If not in cache, perform search
    try:
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results)) or []

        formatted_results = []
        for r in raw_results:
            formatted_results.append({
                "title": safe_str(r.get("title")),
                "url": safe_str(r.get("href")),
                "snippet": safe_str(r.get("body")),
                "source": "DuckDuckGo"
            })

        # Save to cache
        save_to_cache("web_search", query, formatted_results)
        return formatted_results
    except Exception as e:
        return [{"title": "Search Error", "url": "", "snippet": f"Error performing web search: {str(e)}", "source": "Error"}]