#!/usr/bin/env python3
"""
Script to configure handles from handles.json and update USER_CONFIG dynamically.
"""

import re
import sys
import os
import json
from urllib.parse import urlparse
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_manager import DataManager


def parse_url(url):
    """Parse URL to extract platform and username."""
    known_templates = {
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
    known_domains = {
        'codeforces.com': 'Codeforces',
        'leetcode.com': 'LeetCode',
        'vjudge.net': 'Vjudge',
        'atcoder.jp': 'AtCoder',
        'codechef.com': 'CodeChef',
        'cses.fi': 'CSES',
        'toph.co': 'Toph',
        'lightoj.com': 'LightOJ',
        'spoj.com': 'SPOJ',
        'hackerrank.com': 'HackerRank',
        'onlinejudge.org': 'UVa',
        'hackerearth.com': 'HackerEarth'
    }
    for platform, template in known_templates.items():
        # Create regex pattern by escaping and replacing {username} with (.+)
        pattern = re.escape(template).replace(r'\{username\}', r'(.+)')
        match = re.match(pattern + r'/?$', url.strip())  # Allow trailing slash
        if match:
            username = match.group(1)
            return platform, username

    # Try to parse unknown URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path.strip('/')
    if domain and path:
        platform = known_domains.get(domain, domain)
        username = path
        return platform, username

    return None, None


def get_favicon_url(url):
    """Return Google favicon service URL for a given profile URL. Fallback to /favicon.ico if Google fails."""
    parsed = urlparse(url)
    google_favicon = f"https://www.google.com/s2/favicons?domain={parsed.netloc}&sz=16"
    try:
        resp = requests.get(google_favicon, timeout=3)
        if resp.status_code == 200 and resp.content:
            return google_favicon
    except Exception:
        pass
    # Fallback to direct favicon.ico
    return f"https://{parsed.netloc}/favicon.ico"


def update_config_file(new_user_config, new_platform_logos, new_templates):

    import json
    config_path = 'src/config.json'

    # Load current stats to sort platforms by solve count (like README display)
    stats_file = 'stats.json'
    platform_stats = {}
    if os.path.exists(stats_file):
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                platform_stats = json.load(f)
        except Exception:
            platform_stats = {}

    # Only consider platforms that have stats data (shown in README)
    # Filter to platforms that exist in both user config and have stats
    platforms_with_data = [
        platform for platform in new_user_config.keys()
        if platform in platform_stats and platform_stats[platform] is not None
    ]

    # Sort platforms by solve count (descending), same as README display order
    sorted_platforms = sorted(
        platforms_with_data,
        key=lambda p: platform_stats.get(p, 0) if isinstance(platform_stats.get(p), int) else 0,
        reverse=True
    )

    # Codeforces rating colors (core 10 colors)
    base_cf_colors = [
        'A00000',  # Legendary Grandmaster - Dark Red
        'C00000',  # International Grandmaster - Dark Red
        'FF0000',  # Grandmaster - Red
        'FF8C00',  # International Master - Orange
        'CCCC00',  # Master - Yellow
        'AA00AA',  # Candidate Master - Purple
        '0000FF',  # Expert - Blue
        '03A89E',  # Specialist - Cyan
        '00AA00',  # Pupil - Green
        '808080'   # Newbie - Gray
    ]

    # Colors from the "gray side" (lower-rated colors) for stretching when more platforms needed
    gray_side_colors = [
        '808080',  # Newbie - Gray
        '00AA00',  # Pupil - Green
        '03A89E',  # Specialist - Cyan
        '0000FF',  # Expert - Blue
    ]

    # Assign colors: prioritize platforms with data (shown in README), then others
    platform_colors = {}

    # First, assign CF colors to platforms with data (sorted by solve count)
    num_platforms_with_data = len(sorted_platforms)
    num_base_colors = len(base_cf_colors)
    num_gray_colors = len(gray_side_colors)

    for i, platform in enumerate(sorted_platforms):
        if i < num_base_colors:
            # Use base CF colors for first platforms with data
            platform_colors[platform] = base_cf_colors[i]
        else:
            # For platforms with data beyond base colors, stretch from the gray side
            extra_index = i - num_base_colors
            gray_color_index = extra_index // 4
            variation_type = extra_index % 4
            base_color = gray_side_colors[gray_color_index % num_gray_colors]

            # Create variations
            r, g, b = int(base_color[0:2], 16), int(base_color[2:4], 16), int(base_color[4:6], 16)

            if variation_type == 0:
                pass  # Original color
            elif variation_type == 1:
                r, g, b = max(0, r - 40), max(0, g - 40), max(0, b - 40)  # Darker
            elif variation_type == 2:
                r, g, b = min(255, r + 40), min(255, g + 40), min(255, b + 40)  # Lighter
            else:
                if base_color == '808080':  # For gray, make bluish
                    r, g, b = max(0, r - 20), max(0, g - 20), min(255, b + 40)
                else:  # For colored, make muted
                    avg = (r + g + b) // 3
                    r, g, b = (r + avg) // 2, (g + avg) // 2, (b + avg) // 2

            platform_colors[platform] = f'{r:02X}{g:02X}{b:02X}'

    # For platforms without data, assign default gray colors
    platforms_without_data = [
        platform for platform in new_user_config.keys()
        if platform not in platform_stats or platform_stats[platform] is None
    ]

    default_gray = '808080'  # Default gray for platforms without data
    for platform in platforms_without_data:
        platform_colors[platform] = default_gray

    # Create config dict
    config = {
        'USER_CONFIG': new_user_config,
        'PROFILE_DISPLAY_NAMES': {platform: new_user_config[platform] for platform in new_user_config},
        'PLATFORM_URL_TEMPLATES': {platform: new_templates[platform] for platform in new_user_config if new_templates.get(platform)},
        'PLATFORM_LOGOS': {platform: new_platform_logos.get(platform, ('', False)) for platform in new_user_config},
        'PLATFORM_COLORS': platform_colors,
        'ALL_PLATFORMS': sorted(new_user_config.keys()),
        'LAST_KNOWN_FILE': 'last_known_counts.json',
        'STATS_FILE': 'stats.json',
        'README_FILE': 'README.md',
        'MAX_REASONABLE_COUNT': 10000,
        'BDT_TIMEZONE_hours': 6,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DEFAULT_FUNNY_DATE': "1970-01-01"
    }

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)

