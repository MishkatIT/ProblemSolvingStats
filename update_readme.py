#!/usr/bin/env python3
"""
Script to update README.md with the latest statistics from stats.json
"""

import json
import re
import os
import sys
from datetime import datetime


def load_stats():
    """Load statistics from stats.json file."""
    try:
        with open('stats.json', 'r', encoding='utf-8') as f:
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
            with open('last_known_counts.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load last known counts: {e}")
    return {'counts': {}, 'dates': {}}


def _read_text_file(path):
    """Read a text file using UTF-8 (with BOM support).

    On Windows, the default encoding can be cp1252 which may fail for UTF-8 files.
    """
    for encoding in ('utf-8', 'utf-8-sig'):
        try:
            with open(path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # Last resort: replace undecodable bytes so the update can proceed.
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read()


def calculate_total(stats):
    """Calculate total solved problems."""
    total = 0
    for count in stats.values():
        if count is not None and isinstance(count, int):
            total += count
    return total


def _format_human_date(date_str):
    """Convert an ISO date (YYYY-MM-DD) to a human-readable date.

    Falls back to the original string if parsing fails.
    """
    if not date_str or date_str == 'unknown':
        return 'unknown'
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %B %Y')
    except Exception:
        return date_str


def _extract_first_int(text):
    match = re.search(r'\d+', text or '')
    return int(match.group(0)) if match else None


def _upsert_update_metadata_block(readme_content, *, current_date_human, update_source):
    """Insert or update a stable metadata block in README.

    This prevents regex-based drift and makes updates idempotent.
    """
    update_source_title = {
        'manual': 'Manual',
        'automatic': 'Automatic',
    }.get((update_source or '').strip().lower(), 'Unknown')

    block = (
        '<!-- UPDATE_METADATA_START -->\n'
        f'<p align="center"><strong>Updated:</strong> {current_date_human} '
        f'• {update_source_title}</p>\n'
        '<!-- UPDATE_METADATA_END -->'
    )

    # Ensure the metadata block is inserted at the top of the README, after the first heading.
    heading_match = re.search(r'^(# .+?)\n', readme_content, flags=re.MULTILINE)
    if heading_match:
        insert_at = heading_match.end()
        if '<!-- UPDATE_METADATA_START -->' in readme_content and '<!-- UPDATE_METADATA_END -->' in readme_content:
            return re.sub(
                r'<!-- UPDATE_METADATA_START -->.*?<!-- UPDATE_METADATA_END -->',
                block,
                readme_content,
                flags=re.DOTALL,
                count=1,
            )
        else:
            # Replace any existing block with the new block
            readme_content = re.sub(
                r'<!-- UPDATE_METADATA_START -->.*?<!-- UPDATE_METADATA_END -->',
                block,
                readme_content,
                flags=re.DOTALL
            )
            return readme_content[:insert_at] + "\n\n" + block + "\n" + readme_content[insert_at:]

    # Fallback: insert at the very beginning if no heading is found.
    if '<!-- UPDATE_METADATA_START -->' in readme_content and '<!-- UPDATE_METADATA_END -->' in readme_content:
        return re.sub(
            r'<!-- UPDATE_METADATA_START -->.*?<!-- UPDATE_METADATA_END -->',
            block,
            readme_content,
            flags=re.DOTALL,
            count=1,
        )
    else:
        return block + "\n\n" + readme_content


def calculate_percentage(solved, total):
    """Calculate percentage for progress bar."""
    if total == 0:
        return 0.0
    return round((solved / total) * 100, 1)


def update_readme(stats, last_known_info=None, update_source=None):
    """Update README.md with new statistics.
    
    Args:
        stats: Dictionary of platform stats (can contain None values)
        last_known_info: Optional dict with 'counts' and 'dates' for platforms
        update_source: 'manual' or 'automatic' (used for README metadata)
    """
    
    # Read current README
    try:
        readme_content = _read_text_file('README.md')
    except FileNotFoundError:
        print("README.md not found")
        return False
    
    # Load last known info if not provided
    if last_known_info is None:
        last_known_info = load_last_known_info()
    
    # Get current date
    now = datetime.now()
    current_date = now.strftime("%d %B %Y")
    today_iso = now.strftime('%Y-%m-%d')
    
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
    # Match everything between <strong> and </strong> tags with 3 capture groups
    # Updated to match favicon structure instead of emojis
    PLATFORM_PATTERNS = {
        'Codeforces': r'(<strong>Codeforces</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'LeetCode': r'(<strong>LeetCode</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'Vjudge': r'(<strong>Vjudge</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'AtCoder': r'(<strong>AtCoder</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'CodeChef': r'(<strong>CodeChef</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'CSES': r'(<strong>CSES</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'Toph': r'(<strong>Toph</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'LightOJ': r'(<strong>LightOJ</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'SPOJ': r'(<strong>SPOJ</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'HackerRank': r'(<strong>HackerRank</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'UVa': r'(<strong>UVa</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
        'HackerEarth': r'(<strong>HackerEarth</strong>.*?<td align="center"><strong>)(.*?)(</strong>)',
    }
    
    # Determine which platforms were freshly updated vs using last known
    last_known_counts = last_known_info.get('counts', {})
    last_known_dates = last_known_info.get('dates', {})
    last_known_modes = last_known_info.get('modes', {})

    # Build effective counts for totals/progress (prefer stats, then last-known, then README)
    effective_counts = {}
    for platform in PLATFORM_PATTERNS.keys():
        value = stats.get(platform)
        if isinstance(value, int):
            effective_counts[platform] = value
            continue

        cached = last_known_counts.get(platform)
        if isinstance(cached, int):
            effective_counts[platform] = cached
            continue

        # Last resort: parse existing README table value
        pattern = PLATFORM_PATTERNS.get(platform)
        match = re.search(pattern, readme_content, flags=re.DOTALL) if pattern else None
        if match:
            parsed = _extract_first_int(match.group(2))
            if parsed is not None:
                effective_counts[platform] = parsed
                continue

        effective_counts[platform] = None

    # Calculate total from effective counts
    total = sum(v for v in effective_counts.values() if isinstance(v, int))

    if total == 0:
        print("No valid statistics found. Skipping README update.")
        return False

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
    
    # Add/update the explicit update metadata block (date + manual/automatic)
    readme_content = _upsert_update_metadata_block(
        readme_content,
        current_date_human=current_date,
        update_source=update_source,
    )

    # Update individual platform counts and progress for all known platforms.
    # Requirement: always show per-platform last-updated date.
    for platform in PLATFORM_PATTERNS.keys():
        pattern = PLATFORM_PATTERNS[platform]
        match = re.search(pattern, readme_content, flags=re.DOTALL)
        if not match:
            continue

        # Pick count to display: effective count if known, else keep existing number in README.
        count_effective = effective_counts.get(platform)
        if not isinstance(count_effective, int):
            count_from_readme = _extract_first_int(match.group(2))
            if count_from_readme is None:
                continue
            count_effective = count_from_readme

        platform_name, _color = platform_mapping.get(platform, (platform, 'blue'))
        percentage = calculate_percentage(count_effective, total)

        # Pick date to display: last-known date if available; else today if we have a count; else unknown.
        raw_date = last_known_dates.get(platform)
        if raw_date:
            date_str = _format_human_date(raw_date)
        else:
            date_str = current_date if isinstance(count_effective, int) else 'unknown'

        # Get the mode for this specific platform
        platform_mode = last_known_modes.get(platform, 'automatic')
        # Capitalize first letter for display
        mode_display = platform_mode.capitalize() if platform_mode else 'Auto'
        # Choose badge color based on mode
        mode_color = 'orange' if platform_mode == 'manual' else 'green'

        replacement = rf'\g<1>{count_effective}\g<3>'
        readme_content = re.sub(pattern, replacement, readme_content, flags=re.DOTALL, count=1)

        # Update progress percentage
        progress_pattern = rf'({platform_name}.*?Progress-)\d+\.?\d*%25'
        progress_replacement = rf'\g<1>{percentage}%25'
        readme_content = re.sub(progress_pattern, progress_replacement, readme_content, flags=re.DOTALL)

        # Update the "Updated On" column and "Mode" column for each platform
        # Pattern matches: Progress badge -> Updated On date -> Mode badge
        date_and_mode_pattern = rf'({platform_name}.*?Progress-{percentage}%25.*?<td align="left">)[^<]*</td>\s*<td align="center">.*?</td>'
        date_and_mode_replacement = rf'\g<1>{date_str}</td>\n      <td align="center"><img src="https://img.shields.io/badge/{mode_display}-{mode_color}?style=flat" alt="{mode_display}"/></td>'
        readme_content = re.sub(date_and_mode_pattern, date_and_mode_replacement, readme_content, flags=re.DOTALL)
    
    # Update total in footer
    readme_content = re.sub(
        r'(<td align="center"><strong style="font-size: 1\.2em;">)\d+',
        rf'\g<1>{total}',
        readme_content
    )
    
    # Update the "Updated On" column in the footer (total row)
    # Pattern is flexible to handle potential rounding differences in percentage
    readme_content = re.sub(
        r'(TOTAL.*?<td align="center"><strong>\d+(?:\.\d+)?%</strong></td>\s*<td align="center">).*?</td>',
        rf'\g<1>{current_date}</td>',
        readme_content,
        flags=re.DOTALL
    )
    
    # Update key highlights if Codeforces is the top platform
    if isinstance(effective_counts.get('Codeforces'), int):
        cf_count = effective_counts['Codeforces']
        readme_content = re.sub(
            r'(\| )\d+( Problems \|)',
            rf'\g<1>{cf_count}\g<2>',
            readme_content
        )
    
    # Write updated README
    try:
        with open('README.md', 'w', encoding='utf-8', newline='\n') as f:
            f.write(readme_content)
        print(f"✓ README.md updated successfully!")
        print(f"  Total problems: {total}")
        print(f"  Updated on {current_date}")
        return True
    except Exception as e:
        print(f"Error writing README.md: {e}")
        return False


def main():
    """Main function."""
    # Allow passing update source via CLI or env var (useful for GitHub Actions).
    update_source = os.environ.get('UPDATE_SOURCE')
    if len(sys.argv) >= 3 and sys.argv[1] in ('--source', '-s'):
        update_source = sys.argv[2]

    print("Loading statistics...")
    stats = load_stats()
    
    if stats is None:
        return 1
    
    print("\nStatistics loaded:")
    for platform, count in stats.items():
        if count is not None:
            print(f"  {platform}: {count}")
    
    print("\nUpdating README.md...")
    success = update_readme(stats, update_source=update_source)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
