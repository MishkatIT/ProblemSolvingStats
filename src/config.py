#!/usr/bin/env python3
"""
Centralized configuration file for all constants and settings.
This file contains all shared configuration used across the application.
"""

from datetime import timezone, timedelta

# User configuration - Single source of truth for all usernames/IDs
USER_CONFIG = {
    'Codeforces': 'MishkatIT',
    'LeetCode': 'MishkatIT',
    'Vjudge': 'MishkatIT',
    'AtCoder': 'MishkatIT',
    'CodeChef': 'MishkatIT',
    'CSES': '165802',  # User ID
    'Toph': 'MishkatIT',
    'LightOJ': 'mishkatit',  # lowercase
    'SPOJ': 'mishkatit',  # lowercase
    'HackerRank': 'MishkatIT',
    'UVa': '1615470',  # User ID
    'HackerEarth': 'MishkatIT'
}

# Display names for profile table (shown in README)
# Use this to show a consistent, user-friendly name regardless of actual handle/ID
PROFILE_DISPLAY_NAMES = {
    'Codeforces': 'MishkatIT',
    'LeetCode': 'MishkatIT',
    'Vjudge': 'MishkatIT',
    'AtCoder': 'MishkatIT',
    'CodeChef': 'MishkatIT',
    'CSES': 'MishkatIT',
    'Toph': 'MishkatIT',
    'LightOJ': 'MishkatIT',
    'SPOJ': 'MishkatIT',
    'HackerRank': 'MishkatIT',
    'UVa': 'MishkatIT',
    'HackerEarth': 'MishkatIT'
}

# Platform URL templates
PLATFORM_URL_TEMPLATES = {
    'Codeforces': 'https://codeforces.com/profile/{username}',
    'LeetCode': 'https://leetcode.com/{username}/',
    'Vjudge': 'https://vjudge.net/user/{username}',
    'AtCoder': 'https://atcoder.jp/users/{username}',
    'CodeChef': 'https://www.codechef.com/users/{username}',
    'CSES': 'https://cses.fi/user/{username}/',
    'Toph': 'https://toph.co/u/{username}',
    'LightOJ': 'https://lightoj.com/user/{username}',
    'SPOJ': 'https://www.spoj.com/users/{username}/',
    'HackerRank': 'https://www.hackerrank.com/{username}',
    'UVa': 'https://uhunt.onlinejudge.org/id/{username}',
    'HackerEarth': 'https://www.hackerearth.com/@{username}'
}

# Platform configuration constants
PLATFORM_LOGOS = {
    'Codeforces': ('https://cdn.iconscout.com/icon/free/png-16/codeforces-3628695-3029920.png', True),
    'LeetCode': ('https://leetcode.com/favicon-16x16.png', True),
    'Vjudge': ('https://vjudge.net/favicon.ico', True),
    'AtCoder': ('https://atcoder.jp/favicon.ico', True),
    'CodeChef': ('https://cdn.codechef.com/sites/all/themes/abessive/cc-logo.png', True),
    'CSES': ('https://cses.fi/logo.png?1', True),
    'Toph': ('https://toph.co/favicon.ico', True),
    'LightOJ': ('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSq0TU63ijLZ_PaQre3dgnYmJ811t41O-RcHg&s', False),
    'SPOJ': ('https://www.spoj.com/favicon.ico', True),
    'HackerRank': ('https://hrcdn.net/fcore/assets/favicon-ddc852f75a.png', True),
    'UVa': ('https://www.google.com/s2/favicons?domain=onlinejudge.org&sz=16', True),
    'HackerEarth': ('https://www.google.com/s2/favicons?domain=hackerearth.com&sz=16', True)
}

PLATFORM_COLORS = {
    'Codeforces': 'red',
    'LeetCode': 'yellow',
    'Vjudge': 'blueviolet',
    'AtCoder': 'orange',
    'CodeChef': 'brown',
    'CSES': 'lightgray',
    'Toph': 'blue',
    'LightOJ': 'yellow',
    'SPOJ': 'green',
    'HackerRank': 'brightgreen',
    'UVa': 'blue',
    'HackerEarth': 'blue'
}

ALL_PLATFORMS = [
    'Codeforces', 'LeetCode', 'Vjudge', 'AtCoder', 'CodeChef',
    'CSES', 'Toph', 'LightOJ', 'SPOJ', 'HackerRank', 'UVa', 'HackerEarth'
]

# Application constants
LAST_KNOWN_FILE = 'last_known_counts.json'
STATS_FILE = 'stats.json'
README_FILE = 'README.md'

# Validation constants
MAX_REASONABLE_COUNT = 10000  # Maximum expected problem count for validation

# Timezone configuration (BDT - Bangladesh Time, UTC+6)
BDT_TIMEZONE = timezone(timedelta(hours=6))

# User agent for web requests
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Default date for platforms with no recorded solve date
DEFAULT_FUNNY_DATE = "1970-01-01"