def main():
    # Load current config
    config_path = 'src/config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        USER_CONFIG = config.get('USER_CONFIG', {})
        PLATFORM_URL_TEMPLATES = config.get('PLATFORM_URL_TEMPLATES', {})
        PLATFORM_LOGOS = config.get('PLATFORM_LOGOS', {})
    else:
        USER_CONFIG = {}
        PLATFORM_URL_TEMPLATES = {}
        PLATFORM_LOGOS = {}

    # Read handles.json
    if not os.path.exists('handles.json'):
        print("handles.json not found")
        sys.exit(1)

    with open('handles.json', 'r', encoding='utf-8') as f:
        content = json.load(f)

    if not content:
        print("handles.json is empty")
        urls = []
    else:
        urls = content

    # Parse URLs to get new config
    new_user_config = {}
    url_dict = {}
    for url in urls:
        platform, username = parse_url(url)
        if platform:
            new_user_config[platform] = username
            url_dict[platform] = url
        else:
            print(f"Warning: Could not parse URL: {url}")

    # Build new_templates
    new_templates = {}
    for platform in new_user_config:
        url = url_dict[platform]
        username = new_user_config[platform]
        template = url.replace(username, '{username}')
        new_templates[platform] = template

    # Determine added, removed, changed
    current_platforms = set(USER_CONFIG.keys())
    new_platforms = set(new_user_config.keys())

    added = new_platforms - current_platforms
    removed = current_platforms - new_platforms
    changed = {p for p in current_platforms & new_platforms if USER_CONFIG[p] != new_user_config[p]}

    print(f"Added platforms: {added}")
    print(f"Removed platforms: {removed}")
    print(f"Changed platforms: {changed}")

    # Update PLATFORM_LOGOS for new platforms
    new_platform_logos = PLATFORM_LOGOS.copy()
    for platform in added:
        if platform not in new_platform_logos:
            template = new_templates[platform]
            if template:
                url = template.format(username=new_user_config[platform])
                logo_url = get_favicon_url(url)
                new_platform_logos[platform] = (logo_url, True)
                print(f"Added logo for {platform}: {logo_url}")
            else:
                new_platform_logos[platform] = ('', False)

    # Update config.py
    update_config_file(new_user_config, new_platform_logos, new_templates)

    # Clean up last_known_counts for removed platforms
    if removed:
        last_known = DataManager.load_last_known_counts()
        for platform in removed:
            last_known['counts'].pop(platform, None)
            last_known['dates'].pop(platform, None)
            last_known['modes'].pop(platform, None)
            last_known['last_solved_dates'].pop(platform, None)
            last_known['usernames'].pop(platform, None)
        DataManager.save_last_known_counts(last_known)
        print(f"Cleaned data for removed platforms: {removed}")

    print("Configuration updated successfully!")


if __name__ == "__main__":
    main()