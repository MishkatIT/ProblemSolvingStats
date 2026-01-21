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
- AtCoder (API + web scraping fallback)
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
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

from src import USER_CONFIG, MAX_REASONABLE_COUNT, USER_AGENT
from src.data_manager import DataManager


def parse_url(url):
    """Parse URL to extract platform and username."""
    known_templates = {
        'Codeforces': 'https://codeforces.com/profile/{username}',
        'LeetCode': 'https://leetcode.com/{username}/',
        'Vjudge': 'https://vjudge.net/user/{username}',
        'AtCoder': 'https://atcoder.jp/users/{username}',
        'CodeChef': 'https://www.codechef.com/users/{username}',
        'CSES': 'https://cses.fi/user/{username}/',
        'Toph': 'https://toph.co/u/{username}',
        'LightOJ': 'https://lightoj.com/user/{username}',
        'SPOJ': 'https://www.spoj.com/users/{username}/',
        'HackerRank': 'https://www.hackerrank.com/{username}',
        'UVa': 'https://uhunt.onlinejudge.org/id/{username}',
        'HackerEarth': 'https://www.hackerearth.com/@{username}'
    }
    known_domains = {
        'codeforces.com': 'Codeforces',
        'leetcode.com': 'LeetCode',
        'vjudge.net': 'Vjudge',
        'atcoder.jp': 'AtCoder',
        'codechef.com': 'CodeChef',
        'cses.fi': 'CSES',
        'toph.co': 'Toph',
        'lightoj.com': 'LightOJ',
        'spoj.com': 'SPOJ',
        'hackerrank.com': 'HackerRank',
        'onlinejudge.org': 'UVa',
        'hackerearth.com': 'HackerEarth'
    }
    for platform, template in known_templates.items():
        # Create regex pattern by escaping and replacing {username} with (.+)
        pattern = re.escape(template).replace(r'\{username\}', r'(.+)')
        match = re.match(pattern + r'/?$', url.strip())  # Allow trailing slash
        if match:
            username = match.group(1)
            return platform, username

    # Try to parse unknown URL
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path.strip('/')
    if domain and path:
        platform = known_domains.get(domain, domain)
        username = path
        return platform, username

    return None, None


def get_favicon_url(url):
    """Return Google favicon service URL for a given profile URL. Fallback to /favicon.ico if Google fails."""
    parsed = urlparse(url)
    google_favicon = f"https://www.google.com/s2/favicons?domain={parsed.netloc}&sz=16"
    try:
        resp = requests.get(google_favicon, timeout=3)
        if resp.status_code == 200 and resp.content:
            return google_favicon
    except Exception:
        pass
    # Fallback to direct favicon.ico
    return f"https://{parsed.netloc}/favicon.ico"


def update_config_file(new_user_config, new_platform_logos, new_templates):
    """Update the config.json file with new configuration."""
    config_path = 'src/config.json'

    # Colors for platforms
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'cyan', 'magenta']

    # Create config dict
    config = {
        'USER_CONFIG': new_user_config,
        'PROFILE_DISPLAY_NAMES': {platform: new_user_config[platform] for platform in new_user_config},
        'PLATFORM_URL_TEMPLATES': {platform: new_templates[platform] for platform in new_user_config if new_templates.get(platform)},
        'PLATFORM_LOGOS': {platform: new_platform_logos.get(platform, ('', False)) for platform in new_user_config},
        'PLATFORM_COLORS': {platform: colors[hash(platform) % len(colors)] for platform in new_user_config},
        'ALL_PLATFORMS': sorted(new_user_config.keys()),
        'LAST_KNOWN_FILE': 'last_known_counts.json',
        'STATS_FILE': 'stats.json',
        'README_FILE': 'README.md',
        'MAX_REASONABLE_COUNT': 10000,
        'BDT_TIMEZONE_hours': 6,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DEFAULT_FUNNY_DATE': "1970-01-01"
    }

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)


