"""
Academic search tool using the OpenAlex API
"""

import os
import requests
from typing import List, Dict, Optional
from agents import function_tool  # type: ignore

from src.utils.cache import load_from_cache, save_to_cache
from src.utils.formatting import safe_str

@function_tool
def openalex_search(query: str, exact_phrase: bool, filter_field: Optional[str], max_results: int) -> List[Dict]:
    """
    Search academic literature using the OpenAlex API.

    Args:
        query: Search term or query
        exact_phrase: Whether to search for the exact phrase (wrap in quotes)
        filter_field: Specific field to search (title, abstract, etc.)
        max_results: Maximum number of results to return

    Returns a list of academic works matching the query with title, URL, authors, and abstract.
    """
    # Check cache first
    cache_key = f"{query}_{exact_phrase}_{filter_field}"
    cached_results = load_from_cache("openalex", cache_key)
    if cached_results:
        return cached_results

    # Format the query based on parameters
    if exact_phrase:
        formatted_query = f'"{query}"'
    else:
        formatted_query = query

    # Base URL for OpenAlex API
    base_url = "https://api.openalex.org/works"

    # Construct the appropriate URL based on filter field
    if filter_field is not None:
        url = f"{base_url}?filter={filter_field}.search:{formatted_query}"
    else:
        url = f"{base_url}?search={formatted_query}"

    # Add per_page parameter to limit results
    url += f"&per_page={max_results}"

    # Add email for polite usage if available
    email = os.getenv("OPENALEX_EMAIL", "")
    if email and email.strip():
        url += f"&mailto={email}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Process results
        results = []
        for work in data.get("results", []):
            # Extract author names
            authors = []
            for authorship in work.get("authorships", []):
                if authorship.get("author") and authorship["author"].get("display_name"):
                    authors.append(safe_str(authorship["author"]["display_name"]))

            authors_str = ", ".join(authors[:3])
            if len(authors) > 3:
                authors_str += f" and {len(authors) - 3} more"

            # Get DOI or landing page URL
            url = ""
            if work.get("doi"):
                url = f"https://doi.org/{work['doi']}"
            elif work.get("primary_location") and work["primary_location"].get("landing_page_url"):
                url = safe_str(work["primary_location"]["landing_page_url"])

            # Get title
            title = safe_str(work.get("title"))

            # Process abstract
            snippet = "No abstract available"
            abstract_data = work.get("abstract_inverted_index")
            if isinstance(abstract_data, dict):
                try:
                    # OpenAlex stores abstracts as inverted indices, need to reconstruct
                    abstract_words = []
                    for word, positions in abstract_data.items():
                        for position in positions:
                            while len(abstract_words) <= position:
                                abstract_words.append("")
                            abstract_words[position] = word
                    snippet = " ".join(abstract_words)
                except:
                    snippet = "Abstract available but could not be processed"

            # Format publication date
            pub_date = safe_str(work.get("publication_date"))

            # Create result
            result = {
                "title": title,
                "url": url,
                "snippet": snippet,
                "publication_date": pub_date,
                "authors": authors_str,
                "source": "OpenAlex"
            }

            results.append(result)

        # Save to cache
        save_to_cache("openalex", cache_key, results)
        return results

    except Exception as e:
        return [{"title": "Search Error", "url": "", "snippet": f"Error performing OpenAlex search: {str(e)}", "source": "Error"}]