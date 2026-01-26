#!/usr/bin/env python
"""
Script to check if total problem count has been stagnant for 90+ days.
If so, automatically switches the workflow schedule from daily to monthly.
"""

import json
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import LAST_KNOWN_FILE

# Color and rich output
from colorama import init as colorama_init
from rich.console import Console
from rich.panel import Panel
colorama_init(autoreset=True, convert=True, strip=False)

# Check if running in CI environment (GitHub Actions, etc.)
IS_CI = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'

if IS_CI:
    # Use plain text output for CI environments
    import io
    from rich.console import Console as RichConsole
    
    class PlainConsole:
        def print(self, *args, **kwargs):
            # Convert Rich objects to plain text
            messages = []
            for arg in args:
                if hasattr(arg, 'renderable'):
                    # Panel object - extract the inner content
                    messages.append(str(arg.renderable))
                elif hasattr(arg, '__rich_console__') or hasattr(arg, 'render'):
                    # Other Rich renderable objects
                    output = io.StringIO()
                    plain_console = RichConsole(file=output, width=120, no_color=True, force_terminal=False, legacy_windows=True)
                    plain_console.print(arg)
                    messages.append(output.getvalue().strip())
                else:
                    messages.append(str(arg))
            print(' '.join(messages))
    
    console = PlainConsole()
else:
    # Force Windows ANSI support
    if os.name == 'nt':
        os.system('')
        # Additional Windows ANSI enable
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    console = Console(force_terminal=True)


def load_last_known_counts():
    """Load last known counts and metadata."""
    try:
        with open(LAST_KNOWN_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_last_total_update_date(data):
    """
    Get the most recent date when any platform count increased.
    
    Returns:
        datetime object or None
    """
    last_solved_dates = data.get('last_solved_dates', {})
    
    # Filter out default/placeholder dates
    valid_dates = []
    for platform, date_str in last_solved_dates.items():
        if date_str and date_str != '1970-01-01':
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                valid_dates.append(date_obj)
            except ValueError:
                continue
    
    if valid_dates:
        return max(valid_dates)
    return None


def read_workflow_file():
    """Read the workflow YAML file."""
    workflow_path = '.github/workflows/update-stats.yml'
    try:
        with open(workflow_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Workflow file not found: {workflow_path}")
        return None


def is_daily_schedule(content):
    """Check if workflow is on daily schedule."""
    return "cron: '0 17 * * *'" in content or 'cron: "0 17 * * *"' in content


def is_monthly_schedule(content):
    """Check if workflow is on monthly schedule."""
    return "cron: '0 17 1 * *'" in content or 'cron: "0 17 1 * *"' in content


def switch_to_monthly():
    """Switch workflow schedule from daily to monthly."""
    workflow_path = '.github/workflows/update-stats.yml'
    
    try:
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        if is_monthly_schedule(content):
            print("Already on monthly schedule. No change needed.")
            return False
        
        # Replace daily cron with monthly (1st day of month)
        new_content = content.replace(
            "# 11:00 PM Bangladesh Time (BDT) = 17:00 UTC (daily)\n    - cron: '0 17 * * *'",
            "# 11:00 PM Bangladesh Time (BDT) = 17:00 UTC (monthly)\n    - cron: '0 17 1 * *'"
        )
        
        if new_content != content:
            with open(workflow_path, 'w') as f:
                f.write(new_content)
            
            print("[OK] Workflow schedule changed from DAILY to MONTHLY")
            print("  Reason: No problem count updates detected for 90+ days")
            return True
        else:
            print("Warning: Could not find daily schedule pattern to replace")
            return False
            
    except Exception as e:
        print(f"Error switching to monthly schedule: {e}")
        return False


def switch_to_daily():
    """Switch workflow schedule from monthly back to daily."""
    workflow_path = '.github/workflows/update-stats.yml'
    
    try:
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        if is_daily_schedule(content):
            print("Already on daily schedule. No change needed.")
            return False
        
        # Replace monthly cron with daily
        new_content = content.replace(
            "# 11:00 PM Bangladesh Time (BDT) = 17:00 UTC (monthly)\n    - cron: '0 17 1 * *'",
            "# 11:00 PM Bangladesh Time (BDT) = 17:00 UTC (daily)\n    - cron: '0 17 * * *'"
        )
        
        if new_content != content:
            with open(workflow_path, 'w') as f:
                f.write(new_content)
            
            print("[OK] Workflow schedule changed from MONTHLY to DAILY")
            print("  Reason: Recent problem solving activity detected")
            return True
        else:
            print("Warning: Could not find monthly schedule pattern to replace")
            return False
            
    except Exception as e:
        print(f"Error switching to daily schedule: {e}")
        return False


def main():
    """Main function to check and adjust workflow schedule."""
    console.print(Panel(
        "[bold yellow]CHECKING PROBLEM SOLVING ACTIVITY[/bold yellow]\n"
        "[dim yellow]Analyzing recent activity to optimize update schedule[/dim yellow]",
        style="yellow",
        border_style="bold yellow",
        padding=(1, 3)
    ))
    
    # Load data
    data = load_last_known_counts()
    if not data:
        console.print("[bold red][ERROR] No data found. Keeping current schedule.[/bold red]")
        return
    
    # Get last update date
    last_update = get_last_total_update_date(data)
    
    if not last_update:
        console.print("[bold red][ERROR] No valid update dates found. Keeping current schedule.[/bold red]")
        return
    
    # Calculate days since last update
    today = datetime.now()
    days_since_update = (today - last_update).days
    
    console.print(f"[bold white]Last problem count update:[/bold white] [cyan]{last_update.strftime('%Y-%m-%d')}[/cyan]")
    console.print(f"[bold white]Days since last update:[/bold white] [bold magenta]{days_since_update}[/bold magenta] days")
    console.print()
    
    # Read current workflow
    workflow_content = read_workflow_file()
    if not workflow_content:
        console.print("[bold red]Error reading workflow file.[/bold red]")
        return
    
    current_schedule = "DAILY" if is_daily_schedule(workflow_content) else "MONTHLY"
    schedule_color = "green" if current_schedule == "DAILY" else "blue"
    console.print(f"[bold white]Current schedule:[/bold white] [bold {schedule_color}]{current_schedule}[/bold {schedule_color}]")
    console.print()
    
    # Decision logic
    if days_since_update >= 90:
        # Inactive for 90+ days - switch to monthly
        if is_daily_schedule(workflow_content):
            console.print(f"[bold yellow]WARNING:[/bold yellow] No activity for [bold red]{days_since_update}[/bold red] days (threshold: [bold]90[/bold] days)")
            console.print("[bold blue]Switching to monthly schedule...[/bold blue]")
            switch_to_monthly()
        else:
            console.print(f"[bold blue]STATUS:[/bold blue] Inactive period ([bold red]{days_since_update}[/bold red] days). Monthly schedule maintained.")
    else:
        # Recent activity - ensure daily schedule
        if is_monthly_schedule(workflow_content):
            console.print(f"[bold green]SUCCESS:[/bold green] Recent activity detected ([bold cyan]{days_since_update}[/bold cyan] days ago)")
            console.print("[bold blue]Switching to daily schedule...[/bold blue]")
            switch_to_daily()
        else:
            console.print(f"[bold green]STATUS:[/bold green] Active ([bold cyan]{days_since_update}[/bold cyan] days since last update). Daily schedule maintained.")


if __name__ == "__main__":
    main()
