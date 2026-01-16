#!/usr/bin/env python3
"""
Script to update README.md with the latest statistics from stats.json
"""

import json
import re
import os
import sys
from datetime import datetime, timezone, timedelta


# User configuration - Single source of truth for all usernames/IDs
USER_CONFIG = {
    'Codeforces': 'MishkatIT',
    'LeetCode': 'MishkatIT',
    'Vjudge': 'MishkatIT',
    'AtCoder': 'MishkatIT',
    'CodeChef': 'MishkatIT',
    'CSES': '165802',  # User ID
    'Toph': 'MishkatIT',
    'LightOJ': 'mishkatit',  # lowercase
    'SPOJ': 'mishkatit',  # lowercase
    'HackerRank': 'MishkatIT',
    'UVa': '1615470',  # User ID
    'HackerEarth': 'MishkatIT'
}

# Platform URL templates
PLATFORM_URL_TEMPLATES = {
    'Codeforces': 'https://codeforces.com/profile/{username}',
    'LeetCode': 'https://leetcode.com/{username}/',
    'Vjudge': 'https://vjudge.net/user/{username}',
    'AtCoder': 'https://atcoder.jp/users/{username}',
    'CodeChef': 'https://www.codechef.com/users/{username}',
    'CSES': 'https://cses.fi/user/{username}/',
    'Toph': 'https://toph.co/u/{username}',
    'LightOJ': 'https://lightoj.com/user/{username}',
    'SPOJ': 'https://www.spoj.com/users/{username}/',
    'HackerRank': 'https://www.hackerrank.com/{username}',
    'UVa': 'https://uhunt.onlinejudge.org/id/{username}',
    'HackerEarth': 'https://www.hackerearth.com/@{username}'
}


def get_profile_url(platform):
    """Generate profile URL for a platform using username from config."""
    template = PLATFORM_URL_TEMPLATES.get(platform)
    username = USER_CONFIG.get(platform)
    if template and username:
        return template.format(username=username)
    return '#'


# Platform configuration constants
PLATFORM_LOGOS = {
    'Codeforces': ('https://cdn.iconscout.com/icon/free/png-16/codeforces-3628695-3029920.png', True),
    'LeetCode': ('https://leetcode.com/favicon-16x16.png', True),
    'Vjudge': ('https://vjudge.net/favicon.ico', True),
    'AtCoder': ('https://atcoder.jp/favicon.ico', True),
    'CodeChef': ('https://cdn.codechef.com/sites/all/themes/abessive/cc-logo.png', True),
    'CSES': ('https://cses.fi/logo.png?1', True),
    'Toph': ('https://toph.co/favicon.ico', True),
    'LightOJ': ('https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSq0TU63ijLZ_PaQre3dgnYmJ811t41O-RcHg&s', False),
    'SPOJ': ('https://www.spoj.com/favicon.ico', True),
    'HackerRank': ('https://hrcdn.net/fcore/assets/favicon-ddc852f75a.png', True),
    'UVa': ('https://www.google.com/s2/favicons?domain=onlinejudge.org&sz=16', True),
    'HackerEarth': ('https://www.google.com/s2/favicons?domain=hackerearth.com&sz=16', True)
}

PLATFORM_COLORS = {
    'Codeforces': 'red',
    'LeetCode': 'yellow',
    'Vjudge': 'blueviolet',
    'AtCoder': 'orange',
    'CodeChef': 'brown',
    'CSES': 'lightgray',
    'Toph': 'blue',
    'LightOJ': 'yellow',
    'SPOJ': 'green',
    'HackerRank': 'brightgreen',
    'UVa': 'blue',
    'HackerEarth': 'blue'
}

