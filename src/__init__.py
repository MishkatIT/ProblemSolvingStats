#!/usr/bin/env python
"""
src package - Shared modules for Problem Solving Statistics application.
"""

import json
from datetime import timezone, timedelta
import os

# Load config from JSON - find it relative to this file
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Warning: Could not load config.json: {e}. Using default config.")
    config = {}

# Load config with error handling for missing sections
def get_config_with_fallback(key, default, description=""):
    """Get config value with fallback and automatic addition for missing keys."""
    if key not in config:
        print(f"INFO: '{key}' section missing from config.json. Adding it with default value...")
        if description:
            print(f"   {description}")
        
        # Add the missing section to config and save it
        config[key] = default
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"   [OK] Added '{key}' section to config.json")
        except Exception as e:
            print(f"   [ERROR] Failed to save config.json: {e}")
    
    return config.get(key, default)

GITHUB_USERINFO = get_config_with_fallback('GITHUB_USERINFO', {'name': 'Unknown', 'email': 'unknown@example.com', 'username': 'unknown'}, "GitHub user information (name, email, username)")
USER_CONFIG = get_config_with_fallback('USER_CONFIG', {}, "Platform usernames configuration")
PROFILE_DISPLAY_NAMES = get_config_with_fallback('PROFILE_DISPLAY_NAMES', {}, "Display names for platforms")
PLATFORM_URL_TEMPLATES = get_config_with_fallback('PLATFORM_URL_TEMPLATES', {}, "URL templates for platforms")
PLATFORM_LOGOS = get_config_with_fallback('PLATFORM_LOGOS', {}, "Logo URLs for platforms")
PLATFORM_COLORS = get_config_with_fallback('PLATFORM_COLORS', [], "Color codes for platforms")
ALL_PLATFORMS = get_config_with_fallback('ALL_PLATFORMS', [], "List of all supported platforms")
LAST_KNOWN_FILE = get_config_with_fallback('LAST_KNOWN_FILE', 'data/last_known_counts.json', "File path for last known counts")
STATS_FILE = get_config_with_fallback('STATS_FILE', 'data/stats.json', "File path for statistics")
README_FILE = get_config_with_fallback('README_FILE', 'README.md', "File path for README")
MAX_REASONABLE_COUNT = get_config_with_fallback('MAX_REASONABLE_COUNT', 20000, "Maximum reasonable problem count")
BDT_TIMEZONE = timezone(timedelta(hours=get_config_with_fallback('BDT_TIMEZONE_hours', 6, "BDT timezone offset in hours")))
USER_AGENT = get_config_with_fallback('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', "User agent string for web requests")
DEFAULT_FUNNY_DATE = get_config_with_fallback('DEFAULT_FUNNY_DATE', '1970-01-01', "Default date for missing data")

from .utils import (
    get_profile_url, get_current_bdt_date, format_human_date,
    extract_first_int, calculate_percentage, calculate_total,
    format_platform_list, read_text_file, get_platform_badge_info,
    parse_url, update_config_file, cleanup_removed_platforms, get_favicon_url, get_platform_urls,
    extract_github_user_info, update_user_info_in_config
)
from .data_manager import DataManager

__all__ = [
    # Config
    'GITHUB_USERINFO', 'USER_CONFIG', 'PROFILE_DISPLAY_NAMES', 'PLATFORM_URL_TEMPLATES', 'PLATFORM_LOGOS', 'PLATFORM_COLORS',
    'ALL_PLATFORMS', 'LAST_KNOWN_FILE', 'STATS_FILE', 'README_FILE',
    'MAX_REASONABLE_COUNT', 'BDT_TIMEZONE', 'USER_AGENT', 'DEFAULT_FUNNY_DATE',
    # Utils
    'get_profile_url', 'get_current_bdt_date', 'format_human_date',
    'extract_first_int', 'calculate_percentage', 'calculate_total',
    'format_platform_list', 'read_text_file', 'get_platform_badge_info',
    'parse_url', 'update_config_file', 'cleanup_removed_platforms', 'get_favicon_url', 'get_platform_urls',
    'extract_github_user_info', 'update_user_info_in_config',
    # Data Manager
    'DataManager'
]
