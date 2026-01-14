#!/usr/bin/env python3
"""
Script to check which platforms are responding correctly and verify solve counts.
This helps identify which sites are working vs failing when fetching statistics.
Author: MishkatIT
"""

import sys
import json
import argparse
from update_stats import PlatformStats


def check_all_sites():
    """Check all platforms and report their status."""
    fetcher = PlatformStats()
    
    platforms = {
        'Codeforces': fetcher.get_codeforces,
        'LeetCode': fetcher.get_leetcode,
        'Vjudge': fetcher.get_vjudge,
        'AtCoder': fetcher.get_atcoder,
        'CodeChef': fetcher.get_codechef,
        'CSES': fetcher.get_cses,
        'Toph': fetcher.get_toph,
        'LightOJ': fetcher.get_lightoj,
        'SPOJ': fetcher.get_spoj,
        'HackerRank': fetcher.get_hackerrank,
        'UVa': fetcher.get_uva,
        'HackerEarth': fetcher.get_hackerearth,
    }
    
    print("="*70)
    print("PLATFORM STATUS CHECK")
    print("="*70)
    print(f"{'Platform':<15} {'Status':<10} {'Count':<10} {'Details'}")
    print("-"*70)
    
    results = {
        'working': [],
        'failing': [],
        'counts': {}
    }
    
    for platform, fetch_func in platforms.items():
        try:
            count = fetch_func()
            if count is not None and count >= 0:
                status = "✓ OK"
                details = f"Successfully fetched {count} problems"
                results['working'].append(platform)
                results['counts'][platform] = count
                print(f"{platform:<15} {status:<10} {count:<10} {details}")
            else:
                status = "✗ FAIL"
                details = "Returned None or invalid count"
                results['failing'].append(platform)
                results['counts'][platform] = None
                print(f"{platform:<15} {status:<10} {'N/A':<10} {details}")
        except Exception as e:
            status = "✗ ERROR"
            details = str(e)[:40]
            results['failing'].append(platform)
            results['counts'][platform] = None
            print(f"{platform:<15} {status:<10} {'N/A':<10} {details}")
    
    print("-"*70)
    print(f"\nSummary:")
    print(f"  Working platforms: {len(results['working'])}/{len(platforms)}")
    print(f"  Failing platforms: {len(results['failing'])}/{len(platforms)}")
    
    if results['working']:
        print(f"\n  ✓ Working: {', '.join(results['working'])}")
    
    if results['failing']:
        print(f"\n  ✗ Failing: {', '.join(results['failing'])}")
    
    total = sum(c for c in results['counts'].values() if c is not None)
    print(f"\n  Total problems from working platforms: {total}")
    print("="*70)
    
    return results


def check_specific_site(platform_name):
    """Check a specific platform and return its count."""
    fetcher = PlatformStats()
    
    platform_map = {
        'codeforces': ('Codeforces', fetcher.get_codeforces),
        'leetcode': ('LeetCode', fetcher.get_leetcode),
        'vjudge': ('Vjudge', fetcher.get_vjudge),
        'atcoder': ('AtCoder', fetcher.get_atcoder),
        'codechef': ('CodeChef', fetcher.get_codechef),
        'cses': ('CSES', fetcher.get_cses),
        'toph': ('Toph', fetcher.get_toph),
        'lightoj': ('LightOJ', fetcher.get_lightoj),
        'spoj': ('SPOJ', fetcher.get_spoj),
        'hackerrank': ('HackerRank', fetcher.get_hackerrank),
        'uva': ('UVa', fetcher.get_uva),
        'hackerearth': ('HackerEarth', fetcher.get_hackerearth),
    }
    
    platform_key = platform_name.lower()
    
    if platform_key not in platform_map:
        print(f"Error: Unknown platform '{platform_name}'")
        print(f"Available platforms: {', '.join(p[0] for p in platform_map.values())}")
        return None
    
    display_name, fetch_func = platform_map[platform_key]
    
    print("="*70)
    print(f"CHECKING: {display_name}")
    print("="*70)
    
    try:
        print(f"Fetching statistics from {display_name}...", end=' ')
        count = fetch_func()
        
        if count is not None and count >= 0:
            print(f"✓\n")
            print(f"Status: SUCCESS")
            print(f"Problems Solved: {count}")
            print(f"\nThe platform is responding correctly.")
            print("="*70)
            return count
        else:
            print(f"✗\n")
            print(f"Status: FAILED")
            print(f"Problems Solved: N/A")
            print(f"\nThe platform did not return a valid count.")
            print("This could be due to:")
            print("  - Network connectivity issues")
            print("  - Platform API/website changes")
            print("  - Rate limiting or access restrictions")
            print("="*70)
            return None
    except Exception as e:
        print(f"✗\n")
        print(f"Status: ERROR")
        print(f"Error Details: {str(e)}")
        print(f"\nAn error occurred while fetching data.")
        print("="*70)
        return None


