#!/usr/bin/env python
"""
Interactive script to manually update profile display names.
Use this to customize how your profiles appear in the README.

NOTE: This script only changes DISPLAY NAMES, not your actual usernames/handles.
To change your actual usernames/handles, use: python scripts/manage_handle.py
"""


import json
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import USER_CONFIG, PROFILE_DISPLAY_NAMES, PLATFORM_LOGOS, PLATFORM_URL_TEMPLATES
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


def get_change_display_name():
    """Manually input display names for each platform."""
    console.print(Panel(
        "[bold white]Enter custom display names for each platform.[/bold white]\n[bold white]These will be shown in the README instead of usernames.[/bold white]\n[bold white]Press Enter to keep current display name.[/bold white]\n\n[bold yellow]REMINDER: This only changes display names, not actual handles/usernames.[/bold yellow]",
        border_style="cyan", expand=False)
    )

    display_names = {}

    for platform in USER_CONFIG.keys():
        current_display = PROFILE_DISPLAY_NAMES.get(platform, USER_CONFIG.get(platform, 'Unknown'))
        info_lines = []
        info_lines.append(f"[bold magenta]{platform}[/bold magenta]")
        info_lines.append(f"[bold white]Username:[/bold white] [bold]{USER_CONFIG[platform]}[/bold]")
        info_lines.append(f"[bold white]Current Display:[/bold white] [bold cyan]{current_display}[/bold cyan]")
        panel_content = "\n".join(info_lines)
        console.print(Panel(panel_content, border_style="cyan", expand=False))

        while True:
            user_input = input(f"  {platform} - Enter display name (current: '{current_display}'), or press Enter to keep: ").strip()
            if user_input == '':
                display_names[platform] = current_display
                console.print(Panel("→ Kept current display name", border_style="yellow", expand=False))
                break
            elif len(user_input) > 50:
                console.print(Panel("[ERROR] Display name too long (max 50 characters). Please try again.", border_style="red", expand=False))
                continue
            else:
                display_names[platform] = user_input
                console.print(Panel(f"[OK] Display name set to: '{user_input}'", border_style="green", expand=False))
                break

    return display_names


def main():
    """Main function for manual display name updates."""
    console.print(Panel("[bold magenta]Profile Display Name Manager[/bold magenta]\n[bold white]Update your profile display names for the README.[/bold white]\n\n[bold yellow]NOTE: This only changes DISPLAY NAMES, not your actual usernames/handles.[/bold yellow]\n[bold yellow]To change actual handles, use: python scripts/manage_handle.py[/bold yellow]", border_style="magenta", expand=False))

    input("Press Enter to continue...")

    # Get display names
    display_names = get_change_display_name()

    # Update config with new display names
    from src.utils import update_config_file
    update_config_file(USER_CONFIG, PLATFORM_LOGOS, PLATFORM_URL_TEMPLATES, display_names)

    console.print(Panel("[green][OK] Profile display names updated in config[/green]", border_style="green", expand=False))

    # Reload configuration to get updated display names
    import importlib
    import src
    importlib.reload(src)
    # Re-import updated config variables
    from src import PROFILE_DISPLAY_NAMES
    globals()['PROFILE_DISPLAY_NAMES'] = PROFILE_DISPLAY_NAMES

    # Ask if user wants to update README
    while True:
        console.print(Panel("Do you want to update README.md with these changes? (y/n)", border_style="cyan", style="bold black on cyan", expand=False))
        update_readme_choice = input("Your choice (y/n): ").strip().lower()
        if update_readme_choice in ['y', 'n']:
            break
        else:
            console.print(Panel("[red]Please enter 'y' for yes or 'n' for no.[/red]", border_style="red", expand=False))
    
    if update_readme_choice == 'y':
        import update_readme
        import importlib
        importlib.reload(update_readme)
        # Load current stats to update README with existing data but new display names
        current_stats = DataManager.load_stats()
        last_known_info = DataManager.load_last_known_counts(user_config=USER_CONFIG)
        success = update_readme.update_readme(current_stats, last_known_info=last_known_info, update_source='manual')
        if success:
            console.print(Panel(f"[green][OK] README.md has been updated![/green]", border_style="green", expand=False))
        else:
            console.print(Panel("[red][ERROR] Failed to update README.md[/red]", border_style="red", expand=False))

    input("Press Enter to exit...")


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        exit(1)