#!/usr/bin/env python3
"""
Script to update README.md with the latest statistics from stats.json
"""

import json
import re
import os
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


def load_last_known_info():
    """Load last known counts and dates."""
    try:
        if os.path.exists('last_known_counts.json'):
            with open('last_known_counts.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load last known counts: {e}")
    return {'counts': {}, 'dates': {}}


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


def update_readme(stats, last_known_info=None):
    """Update README.md with new statistics.
    
    Args:
        stats: Dictionary of platform stats (can contain None values)
        last_known_info: Optional dict with 'counts' and 'dates' for platforms
    """
    
    # Read current README
    try:
        with open('README.md', 'r') as f:
            readme_content = f.read()
    except FileNotFoundError:
        print("README.md not found")
        return False
    
    # Load last known info if not provided
    if last_known_info is None:
        last_known_info = load_last_known_info()
    
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
    
    # Note format for platforms using last known counts
    NOT_UPDATED_NOTE = '<br/><small>(last updated: {date})</small>'
    NOT_UPDATED_TEXT = '(last updated:'  # Text portion for checking
    NUMBER_PATTERN = r'\d+'  # Pattern to extract numbers
    
    # Platform patterns for updating counts in README table
    # Match everything between <strong> and </strong> tags with 3 capture groups
    PLATFORM_PATTERNS = {
        'Codeforces': r'(🔴\s+Codeforces.*?<td align="center"><strong>)(.*?)(</strong>)',
        'LeetCode': r'(🟢\s+LeetCode.*?<td align="center"><strong>)(.*?)(</strong>)',
        'Vjudge': r'(🟣\s+Vjudge.*?<td align="center"><strong>)(.*?)(</strong>)',
        'AtCoder': r'(🟠\s+AtCoder.*?<td align="center"><strong>)(.*?)(</strong>)',
        'CodeChef': r'(🟤\s+CodeChef.*?<td align="center"><strong>)(.*?)(</strong>)',
        'CSES': r'(⚪\s+CSES.*?<td align="center"><strong>)(.*?)(</strong>)',
        'Toph': r'(🔵\s+Toph.*?<td align="center"><strong>)(.*?)(</strong>)',
        'LightOJ': r'(🟡\s+LightOJ.*?<td align="center"><strong>)(.*?)(</strong>)',
        'SPOJ': r'(🟩\s+SPOJ.*?<td align="center"><strong>)(.*?)(</strong>)',
        'HackerRank': r'(💚\s+HackerRank.*?<td align="center"><strong>)(.*?)(</strong>)',
        'UVa': r'(🔷\s+UVa.*?<td align="center"><strong>)(.*?)(</strong>)',
        'HackerEarth': r'(🌐\s+HackerEarth.*?<td align="center"><strong>)(.*?)(</strong>)',
    }
    
    # Determine which platforms were freshly updated vs using last known
    last_known_counts = last_known_info.get('counts', {})
    last_known_dates = last_known_info.get('dates', {})
    
    # Update individual platform counts
    for platform, count in stats.items():
        if count is None:
            # Handle failed fetches - keep the last count and add a note
            if platform in PLATFORM_PATTERNS:
                pattern = PLATFORM_PATTERNS[platform]
                # Extract the current count from README
                match = re.search(pattern, readme_content, flags=re.DOTALL)
                if match:
                    current_value = match.group(2)  # The content between <strong> and </strong>
                    # Check if note already exists
                    if NOT_UPDATED_TEXT in current_value:
                        # Already has note, keep as is
                        continue
                    else:
                        # Extract just the number (handles any HTML/whitespace before it)
                        number_match = re.search(NUMBER_PATTERN, current_value)
                        if number_match:
                            number = number_match.group(0)
                            # Keep the existing count and add note
                            date_str = last_known_dates.get(platform, 'unknown')
                            note = NOT_UPDATED_NOTE.format(date=date_str)
                            replacement = rf'\g<1>{number} {note}\g<3>'
                            readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL, count=1)
            continue
        
        platform_name, color = platform_mapping.get(platform, (platform, 'blue'))
        percentage = calculate_percentage(count, total)
        
        # Check if this is a fresh update or using last known count
        is_fresh_update = (platform not in last_known_counts or 
                          last_known_counts[platform] != count or
                          last_known_dates.get(platform) == datetime.now().strftime('%Y-%m-%d'))
        
        # Update solved count in table
        if platform in PLATFORM_PATTERNS:
            pattern = PLATFORM_PATTERNS[platform]
            
            if is_fresh_update:
                # Remove any "not updated" notes when we have a fresh fetch
                replacement = rf'\g<1>{count}\g<3>'
            else:
                # This is using last known count, add the date note
                date_str = last_known_dates.get(platform, 'unknown')
                note = NOT_UPDATED_NOTE.format(date=date_str)
                replacement = rf'\g<1>{count} {note}\g<3>'
            
            readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL, count=1)
        
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
