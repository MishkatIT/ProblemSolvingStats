#!/usr/bin/env python3
"""
Script to check if total problem count has been stagnant for 90+ days.
If so, automatically switches the workflow schedule from daily to monthly.
"""

import json
import os
from datetime import datetime, timedelta


def load_last_known_counts():
    """Load last known counts and metadata."""
    try:
        with open('last_known_counts.json', 'r') as f:
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
    return "cron: '40 17 * * *'" in content or 'cron: "40 17 * * *"' in content


def is_monthly_schedule(content):
    """Check if workflow is on monthly schedule."""
    return "cron: '40 17 1 * *'" in content or 'cron: "40 17 1 * *"' in content


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
            "# Run every day at 11:40 PM BDT (17:40 UTC), then add random delay (0-7 minutes)\n    - cron: '40 17 * * *'",
            "# Run on 1st day of each month at 11:40 PM BDT (17:40 UTC), then add random delay (0-7 minutes)\n    - cron: '40 17 1 * *'"
        )
        
        if new_content != content:
            with open(workflow_path, 'w') as f:
                f.write(new_content)
            print("✓ Workflow schedule changed from DAILY to MONTHLY")
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
            "# Run on 1st day of each month at 11:40 PM BDT (17:40 UTC), then add random delay (0-7 minutes)\n    - cron: '40 17 1 * *'",
            "# Run every day at 11:40 PM BDT (17:40 UTC), then add random delay (0-7 minutes)\n    - cron: '40 17 * * *'"
        )
        
        if new_content != content:
            with open(workflow_path, 'w') as f:
                f.write(new_content)
            print("✓ Workflow schedule changed from MONTHLY to DAILY")
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
    print("Checking problem solving activity...\n")
    
    # Load data
    data = load_last_known_counts()
    if not data:
        print("No data found. Keeping current schedule.")
        return
    
    # Get last update date
    last_update = get_last_total_update_date(data)
    
    if not last_update:
        print("No valid update dates found. Keeping current schedule.")
        return
    
    # Calculate days since last update
    today = datetime.now()
    days_since_update = (today - last_update).days
    
    print(f"Last problem count update: {last_update.strftime('%Y-%m-%d')}")
    print(f"Days since last update: {days_since_update}")
    print()
    
    # Read current workflow
    workflow_content = read_workflow_file()
    if not workflow_content:
        return
    
    current_schedule = "DAILY" if is_daily_schedule(workflow_content) else "MONTHLY"
    print(f"Current schedule: {current_schedule}")
    print()
    
    # Decision logic
    if days_since_update >= 90:
        # Inactive for 90+ days - switch to monthly
        if is_daily_schedule(workflow_content):
            print(f"⚠ No activity for {days_since_update} days (threshold: 90 days)")
            switch_to_monthly()
        else:
            print(f"Status: Inactive period ({days_since_update} days). Monthly schedule maintained.")
    else:
        # Recent activity - ensure daily schedule
        if is_monthly_schedule(workflow_content):
            print(f"✓ Recent activity detected ({days_since_update} days ago)")
            switch_to_daily()
        else:
            print(f"Status: Active ({days_since_update} days since last update). Daily schedule maintained.")


if __name__ == "__main__":
    main()