def validate_counts(expected_file='stats.json'):
    """Validate fetched counts against expected values from a JSON file."""
    try:
        with open(expected_file, 'r') as f:
            expected = json.load(f)
    except FileNotFoundError:
        print(f"Error: {expected_file} not found.")
        print("Run with --check-all first to establish baseline counts.")
        return False
    except json.JSONDecodeError:
        print(f"Error: {expected_file} is not valid JSON.")
        return False
    
    fetcher = PlatformStats()
    stats = fetcher.fetch_all_stats()
    
    print("="*70)
    print("VALIDATION REPORT")
    print("="*70)
    print(f"{'Platform':<15} {'Expected':<10} {'Actual':<10} {'Status'}")
    print("-"*70)
    
    all_match = True
    
    for platform in expected.keys():
        expected_count = expected.get(platform)
        actual_count = stats.get(platform)
        
        if expected_count is None and actual_count is None:
            status = "⚠ Both None"
            print(f"{platform:<15} {'N/A':<10} {'N/A':<10} {status}")
        elif expected_count is None:
            status = "⚠ No Expected"
            print(f"{platform:<15} {'N/A':<10} {actual_count or 'N/A':<10} {status}")
        elif actual_count is None:
            status = "✗ Fetch Failed"
            all_match = False
            print(f"{platform:<15} {expected_count:<10} {'N/A':<10} {status}")
        elif expected_count == actual_count:
            status = "✓ Match"
            print(f"{platform:<15} {expected_count:<10} {actual_count:<10} {status}")
        else:
            status = f"⚠ Diff ({actual_count - expected_count:+d})"
            all_match = False
            print(f"{platform:<15} {expected_count:<10} {actual_count:<10} {status}")
    
    print("-"*70)
    
    if all_match:
        print("\n✓ All platforms match expected counts!")
    else:
        print("\n⚠ Some platforms have differences or failures.")
        print("  This may indicate:")
        print("  - New problems were solved")
        print("  - Platform API issues")
        print("  - Network connectivity problems")
    
    print("="*70)
    return all_match


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(
        description='Check which competitive programming platforms are responding correctly.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --check-all              Check all platforms
  %(prog)s --site codeforces        Check only Codeforces
  %(prog)s --site leetcode          Check only LeetCode
  %(prog)s --validate               Validate against stats.json

Available platforms:
  Codeforces, LeetCode, Vjudge, AtCoder, CodeChef, CSES,
  Toph, LightOJ, SPOJ, HackerRank, UVa, HackerEarth
        """
    )
    
    parser.add_argument(
        '--check-all',
        action='store_true',
        help='Check all platforms and show their status'
    )
    
    parser.add_argument(
        '--site',
        type=str,
        help='Check a specific platform (e.g., codeforces, leetcode)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate fetched counts against expected values in stats.json'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not (args.check_all or args.site or args.validate):
        parser.print_help()
        return 0
    
    # Execute requested operation
    if args.validate:
        validate_counts()
    elif args.check_all:
        results = check_all_sites()
        if args.json:
            print("\nJSON Output:")
            print(json.dumps(results, indent=2))
    elif args.site:
        count = check_specific_site(args.site)
        if args.json and count is not None:
            print("\nJSON Output:")
            print(json.dumps({args.site: count}, indent=2))
    
    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        exit(1)
