#!/usr/bin/env python
"""
Shared utility functions used across the application.
"""

import re
import json
import os
import requests
from datetime import datetime
from urllib.parse import urlparse
from . import (
    USER_CONFIG, PLATFORM_URL_TEMPLATES, BDT_TIMEZONE,
    PLATFORM_LOGOS, PLATFORM_COLORS, ALL_PLATFORMS
)
from .data_manager import DataManager


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
    try:
        platform_index = ALL_PLATFORMS.index(platform)
        color = PLATFORM_COLORS[platform_index] if platform_index < len(PLATFORM_COLORS) else 'blue'
    except (ValueError, IndexError):
        color = 'blue'
    return logo_url, use_onerror, color


def parse_url(url):
    """Parse URL to extract platform and username."""
    known_templates = {
        'Codeforces': [
            'https://codeforces.com/profile/{username}'
        ],
        'LeetCode': [
            'https://leetcode.com/u/{username}/'
        ],
        'VJudge': [
            'https://vjudge.net/user/{username}'
        ],
        'AtCoder': [
            'https://atcoder.jp/users/{username}'
        ],
        'CodeChef': [
            'https://www.codechef.com/users/{username}'
        ],
        'CSES': [
            'https://cses.fi/user/{username}/'
        ],
        'Toph': [
            'https://toph.co/u/{username}'
        ],
        'LightOJ': [
            'https://lightoj.com/user/{username}'
        ],
        'SPOJ': [
            'https://www.spoj.com/users/{username}/'
        ],
        'HackerRank': [
            'https://www.hackerrank.com/profile/{username}'
        ],
        'Uva': [
            'https://uhunt.onlinejudge.org/id/{username}'
        ],
        'HackerEarth': [
            'https://www.hackerearth.com/@{username}/'
        ],
        'Kattis': [
            'https://open.kattis.com/users/{username}'
        ],
        'CSAcademy': [
            'https://csacademy.com/user/{username}'
        ],
        'Toki': [
            'https://tlx.toki.id/profiles/{username}'
        ],
        'DMOJ': [
            'https://dmoj.ca/user/{username}'
        ],
        'OmegaUp': [
            'https://omegaup.com/profile/{username}/'
        ],
        'Beecrowd': [
            'https://www.beecrowd.com.br/judge/en/profile/{username}'
        ],
        'Timus': [
            'https://acm.timus.ru/author.aspx?id={username}'
        ],
        'POJ': [
            'http://poj.org/userstatus?user_id={username}'
        ],
        'ZOJ': [
            'https://zoj.pintia.cn/user/{username}'
        ],
        'HDU': [
            'http://acm.hdu.edu.cn/userstatus.php?user={username}'
        ],
        'FZU': [
            'http://acm.fzu.edu.cn/user.php?uname={username}'
        ],
        'SGU': [
            'http://acm.sgu.ru/teaminfo.php?id={username}'
        ],
        'USACO': [
            'http://usaco.org/index.php?page=viewproblem2&cpid={username}'
        ],
        'AOJ': [
            'https://judge.u-aizu.ac.jp/onlinejudge/user.jsp?id={username}',
            'https://onlinejudge.u-aizu.ac.jp/users/{username}'
        ],
        'Yukicoder': [
            'https://yukicoder.me/users/{username}'
        ],
        'AnarchyGolf': [
            'http://golf.shinh.org/u/{username}'
        ],
        'ProjectEuler': [
            'https://projecteuler.net/profile/{username}.png'
        ],
        'Rosalind': [
            'http://rosalind.info/users/{username}/'
        ],
        'COJ': [
            'https://coj.uci.cu/user/useraccount.xhtml?username={username}'
        ],
        'InfoArena': [
            'https://www.infoarena.ro/utilizator/{username}'
        ],
        'KTH': [
            'https://www.kth.se/profile/{username}/'
        ],
        'MSU': [
            'https://acm.msu.ru/user/{username}'
        ],
        'WCIPEG': [
            'https://wcipeg.com/user/{username}'
        ],
        'COCI': [
            'https://hsin.hr/coci/user.php?username={username}'
        ],
        'BOI': [
            'https://boi.cses.fi/users/{username}'
        ],
        'IOI': [
            'https://ioinformatics.org/user/{username}'
        ],
        'CodeJam': [
            'https://codejam.googleapis.com/scoreboard/{username}'
        ],
        'HackerCup': [
            'https://www.facebook.com/hackercup/user/{username}'
        ],
        'TopCoder': [
            'https://www.topcoder.com/members/{username}'
        ],
        'AtCoderABC': [
            'https://atcoder.jp/users/{username}?contestType=algo'
        ],
        'CodeforcesGym': [
            'https://codeforces.com/profile/{username}?gym=true'
        ],
        'LeetCodeCN': [
            'https://leetcode.cn/u/{username}/'
        ],
        'NowCoder': [
            'https://ac.nowcoder.com/acm/contest/profile/{username}'
        ],
        'Luogu': [
            'https://www.luogu.com.cn/user/{username}'
        ],
        'LibreOJ': [
            'https://loj.ac/user/{username}'
        ],
        'UniversalOJ': [
            'https://uoj.ac/user/profile/{username}'
        ],
        'QDUOJ': [
            'https://qduoj.com/user/{username}'
        ],
        'SYZOJ': [
            'https://syzoj.com/user/{username}'
        ],
        'DarkBZOJ': [
            'https://darkbzoj.cc/user/{username}'
        ],
        'LOJ': [
            'https://loj.ac/user/{username}'
        ],
        'BZOJ': [
            'https://www.lydsy.com/JudgeOnline/userinfo.php?user={username}'
        ],
        'Vijos': [
            'https://vijos.org/user/{username}'
        ],
        'HydroOJ': [
            'https://hydro.ac/user/{username}'
        ],
        'UOJ': [
            'https://uoj.ac/user/profile/{username}'
        ]
    }
    known_domains = {
        'codeforces.com': 'Codeforces',
        'leetcode.com': 'LeetCode',
        'vjudge.net': 'VJudge',
        'atcoder.jp': 'AtCoder',
        'codechef.com': 'CodeChef',
        'cses.fi': 'CSES',
        'toph.co': 'Toph',
        'lightoj.com': 'LightOJ',
        'spoj.com': 'SPOJ',
        'hackerrank.com': 'HackerRank',
        'onlinejudge.org': 'Uva',
        'hackerearth.com': 'HackerEarth',
        'open.kattis.com': 'Kattis',
        'csacademy.com': 'CSAcademy',
        'tlx.toki.id': 'Toki',
        'dmoj.ca': 'DMOJ',
        'omegaup.com': 'OmegaUp',
        'beecrowd.com.br': 'Beecrowd',
        'acm.timus.ru': 'Timus',
        'poj.org': 'POJ',
        'zoj.pintia.cn': 'ZOJ',
        'acm.hdu.edu.cn': 'HDU',
        'acm.fzu.edu.cn': 'FZU',
        'acm.sgu.ru': 'SGU',
        'usaco.org': 'USACO',
        'judge.u-aizu.ac.jp': 'AOJ',
        'onlinejudge.u-aizu.ac.jp': 'AOJ',
        'yukicoder.me': 'Yukicoder',
        'golf.shinh.org': 'AnarchyGolf',
        'projecteuler.net': 'ProjectEuler',
        'rosalind.info': 'Rosalind',
        'coj.uci.cu': 'COJ',
        'infoarena.ro': 'InfoArena',
        'kth.se': 'KTH',
        'acm.msu.ru': 'MSU',
        'wcipeg.com': 'WCIPEG',
        'hsin.hr': 'COCI',
        'boi.cses.fi': 'BOI',
        'ioinformatics.org': 'IOI',
        'codejam.googleapis.com': 'CodeJam',
        'facebook.com': 'HackerCup',
        'topcoder.com': 'TopCoder',
        'leetcode.cn': 'LeetCodeCN',
        'ac.nowcoder.com': 'NowCoder',
        'luogu.com.cn': 'Luogu',
        'loj.ac': 'LOJ',
        'uoj.ac': 'UOJ',
        'qduoj.com': 'QDUOJ',
        'syzoj.com': 'SYZOJ',
        'darkbzoj.cc': 'DarkBZOJ',
        'lydsy.com': 'BZOJ',
        'vijos.org': 'Vijos',
        'hydro.ac': 'HydroOJ'
    }
    for platform, templates in known_templates.items():
        for template in templates:
            # Create regex pattern by escaping and replacing {username} with (.+)
            pattern = re.escape(template).replace(r'\{username\}', r'(.+)')
            match = re.match(pattern + r'/?$', url.strip())  # Allow trailing slash
            if match:
                username = match.group(1).rstrip('/')
                return platform, username

    # Advanced fallback for known domains
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith('www.'):
        domain = domain[4:]  # Remove 'www.'
    # For known domains, use the mapped platform name; for unknown, capitalize the root
    platform = known_domains.get(domain, domain.split('.')[0].capitalize())
    path = parsed.path.strip('/')
    if path:
        parts = path.split('/')
        # Take the last non-empty part as username
        username = parts[-1] if parts[-1] else (parts[-2] if len(parts) > 1 else '')
        if username:
            return platform, username
    return None, None