ALL_PLATFORMS = [
    'Codeforces', 'LeetCode', 'Vjudge', 'AtCoder', 'CodeChef',
    'CSES', 'Toph', 'LightOJ', 'SPOJ', 'HackerRank', 'UVa', 'HackerEarth'
]


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
    
    # Filter platforms that have last_solved_dates and sort by date (most recent first)
    # Parse dates and sort, with None/empty dates going to the end
    def parse_date_for_sorting(date_str):
        if not date_str or date_str == "1970-01-01":
            return "0000-00-00"  # Put old/missing dates at the end
        return date_str
    
    platform_order = sorted(
        [p for p in ALL_PLATFORMS if p in last_solved_dates],
        key=lambda p: parse_date_for_sorting(last_solved_dates.get(p, "")),
        reverse=True
    )
    
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
            logo_url, use_onerror = PLATFORM_LOGOS.get(platform, ('', False))
            onerror_attr = ' onerror="this.style.display=\'none\'"' if use_onerror else ''
            platform_cell = f'<img src="{logo_url}" alt="{platform}" width="16" height="16"{onerror_attr}/> <strong>{platform}</strong>'
            rows.append(f'    <tr><td>{platform_cell}</td><td align="right" data-date="{date}">{formatted_date}</td></tr>')
    
    if not rows:
        return ""
    
    section = f"""## 📅 Last Solved by Platform

<div align="center">

<table id="lastSolvedTable" class="sortable">
  <thead>
    <tr>
      <th onclick="sortTable('lastSolvedTable', 0, 'text')" style="cursor: pointer;">🏆 Platform <span class="sort-arrow"></span></th>
      <th onclick="sortTable('lastSolvedTable', 1, 'date')" style="cursor: pointer;" align="right">📅 Last Solved <span class="sort-arrow"></span></th>
    </tr>
  </thead>
  <tbody>
{chr(10).join(rows)}
  </tbody>
</table>

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
            
        profile_url = get_profile_url(platform)
        logo_url, use_onerror = PLATFORM_LOGOS.get(platform, ('', False))
        color = PLATFORM_COLORS.get(platform, 'blue')
        
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
      <td align="center" data-value="{count}"><strong>{count}</strong></td>
      <td><img src="https://img.shields.io/badge/Progress-{percentage}%25-{color}?style=flat-square" alt="{platform} Progress"/></td>
      <td align="left" data-date="{raw_date if raw_date else ''}">{date_str}</td>
      <td align="center"><img src="https://img.shields.io/badge/{mode_display}-{mode_color}?style=flat" alt="{mode_display}"/></td>
    </tr>'''
        rows.append(row)
    
    # Build complete table
    table = f'''<table id="statsTable" class="sortable" align="center">
  <thead>
    <tr>
      <th onclick="sortTable('statsTable', 0, 'text')" style="cursor: pointer;">🎯 Platform <span class="sort-arrow"></span></th>
      <th>👤 Profile</th>
      <th onclick="sortTable('statsTable', 2, 'number')" style="cursor: pointer;">✅ Solved <span class="sort-arrow"></span></th>
      <th>📈 Progress</th>
      <th onclick="sortTable('statsTable', 4, 'date')" style="cursor: pointer;">📅 Updated On <span class="sort-arrow"></span></th>
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

</div>

<script>
// JavaScript for sortable tables
let sortStates = {{}};

function sortTable(tableId, columnIndex, dataType) {{
  const table = document.getElementById(tableId);
  if (!table) return;
  
  const tbody = table.querySelector('tbody');
  if (!tbody) return;
  
  const rows = Array.from(tbody.querySelectorAll('tr'));
  
  // Initialize sort state for this table+column
  const key = tableId + '_' + columnIndex;
  if (!sortStates[key]) {{
    sortStates[key] = 'desc';
  }}
  
  // Toggle sort direction
  const ascending = sortStates[key] === 'desc';
  sortStates[key] = ascending ? 'asc' : 'desc';
  
  // Sort rows
  rows.sort((a, b) => {{
    const cellA = a.cells[columnIndex];
    const cellB = b.cells[columnIndex];
    
    let valueA, valueB;
    
    if (dataType === 'number') {{
      // Extract number from data-value attribute or text content
      valueA = parseInt(cellA.getAttribute('data-value') || cellA.textContent.replace(/[^0-9]/g, '') || '0');
      valueB = parseInt(cellB.getAttribute('data-value') || cellB.textContent.replace(/[^0-9]/g, '') || '0');
    }} else if (dataType === 'date') {{
      // Extract date from data-date attribute or parse text
      valueA = cellA.getAttribute('data-date') || '0000-00-00';
      valueB = cellB.getAttribute('data-date') || '0000-00-00';
    }} else {{
      // Text sorting - extract just the text without HTML
      valueA = cellA.textContent.trim().toLowerCase();
      valueB = cellB.textContent.trim().toLowerCase();
    }}
    
    if (valueA < valueB) return ascending ? -1 : 1;
    if (valueA > valueB) return ascending ? 1 : -1;
    return 0;
  }});
  
  // Re-append rows in sorted order
  rows.forEach(row => tbody.appendChild(row));
  
  // Update sort arrow indicators
  const headers = table.querySelectorAll('th');
  headers.forEach((header, index) => {{
    const arrow = header.querySelector('.sort-arrow');
    if (arrow) {{
      if (index === columnIndex) {{
        arrow.textContent = ascending ? ' ▲' : ' ▼';
      }} else {{
        arrow.textContent = '';
      }}
    }}
  }});
}}
</script>"""
        
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
