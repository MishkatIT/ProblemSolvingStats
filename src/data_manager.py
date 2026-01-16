#!/usr/bin/env python3
"""
Data manager for handling JSON file operations and data persistence.
"""

import json
import os
from datetime import datetime
from src.config import (
    LAST_KNOWN_FILE, STATS_FILE, BDT_TIMEZONE, DEFAULT_FUNNY_DATE, USER_CONFIG
)


class DataManager:
    """Handles loading and saving of JSON data files."""
    
    @staticmethod
    def load_last_known_counts():
        """Load the last known good counts from file.
        
        Returns:
            Dictionary with counts, dates, modes, and last_solved_dates
        """
        try:
            with open(LAST_KNOWN_FILE, 'r') as f:
                data = json.load(f)
                # Ensure all required keys exist
                if 'last_solved_dates' not in data:
                    data['last_solved_dates'] = {}
                if 'modes' not in data:
                    data['modes'] = {}
                if 'counts' not in data:
                    data['counts'] = {}
                if 'dates' not in data:
                    data['dates'] = {}
                if 'usernames' not in data:
                    data['usernames'] = {}
                
                # Check if any username has changed - if so, reset cache for that platform
                usernames_changed = False
                for platform, current_username in USER_CONFIG.items():
                    stored_username = data['usernames'].get(platform)
                    if stored_username and stored_username != current_username:
                        print(f"Username changed for {platform}: {stored_username} -> {current_username}")
                        print(f"Resetting cached data for {platform}")
                        # Clear cached data for this platform
                        data['counts'].pop(platform, None)
                        data['dates'].pop(platform, None)
                        data['modes'].pop(platform, None)
                        data['last_solved_dates'].pop(platform, None)
                        usernames_changed = True
                    # Update stored username
                    data['usernames'][platform] = current_username
                
                # Save immediately if usernames changed
                if usernames_changed:
                    DataManager.save_last_known_counts(data)
                
                return data
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load last known counts: {e}")
        return {'counts': {}, 'dates': {}, 'modes': {}, 'last_solved_dates': {}, 'usernames': {}}
    
    @staticmethod
    def save_last_known_counts(last_known_counts):
        """Save the current known good counts to file.
        
        Args:
            last_known_counts: Dictionary containing counts and metadata
        """
        try:
            with open(LAST_KNOWN_FILE, 'w') as f:
                json.dump(last_known_counts, f, indent=2)
        except (IOError, OSError) as e:
            print(f"Warning: Could not save last known counts: {e}")
    
    @staticmethod
    def update_last_known(last_known_counts, platform, count, mode=None):
        """Update the last known count and mode for a platform.
        
        Args:
            last_known_counts: Dictionary to update
            platform: Platform name
            count: Problem count
            mode: Update mode ('manual' or 'automatic')
        """
        if count is None:
            return
        
        # Ensure all required keys exist
        if 'counts' not in last_known_counts:
            last_known_counts['counts'] = {}
        if 'dates' not in last_known_counts:
            last_known_counts['dates'] = {}
        if 'modes' not in last_known_counts:
            last_known_counts['modes'] = {}
        if 'last_solved_dates' not in last_known_counts:
            last_known_counts['last_solved_dates'] = {}
        if 'usernames' not in last_known_counts:
            last_known_counts['usernames'] = {}

        current_date = datetime.now(BDT_TIMEZONE).strftime('%Y-%m-%d')
        
        # Check if count increased (problem was solved)
        old_count = last_known_counts['counts'].get(platform)
        if old_count is None:
            last_known_counts['last_solved_dates'][platform] = DEFAULT_FUNNY_DATE
        elif count > old_count:
            last_known_counts['last_solved_dates'][platform] = current_date

        last_known_counts['counts'][platform] = count
        last_known_counts['dates'][platform] = current_date
        last_known_counts['usernames'][platform] = USER_CONFIG.get(platform)

        # Update the mode only if it is different
        if mode is not None and last_known_counts['modes'].get(platform) != mode:
            last_known_counts['modes'][platform] = mode
    
    @staticmethod
    def get_last_known(last_known_counts, platform):
        """Get the last known count for a platform.
        
        Args:
            last_known_counts: Dictionary containing counts
            platform: Platform name
            
        Returns:
            Last known count or None
        """
        if 'counts' in last_known_counts:
            return last_known_counts['counts'].get(platform)
        return None
    
    @staticmethod
    def get_last_known_mode(last_known_counts, platform):
        """Get the last known update mode for a platform.
        
        Args:
            last_known_counts: Dictionary containing modes
            platform: Platform name
            
        Returns:
            Last known mode or 'unknown'
        """
        if 'modes' in last_known_counts:
            return last_known_counts['modes'].get(platform, 'unknown')
        return 'unknown'
    
    @staticmethod
    def load_stats():
        """Load statistics from stats.json file.
        
        Returns:
            Dictionary of platform stats or None if failed
        """
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{STATS_FILE} not found. Please run update_stats.py first.")
            return None
        except json.JSONDecodeError:
            print(f"Error parsing {STATS_FILE}")
            return None
    
    @staticmethod
    def save_stats(stats):
        """Save statistics to stats.json file.
        
        Args:
            stats: Dictionary of platform stats
        """
        try:
            with open(STATS_FILE, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2)
            print(f"\n✓ Saved statistics to {STATS_FILE}")
        except Exception as e:
            print(f"\nWarning: Could not write {STATS_FILE}: {e}")
    
    @staticmethod
    def update_manual_stats(stats):
        """Update last known counts with manually entered stats.
        
        Args:
            stats: Dictionary of manually entered stats
        """
        current_date = datetime.now(BDT_TIMEZONE).strftime('%Y-%m-%d')
        
        # Load existing data
        last_known = DataManager.load_last_known_counts()
        
        # Update with new stats and mark as 'manual' mode
        for platform, count in stats.items():
            if count is not None:
                # Check if count increased
                old_count = last_known['counts'].get(platform)
                if old_count is None:
                    last_known['last_solved_dates'][platform] = DEFAULT_FUNNY_DATE
                elif count > old_count:
                    last_known['last_solved_dates'][platform] = current_date
                
                last_known['counts'][platform] = count
                last_known['dates'][platform] = current_date
                last_known['modes'][platform] = 'manual'
        
        # Save
        DataManager.save_last_known_counts(last_known)
