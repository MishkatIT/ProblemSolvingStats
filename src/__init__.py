#!/usr/bin/env python3
"""
src package - Shared modules for Problem Solving Statistics application.
"""

from .config import (
    USER_CONFIG, PLATFORM_URL_TEMPLATES, PLATFORM_LOGOS, PLATFORM_COLORS,
    ALL_PLATFORMS, LAST_KNOWN_FILE, STATS_FILE, README_FILE,
    MAX_REASONABLE_COUNT, BDT_TIMEZONE, USER_AGENT, DEFAULT_FUNNY_DATE
)
from .utils import (
    get_profile_url, get_current_bdt_date, format_human_date,
    extract_first_int, calculate_percentage, calculate_total,
    format_platform_list, read_text_file, get_platform_badge_info
)
from .data_manager import DataManager

__all__ = [
    # Config
    'USER_CONFIG', 'PLATFORM_URL_TEMPLATES', 'PLATFORM_LOGOS', 'PLATFORM_COLORS',
    'ALL_PLATFORMS', 'LAST_KNOWN_FILE', 'STATS_FILE', 'README_FILE',
    'MAX_REASONABLE_COUNT', 'BDT_TIMEZONE', 'USER_AGENT', 'DEFAULT_FUNNY_DATE',
    # Utils
    'get_profile_url', 'get_current_bdt_date', 'format_human_date',
    'extract_first_int', 'calculate_percentage', 'calculate_total',
    'format_platform_list', 'read_text_file', 'get_platform_badge_info',
    # Data Manager
    'DataManager'
]
