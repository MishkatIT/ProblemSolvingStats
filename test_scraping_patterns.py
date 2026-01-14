#!/usr/bin/env python3
"""
Test script to demonstrate the web scraping pattern matching capabilities.
This tests that the regex patterns can correctly extract problem counts from sample HTML.
"""

import re


def test_pattern_matching():
    """Test that various HTML patterns can be matched correctly."""
    
    print("Testing Web Scraping Pattern Matching")
    print("=" * 70)
    
    # Test patterns for different platforms
    test_cases = [
        {
            'platform': 'Codeforces',
            'html': '<div class="info">2386</div><div>problems solved</div>',
            'patterns': [
                r'<div[^>]*>(\d+)</div>\s*<div[^>]*>problem',
                r'(\d+)\s+problem',
            ],
            'expected': 2386
        },
        {
            'platform': 'LeetCode',
            'html': '{"solvedProblem": 412, "total": 3000}',
            'patterns': [
                r'"solvedProblem"\s*:\s*(\d+)',
                r'Solved["\s:]+(\d+)',
            ],
            'expected': 412
        },
        {
            'platform': 'Vjudge',
            'html': '<span>Solved: 346</span>',
            'patterns': [
                r'Solved[:\s]*<[^>]*>(\d+)',
                r'Solved[:\s]*(\d+)',
            ],
            'expected': 346
        },
        {
            'platform': 'AtCoder',
            'html': '<td>158 AC</td>',
            'patterns': [
                r'(\d+)\s+AC',
                r'AC[:\s]+(\d+)',
            ],
            'expected': 158
        },
        {
            'platform': 'CodeChef',
            'html': '<h3>Problems Solved</h3><div><b>3</b></div>',
            'patterns': [
                r'<h3>.*?Problems\s+Solved.*?</h3>\s*<div[^>]*>\s*<b>(\d+)</b>',
                r'"problemsSolved"\s*:\s*(\d+)',
            ],
            'expected': 3
        },
        {
            'platform': 'CSES',
            'html': '64 / 300 tasks solved',
            'patterns': [
                r'(\d+)\s+/\s+\d+\s+task',
                r'Solved:\s*(\d+)',
            ],
            'expected': 64
        },
        {
            'platform': 'Toph',
            'html': '<div>35 solved</div>',
            'patterns': [
                r'(\d+)\s+solved',
                r'Solved:\s*(\d+)',
            ],
            'expected': 35
        },
        {
            'platform': 'LightOJ',
            'html': '<span>Solved: 30</span>',
            'patterns': [
                r'Solved[:\s]*(\d+)',
                r'Problems\s+Solved[:\s]*(\d+)',
            ],
            'expected': 30
        },
        {
            'platform': 'SPOJ',
            'html': '<td>Problems solved:</td><td>21</td>',
            'patterns': [
                r'Problems\s+solved[:\s]*(\d+)',
                r'<td[^>]*>Problems\s+solved[:\s]*</td>\s*<td[^>]*>(\d+)',
                r'solved[:\s]*</td>\s*<td[^>]*>(\d+)',
                r'Solved[:\s]*(\d+)',
            ],
            'expected': 21
        },
        {
            'platform': 'HackerRank',
            'html': '<div>7 challenges solved</div>',
            'patterns': [
                r'(\d+)\s+challenges?\s+solved',
                r'challenges?\s+solved[:\s]*(\d+)',
            ],
            'expected': 7
        },
        {
            'platform': 'UVa',
            'html': '<td>Solved:</td><td>6</td>',
            'patterns': [
                r'Solved[:\s]*(\d+)',
                r'<td[^>]*>Solved[:\s]*</td>\s*<td[^>]*>(\d+)',
            ],
            'expected': 6
        },
        {
            'platform': 'HackerEarth',
            'html': '<span>3 problems solved</span>',
            'patterns': [
                r'(\d+)\s+problem',
                r'Problems\s+Solved[:\s]*(\d+)',
            ],
            'expected': 3
        },
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test in test_cases:
        platform = test['platform']
        html = test['html']
        patterns = test['patterns']
        expected = test['expected']
        
        print(f"\n{platform}:")
        print(f"  HTML sample: {html[:60]}{'...' if len(html) > 60 else ''}")
        
        matched = False
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
            if match:
                count = int(match.group(1))
                if count == expected:
                    print(f"  ✓ Pattern matched: {pattern[:50]}...")
                    print(f"  ✓ Extracted count: {count} (expected: {expected})")
                    matched = True
                    passed_tests += 1
                    break
                else:
                    print(f"  ✗ Pattern matched but wrong count: {count} (expected: {expected})")
            
        if not matched:
            print(f"  ✗ No pattern matched the HTML")
        
        total_tests += 1
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    print("=" * 70)
    
    if passed_tests == total_tests:
        print("\n✓ All pattern matching tests passed!")
        return 0
    else:
        print(f"\n⚠ {total_tests - passed_tests} test(s) failed")
        return 1


def test_sanity_checks():
    """Test that sanity checks work correctly."""
    print("\n\nTesting Sanity Checks")
    print("=" * 70)
    
    MAX_REASONABLE_COUNT = 10000
    
    test_values = [
        (0, False, "Zero is invalid"),
        (-5, False, "Negative is invalid"),
        (1, True, "1 is valid"),
        (100, True, "100 is valid"),
        (9999, True, "9999 is valid"),
        (10000, False, "10000 is at boundary (invalid)"),
        (15000, False, "15000 is too high"),
    ]
    
    passed = 0
    total = len(test_values)
    
    for value, should_be_valid, description in test_values:
        is_valid = 0 < value < MAX_REASONABLE_COUNT
        
        if is_valid == should_be_valid:
            print(f"  ✓ {description}: {value} -> {'Valid' if is_valid else 'Invalid'}")
            passed += 1
        else:
            print(f"  ✗ {description}: Expected {'Valid' if should_be_valid else 'Invalid'}, got {'Valid' if is_valid else 'Invalid'}")
    
    print("\n" + "=" * 70)
    print(f"Sanity Check Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    return 0 if passed == total else 1


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("WEB SCRAPING PATTERN VALIDATION TESTS")
    print("=" * 70)
    
    result1 = test_pattern_matching()
    result2 = test_sanity_checks()
    
    print("\n" + "=" * 70)
    if result1 == 0 and result2 == 0:
        print("✓ ALL TESTS PASSED")
    else:
        print("⚠ SOME TESTS FAILED")
    print("=" * 70 + "\n")
    
    return result1 or result2


if __name__ == "__main__":
    exit(main())
