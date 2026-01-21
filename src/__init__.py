#!/usr/bin/env python3
"""
src package - Shared modules for Problem Solving Statistics application.
"""

import json
from datetime import timezone, timedelta

# Load config from JSON
with open('src/config.json', 'r') as f:
    config = json.load(f)

USER_CONFIG = config['USER_CONFIG']
PROFILE_DISPLAY_NAMES = config['PROFILE_DISPLAY_NAMES']
PLATFORM_URL_TEMPLATES = config['PLATFORM_URL_TEMPLATES']
PLATFORM_LOGOS = config['PLATFORM_LOGOS']
PLATFORM_COLORS = config['PLATFORM_COLORS']
ALL_PLATFORMS = config['ALL_PLATFORMS']
LAST_KNOWN_FILE = config['LAST_KNOWN_FILE']
STATS_FILE = config['STATS_FILE']
README_FILE = config['README_FILE']
MAX_REASONABLE_COUNT = config['MAX_REASONABLE_COUNT']
BDT_TIMEZONE = timezone(timedelta(hours=config['BDT_TIMEZONE_hours']))
USER_AGENT = config['USER_AGENT']
DEFAULT_FUNNY_DATE = config['DEFAULT_FUNNY_DATE']

from .utils import (
    get_profile_url, get_current_bdt_date, format_human_date,
    extract_first_int, calculate_percentage, calculate_total,
    format_platform_list, read_text_file, get_platform_badge_info
)
from .data_manager import DataManager

__all__ = [
    # Config
    'USER_CONFIG', 'PROFILE_DISPLAY_NAMES', 'PLATFORM_URL_TEMPLATES', 'PLATFORM_LOGOS', 'PLATFORM_COLORS',
    'ALL_PLATFORMS', 'LAST_KNOWN_FILE', 'STATS_FILE', 'README_FILE',
    'MAX_REASONABLE_COUNT', 'BDT_TIMEZONE', 'USER_AGENT', 'DEFAULT_FUNNY_DATE',
    # Utils
    'get_profile_url', 'get_current_bdt_date', 'format_human_date',
    'extract_first_int', 'calculate_percentage', 'calculate_total',
    'format_platform_list', 'read_text_file', 'get_platform_badge_info',
    # Data Manager
    'DataManager'
]