def auto_configure_handles():
    """Automatically configure handles from handles.json if it has changed."""
    if not os.path.exists('handles.json'):
        return False  # No handles.json, skip

    try:
        with open('handles.json', 'r', encoding='utf-8') as f:
            urls = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load handles.json: {e}")
        return False

    if not urls:
        return False  # Empty, skip

    # Parse URLs to get new config
    new_user_config = {}
    url_dict = {}
    for url in urls:
        if isinstance(url, str) and url.strip():
            platform, username = parse_url(url.strip())
            if platform:
                new_user_config[platform] = username
                url_dict[platform] = url.strip()

    if not new_user_config:
        return False  # No valid handles

    # Load current config
    config_path = 'src/config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        current_user_config = config.get('USER_CONFIG', {})
        current_platform_logos = config.get('PLATFORM_LOGOS', {})
    else:
        current_user_config = {}
        current_platform_logos = {}

    # Check if changed
    if new_user_config == current_user_config:
        return False  # No changes

    print("Configuration changed, updating...")

    # Build new_templates
    new_templates = {}
    for platform in new_user_config:
        url = url_dict[platform]
        username = new_user_config[platform]
        template = url.replace(username, '{username}')
        new_templates[platform] = template

    # Determine added, removed, changed
    current_platforms = set(current_user_config.keys())
    new_platforms = set(new_user_config.keys())

    added = new_platforms - current_platforms
    removed = current_platforms - new_platforms
    changed = {p for p in current_platforms & new_platforms if current_user_config[p] != new_user_config[p]}

    print(f"Added platforms: {added}")
    print(f"Removed platforms: {removed}")
    print(f"Changed platforms: {changed}")

    # Update PLATFORM_LOGOS for new platforms
    new_platform_logos = current_platform_logos.copy()
    for platform in added:
        if platform not in new_platform_logos:
            template = new_templates[platform]
            if template:
                url = template.format(username=new_user_config[platform])
                logo_url = get_favicon_url(url)
                new_platform_logos[platform] = (logo_url, True)
                print(f"Added logo for {platform}: {logo_url}")
            else:
                new_platform_logos[platform] = ('', False)

    # Update config
    update_config_file(new_user_config, new_platform_logos, new_templates)

    # Clean up last_known_counts for removed platforms
    if removed:
        last_known = DataManager.load_last_known_counts()
        for platform in removed:
            last_known['counts'].pop(platform, None)
            last_known['dates'].pop(platform, None)
            last_known['modes'].pop(platform, None)
            last_known['last_solved_dates'].pop(platform, None)
            last_known['usernames'].pop(platform, None)
        DataManager.save_last_known_counts(last_known)
        print(f"Cleaned data for removed platforms: {removed}")

    print("Configuration updated successfully!")
    return True


