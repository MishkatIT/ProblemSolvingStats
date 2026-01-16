#!/usr/bin/env python3
"""
Interactive script to manually input and update problem-solving statistics.
Use this when automatic fetching is not possible.
"""

from datetime import datetime
from src.config import USER_CONFIG, PLATFORM_URL_TEMPLATES, BDT_TIMEZONE
from src.data_manager import DataManager


def get_manual_stats():
    """Manually input statistics for each platform."""
    print("="*60)
    print("MANUAL STATISTICS INPUT")
    print("="*60)
    print("\nPlease visit each platform and enter the current solve count.")
    print("Press Enter to skip a platform or enter 0 if not applicable.\n")
    
    # Generate platform URLs dynamically from USER_CONFIG and PLATFORM_URL_TEMPLATES
    platforms = {}
    for platform in USER_CONFIG.keys():
        template = PLATFORM_URL_TEMPLATES.get(platform)
        username = USER_CONFIG.get(platform)
        if template and username:
            platforms[platform] = template.format(username=username)
    
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
    DataManager.save_stats(stats)
    
    # Save last known counts with dates
    DataManager.update_manual_stats(stats)
    print("✓ Last known counts updated")
    
    # Ask if user wants to update README
    update = input("\nUpdate README.md with these statistics? (y/n): ").strip().lower()
    if update == 'y':
        import update_readme
        # Load last_known_info for proper date tracking
        last_known_info = DataManager.load_last_known_counts()
        success = update_readme.update_readme(stats, last_known_info=last_known_info, update_source='manual')
        if success:
            print("\n✓ README.md has been updated successfully!")
            print(f"  Last updated: {datetime.now(BDT_TIMEZONE).strftime('%d %B %Y')}")
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
