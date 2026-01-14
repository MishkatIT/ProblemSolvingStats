#!/usr/bin/env python3
"""
Quick update script - Paste the solve counts directly here and run.
"""

import json
from datetime import datetime


# ============================================================================
# UPDATE THESE VALUES WITH CURRENT SOLVE COUNTS
# ============================================================================
# Visit each platform and update the numbers below, then run: python3 quick_update.py
# ============================================================================

CURRENT_STATS = {
    'Codeforces': 2470,      # https://codeforces.com/profile/MishkatIT
    'LeetCode': 393,         # https://leetcode.com/MishkatIT/
    'Vjudge': 346,           # https://vjudge.net/user/MishkatIT
    'AtCoder': 158,          # https://atcoder.jp/users/MishkatIT
    'CodeChef': 74,          # https://www.codechef.com/users/MishkatIT
    'CSES': 64,              # https://cses.fi/user/165802/
    'Toph': 35,              # https://toph.co/u/MishkatIT
    'LightOJ': 30,           # https://lightoj.com/user/mishkatit
    'SPOJ': 21,              # https://www.spoj.com/users/mishkatit/
    'HackerRank': 7,         # https://www.hackerrank.com/MishkatIT
    'UVa': 4,                # https://uhunt.onlinejudge.org/id/1615470
    'HackerEarth': 3,        # https://www.hackerearth.com/@MishkatIT
}

# ============================================================================


def main():
    """Update README with the stats defined above."""
    
    # Validate stats
    for platform, count in CURRENT_STATS.items():
        if not isinstance(count, int) or count < 0:
            print(f"Error: Invalid count for {platform}: {count}")
            return 1
    
    # Calculate total
    total = sum(CURRENT_STATS.values())
    
    print("="*60)
    print("CURRENT STATISTICS")
    print("="*60)
    for platform, count in CURRENT_STATS.items():
        print(f"{platform:15} : {count:5} problems")
    print("="*60)
    print(f"{'TOTAL':15} : {total:5} problems")
    print("="*60)
    
    # Save to JSON
    with open('stats.json', 'w') as f:
        json.dump(CURRENT_STATS, f, indent=2)
    print("\n✓ Statistics saved to stats.json")
    
    # Update README
    import update_readme
    print("\nUpdating README.md...")
    success = update_readme.update_readme(CURRENT_STATS)
    
    if success:
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"README.md has been updated with {total} total problems")
        print(f"Last updated: {datetime.now().strftime('%d %B %Y')}")
        print("\nNext steps:")
        print("  1. Review the changes: git diff README.md")
        print("  2. Commit: git add README.md && git commit -m 'Update statistics'")
        print("  3. Push: git push")
        print("="*60)
    else:
        print("\n✗ Failed to update README.md")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
