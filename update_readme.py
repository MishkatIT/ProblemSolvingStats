#!/usr/bin/env python3
"""
Script to update README.md with the latest statistics from stats.json
"""

import json
import re
import os
import sys
from datetime import datetime, timezone, timedelta


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
                data = json.load(f)
                # Ensure last_solved_dates exists
                if 'last_solved_dates' not in data:
                    data['last_solved_dates'] = {}
                return data
    except Exception as e:
        print(f"Warning: Could not load last known counts: {e}")
    return {'counts': {}, 'dates': {}, 'last_solved_dates': {}}


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


def _replace_marked_section(content, marker_name, new_content):
    """Replace content between HTML comment markers.
    
    Args:
        content: The full content string
        marker_name: Name of the section (e.g., 'STATS_TABLE')
        new_content: New content to insert (without markers)
    
    Returns:
        Updated content string
    """
    start_marker = f'<!-- AUTO_GENERATED_SECTION_START: {marker_name} -->'
    end_marker = f'<!-- AUTO_GENERATED_SECTION_END: {marker_name} -->'
    
    pattern = f'{re.escape(start_marker)}.*?{re.escape(end_marker)}'
    replacement = f'{start_marker}\n{new_content}\n{end_marker}'
    
    # If markers exist, replace; otherwise insert before a known section
    if start_marker in content and end_marker in content:
        return re.sub(pattern, replacement, content, flags=re.DOTALL, count=1)
    else:
        # Markers don't exist yet - will be handled separately
        return content


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


def format_platform_list(platforms):
    """Format a list of platforms into a human-readable string.
    
    Args:
        platforms: List of platform names (should be sorted)
        
    Returns:
        Formatted string (e.g., "Platform1", "Platform1 and Platform2", 
        "Platform1, Platform2, and Platform3")
    """
    if not platforms:
        return "**No platforms**"
    elif len(platforms) == 1:
        return f"**{platforms[0]}**"
    elif len(platforms) == 2:
        return f"**{platforms[0]}** and **{platforms[1]}**"
    else:
        # Multiple platforms: "Platform1, Platform2, and Platform3"
        formatted_list = ", ".join([f"**{p}**" for p in platforms[:-1]])
        return f"{formatted_list}, and **{platforms[-1]}**"


def generate_latest_solve_section(last_known_info):
    """Generate the Latest Solve section showing the most recent activity.
    
    Args:
        last_known_info: Dictionary containing 'last_solved_dates' with platform dates
        
    Returns:
        String containing the markdown section for latest solve information
    """
    last_solved_dates = last_known_info.get('last_solved_dates', {})
    
    if not last_solved_dates:
        return ""
    
    # Find the most recent solve date and all platforms that solved on that date
    date_to_platforms = {}
    for platform, date in last_solved_dates.items():
        if date:
            if date not in date_to_platforms:
                date_to_platforms[date] = []
            date_to_platforms[date].append(platform)
    
    if not date_to_platforms:
        return ""
    
    # Get the most recent date
    most_recent_date = max(date_to_platforms.keys())
    platforms_solved = sorted(date_to_platforms[most_recent_date])
    
    # Format the date
    formatted_date = _format_human_date(most_recent_date)
    
    # Generate platform list
    platform_text = format_platform_list(platforms_solved)
    
    section = f"""## 🎯 Latest Solve

<div align="center">

| 📅 Last Solved | 🏆 Platform(s) |
|:-------------:|:-------------:|
| **{formatted_date}** | {platform_text} |

</div>

---
"""
    return section


