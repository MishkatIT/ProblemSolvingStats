#!/usr/bin/env python3
"""
Script to update README.md with the latest statistics from stats.json
"""

import json
import re
from datetime import datetime


def load_stats():
    """Load statistics from stats.json file."""
    try:
        with open('stats.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("stats.json not found. Please run update_stats.py first.")
        return None
    except json.JSONDecodeError:
        print("Error parsing stats.json")
        return None


def calculate_total(stats):
    """Calculate total solved problems."""
    total = 0
    for count in stats.values():
        if count is not None and isinstance(count, int):
            total += count
    return total


def calculate_percentage(solved, total):
    """Calculate percentage for progress bar."""
    if total == 0:
        return 0.0
    return round((solved / total) * 100, 1)


def update_readme(stats):
    """Update README.md with new statistics."""
    
    # Read current README
    try:
        with open('README.md', 'r') as f:
            readme_content = f.read()
    except FileNotFoundError:
        print("README.md not found")
        return False
    
    # Calculate total
    total = calculate_total(stats)
    
    if total == 0:
        print("No valid statistics found. Skipping README update.")
        return False
    
    # Get current date
    current_date = datetime.now().strftime("%d %B %Y")
    
    # Update last updated badge
    readme_content = re.sub(
        r'Last%20Updated-[^-]+-blue',
        f'Last%20Updated-{current_date.replace(" ", "%20")}-blue',
        readme_content
    )
    
    # Update total problems badge
    readme_content = re.sub(
        r'Total%20Solved-\d+-success',
        f'Total%20Solved-{total}-success',
        readme_content
    )
    
    # Platform mappings
    platform_mapping = {
        'Codeforces': ('Codeforces', 'red'),
        'LeetCode': ('LeetCode', 'yellow'),
        'Vjudge': ('Vjudge', 'blueviolet'),
        'AtCoder': ('AtCoder', 'orange'),
        'CodeChef': ('CodeChef', 'brown'),
        'CSES': ('CSES', 'lightgray'),
        'Toph': ('Toph', 'blue'),
        'LightOJ': ('LightOJ', 'yellow'),
        'SPOJ': ('SPOJ', 'green'),
        'HackerRank': ('HackerRank', 'brightgreen'),
        'UVa': ('UVa', 'blue'),
        'HackerEarth': ('HackerEarth', 'blue'),
    }
    
    # Platform patterns for updating counts in README table
    PLATFORM_PATTERNS = {
        'Codeforces': r'(🔴\s+Codeforces.*?<td align="center"><strong>)[^<]+',
        'LeetCode': r'(🟢\s+LeetCode.*?<td align="center"><strong>)[^<]+',
        'Vjudge': r'(🟣\s+Vjudge.*?<td align="center"><strong>)[^<]+',
        'AtCoder': r'(🟠\s+AtCoder.*?<td align="center"><strong>)[^<]+',
        'CodeChef': r'(🟤\s+CodeChef.*?<td align="center"><strong>)[^<]+',
        'CSES': r'(⚪\s+CSES.*?<td align="center"><strong>)[^<]+',
        'Toph': r'(🔵\s+Toph.*?<td align="center"><strong>)[^<]+',
        'LightOJ': r'(🟡\s+LightOJ.*?<td align="center"><strong>)[^<]+',
        'SPOJ': r'(🟩\s+SPOJ.*?<td align="center"><strong>)[^<]+',
        'HackerRank': r'(💚\s+HackerRank.*?<td align="center"><strong>)[^<]+',
        'UVa': r'(🔷\s+UVa.*?<td align="center"><strong>)[^<]+',
        'HackerEarth': r'(🌐\s+HackerEarth.*?<td align="center"><strong>)[^<]+',
    }
    
    # Update individual platform counts
    for platform, count in stats.items():
        if count is None:
            # Handle failed fetches - mark as "Will be updated manually"
            if platform in PLATFORM_PATTERNS:
                pattern = PLATFORM_PATTERNS[platform]
                replacement = rf'\g<1>⏳ Will be updated manually'
                readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)
            continue
        
        platform_name, color = platform_mapping.get(platform, (platform, 'blue'))
        percentage = calculate_percentage(count, total)
        
        # Update solved count in table
        if platform in PLATFORM_PATTERNS:
            pattern = PLATFORM_PATTERNS[platform]
            replacement = rf'\g<1>{count}'
            readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL)
        
        # Update progress percentage
        progress_pattern = rf'({platform_name}.*?Progress-)\d+\.?\d*%25'
        progress_replacement = rf'\g<1>{percentage}%25'
        readme_content = re.sub(progress_pattern, progress_replacement, readme_content, flags=re.DOTALL)
    
    # Update total in footer
    readme_content = re.sub(
        r'(<td align="center"><strong style="font-size: 1\.2em;">)\d+',
        rf'\g<1>{total}',
        readme_content
    )
    
    # Update key highlights if Codeforces is the top platform
    if stats.get('Codeforces') is not None:
        cf_count = stats['Codeforces']
        readme_content = re.sub(
            r'(\| )\d+( Problems \|)',
            rf'\g<1>{cf_count}\g<2>',
            readme_content
        )
    
    # Write updated README
    try:
        with open('README.md', 'w') as f:
            f.write(readme_content)
        print(f"✓ README.md updated successfully!")
        print(f"  Total problems: {total}")
        print(f"  Last updated: {current_date}")
        return True
    except Exception as e:
        print(f"Error writing README.md: {e}")
        return False


def main():
    """Main function."""
    print("Loading statistics...")
    stats = load_stats()
    
    if stats is None:
        return 1
    
    print("\nStatistics loaded:")
    for platform, count in stats.items():
        if count is not None:
            print(f"  {platform}: {count}")
    
    print("\nUpdating README.md...")
    success = update_readme(stats)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