def get_favicon_url(url):
    """Return Google favicon service URL for a given profile URL. Fallback to /favicon.ico if Google fails."""
    parsed = urlparse(url)
    google_favicon = f"https://www.google.com/s2/favicons?domain={parsed.netloc}&sz=16"
    # Always try Google first, fallback only on exception
    try:
        requests.get(google_favicon, timeout=3)
        return google_favicon
    except Exception:
        pass
    # Fallback to direct favicon.ico
    return f"https://{parsed.netloc}/favicon.ico"


def get_platform_urls():
    """Generate platform URLs for all configured platforms.
    
    Returns:
        Dictionary mapping platform names to their profile URLs
    """
    # Cache platform URLs to avoid regeneration on multiple calls
    if not hasattr(get_platform_urls, '_cached_urls'):
        platforms = {}
        for platform in USER_CONFIG.keys():
            template = PLATFORM_URL_TEMPLATES.get(platform)
            username = USER_CONFIG.get(platform)
            if template and username:
                platforms[platform] = template.format(username=username)
        get_platform_urls._cached_urls = platforms
    
    return get_platform_urls._cached_urls


def update_config_file(new_user_config, new_platform_logos, new_templates, new_display_names=None):
    """Update the config.json file with new configuration."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')

    # Read existing config to preserve sections we don't manage
    existing_config = {}
    try:
        with open(config_path, 'r') as f:
            existing_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Codeforces rating colors (core 10 colors from LGM to Newbie)
    base_cf_colors = [
        'AA0000',  # Legendary Grandmaster
        'FF3333',  # International Grandmaster
        'FF7777',  # Grandmaster
        'FFBB55',  # International Master
        'FFCC88',  # Master
        'FF88FF',  # Candidate Master
        'AAAAFF',  # Expert
        '77DDBB',  # Specialist
        '77FF77',  # Pupil
        'CCCCCC'   # Newbie
    ]

    def interpolate_color(color1, color2, t):
        """Interpolate between two hex colors. t=0 returns color1, t=1 returns color2."""
        r1, g1, b1 = int(color1[0:2], 16), int(color1[2:4], 16), int(color1[4:6], 16)
        r2, g2, b2 = int(color2[0:2], 16), int(color2[2:4], 16), int(color2[4:6], 16)

        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)

        return f'{r:02X}{g:02X}{b:02X}'

    # Generate colors for all platforms
    num_platforms = len(new_user_config)
    platform_colors = []

    if num_platforms <= len(base_cf_colors):
        # No interpolation needed, just use the base colors
        platform_colors = base_cf_colors[:num_platforms]
    else:
        # Assign base CF colors first
        platform_colors = base_cf_colors[:]

        # For additional platforms, create intermediate colors between adjacent CF colors
        # Create one intermediate per consecutive pair, starting from pupil-specialist upward
        extra_colors_needed = num_platforms - len(base_cf_colors)

        # Create pairs between consecutive base colors, from pupil to lgm (excluding newbie)
        # Pairs: (P, S), (S, E), (E, CM), (CM, M), (M, IM), (IM, GM), (GM, IGM), (IGM, LGM)
        color_pairs = []
        for i in range(len(base_cf_colors) - 2, -1, -1):  # From P (index 8) to LGM (index 0)
            color_pairs.append((base_cf_colors[i], base_cf_colors[i - 1]))

        # First, create one intermediate for each pair until we run out of extra colors needed
        for pair_idx, (color1, color2) in enumerate(color_pairs):
            if extra_colors_needed <= 0:
                break
                
            # Find positions to insert between color2 and color1
            try:
                idx1 = platform_colors.index(color1)
                idx2 = platform_colors.index(color2)
                insert_pos = idx2 + 1
            except ValueError:
                insert_pos = len(platform_colors)

            # Create one intermediate for this pair
            t = 0.5  # Middle interpolation
            intermediate = interpolate_color(color1, color2, t)
            platform_colors.insert(insert_pos, intermediate)
            extra_colors_needed -= 1

        # If still need more colors, create additional intermediates starting from newbie side again
        if extra_colors_needed > 0:
            # Add (N, P) pair and create additional intermediates
            newbie_pairs = [(base_cf_colors[9], base_cf_colors[8])]  # (N, P)
            newbie_pairs.extend(color_pairs)  # Add the other pairs
            
            colors_per_pair = (extra_colors_needed + len(newbie_pairs) - 1) // len(newbie_pairs)
            
            for pair_idx, (color1, color2) in enumerate(newbie_pairs):
                if extra_colors_needed <= 0:
                    break
                    
                try:
                    idx1 = platform_colors.index(color1)
                    idx2 = platform_colors.index(color2)
                    insert_pos = idx2 + 1
                except ValueError:
                    insert_pos = len(platform_colors)

                # Create additional intermediates for this pair
                for step in range(min(colors_per_pair, extra_colors_needed)):
                    t = (step + 1) / (colors_per_pair + 1)
                    intermediate = interpolate_color(color1, color2, t)
                    platform_colors.insert(insert_pos, intermediate)
                    extra_colors_needed -= 1
                    
                if len(platform_colors) >= num_platforms:
                    break

    # Create config dict
    display_names = new_display_names if new_display_names is not None else {platform: new_user_config[platform] for platform in new_user_config}
    config = {
        'USER_CONFIG': new_user_config,
        'PROFILE_DISPLAY_NAMES': display_names,
        'PLATFORM_URL_TEMPLATES': {platform: new_templates[platform] for platform in new_user_config if new_templates.get(platform)},
        'PLATFORM_LOGOS': {platform: new_platform_logos.get(platform, ('', False)) for platform in new_user_config},
        'PLATFORM_COLORS': platform_colors,
        'ALL_PLATFORMS': sorted(new_user_config.keys()),
        'LAST_KNOWN_FILE': 'data/last_known_counts.json',
        'STATS_FILE': 'data/stats.json',
        'README_FILE': 'docs/README.md',
        'MAX_REASONABLE_COUNT': 20000,
        'BDT_TIMEZONE_hours': 6,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DEFAULT_FUNNY_DATE': "1970-01-01"
    }

    # Preserve sections that are not managed by this function (like USER_INFO)
    preserved_keys = ['USER_INFO']  # Add other keys here as needed
    for key in preserved_keys:
        if key in existing_config:
            config[key] = existing_config[key]

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)


def cleanup_removed_platforms(removed_platforms):
    """Clean up data for removed platforms from last_known_counts.json.
    
    Args:
        removed_platforms: Set of platform names that were removed
    """
    if not removed_platforms:
        return
        
    last_known = DataManager.load_last_known_counts()
    for platform in removed_platforms:
        last_known['counts'].pop(platform, None)
        last_known['dates'].pop(platform, None)
        last_known['modes'].pop(platform, None)
        last_known['last_solved_dates'].pop(platform, None)
        last_known['usernames'].pop(platform, None)
    DataManager.save_last_known_counts(last_known)


def extract_github_user_info():
    """Extract GitHub user information from git remote and GitHub API.
    
    Returns:
        dict: Dictionary containing 'name' and 'email' from GitHub
    """
    import subprocess
    
    try:
        # Get the remote URL
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode != 0:
            return None
            
        remote_url = result.stdout.strip()
        
        # Extract username from GitHub URL
        # Format: https://github.com/username/repo.git
        if 'github.com' in remote_url:
            parts = remote_url.split('github.com/')[1].split('/')[0]
            username = parts
            
            # Fetch user info from GitHub API
            api_url = f"https://api.github.com/users/{username}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                user_data = response.json()
                name = user_data.get('name', '')
                
                # Get email from git config if GitHub API doesn't provide it
                email = user_data.get('email')
                if not email:
                    email_result = subprocess.run(['git', 'config', '--global', 'user.email'], 
                                                capture_output=True, text=True, cwd='.')
                    if email_result.returncode == 0:
                        email = email_result.stdout.strip()
                
                return {
                    'name': name.strip() if name else '',
                    'email': email
                }
    
    except Exception as e:
        print(f"Error extracting GitHub user info: {e}")
    
    return None


def update_user_info_in_config():
    """Update USER_INFO in config.json with GitHub user information."""
    user_info = extract_github_user_info()
    if user_info:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        # Load current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update USER_INFO
        config['USER_INFO'] = user_info
        
        # Save back to config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"Updated USER_INFO in config.json: {user_info}")
        return True
    
    print("Could not extract GitHub user information")
    return False


def get_codeforces_rating_color(max_rating):
    """
    Get the color associated with a Codeforces rating.
    
    Args:
        max_rating: The user's maximum Codeforces rating
        
    Returns:
        Hex color code for the rating tier
    """
    if max_rating is None:
        return 'CCCCCC'  # Newbie - Light Gray
    
    # Codeforces rating tiers and their colors (Official)
    if max_rating >= 2900:
        return 'AA0000'  # Legendary Grandmaster
    elif max_rating >= 2600:
        return 'FF3333'  # International Grandmaster
    elif max_rating >= 2400:
        return 'FF7777'  # Grandmaster
    elif max_rating >= 2300:
        return 'FFBB55'  # International Master
    elif max_rating >= 2200:
        return 'FFCC88'  # Master
    elif max_rating >= 1900:
        return 'FF88FF'  # Candidate Master
    elif max_rating >= 1600:
        return 'AAAAFF'  # Expert
    elif max_rating >= 1400:
        return '77DDBB'  # Specialist
    elif max_rating >= 1200:
        return '77FF77'  # Pupil
    else:
        return 'CCCCCC'  # Newbie


def get_interpolated_codeforces_color(rating, base_rating=None):
    """
    Get an interpolated color based on rating position within Codeforces tiers.
    If base_rating is provided and rating > base_rating, creates intermediate colors.
    
    Args:
        rating: The rating to get color for
        base_rating: The base rating to compare against (optional)
        
    Returns:
        Hex color code interpolated within the appropriate tier range
    """
    if rating is None:
        return '808080'  # Gray for unknown
    
    # Define rating tiers with their ranges and colors
    tiers = [
        (0, 1199, 'CCCCCC', 'CCCCCC'),      # Newbie
        (1200, 1399, 'CCCCCC', '77FF77'),   # Newbie to Pupil
        (1400, 1599, '77FF77', '77DDBB'),   # Pupil to Specialist  
        (1600, 1899, '77DDBB', 'AAAAFF'),   # Specialist to Expert
        (1900, 2199, 'AAAAFF', 'FF88FF'),   # Expert to Candidate Master
        (2200, 2399, 'FF88FF', 'FFCC88'),   # Candidate Master to Master
        (2400, 2599, 'FFCC88', 'FF7777'),   # Master to Grandmaster
        (2600, 2899, 'FF7777', 'FF3333'),   # Grandmaster to International GM
        (2900, float('inf'), 'FF3333', 'AA0000')  # International GM to Legendary GM
    ]
    
    # Find the appropriate tier
    for min_rating, max_rating, color1, color2 in tiers:
        if min_rating <= rating < max_rating:
            if min_rating == max_rating:  # Single color tier
                return color1
            
            # Calculate interpolation factor within this tier
            if max_rating == float('inf'):
                # For the highest tier, just return the color
                return color1
            
            # Interpolate between color1 and color2
            t = (rating - min_rating) / (max_rating - min_rating)
            
            # If base_rating is provided and rating > base_rating, 
            # create intermediate colors by adjusting the interpolation
            if base_rating is not None and rating > base_rating:
                # Boost the interpolation factor to create brighter/more advanced colors
                t = min(1.0, t + 0.3)  # Add 30% boost, capped at 1.0
            
            return interpolate_color(color1, color2, t)
    
    return '808080'  # Default to gray


def interpolate_color(color1, color2, t):
    """
    Interpolate between two hex colors.
    
    Args:
        color1: First hex color (6 characters)
        color2: Second hex color (6 characters) 
        t: Interpolation factor (0.0 = color1, 1.0 = color2)
        
    Returns:
        Interpolated hex color
    """
    r1, g1, b1 = int(color1[0:2], 16), int(color1[2:4], 16), int(color1[4:6], 16)
    r2, g2, b2 = int(color2[0:2], 16), int(color2[2:4], 16), int(color2[4:6], 16)

    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)

    return f'{r:02X}{g:02X}{b:02X}'