def generate_platform_last_solved_table(last_known_info):
    """Generate a table showing last solved date for each platform.
    
    Args:
        last_known_info: Dictionary containing 'last_solved_dates' with platform dates
        
    Returns:
        String containing the markdown table for all platform last solved dates
    """
    last_solved_dates = last_known_info.get('last_solved_dates', {})
    
    if not last_solved_dates:
        return ""
    
    # Get counts for sorting
    counts = last_known_info.get('counts', {})
    
    # All platforms
    all_platforms = [
        'Codeforces', 'LeetCode', 'Vjudge', 'AtCoder', 'CodeChef', 
        'CSES', 'Toph', 'LightOJ', 'SPOJ', 'HackerRank', 'UVa', 'HackerEarth'
    ]
    
    # Filter platforms that have last_solved_dates and sort by count (descending)
    platform_order = sorted(
        [p for p in all_platforms if p in last_solved_dates],
        key=lambda p: counts.get(p, 0),
        reverse=True
    )
    
    # Platform favicon/logo URLs (matching the main stats table exactly)
    platform_logos = {
        'Codeforces': ('https://cdn.iconscout.com/icon/free/png-16/codeforces-3628695-3029920.png', True),
        'LeetCode': ('https://leetcode.com/favicon-16x16.png', True),
        'Vjudge': ('https://vjudge.net/favicon.ico', True),
        'AtCoder': ('https://atcoder.jp/favicon.ico', True),
        'CodeChef': ('https://cdn.codechef.com/sites/all/themes/abessive/cc-logo.png', True),
        'CSES': ('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBmaWxsPSIjODA4MDgwIiBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTEgMTcuOTNjLTMuOTUtLjQ5LTctMy44NS03LTcuOTMgMC0uNjIuMDgtMS4yMS4yMS0xLjc5TDkgMTV2MWMwIDEuMS45IDIgMiAydjEuOTN6bTYuOS0yLjU0Yy0uMjYtLjgxLTEtMS4zOS0xLjktMS4zOWgtMXYtM2MwLS41NS0uNDUtMS0xLTFIOHYtMmgyYy41NSAwIDEtLjQ1IDEtMVY3aDJjMS4xIDAgMi0uOSAyLTJ2LS40MWMyLjkzIDEuMTkgNSA0LjA2IDUgNy40MSAwIDIuMDgtLjggMy45Ny0yLjEgNS4zOXoiLz48L3N2Zz4=', False),
        'Toph': ('https://toph.co/favicon.ico', True),
        'LightOJ': ('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSq0TU63ijLZ_PaQre3dgnYmJ811t41O-RcHg&s', False),
        'SPOJ': ('https://www.spoj.com/favicon.ico', True),
        'HackerRank': ('https://hrcdn.net/fcore/assets/favicon-ddc852f75a.png', True),
        'UVa': ('https://www.google.com/s2/favicons?domain=onlinejudge.org&sz=16', True),
        'HackerEarth': ('https://www.google.com/s2/favicons?domain=hackerearth.com&sz=16', True)
    }
    
    # Build table rows
    rows = []
    for platform in platform_order:
        if platform in last_solved_dates:
            date = last_solved_dates[platform]
            if date:
                formatted_date = _format_human_date(date)
            else:
                formatted_date = "_Not recorded_"
            
            # Add platform with logo (matching main stats table format)
            logo_url, use_onerror = platform_logos.get(platform, ('', False))
            onerror_attr = ' onerror="this.style.display=\'none\'"' if use_onerror else ''
            platform_cell = f'<img src="{logo_url}" alt="{platform}" width="16" height="16"{onerror_attr}/> <strong>{platform}</strong>'
            rows.append(f"| {platform_cell} | {formatted_date} |")
    
    if not rows:
        return ""
    
    section = f"""## 📅 Last Solved by Platform

<div align="center">

| 🏆 Platform | 📅 Last Solved |
|:----------|:--------------|
{chr(10).join(rows)}

</div>

---
"""
    return section


