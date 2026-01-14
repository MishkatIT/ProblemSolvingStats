#!/usr/bin/env python3
"""
Script to fetch and update problem-solving statistics from various competitive programming platforms.
Author: MishkatIT

This script fetches problem counts from 12 competitive programming platforms using:
1. Official APIs where available (primary method)
2. Web scraping as a fallback when APIs are unavailable or fail

Web Scraping Features:
- Multiple regex patterns for each platform to handle HTML structure changes
- Automatic fallback from API to web scraping when needed
- Sanity checks on scraped data to validate reasonable counts
- Error handling to continue fetching from other platforms if one fails

Supported Platforms:
- Codeforces (API + web scraping fallback)
- LeetCode (GraphQL API + web scraping fallback)
- Vjudge (web scraping)
- AtCoder (web scraping)
- CodeChef (web scraping)
- CSES (web scraping)
- Toph (web scraping)
- LightOJ (web scraping)
- SPOJ (web scraping)
- HackerRank (web scraping)
- UVa (API + web scraping fallback)
- HackerEarth (web scraping)
"""

import re
import json
import sys
import os
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import datetime


class PlatformStats:
    """Class to handle fetching statistics from different platforms."""
    
    LAST_KNOWN_FILE = 'last_known_counts.json'
    MAX_REASONABLE_COUNT = 10000  # Maximum expected problem count for validation
    
    def __init__(self):
        self.stats = {}
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.last_known_counts = self._load_last_known_counts()
    
    def _load_last_known_counts(self):
        """Load the last known good counts from file."""
        try:
            with open(self.LAST_KNOWN_FILE, 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            # File doesn't exist yet, will be created on first save
            pass
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load last known counts: {e}")
        return {'counts': {}, 'dates': {}}
    
    def _save_last_known_counts(self):
        """Save the current known good counts to file."""
        try:
            with open(self.LAST_KNOWN_FILE, 'w') as f:
                json.dump(self.last_known_counts, f, indent=2)
        except (IOError, OSError) as e:
            print(f"Warning: Could not save last known counts: {e}")
    
    def _update_last_known(self, platform, count):
        """Update the last known count for a platform."""
        if count is not None:
            if 'counts' not in self.last_known_counts:
                self.last_known_counts['counts'] = {}
            if 'dates' not in self.last_known_counts:
                self.last_known_counts['dates'] = {}
            
            self.last_known_counts['counts'][platform] = count
            self.last_known_counts['dates'][platform] = datetime.now().strftime('%Y-%m-%d')
    
    def _get_last_known(self, platform):
        """Get the last known count for a platform."""
        if 'counts' in self.last_known_counts:
            return self.last_known_counts['counts'].get(platform)
        return None
    
    def fetch_url(self, url, use_api=False):
        """Fetch URL with proper headers."""
        try:
            headers = {'User-Agent': self.user_agent}
            if use_api:
                headers['Accept'] = 'application/json'
            
            req = Request(url, headers=headers)
            with urlopen(req, timeout=10) as response:
                content = response.read()
                if use_api:
                    return json.loads(content.decode('utf-8'))
                return content.decode('utf-8')
        except (URLError, HTTPError) as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def get_codeforces(self):
        """Fetch Codeforces statistics."""
        try:
            # Try API first
            url = "https://codeforces.com/api/user.status?handle=MishkatIT&from=1&count=10000"
            data = self.fetch_url(url, use_api=True)
            
            if data and data.get('status') == 'OK':
                submissions = data.get('result', [])
                solved = set()
                for sub in submissions:
                    if sub.get('verdict') == 'OK':
                        problem = sub.get('problem', {})
                        problem_id = f"{problem.get('contestId')}_{problem.get('index')}"
                        solved.add(problem_id)
                return len(solved)
            
            # Fallback to scraping profile page
            print("  API failed, trying web scraping...")
            url = "https://codeforces.com/profile/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for problem count
                patterns = [
                    r'<div[^>]*>(\d+)</div>\s*<div[^>]*>problem',
                    r'(\d+)\s+problem',
                    r'>(\d+)<.*?>problem',
                    r'problems?[:\s]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting Codeforces stats: {e}")
        return None
    
    def get_leetcode(self):
        """Fetch LeetCode statistics."""
        try:
            # Try LeetCode GraphQL API first
            url = "https://leetcode.com/graphql"
            query = {
                "query": """
                    query getUserProfile($username: String!) {
                        matchedUser(username: $username) {
                            submitStats {
                                acSubmissionNum {
                                    count
                                }
                            }
                        }
                    }
                """,
                "variables": {"username": "MishkatIT"}
            }
            
            headers = {
                'User-Agent': self.user_agent,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            req = Request(url, 
                         data=json.dumps(query).encode('utf-8'),
                         headers=headers,
                         method='POST')
            
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                ac_stats = data.get('data', {}).get('matchedUser', {}).get('submitStats', {}).get('acSubmissionNum', [])
                if ac_stats:
                    # First element is total accepted
                    return int(ac_stats[0].get('count', 0))
            
        except Exception as e:
            print(f"  API failed: {e}")
        
        # Fallback to web scraping
        try:
            print("  Trying web scraping...")
            url = "https://leetcode.com/MishkatIT/"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for LeetCode profile
                patterns = [
                    r'"solvedProblem"\s*:\s*(\d+)',
                    r'Solved["\s:]+(\d+)',
                    r'<span[^>]*>(\d+)</span>\s*<span[^>]*>Solved</span>',
                    r'(\d+)\s+/\s+\d+\s+Solved',
                    r'data-solved["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Web scraping failed: {e}")
        
        return None
    
    def get_vjudge(self):
        """Fetch Vjudge statistics."""
        try:
            url = "https://vjudge.net/user/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for solved count
                patterns = [
                    r'Solved[:\s]*<[^>]*>(\d+)',
                    r'Solved[:\s]*(\d+)',
                    r'<a[^>]*>(\d+)</a>[^<]*Solved',
                    r'solved["\s:=]+(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                    r'"solved"\s*:\s*(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting Vjudge stats: {e}")
        return None
    
    def get_atcoder(self):
        """Fetch AtCoder statistics."""
        try:
            url = "https://atcoder.jp/users/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for AC count
                patterns = [
                    r'(\d+)\s+AC',
                    r'AC[:\s]+(\d+)',
                    r'<td[^>]*>(\d+)</td>\s*<td[^>]*>AC</td>',
                    r'"ac"\s*:\s*(\d+)',
                    r'data-ac["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting AtCoder stats: {e}")
        return None
    
    def get_codechef(self):
        """Fetch CodeChef statistics using web scraping."""
        try:
            url = "https://www.codechef.com/users/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns to extract the problem count
                patterns = [
                    # CodeChef specific patterns
                    r'<h3>.*?Problems\s+Solved.*?</h3>\s*<div[^>]*>\s*<b>(\d+)</b>',
                    r'Problems\s+Solved[:\s]*</.*?>\s*<.*?>(\d+)</.*?>',
                    r'<div[^>]*>\s*Problems\s+Solved\s*</div>\s*<div[^>]*>\s*(\d+)',
                    r'<article[^>]*>.*?<h3>Problems.*?Solved</h3>.*?<div[^>]*>.*?<b>(\d+)</b>',
                    r'problems-solved[^>]*>.*?(\d+)',
                    r'fully\s+solved.*?(\d+)',
                    # Generic patterns
                    r'"problemsSolved"\s*:\s*(\d+)',
                    r'data-problems["\s:=]+(\d+)',
                    r'problem[s]?\s+solved[:\s]*(\d+)',
                    r'<span[^>]*>(\d+)</span>\s*<[^>]*>\s*Problems\s+Solved',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        count = int(match.group(1))
                        # Sanity check - CodeChef count should be reasonable
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
                
                # If no pattern matched, log for debugging
                print("  Warning: Could not find problem count in CodeChef HTML")
                
        except Exception as e:
            print(f"  Error getting CodeChef stats: {e}")
        return None
    
    def get_cses(self):
        """Fetch CSES statistics."""
        try:
            url = "https://cses.fi/user/165802/"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for tasks solved
                patterns = [
                    r'(\d+)\s+/\s+\d+\s+task',
                    r'Solved:\s*(\d+)',
                    r'<td[^>]*>(\d+)</td>\s*<td[^>]*>/\s*\d+\s+task',
                    r'"solved"\s*:\s*(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting CSES stats: {e}")
        return None
    
    def get_toph(self):
        """Fetch Toph statistics."""
        try:
            url = "https://toph.co/u/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for solved count
                patterns = [
                    r'(\d+)\s+solved',
                    r'Solved:\s*(\d+)',
                    r'<span[^>]*>(\d+)</span>\s*<[^>]*>\s*solved',
                    r'"solved"\s*:\s*(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting Toph stats: {e}")
        return None
    
    def get_lightoj(self):
        """Fetch LightOJ statistics."""
        try:
            url = "https://lightoj.com/user/mishkatit"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for solved problems
                patterns = [
                    r'Solved[:\s]*(\d+)',
                    r'Problems\s+Solved[:\s]*(\d+)',
                    r'<span[^>]*>(\d+)</span>\s*<[^>]*>\s*Solved',
                    r'"solved"\s*:\s*(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting LightOJ stats: {e}")
        return None
    
    def get_spoj(self):
        """Fetch SPOJ statistics."""
        try:
            url = "https://www.spoj.com/users/mishkatit/"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for problems solved
                patterns = [
                    r'Problems\s+solved[:\s]*(\d+)',
                    r'Solved[:\s]*(\d+)',
                    r'<td[^>]*>Problems\s+solved[:\s]*</td>\s*<td[^>]*>(\d+)',
                    r'"solved"\s*:\s*(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting SPOJ stats: {e}")
        return None
    
    def get_hackerrank(self):
        """Fetch HackerRank statistics."""
        try:
            url = "https://www.hackerrank.com/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for challenges solved
                patterns = [
                    r'(\d+)\s+challenges?\s+solved',
                    r'challenges?\s+solved[:\s]*(\d+)',
                    r'<span[^>]*>(\d+)</span>\s*<[^>]*>\s*challenges?\s+solved',
                    r'"challengesSolved"\s*:\s*(\d+)',
                    r'data-challenges["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting HackerRank stats: {e}")
        return None
    
    def get_uva(self):
        """Fetch UVa statistics."""
        try:
            # Try uhunt API first
            url = "https://uhunt.onlinejudge.org/api/subs-user/1615470"
            data = self.fetch_url(url, use_api=True)
            if data:
                solved = set()
                for sub in data.get('subs', []):
                    if len(sub) > 2 and sub[2] == 90:  # 90 is AC verdict
                        solved.add(sub[1])  # problem ID
                return len(solved)
        except Exception as e:
            print(f"  API failed: {e}")
        
        # Fallback to web scraping uhunt profile
        try:
            print("  Trying web scraping...")
            url = "https://uhunt.onlinejudge.org/id/1615470"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for solved count
                patterns = [
                    r'Solved[:\s]*(\d+)',
                    r'<td[^>]*>Solved[:\s]*</td>\s*<td[^>]*>(\d+)',
                    r'"solved"\s*:\s*(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Web scraping failed: {e}")
        
        return None
    
    def get_hackerearth(self):
        """Fetch HackerEarth statistics."""
        try:
            url = "https://www.hackerearth.com/@MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for problems solved
                patterns = [
                    r'(\d+)\s+problem',
                    r'Problems\s+Solved[:\s]*(\d+)',
                    r'<span[^>]*>(\d+)</span>\s*<[^>]*>\s*problem',
                    r'"problemsSolved"\s*:\s*(\d+)',
                    r'data-problems["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < self.MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting HackerEarth stats: {e}")
        return None
    
    def fetch_all_stats(self, verbose=True):
        """Fetch statistics from all platforms."""
        platforms = {
            'Codeforces': self.get_codeforces,
            'LeetCode': self.get_leetcode,
            'Vjudge': self.get_vjudge,
            'AtCoder': self.get_atcoder,
            'CodeChef': self.get_codechef,
            'CSES': self.get_cses,
            'Toph': self.get_toph,
            'LightOJ': self.get_lightoj,
            'SPOJ': self.get_spoj,
            'HackerRank': self.get_hackerrank,
            'UVa': self.get_uva,
            'HackerEarth': self.get_hackerearth,
        }
        
        if verbose:
            print("Fetching statistics from all platforms...\n")
        
        results = {}
        working_count = 0
        
        for platform, fetch_func in platforms.items():
            if verbose:
                print(f"Fetching {platform}...", end=' ')
            try:
                count = fetch_func()
                if count is not None:
                    results[platform] = count
                    working_count += 1
                    self._update_last_known(platform, count)
                    if verbose:
                        print(f"✓ {count} problems")
                else:
                    # Fetch failed, try to use last known count
                    last_known = self._get_last_known(platform)
                    if last_known is not None:
                        results[platform] = last_known
                        if verbose:
                            last_date = self.last_known_counts.get('dates', {}).get(platform, 'unknown date')
                            print(f"⚠ Using last known count: {last_known} (from {last_date})")
                    else:
                        if verbose:
                            print("✗ Failed (no last known count)")
                        results[platform] = None
            except Exception as e:
                if verbose:
                    print(f"✗ Error: {e}")
                # Try to use last known count
                last_known = self._get_last_known(platform)
                if last_known is not None:
                    results[platform] = last_known
                    if verbose:
                        last_date = self.last_known_counts.get('dates', {}).get(platform, 'unknown date')
                        print(f"  Using last known count: {last_known} (from {last_date})")
                else:
                    results[platform] = None
        
        # Save the updated last known counts
        self._save_last_known_counts()
        
        if verbose:
            print(f"\nSuccessfully fetched from {working_count}/{len(platforms)} platforms")
        
        return results


def main():
    """Main function to fetch and display statistics."""
    fetcher = PlatformStats()
    stats = fetcher.fetch_all_stats()
    
    print("\n" + "="*60)
    print("SUMMARY OF PROBLEM SOLVING STATISTICS")
    print("="*60)
    
    total = 0
    for platform, count in stats.items():
        if count is not None:
            print(f"{platform:15} : {count:5} problems")
            total += count
        else:
            print(f"{platform:15} : Failed to fetch")
    
    print("="*60)
    print(f"{'TOTAL':15} : {total:5} problems")
    print("="*60)
    
    # Output JSON for easy parsing
    print("\n\nJSON Output:")
    print(json.dumps(stats, indent=2))
    
    return stats


if __name__ == "__main__":
    main()
