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
from src import (parse_url, update_config_file, get_favicon_url, 
                update_user_info_in_config)

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
            content = json.loads(file_content)
    except json.JSONDecodeError as e:
        # JSON syntax errors - show error and stop
        print(f"[ERROR] Syntax error in handles.json: {e}")
        print("[ERROR] handles.json should look like this:")
        print('[')
        print('  "https://codeforces.com/profile/your_username",')
        print('  "https://leetcode.com/your_username",')
        print('  "https://atcoder.jp/users/your_username"')
        print(']')
        sys.exit(1)  # Stop immediately on syntax error

    if not content:
        print("handles.json is empty")
        print("[INIT] Initializing handles.json with sample format...")
        sample_handles = [
            "https://codeforces.com/profile/your_username",
            "https://atcoder.jp/users/your_username",
            "https://www.codechef.com/users/your_username"
        ]
        try:
            with open(handles_path, 'w', encoding='utf-8') as f:
                json.dump(sample_handles, f, indent=2)
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
    
    # Ensure all platforms have display names (usually same as username)
    new_display_names = PROFILE_DISPLAY_NAMES_GLOBAL.copy()
    for platform in new_user_config:
        if platform not in new_display_names or not new_display_names.get(platform):
            new_display_names[platform] = new_user_config[platform]
            print(f"Added display name for {platform}")
    
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
    update_config_file(new_user_config, new_platform_logos, new_templates_full)
    
    # Try to update user info from GitHub (optional, won't break if it fails)
    print("Attempting to update user information from GitHub...")
    try:
        user_info_success = update_user_info_in_config()
        if user_info_success:
            print("[OK] User information updated successfully!")
        else:
            print("[WARNING] Could not update user information (this is optional)")
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