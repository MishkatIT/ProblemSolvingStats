#!/usr/bin/env python
"""
Interactive script to manually input and update problem-solving statistics.
Use this when automatic fetching is not possible.
"""


import json
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import USER_CONFIG, MAX_REASONABLE_COUNT
from src.data_manager import DataManager

# Color and rich output
from colorama import init as colorama_init
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from rich import box
colorama_init(autoreset=True)
# Force Windows ANSI support
if os.name == 'nt':
    os.system('')
console = Console()


def load_handles_urls():
    """Load URLs directly from handles.json instead of generating them."""
    handles_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'handles.json')
    if os.path.exists(handles_file):
        try:
            with open(handles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old array format and new object format
            if isinstance(data, list):
                urls = data
            elif isinstance(data, dict) and 'urls' in data:
                urls = data['urls']
            else:
                urls = []
                
        except json.JSONDecodeError as e:
            print(f"[ERROR] Syntax error in handles.json: {e}")
            print("[ERROR] handles.json should look like this:")
            print('{')
            print('  "_comment": "Complete URLs to your profiles on each platform",')
            print('  "urls": [')
            print('    "https://codeforces.com/profile/your_username",')
            print('    "https://cses.fi/user/your_username/"')
            print('  ]')
            print('}')
            print("See _examples field in existing handles.json for all supported platforms")
            sys.exit(1)
        return urls
    return []


def get_manual_stats():
    """Manually input statistics for each platform."""
    console.print(Panel(
        "[bold white]Please visit each platform and enter the current solve count.[/bold white]\n[bold white]Press Enter to skip a platform or enter 0 if not applicable.[/bold white]",
        border_style="cyan", expand=False)
    )
    
    # Load URLs directly from handles.json
    urls = load_handles_urls()
    
    # Load last known counts to show current values
    last_known = DataManager.load_last_known_counts()
    
    stats = {}
    
    # Iterate through platforms and match with URLs
    for i, platform in enumerate(USER_CONFIG.keys()):
        url = urls[i] if i < len(urls) else f"https://{platform.lower()}.com"
        current_count = last_known['counts'].get(platform)
        last_update = last_known['dates'].get(platform, 'never')
        mode = last_known['modes'].get(platform, 'unknown')
        # Build info for this platform
        info_lines = []
        info_lines.append(f"[bold magenta]{platform}[/bold magenta]")
        info_lines.append(f"[bold white]🔗 {url}[/bold white]")
        if current_count is not None:
            info_lines.append(f"[bold white]Current:[/bold white] [bold]{current_count}[/bold] problems [bold cyan](last updated: {last_update}, mode: {mode})[/bold cyan]")
        else:
            info_lines.append("[bold white]Current: No data available[/bold white]")
        panel_content = "\n".join(info_lines)
        console.print(Panel(panel_content, border_style="cyan", expand=False))
        while True:
            try:
                user_input = input(f"  {platform} - Enter solve count (current: {current_count or '?'}), or press Enter to skip: ").strip()
                if user_input == '':
                    stats[platform] = None
                    console.print(Panel("→ Skipped", border_style="yellow", expand=False))
                    break
                count = int(user_input)
                if count <= 0:
                    console.print(Panel("[ERROR] Count must be positive. Please try again.", border_style="red", expand=False))
                    continue
                if count > MAX_REASONABLE_COUNT:
                    confirm = input(f"  [WARNING] Count {count} seems very high. Continue? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                stats[platform] = count
                console.print(Panel(f"[OK] Recorded: {count} problems", border_style="green", expand=False))
                break
            except ValueError:
                console.print(Panel("[ERROR] Invalid input. Please enter a number.", border_style="red", expand=False))
    
    return stats


def main():
    """Main function for manual statistics input."""
    # Ensure configuration is up to date before proceeding
    console.print(Panel("Configuring handles from handles.json...", border_style="blue", expand=False))
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'scripts/configure_handles.py'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            console.print(Panel(f"[red]ERROR: configure_handles failed: {result.stdout}\nCannot continue with invalid handles.json[/red]", border_style="red", expand=False))
            console.print(Panel("[red]Please fix the syntax error in handles.json and try again.[/red]", border_style="red", expand=False))
            return 1  # Exit with error code
        elif result.stdout.strip():
            console.print(Panel(result.stdout.strip(), border_style="green", expand=False))
        # Reload configuration after configure_handles potentially updated it
        console.print(Panel("Reloading configuration...", border_style="blue", expand=False))
        import importlib
        import src
        importlib.reload(src)
        import src.data_manager
        importlib.reload(src.data_manager)
        # Re-import the updated config variables
        from src import BDT_TIMEZONE, USER_CONFIG, MAX_REASONABLE_COUNT
        globals()['BDT_TIMEZONE'] = BDT_TIMEZONE
        globals()['USER_CONFIG'] = USER_CONFIG
        globals()['MAX_REASONABLE_COUNT'] = MAX_REASONABLE_COUNT
        
    except Exception as e:
        console.print(Panel(f"Warning: configure_handles or config reload failed: {e}\nContinuing with existing configuration...", border_style="yellow", expand=False))
    
    console.print(Panel("[bold magenta]This script helps you manually update problem-solving statistics.[/bold magenta]\n[bold white]You'll need to visit each platform and enter the current solve count.[/bold white]", border_style="magenta", expand=False))
    
    input("Press Enter to continue...")
    
    stats = get_manual_stats()
    
    total = sum(count for count in stats.values() if count is not None)
    table = Table(show_header=True, header_style="bold white", box=box.ROUNDED, show_lines=False, padding=(0,1))
    table.add_column("Platform", style="bold cyan", justify="left", no_wrap=True)
    table.add_column("Count", style="bold green", justify="right", no_wrap=True)
    for platform, count in stats.items():
        if count is not None:
            table.add_row(platform, str(count))
        else:
            table.add_row(platform, "[yellow]Skipped[/yellow]")
    summary_text = f"[bold green]Total Solved:[/bold green] [bold yellow]{total}[/bold yellow]"
    group = Group(table, summary_text)
    console.print(Panel(group, title="📋 SUMMARY", title_align="left", border_style="magenta", padding=(0,1), width=48))

    # Save to JSON
    DataManager.save_stats(stats)
    DataManager.update_manual_stats(stats)
    console.print(Panel("[green][OK] Last known counts updated[/green]", border_style="green", expand=False))

    # Ask if user wants to update README
    console.print(Panel("Do you want to update README.md with these statistics? (y/n)", border_style="cyan", style="bold black on cyan", expand=False))
    update = input("Your choice (y/n): ").strip().lower()
    if update == 'y':
        import update_readme
        last_known_info = DataManager.load_last_known_counts()
        success = update_readme.update_readme(stats, last_known_info=last_known_info, update_source='manual')
        if success:
            console.print(Panel(f"[green][OK] README.md has been updated successfully!\n  Last updated: {datetime.now(BDT_TIMEZONE).strftime('%d %B %Y')}[/green]", border_style="green", expand=False))
        else:
            console.print(Panel("[red][ERROR] Failed to update README.md[/red]", border_style="red", expand=False))
    else:
        console.print(Panel("[yellow]You can update README.md later by running: python scripts/update_readme.py[/yellow]", border_style="yellow", expand=False))
    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        exit(1)
