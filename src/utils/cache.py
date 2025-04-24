"""
Cache utilities for storing and retrieving search results
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path

# Create a cache directory
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_path(tool_name: str, query: str) -> Path:
    """Generate a unique cache file path based on tool name and query"""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    return CACHE_DIR / f"{tool_name}_{query_hash}.json"

def load_from_cache(tool_name: str, query: str) -> Optional[List[Dict]]:
    """Load cached results if available"""
    cache_path = get_cache_path(tool_name, query)
    if cache_path.exists():
        try:
            with open(cache_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    return None

def save_to_cache(tool_name: str, query: str, results: List[Dict]) -> None:
    """Save results to cache"""
    cache_path = get_cache_path(tool_name, query)
    try:
        with open(cache_path, "w") as f:
            json.dump(results, f)
    except IOError:
        pass  # Fail silently if cache can't be written

def clear_cache() -> int:
    """Clear all cached search results

    Returns:
        int: Number of cache files deleted
    """
    count = 0
    if CACHE_DIR.exists():
        for cache_file in CACHE_DIR.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except:
                pass
    return count