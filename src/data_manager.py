#!/usr/bin/env python
"""
Data manager for handling JSON file operations and data persistence.
"""

import json
from datetime import datetime
from . import (
    LAST_KNOWN_FILE, STATS_FILE, BDT_TIMEZONE, DEFAULT_FUNNY_DATE, USER_CONFIG
)


class DataManager:
    """Handles loading and saving of JSON data files."""
    
    @staticmethod
    def cleanup_cached_data(last_known_counts=None, force_save=True, user_config=None):
        """Clean up cached data for platforms no longer in config and handle username changes.
        
        Args:
            last_known_counts: Dictionary to clean up (loads from file if None)
            force_save: Whether to save changes immediately
            user_config: Current user config (uses global if None)
            
        Returns:
            Updated last_known_counts dictionary
        """
        if user_config is None:
            user_config = USER_CONFIG
        if last_known_counts is None:
            try:
                with open(LAST_KNOWN_FILE, 'r') as f:
                    last_known_counts = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                last_known_counts = {
                    'counts': {}, 'dates': {}, 'modes': {}, 
                    'last_solved_dates': {}, 'usernames': {}
                }
        
        # Ensure all required keys exist
        last_known_counts.setdefault('counts', {})
        last_known_counts.setdefault('dates', {})
        last_known_counts.setdefault('modes', {})
        last_known_counts.setdefault('last_solved_dates', {})
        last_known_counts.setdefault('usernames', {})
        last_known_counts.setdefault('ratings', {})
        
        # Clean up usernames for platforms no longer in config
        current_platforms = set(user_config.keys())
        stored_platforms = set(last_known_counts['usernames'].keys())
        removed_platforms = stored_platforms - current_platforms
        
        if removed_platforms:
            print(f"Removing cached data for platforms no longer in config: {removed_platforms}")
            for platform in removed_platforms:
                last_known_counts['counts'].pop(platform, None)
                last_known_counts['dates'].pop(platform, None)
                last_known_counts['modes'].pop(platform, None)
                last_known_counts['last_solved_dates'].pop(platform, None)
                last_known_counts['usernames'].pop(platform, None)
        
        # Check if any username has changed - if so, reset cache for that platform
        usernames_changed = False
        for platform, current_username in user_config.items():
            stored_username = last_known_counts['usernames'].get(platform)
            if stored_username and stored_username != current_username:
                print(f"Username changed for {platform}: {stored_username} -> {current_username}")
                print(f"Resetting cached data for {platform}")
                # Clear cached data for this platform
                last_known_counts['counts'].pop(platform, None)
                last_known_counts['dates'].pop(platform, None)
                last_known_counts['modes'].pop(platform, None)
                last_known_counts['last_solved_dates'].pop(platform, None)
                usernames_changed = True
            # Update stored username
            last_known_counts['usernames'][platform] = current_username
        
        # Save immediately if requested and changes were made
        if force_save and (usernames_changed or removed_platforms or last_known_counts):
            DataManager.save_last_known_counts(last_known_counts)
        
        return last_known_counts
    
    @staticmethod
    def load_last_known_counts():
        """Load the last known good counts from file.
        
        Returns:
            Dictionary with counts, dates, modes, and last_solved_dates
        """
        try:
            with open(LAST_KNOWN_FILE, 'r') as f:
                data = json.load(f)
                # Use the centralized cleanup method
                return DataManager.cleanup_cached_data(data, force_save=True)
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load last known counts: {e}")
        return {'counts': {}, 'dates': {}, 'modes': {}, 'last_solved_dates': {}, 'usernames': {}, 'ratings': {}}
    
    @staticmethod
    def save_last_known_counts(last_known_counts):
        """Save the current known good counts to file.
        
        Args:
            last_known_counts: Dictionary containing counts and metadata
        """
        try:
            with open(LAST_KNOWN_FILE, 'w', encoding='utf-8') as f:
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
            print(f"{STATS_FILE} not found. Please run auto_update.py first.")
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
            print(f"\n[OK] Saved statistics to {STATS_FILE}")
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
