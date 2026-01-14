#!/usr/bin/env python3
"""
Master test runner for all web scraping tests.
Runs pattern tests, unit tests, and integration tests in sequence.
"""

import sys
import subprocess


def run_command(cmd, description):
    """Run a command and return success status."""
    print("\n" + "="*70)
    print(f"Running: {description}")
    print("="*70)
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=False,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def main():
    """Run all test suites."""
    print("\n" + "="*70)
    print("WEB SCRAPING TEST SUITE - MASTER RUNNER")
    print("="*70)
    print("\nThis will run all available tests to verify web scraping works correctly.")
    print("="*70)
    
    tests = [
        ("python3 test_scraping_patterns.py", "Pattern Matching Tests"),
        ("python3 test_web_scraping.py", "Comprehensive Unit Tests"),
        ("python3 test_integration.py", "Integration Tests with Mock Data"),
    ]
    
    results = {}
    
    for cmd, description in tests:
        success = run_command(cmd, description)
        results[description] = success
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUITE SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {test_name}")
        all_passed = all_passed and passed
    
    print("="*70)
    
    if all_passed:
        print("\n✓ ALL TEST SUITES PASSED!")
        print("\nWeb scraping functionality is working correctly.")
        print("The system is ready to fetch statistics from all 12 platforms")
        print("when running in an environment with network access (e.g., GitHub Actions).")
        print("="*70)
        return 0
    else:
        print("\n✗ SOME TEST SUITES FAILED")
        print("\nPlease review the failed tests above.")
        print("="*70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
