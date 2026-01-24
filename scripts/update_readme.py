#!/usr/bin/env python
"""
Script to update README.md with the latest statistics from stats.json
"""


import re
import os
import sys
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# Color and rich output
from colorama import init as colorama_init
from rich.console import Console
from rich.panel import Panel

colorama_init(autoreset=True)
console = Console()
# Import shared modules
from src import (
    USER_CONFIG, PROFILE_DISPLAY_NAMES, PLATFORM_LOGOS, 
    PLATFORM_COLORS, ALL_PLATFORMS, BDT_TIMEZONE, README_FILE
)
from src.utils import (
    get_profile_url, format_human_date, calculate_percentage,
    format_platform_list, read_text_file
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
        last_known_info: Dictionary containing 'last_solved_dates' with actual solve dates
        
    Returns:
        String containing the markdown section for latest solve information
    """
    # Use 'last_solved_dates' field which contains actual problem solve dates
    last_solved_dates = last_known_info.get('last_solved_dates', {})
    
    if not last_solved_dates:
        # Return placeholder when no data is available
        return """<div align="center">

| 📅 Latest Solve | 🏆 Platform |
|:---------------:|:-------------:|
| _No recent activity recorded yet_ | _Update stats to see latest solves_ |

</div>

---
"""
    
    # Find the most recent solve date and all platforms that solved on that date
    # Use actual dates from the last_solved_dates field
    date_to_platforms = {}
    for platform, date in last_solved_dates.items():
        if date and date.strip():
            if date not in date_to_platforms:
                date_to_platforms[date] = []
            date_to_platforms[date].append(platform)
    
    if not date_to_platforms:
        # Return placeholder when no dates exist
        return """<div align="center">

| 📅 Latest Solve | 🏆 Platform |
|:---------------:|:-------------:|
| _No recent activity recorded yet_ | _Update stats to see latest solves_ |

</div>

---
"""
    
    # Get the most recent date
    most_recent_date = max(date_to_platforms.keys())
    platforms_solved = sorted(date_to_platforms[most_recent_date])
    
    # Format the date
    formatted_date = format_human_date(most_recent_date)
    
    # Generate platform list
    platform_text = format_platform_list(platforms_solved)
    
    # Determine the correct heading based on number of platforms
    platform_heading = "Platforms" if len(platforms_solved) > 1 else "Platform"
    
    section = f"""<div align="center">

| 📅 Last Solved | 🏆 {platform_heading} |
|:-------------:|:-------------:|
| **{formatted_date}** | {platform_text} |

</div>

---
"""
    return section


def generate_platform_last_solved_table(last_known_info):
    """Generate a table showing last solved date for each platform.
    
    Args:
        last_known_info: Dictionary containing 'last_solved_dates' with actual solve dates
        
    Returns:
        String containing the markdown table for all platform last solved dates
    """
    # Use 'last_solved_dates' field which contains actual problem solve dates
    last_solved_dates = last_known_info.get('last_solved_dates', {})
    
    if not last_solved_dates:
        # Return placeholder table when no data is available
        return """<div align="center">

<table>
  <thead>
    <tr>
      <th>🏆 Platform</th>
      <th align="right">📅 Last Solved</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="2" align="center" style="font-style: italic;">No solve activity recorded yet</td>
    </tr>
    <tr>
      <td colspan="2" align="center" style="font-size: 0.9em; color: #666;">Run manual updates to track solve history</td>
    </tr>
  </tbody>
</table>

</div>

---
"""
    
    # Check if we have any valid (non-empty) dates
    has_valid_dates = any(date and date.strip() for date in last_solved_dates.values())
    
    if not has_valid_dates:
        # Return placeholder table when no data is available
        return """<div align="center">

<table>
  <thead>
    <tr>
      <th>🏆 Platform</th>
      <th align="right">📅 Last Solved</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="2" align="center" style="font-style: italic;">No solve activity recorded yet</td>
    </tr>
    <tr>
      <td colspan="2" align="center" style="font-size: 0.9em; color: #666;">Run manual updates to track solve history</td>
    </tr>
  </tbody>
</table>

</div>

---
"""
    
    # Filter platforms that have valid dates and sort by date (most recent first)
    # Parse dates and sort, with None/empty dates going to the end
    def parse_date_for_sorting(date_str):
        if not date_str or not date_str.strip():
            return "0000-00-00"  # Put missing dates at the end
        return date_str
    
    platform_order = sorted(
        [p for p in ALL_PLATFORMS if p in last_solved_dates and last_solved_dates.get(p) and last_solved_dates.get(p).strip()],
        key=lambda p: parse_date_for_sorting(last_solved_dates.get(p, "")),
        reverse=True
    )
    
    # Build table rows
    rows = []
    for platform in platform_order:
        if platform in last_solved_dates:
            date = last_solved_dates[platform]
            if date and date.strip():
                formatted_date = format_human_date(date)
            else:
                formatted_date = "_Not recorded_"
            
            # Add platform with logo (matching main stats table format)
            logo_url, use_onerror = PLATFORM_LOGOS.get(platform, ('', False))
            onerror_attr = ' onerror="this.style.display=\'none\'"' if use_onerror else ''
            platform_cell = f'<img src="{logo_url}" alt="{platform}" width="16" height="16"{onerror_attr}/> <strong>{platform}</strong>'
            rows.append(f'    <tr><td>{platform_cell}</td><td align="right" data-date="{date}">{formatted_date}</td></tr>')
    
    if not rows:
        # Fallback placeholder if no rows were built (shouldn't happen with the above logic)
        return """<div align="center">

<table>
  <thead>
    <tr>
      <th>🏆 Platform</th>
      <th align="right">📅 Last Solved</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="2" align="center" style="font-style: italic;">No solve activity recorded yet</td>
    </tr>
    <tr>
      <td colspan="2" align="center" style="font-size: 0.9em; color: #666;">Run manual updates to track solve history</td>
    </tr>
  </tbody>
</table>

</div>

---
"""
    
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
    """Generate the main platform statistics table as markdown (GitHub-compatible with borders).
    
    Args:
        effective_counts: Dictionary of effective counts for each platform
        current_date: Current date string
        today_iso: Today's date in ISO format
        stats: Dictionary of platform stats
        last_known_info: Last known information
        
    Returns:
        String containing the markdown table for platform statistics
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
    for sorted_index, platform in enumerate(sorted_platforms):
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
        
        # Set color based on sorted position - platforms are sorted by solve count (descending)
        # Top platform (highest solve count) gets first color, second gets second color, etc.
        if sorted_index < len(PLATFORM_COLORS):
            base_color = PLATFORM_COLORS[sorted_index]
        else:
            # Fallback if we have more platforms than colors
            print(f"Warning: No color defined for sorted position {sorted_index} (platform: {platform})")
            base_color = '808080'  # Default gray as fallback
        
        # Use the same color for both auto and manual modes (based on sorted position)
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
        
        mode_display = platform_mode.capitalize() if platform_mode else 'Unknown'
        mode_color = 'F44336' if platform_mode == 'manual' else '2196F3'
        
        # Create markdown table row
        logo_md = f'<img src="{logo_url}" width="16" height="16" alt="{platform} logo"/>' if logo_url else '🏆'
        progress_badge = f'![Progress](https://img.shields.io/badge/Progress-{percentage}%25-{color}?style=flat-square)'
        mode_badge = f'![{mode_display}](https://img.shields.io/badge/{mode_display}-{mode_color}?style=flat)'
        
        row = f'| {logo_md} **{platform}** | [{display_name}]({profile_url}) | **{count}** | {progress_badge} | {date_str} | {mode_badge} |'
        rows.append(row)
    
    # Build markdown table
    table = f'''| 🎯 Platform | 👤 Profile | ✅ Solved | 📈 Progress | 📅 Updated On | 🔄 Mode |
|-------------|------------|-----------|-------------|---------------|----------|
{chr(10).join(rows)}
| 🎖️ **TOTAL** | | **{total}** | **100%** | {current_date} | |'''
    
    return table + '\n\n---\n'
    
    return table + '\n\n---\n'


def generate_philosophical_status(last_known_info):
    """Generate philosophical status line based on activity."""
    from datetime import datetime, timedelta
    
    last_solved_dates = last_known_info.get('last_solved_dates', {})
    if not last_solved_dates:
        return "<p align='center'><span style='color: red;'>Inactive: In the quiet moments, the mind prepares for new challenges.</span></p>"
    
    # Get the most recent solve date
    dates = []
    for date_str in last_solved_dates.values():
        if date_str and date_str != '1970-01-01':
            try:
                dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
            except ValueError:
                pass
    
    if not dates:
        return "<p align='center'><span style='color: red;'>Inactive: In the quiet moments, the mind prepares for new challenges.</span></p>"
    
    max_date = max(dates)
    one_year_ago = datetime.now() - timedelta(days=365)
    
    if max_date > one_year_ago:
        return "<p align='center'><span style='color: green;'>User Active: The journey of problem-solving is a path to endless growth.</span></p>"
    else:
        return "<p align='center'><span style='color: red;'>User Inactive: In the quiet moments, the mind prepares for new challenges.</span></p>"


def update_readme(stats, last_known_info=None, update_source=None):
    """Update README.md with new statistics.
    
    Args:
        stats: Dictionary of platform stats (can contain None values)
        last_known_info: Optional dict with 'counts' and 'dates' for platforms
        update_source: 'manual' or 'automatic' (used for README metadata)
    """
    
    # Validate that ALL_PLATFORMS and PLATFORM_COLORS are properly synchronized
    if len(ALL_PLATFORMS) != len(PLATFORM_COLORS):
        print(f"Warning: ALL_PLATFORMS ({len(ALL_PLATFORMS)}) and PLATFORM_COLORS ({len(PLATFORM_COLORS)}) lengths don't match!")
        print("This may cause color assignment issues. Run configure_handles.py to fix.")
    
    # Read current README
    try:
        readme_content = read_text_file(README_FILE)
    except FileNotFoundError:
        print(f"{README_FILE} not found")
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

    # Always update README, even with no valid statistics
    # (URLs, configuration, or other metadata might have changed)
    console.print(Panel(f"[bold blue]Updating README with [yellow]{total}[/yellow] total problems...[/bold blue]", border_style="blue", expand=False))

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
    
    # Add dynamic Codeforces rating styling
    from src.utils import get_codeforces_rating_color
    cf_rating_info = last_known_info.get('ratings', {}).get('Codeforces', {})
    max_rating = cf_rating_info.get('max') if cf_rating_info else None
    rating_color = get_codeforces_rating_color(max_rating)
    
    # Add rating-based background styling to the main header
    if max_rating:
        # Update the background color
        rating_bg_pattern = r'background: #[0-9A-Fa-f]{6}'
        new_bg_style = f'background: #{rating_color}'
        readme_content = re.sub(rating_bg_pattern, new_bg_style, readme_content)
        
        # Update the border color to match
        rating_border_pattern = r'border: 2px solid #[0-9A-Fa-f]{6}'
        new_border_style = f'border: 2px solid #{rating_color}'
        readme_content = re.sub(rating_border_pattern, new_border_style, readme_content)
    
    # Add/update the explicit update metadata block (date + manual/automatic)
    readme_content = _upsert_update_metadata_block(
        readme_content,
        current_date_human=current_date_with_time,
        update_source=update_source,
    )

    # Update the title badge color based on Codeforces rating
    cf_rating_info = last_known_info.get('ratings', {}).get('Codeforces', {})
    max_rating = cf_rating_info.get('max') if cf_rating_info else None
    if max_rating:
        from src.utils import get_codeforces_rating_color
        rating_color = get_codeforces_rating_color(max_rating)
        # Update the color in the title badge
        readme_content = re.sub(
            r'badge/🏆_Problem_Solving_Statistics-[0-9A-Fa-f]{6}',
            f'badge/🏆_Problem_Solving_Statistics-{rating_color}',
            readme_content
        )

    # Regenerate the main platform statistics table (sorted by solve count)
    new_table = generate_platform_statistics_table(effective_counts, current_date, today_iso, stats, last_known_info)
    
    # Replace the table using markers (or fallback to pattern matching)
    if '<!-- AUTO_GENERATED_SECTION_START: STATS_TABLE -->' in readme_content:
        readme_content = _replace_marked_section(readme_content, 'STATS_TABLE', new_table)
    
    # Generate philosophical status
    philosophical_status = generate_philosophical_status(last_known_info)
    if '<!-- AUTO_GENERATED_SECTION_START: PHILOSOPHICAL_STATUS -->' in readme_content:
        readme_content = _replace_marked_section(readme_content, 'PHILOSOPHICAL_STATUS', philosophical_status)
    
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

## 🏆 Key Highlights

| 🥇 Top Platform | 🎯 Main Focus | 📚 Platforms Active |
|:---------------:|:-------------:|:------------------:|
| **{top_platform}** | **Competitive Programming** | **{active_platforms}** |
| {top_count} Problems | Algorithm Mastery | Multi-Platform |

</div>"""
    else:
        # Fallback when no valid statistics exist
        key_highlights = f"""<div align="center">

## 🏆 Key Highlights

| 🥇 Top Platform | 🎯 Main Focus | 📚 Platforms Active |
|:---------------:|:-------------:|:------------------:|
| **None** | **Competitive Programming** | **0** |
| 0 Problems | Algorithm Mastery | Multi-Platform |

</div>"""
    # Insert or update the Latest Solve section (always show, even with placeholder)
    latest_solve_section = generate_latest_solve_section(last_known_info)
    if '<!-- AUTO_GENERATED_SECTION_START: LATEST_SOLVE -->' in readme_content:
        readme_content = _replace_marked_section(readme_content, 'LATEST_SOLVE', latest_solve_section)
    
    # Insert or update the Platform Last Solved Table (always show, even with placeholder)
    platform_table_section = generate_platform_last_solved_table(last_known_info)
    if '<!-- AUTO_GENERATED_SECTION_START: PLATFORM_LAST_SOLVED -->' in readme_content:
        readme_content = _replace_marked_section(readme_content, 'PLATFORM_LAST_SOLVED', platform_table_section)
        
        # Replace Key Highlights section
        if '<!-- AUTO_GENERATED_SECTION_START: KEY_HIGHLIGHTS -->' in readme_content:
            readme_content = _replace_marked_section(readme_content, 'KEY_HIGHLIGHTS', key_highlights)
    
    # Write updated README
    try:
        with open(README_FILE, 'w', encoding='utf-8', newline='\n') as f:
            f.write(readme_content)
        console.print(Panel(f"[green][OK] README.md updated successfully![/green]", border_style="green", expand=False))
        console.print(f"[bold yellow]  Total problems:[/bold yellow] [bold]{total}[/bold]")
        console.print(f"[bold cyan]  Updated on {current_date}[/bold cyan]")
        console.print(Panel("[yellow][NOTE] Some platforms might be missing. Consider manual update.[/yellow]", border_style="yellow", expand=False))
        console.print(Panel("[white]Run the following command to manually update:\n  [bold]python scripts/manual_update.py[/bold][/white]", border_style="white", expand=False))
        return True
    except Exception as e:
        console.print(Panel(f"[red]Error writing README.md: {e}[/red]", border_style="red", expand=False))
        return False


def main():
    """Main function."""
    # Allow passing update source via CLI or env var (useful for GitHub Actions).
    update_source = os.environ.get('UPDATE_SOURCE')
    if len(sys.argv) >= 3 and sys.argv[1] in ('--source', '-s'):
        update_source = sys.argv[2]

    console.print(Panel(
        "[bold cyan]LOADING STATISTICS[/bold cyan]\n"
        "[dim cyan]Fetching latest problem-solving data from all platforms...[/dim cyan]",
        style="cyan",
        border_style="bold cyan",
        padding=(1, 3)
    ))
    stats = DataManager.load_stats()
    if stats is None:
        return 1
    console.print("\n[bold green]Statistics loaded:[/bold green]")
    for platform, count in stats.items():
        if count is not None:
            console.print(f"[cyan]  • {platform}:[/cyan] [bold white]{count:,}[/bold white] problems")
    console.print(Panel("[bold blue]Updating README.md...[/bold blue]", border_style="blue", expand=False))
    success = update_readme(stats, update_source=update_source)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
