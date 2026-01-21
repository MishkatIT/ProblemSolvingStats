#!/usr/bin/env python3
"""
Shared utility functions used across the application.
"""

import re
from datetime import datetime
from src import (
    USER_CONFIG, PLATFORM_URL_TEMPLATES, BDT_TIMEZONE,
    PLATFORM_LOGOS, PLATFORM_COLORS
)


def get_profile_url(platform):
    """Generate profile URL for a platform using username from config.
    
    Args:
        platform: Platform name
        
    Returns:
        Profile URL string or '#' if not found
    """
    template = PLATFORM_URL_TEMPLATES.get(platform)
    username = USER_CONFIG.get(platform)
    if template and username:
        return template.format(username=username)
    return '#'


def get_current_bdt_date():
    """Get current date in BDT timezone.
    
    Returns:
        Tuple of (formatted_date, date_with_time, iso_date)
    """
    now = datetime.now(BDT_TIMEZONE)
    current_date = now.strftime("%d %B %Y")
    current_date_with_time = now.strftime("%d %B %Y at %I:%M:%S %p")
    today_iso = now.strftime('%Y-%m-%d')
    return current_date, current_date_with_time, today_iso


def format_human_date(date_str):
    """Convert an ISO date (YYYY-MM-DD) to a human-readable date.
    
    Args:
        date_str: ISO date string
        
    Returns:
        Human-readable date string or original if parsing fails
    """
    if not date_str or date_str == 'unknown':
        return 'unknown'
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %B %Y')
    except Exception:
        return date_str


def extract_first_int(text):
    """Extract the first integer from text.
    
    Args:
        text: Text to search
        
    Returns:
        First integer found or None
    """
    match = re.search(r'\d+', text or '')
    return int(match.group(0)) if match else None


def calculate_percentage(solved, total):
    """Calculate percentage for progress bar.
    
    Args:
        solved: Number of problems solved
        total: Total number of problems
        
    Returns:
        Percentage as float
    """
    if total == 0:
        return 0.0
    return round((solved / total) * 100, 1)


def calculate_total(stats):
    """Calculate total solved problems.
    
    Args:
        stats: Dictionary of platform stats
        
    Returns:
        Total count as integer
    """
    total = 0
    for count in stats.values():
        if count is not None and isinstance(count, int):
            total += count
    return total


def format_platform_list(platforms):
    """Format a list of platforms into a human-readable string.
    
    Args:
        platforms: List of platform names (should be sorted)
        
    Returns:
        Formatted string (e.g., "Platform1", "Platform1 and Platform2", 
        "Platform1, Platform2, and Platform3")
    """
    if not platforms:
        return "**No platforms**"
    elif len(platforms) == 1:
        return f"**{platforms[0]}**"
    elif len(platforms) == 2:
        return f"**{platforms[0]}** and **{platforms[1]}**"
    else:
        formatted_list = ", ".join([f"**{p}**" for p in platforms[:-1]])
        return f"{formatted_list}, and **{platforms[-1]}**"


def read_text_file(path):
    """Read a text file using UTF-8 (with BOM support).
    
    On Windows, the default encoding can be cp1252 which may fail for UTF-8 files.
    
    Args:
        path: Path to text file
        
    Returns:
        File contents as string
    """
    for encoding in ('utf-8', 'utf-8-sig'):
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # Last resort: replace undecodable bytes
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def get_platform_badge_info(platform):
    """Get badge information for a platform.
    
    Args:
        platform: Platform name
        
    Returns:
        Tuple of (logo_url, use_onerror, color)
    """
    logo_url, use_onerror = PLATFORM_LOGOS.get(platform, ('', False))
    color = PLATFORM_COLORS.get(platform, 'blue')
    return logo_url, use_onerror, color