class PlatformStats:
    """Class to handle fetching statistics from different platforms."""
    
    def __init__(self, user_config=None):
        self.user_config = user_config or USER_CONFIG
        self.stats = {}
        self.user_agent = USER_AGENT
        self.last_known_counts = DataManager.load_last_known_counts()

    def _save_last_known_counts(self):
        """Save the current known good counts to file."""
        DataManager.save_last_known_counts(self.last_known_counts)
    
    def _get_last_known(self, platform):
        """Get the last known count for a platform."""
        return DataManager.get_last_known(self.last_known_counts, platform)
    
    def _get_last_known_mode(self, platform):
        """Get the last known update mode for a platform."""
        return DataManager.get_last_known_mode(self.last_known_counts, platform)

    def _update_last_known(self, platform, count, mode=None):
        """Update the last known count and mode for a platform."""
        DataManager.update_last_known(self.last_known_counts, platform, count, mode)
    
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
            url = f"https://codeforces.com/profile/{self.user_config['Codeforces']}"
            html = self.fetch_url(url)
            if html:
                patterns = [
                    # actual current CF profile source (best)
                    r'class="_UserActivityFrame_counterValue">\s*(\d+)\s+problems',

                    # fallback (older / alternative)
                    r'Problems\s+solved:\s*(\d+)',
                    r'class="problem-count">\s*(\d+)\s*<',

                    # legacy JS (rare)
                    r'"solvedProblemCount"\s*:\s*(\d+)',
                    r'"solvedProblems"\s*:\s*(\d+)',
                    r'var\s+solvedProblems\s*=\s*(\d+)',
                ]

                for pat in patterns:
                    m = re.search(pat, html, re.IGNORECASE)
                    if m:
                        cnt = int(m.group(1))
                        if 0 < cnt < MAX_REASONABLE_COUNT:
                            return cnt

            else:
                print("  web scraping failed, Trying api...")
                url = f"https://codeforces.com/api/user.status?handle={self.user_config['Codeforces']}&from=1&count=10000"
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
                
                print("  API failed")
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
                "variables": {"username": self.user_config['LeetCode']}
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
            print(f"  Error getting LeetCode stats (API): {e}")
        
        # Fallback to web scraping
        try:
            print("  Trying web scraping...")
            url = f"https://leetcode.com/{self.user_config['LeetCode']}/"
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
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Web scraping failed: {e}")
        
        return None
    
    def get_vjudge(self):
        """Fetch Vjudge statistics."""
        try:
            url = f"https://vjudge.net/user/{self.user_config['Vjudge']}"
            html = self.fetch_url(url)
            if html:
                patterns = [
                    # Exact match for current VJudge structure
                    r'<a[^>]*title="Overall solved[^"]*"[^>]*>(\d+)</a>',

                    # Fallbacks (in case HTML changes)
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
                        cnt = int(match.group(1))
                        if 0 < cnt < MAX_REASONABLE_COUNT:
                            return cnt

        except Exception as e:
            print(f"  Error getting Vjudge stats: {e}")
        return None
    
    def get_atcoder(self):
        """Fetch AtCoder statistics."""
        try:
            # Try API first (requests handles gzip/deflate reliably)
            # Note: API expects lowercase username
            try:
                import requests

                url = "https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions"
                user = self.user_config['AtCoder']

                solved = set()
                from_second = 0

                # The API supports incremental fetching via from_second.
                # Some environments may get truncated responses; loop defensively.
                with requests.Session() as session:
                    for _ in range(50):
                        res = session.get(url, params={"user": user, "from_second": from_second}, timeout=30)
                        res.raise_for_status()
                        batch = res.json()

                        if not isinstance(batch, list) or not batch:
                            break

                        max_epoch = None
                        for sub in batch:
                            if not isinstance(sub, dict):
                                continue
                            if sub.get('result') == 'AC' and sub.get('problem_id'):
                                solved.add(sub['problem_id'])
                            epoch = sub.get('epoch_second')
                            if isinstance(epoch, int):
                                max_epoch = epoch if max_epoch is None else max(max_epoch, epoch)

                        if max_epoch is None or max_epoch < from_second:
                            break
                        from_second = max_epoch + 1

                count = len(solved)
                if 0 <= count < MAX_REASONABLE_COUNT:
                    return count
            except Exception as e:
                print(f"  AtCoder requests API failed: {e}")
            
            # Fallback to web scraping profile page
            print("  API failed, trying web scraping...")
            # Note: Profile page uses mixed case username
            url = f"https://atcoder.jp/users/{self.user_config['AtCoder']}"
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
                        if 0 <= count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting AtCoder stats: {e}")
        return None
    
    def get_codechef(self):
        """Fetch CodeChef statistics using web scraping."""
        try:
            url = f"https://www.codechef.com/users/{self.user_config['CodeChef']}"
            html = self.fetch_url(url)
            if html:
                # Prefer the explicit summary line many profiles include:
                # e.g. "Total Problems Solved: 123"
                explicit_patterns = [
                    r'Total\s+Problems\s+Solved\s*:\s*(\d+)',
                    r'Total\s+Problems\s+Solved\s*</[^>]+>\s*(\d+)',
                ]

                # Search raw HTML first
                for pattern in explicit_patterns:
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        count = int(match.group(1))
                        if 0 <= count < MAX_REASONABLE_COUNT:
                            return count

                # Then search a tag-stripped version to handle HTML elements between words
                text_only = re.sub(r'<[^>]+>', ' ', html)
                text_only = re.sub(r'\s+', ' ', text_only)
                for pattern in explicit_patterns:
                    match = re.search(pattern, text_only, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 <= count < MAX_REASONABLE_COUNT:
                            return count

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
                        if 0 <= count < MAX_REASONABLE_COUNT:
                            return count
                
                # If no pattern matched, log for debugging
                print("  Warning: Could not find problem count in CodeChef HTML")
                
        except Exception as e:
            print(f"  Error getting CodeChef stats: {e}")
        return None
    
    def get_cses(self):
        """Fetch CSES statistics."""
        try:
            url = f"https://cses.fi/user/{self.user_config['CSES']}/"
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
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting CSES stats: {e}")
        return None
    
    def get_toph(self):
        """Fetch Toph statistics."""
        try:
            url = f"https://toph.co/u/{self.user_config['Toph']}"
            html = self.fetch_url(url)
            if html:
                soup = BeautifulSoup(html, "html.parser")
                for t in soup.select("div.title"):
                    if t.text.strip() == "Solutions":
                        cnt = int(t.find_previous("div", class_="value").text)
                        return cnt


        except Exception as e:
            print(f"  Error getting Toph stats: {e}")
        return None
    
    def get_lightoj(self):
        """Fetch LightOJ statistics."""
        try:
            url = f"https://lightoj.com/user/{self.user_config['LightOJ']}"
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
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting LightOJ stats: {e}")
        return None
    
    def get_spoj(self):
        """Fetch SPOJ statistics."""
        try:
            url = f"https://www.spoj.com/users/{self.user_config['SPOJ']}/"
            html = self.fetch_url(url)
            if html:
                # Try multiple patterns for problems solved
                patterns = [
                    r'Problems\s+solved[:\s]*(\d+)',
                    r'<td[^>]*>Problems\s+solved[:\s]*</td>\s*<td[^>]*>(\d+)',
                    r'solved[:\s]*</td>\s*<td[^>]*>(\d+)',
                    r'Solved[:\s]*(\d+)',
                    r'"solved"\s*:\s*(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting SPOJ stats: {e}")
        return None
    
    def get_hackerrank(self):
        """Fetch HackerRank statistics."""
        try:
            url = f"https://www.hackerrank.com/{self.user_config['HackerRank']}"
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
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting HackerRank stats: {e}")
        return None
    
    def get_uva(self):
        """Fetch UVa statistics."""
        try:
            # Try uhunt API first
            url = f"https://uhunt.onlinejudge.org/api/subs-user/{self.user_config['UVa']}"
            data = self.fetch_url(url, use_api=True)
            if data:
                solved = set()
                for sub in data.get('subs', []):
                    if len(sub) > 2 and sub[2] == 90:  # 90 is AC verdict
                        solved.add(sub[1])  # problem ID
                return len(solved)
        except Exception as e:
            print(f"  Error getting UVa stats (API): {e}")
        
        # Fallback to web scraping uhunt profile
        try:
            print("  Trying web scraping...")
            url = f"https://uhunt.onlinejudge.org/id/{self.user_config['UVa']}"
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
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Web scraping failed: {e}")
        
        return None
    
    def get_hackerearth(self):
        """Fetch HackerEarth statistics."""
        try:
            url = f"https://www.hackerearth.com/@{USER_CONFIG['HackerEarth']}"
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
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting HackerEarth stats: {e}")
        return None
    
    def fetch_all_stats(self, verbose=True):
        """Fetch statistics from all platforms."""
        platforms = {}
        for platform in self.user_config:
            method_name = f'get_{platform.lower()}'
            if hasattr(self, method_name):
                platforms[platform] = getattr(self, method_name)
        
        if verbose:
            print("Fetching statistics from all platforms...\n")
        
        results = {}
        working_count = 0
        
        for platform, fetch_func in platforms.items():
            if verbose:
                print(f"Fetching {platform}...")
                print(end=' ')
            try:
                count = fetch_func()
                if count is not None:
                    results[platform] = count
                    working_count += 1
                    # Data successfully fetched - update count, date, and mode to 'automatic'
                    self._update_last_known(platform, count, mode='automatic')
                    if verbose:
                        print(f"✓ {count} problems")
                else:
                    # Fetch failed, try to use last known count
                    last_known = self._get_last_known(platform)
                    if last_known is not None:
                        results[platform] = last_known
                        # Do NOT update mode when using cached data - keep the last stored mode
                        if verbose:
                            last_date = self.last_known_counts.get('dates', {}).get(platform, 'unknown date')
                            last_mode = self._get_last_known_mode(platform)
                            print(f"⚠ Using last known count: {last_known} (from {last_date}, mode: {last_mode})")
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
                    # Do NOT update mode when using cached data - keep the last stored mode
                    if verbose:
                        last_date = self.last_known_counts.get('dates', {}).get(platform, 'unknown date')
                        last_mode = self._get_last_known_mode(platform)
                        print(f"  Using last known count: {last_known} (from {last_date}, mode: {last_mode})")
                else:
                    results[platform] = None
        
        # Save the updated last known counts
        self._save_last_known_counts()
        
        if verbose:
            print(f"\nSuccessfully fetched from {working_count}/{len(platforms)} platforms")
        
        return results


def main():
    """Main function to fetch and display statistics."""
    # Auto-configure handles if changed
    config_updated = auto_configure_handles()
    if config_updated:
        # Reload config after update
        import importlib
        import src
        importlib.reload(src)
        # Get updated config
        from src import USER_CONFIG as updated_user_config
    else:
        updated_user_config = USER_CONFIG
    
    fetcher = PlatformStats(user_config=updated_user_config)
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

    # Persist stats for README updater and repo tracking
    DataManager.save_stats(stats)

    # Update README after fetching (useful for scheduled automation)
    try:
        import update_readme
        # Pass update_source as 'automatic' for auto-updates
        update_readme.update_readme(stats, last_known_info=fetcher.last_known_counts, update_source='automatic')
    except Exception as e:
        print(f"Warning: README update skipped/failed: {e}")
    
    # Check and adjust schedule based on solving activity
    try:
        print("\n" + "="*60)
        print("Checking if schedule adjustment is needed...")
        print("="*60)
        import subprocess
        result = subprocess.run(['python', 'check_and_adjust_schedule.py'], 
                              capture_output=True, text=True, timeout=30)
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"Schedule check warning: {result.stderr}")
    except Exception as e:
        print(f"Note: Schedule check skipped: {e}")
    
    return stats


if __name__ == "__main__":
    main()
