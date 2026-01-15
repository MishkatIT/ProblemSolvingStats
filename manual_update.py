#!/usr/bin/env python3
"""
Interactive script to manually input and update problem-solving statistics.
Use this when automatic fetching is not possible.
"""

import json
import os
from datetime import datetime, timezone, timedelta


def get_manual_stats():
    """Manually input statistics for each platform."""
    print("="*60)
    print("MANUAL STATISTICS INPUT")
    print("="*60)
    print("\nPlease visit each platform and enter the current solve count.")
    print("Press Enter to skip a platform or enter 0 if not applicable.\n")
    
    platforms = {
        'Codeforces': 'https://codeforces.com/profile/MishkatIT',
        'LeetCode': 'https://leetcode.com/MishkatIT/',
        'Vjudge': 'https://vjudge.net/user/MishkatIT',
        'AtCoder': 'https://atcoder.jp/users/MishkatIT',
        'CodeChef': 'https://www.codechef.com/users/MishkatIT',
        'CSES': 'https://cses.fi/user/165802/',
        'Toph': 'https://toph.co/u/MishkatIT',
        'LightOJ': 'https://lightoj.com/user/mishkatit',
        'SPOJ': 'https://www.spoj.com/users/mishkatit/',
        'HackerRank': 'https://www.hackerrank.com/MishkatIT',
        'UVa': 'https://uhunt.onlinejudge.org/id/1615470',
        'HackerEarth': 'https://www.hackerearth.com/@MishkatIT',
    }
    
    stats = {}
    
    for platform, url in platforms.items():
        print(f"\n{platform}")
        print(f"  URL: {url}")
        while True:
            try:
                user_input = input(f"  Enter solve count (current: ?): ").strip()
                if user_input == '':
                    stats[platform] = None
                    print("  → Skipped")
                    break
                count = int(user_input)
                if count < 0:
                    print("  ✗ Count cannot be negative. Please try again.")
                    continue
                stats[platform] = count
                print(f"  ✓ Recorded: {count} problems")
                break
            except ValueError:
                print("  ✗ Invalid input. Please enter a number.")
    
    return stats


def save_last_known_counts(stats):
    """Save the manually entered statistics as last known counts."""
    # Use BDT timezone (UTC+6) for consistency
    bdt_tz = timezone(timedelta(hours=6))
    current_date = datetime.now(bdt_tz).strftime('%Y-%m-%d')
    
    # Load existing data
    last_known = {'counts': {}, 'dates': {}, 'modes': {}, 'last_solved_dates': {}}
    if os.path.exists('last_known_counts.json'):
        try:
            with open('last_known_counts.json', 'r') as f:
                last_known = json.load(f)
                # Ensure all required keys exist
                if 'modes' not in last_known:
                    last_known['modes'] = {}
                if 'last_solved_dates' not in last_known:
                    last_known['last_solved_dates'] = {}
        except (json.JSONDecodeError, IOError) as e:
            # Log the error but continue with default structure
            print(f"Warning: Could not load existing last_known_counts.json: {e}")
            print("Starting with fresh data structure.")
    
    # Update with new stats and mark as 'manual' mode
    for platform, count in stats.items():
        if count is not None:
            # Check if count increased (problem was solved)
            # Only update if count is strictly greater than previous count
            # This handles the case where counts may fluctuate due to platform changes
            old_count = last_known['counts'].get(platform)
            if old_count is None or count > old_count:
                # Count increased or first time seeing this platform, update last solved date
                last_known['last_solved_dates'][platform] = current_date
            # If count decreased or stayed the same, keep the existing last_solved_date
            
            last_known['counts'][platform] = count
            last_known['dates'][platform] = current_date
            last_known['modes'][platform] = 'manual'
    
    # Save
    with open('last_known_counts.json', 'w') as f:
        json.dump(last_known, f, indent=2)


def main():
    """Main function for manual statistics input."""
    print("\nThis script helps you manually update problem-solving statistics.")
    print("You'll need to visit each platform and enter the current solve count.\n")
    
    input("Press Enter to continue...")
    
    stats = get_manual_stats()
    
    # Calculate total
    total = sum(count for count in stats.values() if count is not None)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for platform, count in stats.items():
        if count is not None:
            print(f"{platform:15} : {count:5} problems")
        else:
            print(f"{platform:15} : Skipped")
    print("="*60)
    print(f"{'TOTAL':15} : {total:5} problems")
    print("="*60)
    
    # Save to JSON
    with open('stats.json', 'w') as f:
        json.dump(stats, f, indent=2)
    print("\n✓ Statistics saved to stats.json")
    
    # Save last known counts with dates
    save_last_known_counts(stats)
    print("✓ Last known counts updated")
    
    # Ask if user wants to update README
    update = input("\nUpdate README.md with these statistics? (y/n): ").strip().lower()
    if update == 'y':
        import update_readme
        # Load last_known_info for proper date tracking
        last_known_info = update_readme.load_last_known_info()
        success = update_readme.update_readme(stats, last_known_info=last_known_info, update_source='manual')
        if success:
            print("\n✓ README.md has been updated successfully!")
            bdt_tz = timezone(timedelta(hours=6))
            print(f"  Last updated: {datetime.now(bdt_tz).strftime('%d %B %Y')}")
        else:
            print("\n✗ Failed to update README.md")
    else:
        print("\nYou can update README.md later by running: python3 update_readme.py")
    
    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        exit(1)
