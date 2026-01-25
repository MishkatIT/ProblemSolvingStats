#!/usr/bin/env python
"""
Interactive script to manage handles for competitive programming platforms.
Use this to add new handles or change existing usernames/handles for each platform.
"""

import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import USER_CONFIG
import known_platforms
PLATFORM_URL_TEMPLATES = known_platforms.PLATFORM_URL_TEMPLATES
generate_url_from_template = known_platforms.generate_url_from_template

# Color and rich output
from colorama import init as colorama_init
from rich.console import Console
from rich.panel import Panel
colorama_init(autoreset=True)
# Force Windows ANSI support
if os.name == 'nt':
    os.system('')
console = Console()


def load_handles_urls():
    """Load URLs from handles.json."""
    handles_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'handles.json')
    try:
        with open(handles_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('urls', {})
    except:
        return {}


def get_available_platforms():
    """Get all platforms from ALL_PLATFORMS config and auto_update.py methods."""
    platforms = set()
    
    # Get platforms from config.json ALL_PLATFORMS
    try:
        import json
        config_file = os.path.join(os.path.dirname(__file__), '..', 'src', 'config.json')
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        all_platforms = config.get('ALL_PLATFORMS', [])
        platforms.update(all_platforms)
    except:
        pass
    
    # Get platforms from auto_update.py methods
    auto_update_file = os.path.join(os.path.dirname(__file__), 'auto_update.py')
    if os.path.exists(auto_update_file):
        try:
            with open(auto_update_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find all def get_* methods
            import re
            pattern = r'def get_(\w+)\(self\):'
            matches = re.findall(pattern, content)
            
            for match in matches:
                # Convert to proper title case with special handling
                platform_name = match
                
                # Only include if we have a URL template
                if platform_name in PLATFORM_URL_TEMPLATES:
                    platforms.add(platform_name)
                
        except:
            pass
    
    return sorted(list(platforms))


def display_platform_options():
    """Get platform URL map without displaying table."""
    platforms = get_available_platforms()

    # Simple url_map
    url_map = {}
    for platform in platforms:
        url_map[platform] = {
            'url': generate_url_from_template(platform, USER_CONFIG.get(platform, '')),
            'username': USER_CONFIG.get(platform, '')
        }

    return url_map


def change_handle(platform, current_data):
    """Change handle for a specific platform."""
    current_username = current_data['username']

    # Ask for new username
    try:
        new_username = input(f"Enter new {platform} username/handle (or press Enter to keep current): ").strip()
    except EOFError:
        new_username = ''

    if not new_username:
        if current_username:
            console.print(Panel("→ No changes made", border_style="yellow", expand=False))
            return current_data['url']
        else:
            console.print(Panel("[red]ERROR: Username cannot be empty for new entries[/red]", border_style="red", expand=False))
            return current_data['url']

    # Generate new URL from template
    new_url = generate_url_from_template(platform, new_username)

    # Auto-save
    console.print(Panel(f"[green]✓ Updated {platform} handle to: {new_username}[/green]", border_style="green", expand=False))
    return new_url


def add_new_platform():
    """Guide user to add a new platform."""
    console.print(Panel(
        "[bold white]Adding a New Platform[/bold white]\n"
        "[bold cyan]To add support for a new platform:[/bold cyan]\n\n"
        "1. [bold yellow]Add your handle to config/handles.json[/bold yellow]\n"
        "   Add the URL for the new platform to the 'urls' array\n\n"
        "2. [bold yellow]Edit scripts/known_platforms.py[/bold yellow] and add:\n"
        "   - URL template to PLATFORM_URL_TEMPLATES (if not already there)\n"
        "   - Domain to KNOWN_DOMAINS (if not already there)\n\n"
        "3. [bold yellow]Implement a fetch method in scripts/auto_update.py[/bold yellow]\n"
        "   Add a method like: def get_PlatformName(self): (see existing methods)\n"
        "   - If you don't implement it, you can manually update solve count of that \n"
        "     website by using [green] scripts/manual_update.py [green] \n",
        border_style="magenta", expand=False)
    )


def delete_handle(platform):
    """Delete handle for a specific platform."""
    global USER_CONFIG
    current_username = USER_CONFIG.get(platform, '')
    current_url = generate_url_from_template(platform, current_username)

    console.print(Panel(
        f"[bold cyan]Platform: {platform}[/bold cyan]\n"
        f"Current handle: [green]{current_username}[/]\n"
        f"Current URL: {current_url}",
        border_style="blue", expand=False)
    )

    # Confirm deletion
    console.print(f"\n[bold red]WARNING: This will permanently remove the handle for {platform}![/]")
    try:
        confirm = input("Are you sure you want to delete this handle? (yes/no): ").strip().lower()
    except EOFError:
        confirm = 'no'

    if confirm not in ['yes', 'y']:
        console.print(Panel("-> Deletion cancelled", border_style="yellow", expand=False))
        return False

    # Delete the handle - remove the key entirely
    urls = load_handles_urls()
    handles_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'handles.json')

    # Remove the platform key
    urls.pop(platform, None)

    # Save changes
    data = {'urls': urls}
    try:
        with open(handles_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        console.print(Panel(f"[green]✓ Successfully deleted {platform} handle[/green]", border_style="green", expand=False))

        # Run configuration validation and cleanup
        try:
            import sync_profiles
            sync_profiles.main()
            # Reload src to get updated USER_CONFIG
            import importlib
            import src
            importlib.reload(src)
            USER_CONFIG = src.USER_CONFIG
        except Exception as e:
            console.print(Panel(f"[yellow]Warning: Configuration validation failed: {e}[/yellow]", border_style="yellow", expand=False))

        return True

    except Exception as e:
        console.print(Panel(f"[red]ERROR: Failed to delete handle: {e}[/red]", border_style="red", expand=False))
        return False


def delete_all_handles(configured_platforms):
    """Delete all configured handles."""
    global USER_CONFIG
    console.print(Panel(
        f"[bold red]DELETE ALL HANDLES[/bold red]\n"
        f"[bold white]This will permanently remove handles for ALL {len(configured_platforms)} platforms:[/bold white]\n" +
        "\n".join(f"• {platform} ({USER_CONFIG.get(platform, '')})" for platform in configured_platforms),
        border_style="red", expand=False)
    )

    # Confirm deletion
    console.print(f"\n[bold red]WARNING: This action cannot be undone![/]")
    try:
        confirm = input("Are you sure you want to delete ALL handles? (yes/no): ").strip().lower()
    except EOFError:
        confirm = 'no'

    if confirm not in ['yes', 'y']:
        console.print(Panel("-> Bulk deletion cancelled", border_style="yellow", expand=False))
        return False

    # Delete all handles
    urls = load_handles_urls()
    handles_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'handles.json')
    deleted_count = 0

    for platform in configured_platforms:
        urls.pop(platform, None)  # Remove the key entirely
        deleted_count += 1

    # Save changes
    data = {'urls': urls}
    try:
        with open(handles_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        console.print(Panel(f"[green]✓ Successfully deleted {deleted_count} handles[/green]", border_style="green", expand=False))

        # Run configuration validation and cleanup
        try:
            import sync_profiles
            sync_profiles.main()
            # Reload src to get updated USER_CONFIG
            import importlib
            import src
            importlib.reload(src)
            USER_CONFIG = src.USER_CONFIG
        except Exception as e:
            console.print(Panel(f"[yellow]Warning: Configuration validation failed: {e}[/yellow]", border_style="yellow", expand=False))

        return True

    except Exception as e:
        console.print(Panel(f"[red]ERROR: Failed to delete handles: {e}[/red]", border_style="red", expand=False))
        return False


def show_change_add_menu():
    """Show the menu for changing or adding handles."""
    global USER_CONFIG
    while True:
        # Display current platform handles
        url_map = display_platform_options()
        
        console.print(Panel(
            "[bold white]Available Platforms for Handle Configuration[/bold white]\n"
            "[bold cyan]Select a platform to change its handle/username.[/bold cyan]",
            border_style="cyan", expand=False)
        )
        
        # Ask user to select option
        platforms = get_available_platforms()
        console.print(f"\n[bold white]Options:[/bold white]")

        console.print(f"[bold magenta]0. Check all platforms automatically one by one (skip or update if needed)[/bold magenta]")
        
        for i, platform in enumerate(platforms, 1):
            handle = USER_CONFIG.get(platform, "Not configured")
            if handle == "Not configured":
                handle_color = "[red]"
            else:
                handle_color = "[green]"
            console.print(f"[bold bright_cyan]{i}.[/bold bright_cyan] {platform} ({handle_color}{handle}[/])")

        console.print(f"[bold red]{len(platforms)+1}. Add new platform[/bold red]")
        console.print(f"[bold bright_cyan]b.[/bold bright_cyan] Back to main menu")

        try:
            choice = input("\nYour choice: ").strip().lower()
        except EOFError:
            choice = 'b'

        if choice == 'b':
            break
        elif choice == '0':
            # Sequential mode
            urls = load_handles_urls()
            changes_made = False

            for platform in platforms:
                current_username = USER_CONFIG.get(platform, '')
                current_url = generate_url_from_template(platform, current_username)
                
                console.print(Panel(
                    f"[bold cyan]Platform: {platform}[/bold cyan]\n"
                    f"Current handle: {current_username or '[red]Not configured[/red]'}\n"
                    f"Current URL: {current_url}",
                    border_style="blue", expand=False)
                )
                
                try:
                    new_username = input("Enter new handle (or press Enter to skip): ").strip()
                except EOFError:
                    new_username = ''
                
                if new_username:
                    new_url = generate_url_from_template(platform, new_username)
                    
                    # Update urls dictionary
                    urls[platform] = new_url
                    
                    console.print(Panel(f"[green]✓ Updated {platform} handle to: {new_username}[/green]", border_style="green", expand=False))
                    changes_made = True
                else:
                    console.print(Panel("→ Skipped", border_style="yellow", expand=False))

            if changes_made:
                # Save to handles.json
                handles_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'handles.json')
                try:
                    with open(handles_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    if isinstance(data, dict) and 'urls' in data:
                        data['urls'] = urls
                    else:
                        data = {'urls': urls}

                    with open(handles_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)

                    console.print(Panel("[green]✓ All changes saved successfully![/green]", border_style="green", expand=False))
                    
                    # Run configuration validation and cleanup
                    try:
                        import sync_profiles
                        sync_profiles.main()
                        # Reload src to get updated USER_CONFIG
                        import importlib
                        import src
                        importlib.reload(src)
                        USER_CONFIG = src.USER_CONFIG
                    except Exception as e:
                        console.print(Panel(f"[yellow]Warning: Configuration validation failed: {e}[/yellow]", border_style="yellow", expand=False))

                except Exception as e:
                    console.print(Panel(f"[red]ERROR: Failed to save changes: {e}[/red]", border_style="red", expand=False))
            else:
                console.print(Panel("[yellow]No changes made.[/yellow]", border_style="yellow", expand=False))

            try:
                input("Press Enter to continue...")
            except EOFError:
                pass
        else:
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(platforms):
                    platform = platforms[choice_num - 1]
                    current_data = url_map[platform]
                    
                    # Display current platform info like in sequential mode
                    current_username = current_data['username']
                    current_url = current_data['url']
                    console.print(Panel(
                        f"[bold cyan]Platform: {platform}[/bold cyan]\n"
                        f"Current handle: {current_username or '[red]Not configured[/red]'}\n"
                        f"Current URL: {current_url}",
                        border_style="blue", expand=False)
                    )
                    
                    new_url = change_handle(platform, current_data)

                    if new_url != current_data['url']:
                        # Update handles.json
                        urls = load_handles_urls()
                        handles_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'handles.json')

                        # Update the URL for this platform
                        urls[platform] = new_url

                        # Save to handles.json
                        try:
                            with open(handles_file, 'r', encoding='utf-8') as f:
                                data = json.load(f)

                            if isinstance(data, dict) and 'urls' in data:
                                data['urls'] = urls
                            else:
                                data = {'urls': urls}

                            with open(handles_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, indent=2)

                            console.print(Panel("[green]✓ Handle updated successfully![/green]", border_style="green", expand=False))
                            
                            # Run configuration validation and cleanup
                            try:
                                import sync_profiles
                                sync_profiles.main()
                                # Reload src to get updated USER_CONFIG
                                import importlib
                                import src
                                importlib.reload(src)
                                USER_CONFIG = src.USER_CONFIG
                            except Exception as e:
                                console.print(Panel(f"[yellow]Warning: Configuration validation failed: {e}[/yellow]", border_style="yellow", expand=False))

                            # Display updated table
                            display_platform_options()

                        except Exception as e:
                            console.print(Panel(f"[red]ERROR: Failed to save changes: {e}[/red]", border_style="red", expand=False))

                elif choice_num == len(platforms) + 1:
                    add_new_platform()
                    try:
                        input("Press Enter to continue...")
                    except EOFError:
                        pass
                else:
                    console.print(Panel("[red]ERROR: Invalid choice[/red]", border_style="red", expand=False))

            except ValueError:
                console.print(Panel("[red]ERROR: Please enter a valid number or 'b'[/red]", border_style="red", expand=False))


def show_delete_menu():
    """Show the menu for deleting handles."""
    global USER_CONFIG
    while True:
        # Get configured platforms
        platforms = get_available_platforms()
        configured_platforms = []
        
        console.print(Panel(
            "[bold white]Available Platforms for Handle Deletion[/bold white]\n"
            "[bold cyan]Select a platform to delete its handle/username.[/bold cyan]",
            border_style="cyan", expand=False)
        )

        console.print(f"\n[bold white]Configured Platforms:[/bold white]")

        for i, platform in enumerate(platforms, 1):
            handle = USER_CONFIG.get(platform, "")
            if handle:  # Only show platforms with configured handles
                console.print(f"[bold bright_cyan]{len(configured_platforms)+1}.[/bold bright_cyan] {platform} ([green]{handle}[/])")
                configured_platforms.append(platform)

        if not configured_platforms:
            console.print("[yellow]No platforms have configured handles to delete.[/]")
            try:
                input("Press Enter to continue...")
            except EOFError:
                pass
            break

        console.print(f"[bold red]0.[/bold red] Delete ALL handles")
        console.print(f"[bold bright_cyan]b.[/bold bright_cyan] Back to main menu")

        try:
            choice = input("\nYour choice: ").strip().lower()
        except EOFError:
            choice = 'b'

        if choice == 'b':
            break
        elif choice == '0':
            # Delete all handles
            delete_all_handles(configured_platforms)
        else:
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(configured_platforms):
                    platform = configured_platforms[choice_num - 1]
                    delete_handle(platform)
                else:
                    console.print(Panel("[red]ERROR: Invalid choice[/red]", border_style="red", expand=False))
            except ValueError:
                console.print(Panel("[red]ERROR: Please enter a valid number or 'b'[/red]", border_style="red", expand=False))

        try:
            input("\nPress Enter to continue...")
        except EOFError:
            pass


def main():
    """Main function for handle configuration."""
    global USER_CONFIG
    console.print(Panel(
        "[bold magenta]Handle Management Tool[/bold magenta]\n"
        "[bold white]This tool helps you manage your usernames/handles for competitive programming platforms.[/bold white]",
        border_style="magenta", expand=False)
    )

    try:
        input("Press Enter to continue...")
    except EOFError:
        pass

    while True:
        console.print(Panel(
            "[bold white]Main Menu[/bold white]\n"
            "[bold cyan]Choose an operation:[/bold cyan]",
            border_style="cyan", expand=False)
        )

        console.print(f"\n[bold white]Options:[/bold white]")
        console.print(f"[bold green]1. Change or add handles[/bold green]")
        console.print(f"[bold red]2. Delete handles[/bold red]")
        console.print(f"[bold bright_cyan]q. Quit[/bold bright_cyan]")

        try:
            choice = input("\nYour choice: ").strip().lower()
        except EOFError:
            choice = 'q'

        if choice == 'q':
            break
        elif choice == '1':
            show_change_add_menu()
        elif choice == '2':
            show_delete_menu()
        else:
            console.print(Panel("[red]ERROR: Please enter 1, 2, or 'q'[/red]", border_style="red", expand=False))

    console.print(Panel("[green]Handle management completed![/green]", border_style="green", expand=False))
    return 0


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        exit(1)