#!/usr/bin/env python
"""
Script to configure handles from handles.json and update USER_CONFIG dynamically.
"""

import sys
import os

print("sys.executable:", sys.executable)

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, project_root)
print("sys.path[:3]:", sys.path[:3])

import json

# Import src module and functions
from src import (parse_url, update_config_file, get_favicon_url
                # update_user_info_in_config
                )

# Import config variables with aliases to avoid scoping issues
from src import USER_CONFIG as USER_CONFIG_GLOBAL
from src import PLATFORM_URL_TEMPLATES as PLATFORM_URL_TEMPLATES_GLOBAL
from src import PROFILE_DISPLAY_NAMES as PROFILE_DISPLAY_NAMES_GLOBAL  
from src import PLATFORM_LOGOS as PLATFORM_LOGOS_GLOBAL

print(f"Imported USER_CONFIG: {type(USER_CONFIG_GLOBAL)}, length: {len(USER_CONFIG_GLOBAL) if hasattr(USER_CONFIG_GLOBAL, '__len__') else 'N/A'}")

try:
    from src.data_manager import DataManager
    print("Imports successful")
except Exception as e:
    print("Import error:", e)
    import sys
    sys.exit(1)


def main():
    # Use imported config values (already loaded by src/__init__.py)
    # No need to reload config.json as src module handles this
    print("USER_CONFIG:", USER_CONFIG_GLOBAL)
    print("Length:", len(USER_CONFIG_GLOBAL))

    # Read and check handles.json
    handles_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'handles.json')
    if not os.path.exists(handles_path):
        print("handles.json not found")
        sys.exit(1)

    try:
        with open(handles_path, 'r', encoding='utf-8') as f:
            file_content = f.read().strip()
        
        if not file_content:
            # File is empty or whitespace-only - silently reinitialize
            content = []
        else:
            data = json.loads(file_content)
            # Handle both old array format and new object format
            if isinstance(data, list):
                content = data
            elif isinstance(data, dict) and 'urls' in data:
                content = data['urls']
            else:
                content = []
    except json.JSONDecodeError as e:
        # JSON syntax errors - show error and stop
        print(f"[ERROR] Syntax error in handles.json: {e}")
        print("[ERROR] handles.json should look like this:")
        print('{')
        print('  "urls": [')
        print('    "https://cses.fi/user/your_username/",')
        print('    "https://codeforces.com/profile/your_username"')
        print('  ],')
        print('  "_comment": "Complete URLs to your profiles on each platform at above section"')
        print('}')
        print("See _examples field in existing handles.json for all supported platforms")
        sys.exit(1)  # Stop immediately on syntax error

    if not content:
        print("handles.json is empty")
        print("[INIT] Initializing handles.json with sample format...")
        sample_data = {
            "urls": [
                "https://cses.fi/user/your_username/",
                "https://codeforces.com/profile/your_username",
                "https://atcoder.jp/users/your_username",
                "https://www.codechef.com/users/your_username"
            ],
            "_comment": "Complete URLs to your profiles on each platform at above section. Format: https://platform.com/path/your_username",
            "_examples": {
                "CSES": "https://cses.fi/user/your_username/",
                "Codeforces": "https://codeforces.com/profile/your_username",
                "LeetCode": "https://leetcode.com/u/your_username/",
                "AtCoder": "https://atcoder.jp/users/your_username",
                "CodeChef": "https://www.codechef.com/users/your_username",
                "HackerRank": "https://www.hackerrank.com/profile/your_username",
                "HackerEarth": "https://www.hackerearth.com/@your_username/",
                "SPOJ": "https://www.spoj.com/users/your_username/",
                "UVA": "https://uhunt.onlinejudge.org/id/your_username",
                "Timus": "https://acm.timus.ru/author.aspx?id=your_username",
                "TopCoder": "https://www.topcoder.com/members/your_username",
                "Kattis": "https://open.kattis.com/users/your_username",
                "DMOJ": "https://dmoj.ca/user/your_username",
                "Toph": "https://toph.co/u/your_username",
                "LightOJ": "https://lightoj.com/user/your_username",
                "VJudge": "https://vjudge.net/user/your_username",
                "CSAcademy": "https://csacademy.com/user/your_username",
                "Toki": "https://tlx.toki.id/profiles/your_username",
                "OmegaUp": "https://omegaup.com/profile/your_username/",
                "Beecrowd": "https://www.beecrowd.com.br/judge/en/profile/your_username",
                "POJ": "http://poj.org/userstatus?user_id=your_username",
                "ZOJ": "https://zoj.pintia.cn/user/your_username",
                "HDU": "http://acm.hdu.edu.cn/userstatus.php?user=your_username",
                "FZU": "http://acm.fzu.edu.cn/user.php?uname=your_username",
                "SGU": "http://acm.sgu.ru/teaminfo.php?id=your_username",
                "AOJ": "https://judge.u-aizu.ac.jp/onlinejudge/user.jsp?id=your_username",
                "Yukicoder": "https://yukicoder.me/users/your_username",
                "ProjectEuler": "https://projecteuler.net/profile/your_username.png",
                "COJ": "https://coj.uci.cu/user/useraccount.xhtml?username=your_username",
                "InfoArena": "https://www.infoarena.ro/utilizator/your_username",
                "KTH": "https://www.kth.se/profile/your_username/",
                "MSU": "https://acm.msu.ru/user/your_username",
                "WCIPEG": "https://wcipeg.com/user/your_username",
                "COCI": "https://hsin.hr/coci/user.php?username=your_username",
                "BOI": "https://boi.cses.fi/users/your_username",
                "IOI": "https://ioinformatics.org/user/your_username",
                "CodeJam": "https://codejam.googleapis.com/scoreboard/your_username",
                "HackerCup": "https://www.facebook.com/hackercup/user/your_username",
                "AtCoderABC": "https://atcoder.jp/users/your_username?contestType=algo",
                "CodeforcesGym": "https://codeforces.com/profile/your_username?gym=true",
                "LeetCodeCN": "https://leetcode.cn/u/your_username/",
                "NowCoder": "https://ac.nowcoder.com/acm/contest/profile/your_username",
                "Luogu": "https://www.luogu.com.cn/user/your_username",
                "LibreOJ": "https://loj.ac/user/your_username",
                "UniversalOJ": "https://uoj.ac/user/profile/your_username",
                "QDUOJ": "https://qduoj.com/user/your_username"
            }
        }
        try:
            with open(handles_path, 'w', encoding='utf-8') as f:
                json.dump(sample_data, f, indent=2)
            print("[OK] Created handles.json with sample handles")
            print("[INFO] Please edit handles.json and replace 'your_username' with your actual usernames")
            print("[INIT] Run this script again after updating handles.json")
            return  # Exit early, let user configure first
        except Exception as e:
            print(f"[ERROR] Failed to create sample handles.json: {e}")
            urls = []
            return
    else:
        # Validate that content is a list
        if not isinstance(content, list):
            print("[ERROR] handles.json should be a JSON array (list) of URLs")
            print("[INFO] Example: [\"https://codeforces.com/profile/username\"]")
            urls = []
        else:
            urls = content
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

    # Determine added, removed, changed BEFORE updating config
    current_platforms = set(USER_CONFIG_GLOBAL.keys())
    new_platforms = set(new_user_config.keys())

    added = new_platforms - current_platforms
    removed = current_platforms - new_platforms
    changed = {p for p in current_platforms & new_platforms if USER_CONFIG_GLOBAL[p] != new_user_config[p]}

    print(f"Added platforms: {added}")
    print(f"Removed platforms: {removed}")
    print(f"Changed platforms: {changed}")

    # Comprehensive config validation and repair for all platforms
    print("Validating and repairing all config fields for all platforms...")
    
    # Ensure all platforms have URL templates
    new_templates_full = PLATFORM_URL_TEMPLATES_GLOBAL.copy()
    for platform in new_user_config:
        if platform not in new_templates_full or not new_templates_full.get(platform):
            if platform in new_templates:
                new_templates_full[platform] = new_templates[platform]
                print(f"Added URL template for {platform}")
            else:
                print(f"Warning: No URL template available for {platform}")
    
    # Update display names only for added/changed platforms, remove for removed platforms
    new_display_names = PROFILE_DISPLAY_NAMES_GLOBAL.copy()
    
    # Handle added and changed platforms: set/update display name to handle name
    for platform in added | changed:
        new_display_names[platform] = new_user_config[platform]
        action = "Added" if platform in added else "Updated"
        print(f"{action} display name for {platform}: {new_user_config[platform]}")
    
    # Handle removed platforms: remove display name
    for platform in removed:
        if platform in new_display_names:
            del new_display_names[platform]
            print(f"Removed display name for {platform}")
    
    # For existing unchanged platforms: keep display names as they are (don't modify)
    
    # Ensure all platforms have valid logos
    new_platform_logos = PLATFORM_LOGOS_GLOBAL.copy()
    for platform in new_user_config:
        # Check if platform needs a logo (missing, empty, or invalid)
        current_logo = new_platform_logos.get(platform, ('', False))
        needs_logo = (platform not in new_platform_logos or 
                     not current_logo[0] or 
                     current_logo[0].strip() == '')
        
        if needs_logo:
            template = new_templates_full.get(platform)
            if template:
                url = template.format(username=new_user_config[platform])
                logo_url = get_favicon_url(url)
                new_platform_logos[platform] = (logo_url, True)
                if platform in added:
                    print(f"Added logo for {platform}: {logo_url}")
                else:
                    print(f"Repaired logo for {platform}: {logo_url}")
            else:
                new_platform_logos[platform] = ('', False)
                print(f"Warning: Could not set logo for {platform} (no template)")

    # Update config with all validated data
    update_config_file(new_user_config, new_platform_logos, new_templates_full, new_display_names)
    
    # Try to update user info from GitHub (optional, won't break if it fails)
    print("Attempting to update user information from GitHub...")
    try:
        # user_info_success = update_user_info_in_config()
        # if user_info_success:
        #     print("[OK] User information updated successfully!")
        # else:
        #     print("[WARNING] Could not update user information (this is optional)")
        print("[INFO] GitHub user info update is commented out")
    except Exception as e:
        print(f"[WARNING] Failed to update user information: {e} (this is optional)")
    
    # Reload the config to update global variables
    import importlib
    import src
    importlib.reload(src)
    from src import USER_CONFIG

    # Update usernames in last_known_counts for all current platforms first
    last_known = DataManager.load_last_known_counts()
    for platform, username in USER_CONFIG.items():
        last_known['usernames'][platform] = username
    
    # Now use the centralized cleanup method to handle username changes
    # This will detect changes and reset cache for changed platforms
    print("Cleaning up cached data for changed/removed platforms...")
    last_known = DataManager.cleanup_cached_data(last_known, force_save=True, user_config=USER_CONFIG)
    
    print("Configuration and cache cleanup completed successfully!")


if __name__ == "__main__":
    main()