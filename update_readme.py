#!/usr/bin/env python3
"""
Script to update README.md with the latest statistics from stats.json
"""

import re
import os
import sys
from datetime import datetime, timezone, timedelta

# Import shared modules
from src import (
    USER_CONFIG, PROFILE_DISPLAY_NAMES, PLATFORM_URL_TEMPLATES, PLATFORM_LOGOS, 
    PLATFORM_COLORS, ALL_PLATFORMS, BDT_TIMEZONE
)
from src.utils import (
    get_profile_url, format_human_date, calculate_percentage,
    calculate_total, format_platform_list, read_text_file,
    extract_first_int
)
from src.data_manager import DataManager


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
    formatted_date = format_human_date(most_recent_date)
    
    # Generate platform list
    platform_text = format_platform_list(platforms_solved)
    
    section = f"""<div align="center">

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
                formatted_date = format_human_date(date)
            else:
                formatted_date = "_Not recorded_"
            
            # Add platform with logo (matching main stats table format)
            logo_url, use_onerror = PLATFORM_LOGOS.get(platform, ('', False))
            onerror_attr = ' onerror="this.style.display=\'none\'"' if use_onerror else ''
            platform_cell = f'<img src="{logo_url}" alt="{platform}" width="16" height="16"{onerror_attr}/> <strong>{platform}</strong>'
            rows.append(f'    <tr><td>{platform_cell}</td><td align="right" data-date="{date}">{formatted_date}</td></tr>')
    
    if not rows:
        return ""
    
    section = f"""<div align="center">

<table>
  <thead>
    <tr>
      <th>🏆 Platform</th>
      <th align="right">📅 Last Solved</th>
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
        display_name = PROFILE_DISPLAY_NAMES.get(platform, USER_CONFIG.get(platform, 'Unknown'))
        logo_url, use_onerror = PLATFORM_LOGOS.get(platform, ('', False))
        
        onerror_attr = ' onerror="this.style.display=\'none\'"' if use_onerror else ''
        percentage = calculate_percentage(count, total)
        
        # Determine date and mode
        platform_mode = last_known_modes.get(platform, 'automatic')
        raw_date = last_known_dates.get(platform)
        
        # Set color based on update mode
        base_color = PLATFORM_COLORS.get(platform, 'blue')
        if platform_mode == 'manual':
            # For manual updates, use modern darker variants
            color_variants = {
                'red': '8B0000',      # Dark red
                'blue': '00008B',     # Dark blue  
                'green': '006400',    # Dark green
                'yellow': 'B8860B',   # Dark goldenrod
                'orange': 'FF4500',   # Orange red
                'purple': '4B0082',   # Indigo
                'pink': 'C71585',     # Medium violet red
                'brown': '8B4513',    # Saddle brown
                'cyan': '008B8B',     # Dark cyan
                'magenta': '8B008B'   # Dark magenta
            }
            color = color_variants.get(base_color, '2F4F4F')  # Dark slate gray fallback
        else:
            color = base_color
        
        is_fresh_today = (platform in stats and 
                         stats[platform] is not None and 
                         raw_date == today_iso)
        
        if is_fresh_today:
            date_str = current_date
        else:
            if raw_date:
                date_str = format_human_date(raw_date)
            else:
                date_str = current_date if isinstance(count, int) else 'unknown'
        
        mode_display = platform_mode.capitalize() if platform_mode else 'Auto'
        mode_color = 'F44336' if platform_mode == 'manual' else '2196F3'
        
        row = f'''    <tr>
      <td><img src="{logo_url}" width="16" height="16"{onerror_attr}/> <strong>{platform}</strong></td>
      <td><a href="{profile_url}">{display_name}</a></td>
      <td align="center" data-value="{count}"><strong>{count}</strong></td>
      <td><img src="https://img.shields.io/badge/Progress-{percentage}%25-{color}?style=flat-square" alt="{platform} Progress"/></td>
      <td align="left" data-date="{raw_date if raw_date else ''}">{date_str}</td>
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
    
    return table + '\n\n---\n'


def update_readme(stats, last_known_info=None, update_source=None):
    """Update README.md with new statistics.
    
    Args:
        stats: Dictionary of platform stats (can contain None values)
        last_known_info: Optional dict with 'counts' and 'dates' for platforms
        update_source: 'manual' or 'automatic' (used for README metadata)
    """
    
    # Read current README
    try:
        readme_content = read_text_file('README.md')
    except FileNotFoundError:
        print("README.md not found")
        return False
    
    # Load last known info if not provided
    if last_known_info is None:
        last_known_info = DataManager.load_last_known_counts()
    
    # Get current date in BDT (UTC+6)
    now = datetime.now(BDT_TIMEZONE)
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
        key_highlights = f"""<div align="center">

| 🥇 Top Platform | 🎯 Main Focus | 📚 Platforms Active |
|:---------------:|:-------------:|:------------------:|
| **{top_platform}** | **Competitive Programming** | **{active_platforms}** |
| {top_count} Problems | Algorithm Mastery | Multi-Platform |

</div>"""
        
        # Replace Key Highlights section
        if '<!-- AUTO_GENERATED_SECTION_START: KEY_HIGHLIGHTS -->' in readme_content:
            readme_content = _replace_marked_section(readme_content, 'KEY_HIGHLIGHTS', key_highlights)
    
    # Insert or update the Latest Solve section
    latest_solve_section = generate_latest_solve_section(last_known_info)
    if latest_solve_section:
        if '<!-- AUTO_GENERATED_SECTION_START: LATEST_SOLVE -->' in readme_content:
            readme_content = _replace_marked_section(readme_content, 'LATEST_SOLVE', latest_solve_section)
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
        print("\n⚠️ Note: Some platforms might be missing. Consider manual update.")
        print("Run the following command to manually update:")
        print("  python manual_update.py")
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
    stats = DataManager.load_stats()
    
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