def generate_platform_statistics_table(effective_counts, current_date, today_iso, stats, last_known_info):
    """Generate the main platform statistics table sorted by solve count.
    
    Args:
        effective_counts: Dictionary of effective counts for each platform
        current_date: Current date string
        today_iso: Today's date in ISO format
        stats: Dictionary of platform stats
        last_known_info: Last known information
        
    Returns:
        String containing the HTML table for platform statistics
    """
    # Platform metadata
    platform_profiles = {
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
        'HackerEarth': 'https://www.hackerearth.com/@MishkatIT'
    }
    
    platform_logos = {
        'Codeforces': ('https://cdn.iconscout.com/icon/free/png-16/codeforces-3628695-3029920.png', True, 'red'),
        'LeetCode': ('https://leetcode.com/favicon-16x16.png', True, 'yellow'),
        'Vjudge': ('https://vjudge.net/favicon.ico', True, 'blueviolet'),
        'AtCoder': ('https://atcoder.jp/favicon.ico', True, 'orange'),
        'CodeChef': ('https://cdn.codechef.com/sites/all/themes/abessive/cc-logo.png', True, 'brown'),
        'CSES': ('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBmaWxsPSIjODA4MDgwIiBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnptLTEgMTcuOTNjLTMuOTUtLjQ5LTctMy44NS03LTcuOTMgMC0uNjIuMDgtMS4yMS4yMS0xLjc5TDkgMTV2MWMwIDEuMS45IDIgMiAydjEuOTN6bTYuOS0yLjU0Yy0uMjYtLjgxLTEtMS4zOS0xLjktMS4zOWgtMXYtM2MwLS41NS0uNDUtMS0xLTFIOHYtMmgyYy41NSAwIDEtLjQ1IDEtMVY3aDJjMS4xIDAgMi0uOSAyLTJ2LS40MWMyLjkzIDEuMTkgNSA0LjA2IDUgNy40MSAwIDIuMDgtLjggMy45Ny0yLjEgNS4zOXoiLz48L3N2Zz4=', False, 'lightgray'),
        'Toph': ('https://toph.co/favicon.ico', True, 'blue'),
        'LightOJ': ('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSq0TU63ijLZ_PaQre3dgnYmJ811t41O-RcHg&s', False, 'yellow'),
        'SPOJ': ('https://www.spoj.com/favicon.ico', True, 'green'),
        'HackerRank': ('https://hrcdn.net/fcore/assets/favicon-ddc852f75a.png', True, 'brightgreen'),
        'UVa': ('https://www.google.com/s2/favicons?domain=onlinejudge.org&sz=16', True, 'blue'),
        'HackerEarth': ('https://www.google.com/s2/favicons?domain=hackerearth.com&sz=16', True, 'blue')
    }
    
    # Sort platforms by effective count (descending)
    sorted_platforms = sorted(
        effective_counts.keys(),
        key=lambda p: effective_counts.get(p, 0) if isinstance(effective_counts.get(p), int) else 0,
        reverse=True
    )
    
    # Calculate total
    total = sum(v for v in effective_counts.values() if isinstance(v, int))
    
    # Get last known info
    last_known_dates = last_known_info.get('dates', {})
    last_known_modes = last_known_info.get('modes', {})
    
    # Build table rows
    rows = []
    for platform in sorted_platforms:
        count = effective_counts.get(platform)
        if not isinstance(count, int):
            continue
            
        profile_url = platform_profiles.get(platform, '#')
        logo_url, use_onerror, color = platform_logos.get(platform, ('', False, 'blue'))
        
        onerror_attr = ' onerror="this.style.display=\'none\'"' if use_onerror else ''
        percentage = calculate_percentage(count, total)
        
        # Determine date and mode
        platform_mode = last_known_modes.get(platform, 'automatic')
        raw_date = last_known_dates.get(platform)
        
        is_fresh_today = (platform in stats and 
                         stats[platform] is not None and 
                         raw_date == today_iso)
        
        if is_fresh_today:
            date_str = current_date
        else:
            if raw_date:
                date_str = _format_human_date(raw_date)
            else:
                date_str = current_date if isinstance(count, int) else 'unknown'
        
        mode_display = platform_mode.capitalize() if platform_mode else 'Auto'
        mode_color = 'orange' if platform_mode == 'manual' else 'green'
        
        row = f'''    <tr>
      <td><img src="{logo_url}" width="16" height="16"{onerror_attr}/> <strong>{platform}</strong></td>
      <td><a href="{profile_url}">MishkatIT</a></td>
      <td align="center"><strong>{count}</strong></td>
      <td><img src="https://img.shields.io/badge/Progress-{percentage}%25-{color}?style=flat-square" alt="{platform} Progress"/></td>
      <td align="left">{date_str}</td>
      <td align="center"><img src="https://img.shields.io/badge/{mode_display}-{mode_color}?style=flat" alt="{mode_display}"/></td>
    </tr>'''
        rows.append(row)
    
    # Build complete table
    table = f'''<table align="center">
  <thead>
    <tr>
      <th>🎯 Platform</th>
      <th>👤 Profile</th>
      <th>✅ Solved</th>
      <th>📈 Progress</th>
      <th>📅 Updated On</th>
      <th>🔄 Mode</th>
    </tr>
  </thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
  <tfoot>
    <tr>
      <td colspan="2" align="center"><strong>🎖️ TOTAL</strong></td>
      <td align="center"><strong style="font-size: 1.2em;">{total}</strong></td>
      <td align="center"><strong>100%</strong></td>
      <td align="center">{current_date}</td>
      <td></td>
    </tr>
  </tfoot>
</table>'''
    
    return table


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
    
    # Get current date in BDT (UTC+6)
    bdt_tz = timezone(timedelta(hours=6))
    now = datetime.now(bdt_tz)
    current_date = now.strftime("%d %B %Y")
    current_date_with_time = now.strftime("%d %B %Y at %I:%M:%S %p")
    today_iso = now.strftime('%Y-%m-%d')
    
    # All platforms we track
    ALL_PLATFORMS = [
        'Codeforces', 'LeetCode', 'Vjudge', 'AtCoder', 'CodeChef',
        'CSES', 'Toph', 'LightOJ', 'SPOJ', 'HackerRank', 'UVa', 'HackerEarth'
    ]
    
    # Determine which platforms were freshly updated vs using last known
    last_known_counts = last_known_info.get('counts', {})
    last_known_dates = last_known_info.get('dates', {})
    last_known_modes = last_known_info.get('modes', {})

    # Build effective counts for totals/progress (prefer stats, then last-known)
    effective_counts = {}
    for platform in ALL_PLATFORMS:
        value = stats.get(platform)
        if isinstance(value, int):
            effective_counts[platform] = value
            continue

        cached = last_known_counts.get(platform)
        if isinstance(cached, int):
            effective_counts[platform] = cached
            continue

        # Platform not found in stats or cache
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
        current_date_human=current_date_with_time,
        update_source=update_source,
    )

    # Regenerate the main platform statistics table (sorted by solve count)
    new_table = generate_platform_statistics_table(effective_counts, current_date, today_iso, stats, last_known_info)
    
    # Replace the table using markers (or fallback to pattern matching)
    if '<!-- AUTO_GENERATED_SECTION_START: STATS_TABLE -->' in readme_content:
        readme_content = _replace_marked_section(readme_content, 'STATS_TABLE', new_table)
    else:
        # Fallback: wrap existing table with markers for future updates
        table_pattern = r'(<table align="center">.*?</table>)'
        wrapped_table = f'<!-- AUTO_GENERATED_SECTION_START: STATS_TABLE -->\n{new_table}\n<!-- AUTO_GENERATED_SECTION_END: STATS_TABLE -->'
        readme_content = re.sub(table_pattern, wrapped_table, readme_content, flags=re.DOTALL, count=1)
    
    # Update Key Highlights section dynamically
    # Find the top platform (highest solve count)
    sorted_by_count = sorted(
        [(p, c) for p, c in effective_counts.items() if isinstance(c, int)],
        key=lambda x: x[1],
        reverse=True
    )
    
    if sorted_by_count:
        top_platform, top_count = sorted_by_count[0]
        active_platforms = len([c for c in effective_counts.values() if isinstance(c, int) and c > 0])
        
        # Generate Key Highlights section
        key_highlights = f"""## 🌟 Key Highlights

<div align="center">

| 🥇 Top Platform | 🎯 Main Focus | 📚 Platforms Active |
|:---------------:|:-------------:|:------------------:|
| **{top_platform}** | **Competitive Programming** | **{active_platforms}** |
| {top_count} Problems | Algorithm Mastery | Multi-Platform |

</div>"""
        
        # Replace Key Highlights section
        if '<!-- AUTO_GENERATED_SECTION_START: KEY_HIGHLIGHTS -->' in readme_content:
            readme_content = _replace_marked_section(readme_content, 'KEY_HIGHLIGHTS', key_highlights)
        elif '## 🌟 Key Highlights' in readme_content:
            # Wrap existing section with markers
            pattern = r'(## 🌟 Key Highlights.*?</div>)'
            wrapped_section = f'<!-- AUTO_GENERATED_SECTION_START: KEY_HIGHLIGHTS -->\n{key_highlights}\n<!-- AUTO_GENERATED_SECTION_END: KEY_HIGHLIGHTS -->'
            readme_content = re.sub(pattern, wrapped_section, readme_content, flags=re.DOTALL, count=1)
    
    # Insert or update the Latest Solve section
    latest_solve_section = generate_latest_solve_section(last_known_info)
    if latest_solve_section:
        if '<!-- AUTO_GENERATED_SECTION_START: LATEST_SOLVE -->' in readme_content:
            readme_content = _replace_marked_section(readme_content, 'LATEST_SOLVE', latest_solve_section)
        elif '## 🎯 Latest Solve' in readme_content or '## 🎯 Last Activity' in readme_content:
            # Wrap existing section with markers
            pattern = r'(\n*## 🎯 (?:Latest Solve|Last Activity).*?---\n+)'
            wrapped_section = f'<!-- AUTO_GENERATED_SECTION_START: LATEST_SOLVE -->\n{latest_solve_section}\n<!-- AUTO_GENERATED_SECTION_END: LATEST_SOLVE -->\n'
            readme_content = re.sub(pattern, wrapped_section, readme_content, flags=re.DOTALL, count=1)
        else:
            # Insert new section before "Key Highlights"
            key_highlights_pos = readme_content.find('## 🌟 Key Highlights')
            if key_highlights_pos != -1:
                wrapped_section = f'\n<!-- AUTO_GENERATED_SECTION_START: LATEST_SOLVE -->\n{latest_solve_section}\n<!-- AUTO_GENERATED_SECTION_END: LATEST_SOLVE -->\n'
                readme_content = readme_content[:key_highlights_pos] + wrapped_section + readme_content[key_highlights_pos:]
    else:
        # Remove the section if it exists
        if '<!-- AUTO_GENERATED_SECTION_START: LATEST_SOLVE -->' in readme_content:
            pattern = r'<!-- AUTO_GENERATED_SECTION_START: LATEST_SOLVE -->.*?<!-- AUTO_GENERATED_SECTION_END: LATEST_SOLVE -->\n*'
            readme_content = re.sub(pattern, '', readme_content, flags=re.DOTALL)
    
    # Insert or update the Platform Last Solved Table
    platform_table_section = generate_platform_last_solved_table(last_known_info)
    if platform_table_section:
        if '<!-- AUTO_GENERATED_SECTION_START: PLATFORM_LAST_SOLVED -->' in readme_content:
            readme_content = _replace_marked_section(readme_content, 'PLATFORM_LAST_SOLVED', platform_table_section)
        elif '## 📅 Last Solved by Platform' in readme_content:
            # Wrap existing section with markers
            pattern = r'(\n*## 📅 Last Solved by Platform.*?---\n+)'
            wrapped_section = f'<!-- AUTO_GENERATED_SECTION_START: PLATFORM_LAST_SOLVED -->\n{platform_table_section}\n<!-- AUTO_GENERATED_SECTION_END: PLATFORM_LAST_SOLVED -->\n'
            readme_content = re.sub(pattern, wrapped_section, readme_content, flags=re.DOTALL, count=1)
        else:
            # Insert before "Key Highlights" section
            key_highlights_pos = readme_content.find('## 🌟 Key Highlights')
            if key_highlights_pos != -1:
                wrapped_section = f'\n<!-- AUTO_GENERATED_SECTION_START: PLATFORM_LAST_SOLVED -->\n{platform_table_section}\n<!-- AUTO_GENERATED_SECTION_END: PLATFORM_LAST_SOLVED -->\n'
                readme_content = readme_content[:key_highlights_pos] + wrapped_section + readme_content[key_highlights_pos:]
    else:
        # Remove the section if it exists
        if '<!-- AUTO_GENERATED_SECTION_START: PLATFORM_LAST_SOLVED -->' in readme_content:
            pattern = r'<!-- AUTO_GENERATED_SECTION_START: PLATFORM_LAST_SOLVED -->.*?<!-- AUTO_GENERATED_SECTION_END: PLATFORM_LAST_SOLVED -->\n*'
            readme_content = re.sub(pattern, '', readme_content, flags=re.DOTALL)
    
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
