"""
Text formatting utilities for handling strings and output formatting
"""

import re
import datetime
from typing import Any, Optional

def safe_str(value: Any) -> str:
    """Safely convert any value to string, handling None values"""
    if value is None:
        return ""
    return str(value)

def sanitize_filename(text: str, max_length: int = 50) -> str:
    """
    Convert a string to a safe filename by replacing non-alphanumeric characters

    Args:
        text: Text to sanitize
        max_length: Maximum length for the resulting filename

    Returns:
        Sanitized filename string
    """
    # Replace non-alphanumeric characters with underscores
    sanitized = "".join(c if c.isalnum() else "_" for c in text)
    # Limit length
    return sanitized[:max_length]

def get_timestamp() -> str:
    """Get the current timestamp in a format suitable for filenames"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def get_formatted_time() -> str:
    """Get the current time in a human-readable format"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_formatted_duration(seconds: float) -> str:
    """Format a duration in seconds to a readable string"""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes} minutes and {remaining_seconds:.2f} seconds"