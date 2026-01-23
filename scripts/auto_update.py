#!/usr/bin/env python
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
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Add src to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src import USER_CONFIG, MAX_REASONABLE_COUNT, USER_AGENT
from src.data_manager import DataManager

# Color and rich output
from colorama import init as colorama_init
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

colorama_init(autoreset=True)
console = Console()


class PlatformStats:
    """Class to handle fetching statistics from different platforms."""

    def fetch_with_selenium(self, url, wait_xpath=None):
        """Fetch page HTML using Selenium for JavaScript-rendered content. Optionally wait for an element by XPath."""
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        if wait_xpath:
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, wait_xpath))
                )
            except Exception as e:
                print(f"Timeout waiting for dynamic content at {url}")
        html = driver.page_source
        driver.quit()
        return html
    
    def __init__(self, user_config=None):
        self.user_config = user_config or USER_CONFIG
        self.stats = {}
        self.user_agent = USER_AGENT
        self.last_known_counts = DataManager.load_last_known_counts()

    def fetch_url(self, url, use_api=False, platform=None, check_status=True):
        """Fetch URL with proper headers, including platform-specific browser headers.
        
        Args:
            url: The URL to fetch
            use_api: Whether this is an API call (affects Accept header)
            platform: Platform name for specific headers
            check_status: Whether to explicitly check HTTP status code is 200
            
        Returns:
            Content string if successful, None if failed
        """
        try:
            # Default headers
            headers = {'User-Agent': self.user_agent}
            if use_api:
                headers['Accept'] = 'application/json'

            # Platform-specific browser headers
            if platform == "toki":
                headers.update({
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Connection": "keep-alive"
                })
            elif platform == "csacademy":
                headers.update({
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "X-Requested-With": "XMLHttpRequest",
                    "Connection": "keep-alive"
                })

            req = Request(url, headers=headers)
            with urlopen(req, timeout=10) as response:
                if check_status and response.getcode() != 200:
                    print(f"  HTTP {response.getcode()} for {url}")
                    return None
                    
                content = response.read()
                if use_api:
                    return json.loads(content.decode('utf-8'))
                return content.decode('utf-8')
        except HTTPError as e:
            if check_status:
                print(f"  HTTP {e.code} error for {url}")
            else:
                print(f"Error fetching {url}: {e}")
            return None
        except URLError as e:
            print(f"  Network error fetching {url}: {e}")
            return None
    
    def get_codeforces(self):
        """Fetch Codeforces statistics and rating."""
        try:
            # First get rating information
            rating_url = f"https://codeforces.com/api/user.info?handles={self.user_config['Codeforces']}"
            rating_data = self.fetch_url(rating_url, use_api=True)
            
            rating_info = None
            if rating_data and rating_data.get('status') == 'OK':
                user_info = rating_data.get('result', [{}])[0]
                rating_info = {
                    'current': user_info.get('rating'),
                    'max': user_info.get('maxRating'),
                    'rank': user_info.get('rank'),
                    'max_rank': user_info.get('maxRank')
                }
            
            url = f"https://codeforces.com/profile/{self.user_config['Codeforces']}"
            html = self.fetch_url(url)
            if not html:
                return None
                
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
                        return {'count': cnt, 'rating': rating_info}

            else:
                print("  web scraping failed, Trying api...")
                url = f"https://codeforces.com/api/user.status?handle={self.user_config['Codeforces']}&from=1&count=20000"
                data = self.fetch_url(url, use_api=True)
                
                if data and data.get('status') == 'OK':
                    submissions = data.get('result', [])
                    solved = set()
                    for sub in submissions:
                        if sub.get('verdict') == 'OK':
                            problem = sub.get('problem', {})
                            problem_id = f"{problem.get('contestId')}_{problem.get('index')}"
                            solved.add(problem_id)
                    return {'count': len(solved), 'rating': rating_info}
                elif data and data.get('status') == 'FAILED':
                    print(f"  Codeforces API error: {data.get('comment', 'Unknown error')}")
                    return None
                
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
            url = f"https://vjudge.net/user/{self.user_config['VJudge']}"
            html = self.fetch_url(url)
            if not html:
                return None
                
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
            if not html:
                return None
                
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
            if not html:
                return None
                
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
            if not html:
                return None
                
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
            if not html:
                return None
                
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
            url = f"https://www.spoj.com/users/{USER_CONFIG['SPOJ']}/"
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
            # Check if user exists by fetching profile page
            profile_url = f"https://uhunt.onlinejudge.org/id/{self.user_config['Uva']}"
            html = self.fetch_url(profile_url, check_status=True)
            if not html:
                return None
            
            # Try uhunt API
            url = f"https://uhunt.onlinejudge.org/api/subs-user/{self.user_config['Uva']}"
            data = self.fetch_url(url, use_api=True, check_status=True)
            if data and 'subs' in data:
                solved = set()
                for sub in data['subs']:
                    if len(sub) > 2 and sub[2] == 90:  # 90 is AC verdict
                        solved.add(sub[1])  # problem ID
                return len(solved)
        except Exception as e:
            print(f"  Error getting UVa stats (API): {e}")
        
        # Fallback to web scraping uhunt profile
        try:
            print("  Trying web scraping...")
            url = f"https://uhunt.onlinejudge.org/id/{self.user_config['Uva']}"
            html = self.fetch_url(url, check_status=True)
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
            url = f"https://www.hackerearth.com/@{self.user_config['HackerEarth']}"
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
    
    def get_kattis(self):
        """Fetch Kattis statistics."""
        try:
            url = f"https://open.kattis.com/users/{self.user_config['Kattis']}"
            html = self.fetch_url(url)
            if html:
                # Look for solved problems count
                patterns = [
                    r'(\d+)\s+problems?\s+solved',
                    r'Solved[:\s]*(\d+)',
                    r'Problems\s+solved[:\s]*(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting Kattis stats: {e}")
        return None
    
    def get_csacademy(self):
        """Fetch CSAcademy statistics using Selenium for JS-rendered content."""
        try:
            url = f"https://csacademy.com/user/{self.user_config['CSAcademy']}"
            # Wait for the profile username to appear (unique to loaded profile)
            wait_xpath = f"//h1[contains(text(), '{self.user_config['CSAcademy']}')]"
            html = self.fetch_with_selenium(url, wait_xpath=wait_xpath)
            if html:
                patterns = [
                    r'<span style="font-size: 1\.3em; margin-bottom: 10px;">Problems solved:\s*(\d+)</span>',
                    r'(\d+)\s+problems?\s+solved',
                    r'Solved[:\s]*(\d+)',
                    r'Problems\s+solved[:\s]*(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                    r'(\d+)\s+problems',
                    r'Problems[:\s]*(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
        except Exception as e:
            print(f"  Error getting CSAcademy stats: {e}")
        return None
    
    def get_toki(self):
        """Fetch Toki statistics using Selenium for JS-rendered content."""
        try:
            url = f"https://tlx.toki.id/profiles/{self.user_config['Toki']}"
            # Wait for the AC label to appear (unique to loaded profile)
            wait_xpath = "//b[text()='AC']"
            html = self.fetch_with_selenium(url, wait_xpath=wait_xpath)
            if html:
                patterns = [
                    r'<li[^>]*>.*?<b[^>]*>AC</b>.*?:.*?(\d+).*?</li>',
                    r'<li[^>]*>\s*<b[^>]*>\s*AC\s*</b>\s*:\s*(\d+)\s*</li>',
                    r'<li><b>AC</b>:\s*(\d+)</li>',
                    r'AC\s*:\s*(\d+)',
                    r'<b>AC</b>\s*:\s*(\d+)',
                    r'(\d+)\s+problems?\s+solved',
                    r'Solved[:\s]*(\d+)',
                    r'Problems\s+solved[:\s]*(\d+)',
                    r'data-solved["\s:=]+(\d+)',
                    r'(\d+)\s+problems',
                    r'Problems[:\s]*(\d+)',
                ]
                for pattern in patterns:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if 0 < count < MAX_REASONABLE_COUNT:
                            return count
            else:
                pass  # No HTML received, will return None
        except Exception as e:
            print(f"  Error getting Toki stats: {e}")
        return None
    
    def fetch_all_stats(self, verbose=True, max_workers=6):
        """Fetch statistics from all platforms using parallel processing."""
        platforms = {}
        missing_methods = []
        for platform in self.user_config:
            method_name = f'get_{platform.lower()}'
            if hasattr(self, method_name):
                platforms[platform] = getattr(self, method_name)
            else:
                missing_methods.append(platform)
        
        if verbose:
            from rich.live import Live
            funny_messages = [
                "[ROBOT] Machines think, we build their minds...",
                "[COFFEE] Waiting as computers wake from sleep...",
                "[TARGET] Chasing perfect answers in numbers...",
                "[ROCKET] Sending questions to the digital stars...",
                "[BRAIN] Training smart machines to think...",
                "[CLOCK] Time moves fast when gathering info...",
                "[CIRCUS] Many places, one big show...",
                "[HERO] Hero saves the day with data...",
                "[STAR] Collecting bright points from code space...",
                "[ART] Drawing pictures with solve numbers...",
                "[DETECTIVE] Exploring strange computer answers...",
                "[CIRCUS] Balancing many computer requests...",
                "[WIZARD] Using magic to get information...",
                "[MASK] Pretending to be different for each site...",
                "[UNICORN] Magic and math working as one...",
                "[CIRCUS] Big celebration of different places...",
                "[HEROINE] Hero puts together all the info...",
                "[RAINBOW] Looking for treasure in solve numbers...",
                "[CIRCUS] Playing tricks to get web data...",
                "[HERO] Fixing things, one computer call at a time...",
                "[ROBOT] Computer rules greet us...",
                "[COFFEE] Making new solve numbers...",
                "[TARGET] Hit the target, almost have the info...",
                "[ROCKET] Going far, getting more data...",
                "[ICE] Starting talks with quiet computers...",
                "[CIRCUS] Fun place full of information...",
                "[HERO] Many tasks working at once...",
                "[STAR] Everything coming together perfectly...",
                "[ART] Making beautiful number pictures...",
                "[DETECTIVE] Figuring out why computers are slow...",
                "[CIRCUS] Doing tricks with computer connections...",
                "[WIZARD] Calling information from the sky...",
                "[MASK] Pretending to be a regular web viewer...",
                "[UNICORN] Magic changing data into new forms...",
                "[HOURGLASS] Time passes, code stays...",
                "[EARTH] World changes, code grows...",
                "[DISK] Data disappears, ideas stay...",
                "[GALAXY] In endless digital space, we code...",
                "[LIGHTNING] Code outlives whole societies...",
                "[SWIRL] Code flows like never-ending rivers...",
                "[CRYSTAL] Ideas go beyond our bodies...",
                "[MOON] In empty space, code speaks softly...",
                "[THOUGHT] Code has dreams in computer chips...",
                "[DANCE] Code moves through time like a dance...",
                "[SCROLL] Code is like poems for robots...",
                "[CYCLE] In the big computer world, we fix bugs...",
                "[COMET] Information travels forever...",
                "[BALANCE] Shapes and patterns never die...",
                "[CIRCUS] Code makes sounds in the emptiness...",
                "[STAR] In this huge computer game, we calculate...",
                "[HOURGLASS] Code creates worlds, time breaks them...",
                "[SEARCH] Code looks for real truth in numbers...",
                "[MOON] Code is the way to live forever..."
            ]
            
            import time
            import random
            
            # Initial message
            current_display = Panel("[bold cyan]Fetching statistics from all platforms (parallel processing)...[/bold cyan]", expand=False)
            
            results = {}
            messages = {}
            working_count = 0
            fresh_fetches = {}  # Track which platforms had fresh data
            fetch_times = {}  # Track fetch times for each platform
            
            def fetch_single_platform(platform):
                """Fetch stats for a single platform and return results."""
                start_time = time.time()
                fetch_func = platforms[platform]
                try:
                    result = fetch_func()
                    end_time = time.time()
                    fetch_time = end_time - start_time
                    
                    # Handle both old format (just count) and new format (dict with count and rating)
                    if isinstance(result, dict):
                        count = result.get('count')
                        rating_info = result.get('rating')
                    else:
                        count = result
                        rating_info = None
                    
                    if count is not None:
                        # Data successfully fetched - update count, date, and mode to 'automatic'
                        DataManager.update_last_known(self.last_known_counts, platform, count, mode='automatic')
                        
                        # Store rating info if available (for Codeforces)
                        if rating_info and platform == 'Codeforces':
                            self.last_known_counts.setdefault('ratings', {})
                            self.last_known_counts['ratings']['Codeforces'] = rating_info
                            DataManager.save_last_known_counts(self.last_known_counts)
                        
                        return platform, count, None, True, fetch_time  # True for is_fresh
                    else:
                        # Fetch failed, try to use last known count
                        last_known = DataManager.get_last_known(self.last_known_counts, platform)
                        if last_known is not None:
                            # Do NOT update mode when using cached data - keep the last stored mode
                            last_date = self.last_known_counts.get('dates', {}).get(platform, 'unknown date')
                            last_mode = DataManager.get_last_known_mode(self.last_known_counts, platform)
                            end_time = time.time()
                            fetch_time = end_time - start_time
                            return platform, last_known, f"Fetch failed - Using cached count: {last_known} (from {last_date}, mode: {last_mode})", False, fetch_time  # False for is_fresh
                        else:
                            end_time = time.time()
                            fetch_time = end_time - start_time
                            return platform, None, "Fetch failed - No cached data available", False, fetch_time
                except Exception as e:
                    # Try to use last known count
                    last_known = DataManager.get_last_known(self.last_known_counts, platform)
                    if last_known is not None:
                        # Do NOT update mode when using cached data - keep the last stored mode
                        last_date = self.last_known_counts.get('dates', {}).get(platform, 'unknown date')
                        last_mode = DataManager.get_last_known_mode(self.last_known_counts, platform)
                        end_time = time.time()
                        fetch_time = end_time - start_time
                        return platform, last_known, f"Exception occurred - Using cached count: {last_known} (from {last_date}, mode: {last_mode})", False, fetch_time  # False for is_fresh
                    else:
                        end_time = time.time()
                        fetch_time = end_time - start_time
                        return platform, None, f"Exception occurred - No cached data available", False, fetch_time
            
            # Use ThreadPoolExecutor for parallel fetching with Live display
            with Live(current_display, console=console, refresh_per_second=2) as live:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_platform = {executor.submit(fetch_single_platform, platform): platform for platform in platforms}
                    
                    # # Start funny message Live display with blank screen initially
                    funny_message_display = Panel("", expand=False)  # Start with empty display
                    funny_live = Live(funny_message_display, console=console, refresh_per_second=1)
                    funny_live.start()
                    
                    # Start funny message printing thread
                    funny_printing_running = True
                    def print_funny_messages():
                        time.sleep(3.0)  # Wait 3 seconds before starting messages
                        while funny_printing_running:
                            funny_message = random.choice(funny_messages)
                            # Update the funny message display
                            new_display = Panel(f"[bold bright_magenta]🎭 {funny_message}[/bold bright_magenta]", expand=False)
                            funny_live.update(new_display)
                            time.sleep(4.0)  # Print every 4 seconds
                    
                    funny_thread = threading.Thread(target=print_funny_messages, daemon=True)
                    funny_thread.start()
                    
                    funny_thread = threading.Thread(target=print_funny_messages, daemon=True)
                    funny_thread.start()
                    
                    completed_count = 0
                    for future in as_completed(future_to_platform):
                        platform = future_to_platform[future]
                        
                        # Update display to show current platform being fetched
                        current_display = Panel(f"[bold cyan]Fetching statistics from all platforms...[/bold cyan]\n[bold bright_blue]Currently fetching: {platform}[/bold bright_blue]", expand=False)
                        live.update(current_display)
                        
                        try:
                            platform_name, count, message, is_fresh, fetch_time = future.result()
                            results[platform_name] = count
                            messages[platform_name] = message
                            fetch_times[platform_name] = fetch_time
                            if count is not None:
                                if is_fresh:
                                    working_count += 1
                                fresh_fetches[platform_name] = is_fresh
                        except Exception as e:
                            results[platform] = None
                            messages[platform] = f"Unexpected error: {e}"
                        
                        completed_count += 1
                        # Add small delay to make the process visible
                        time.sleep(0.1)
                
                # Stop the funny message Live display
                funny_printing_running = False
                funny_thread.join(timeout=1.0)
                funny_live.stop()
                
                # Show completion message
                time.sleep(1.0)  # Brief pause
                completion_display = Panel("[bold green]Fetching completed![/bold green]", expand=False)
                live.update(completion_display)
            
            # Now print all platform results after the Live display
            # (Removed - results will be shown in summary table instead)
        
        # Handle platforms without implemented fetch methods
        for platform in missing_methods:
            results[platform] = None
            messages[platform] = "No method implemented - Try manual update"
            fresh_fetches[platform] = False  # Not fresh since no fetch method
            if verbose:
                console.print(f"{platform:<12} [bold bright_red][NO METHOD][/bold bright_red] [dim red]└─ No method implemented - Try manual update[/dim red]")
        
        # Save the updated last known counts
        DataManager.save_last_known_counts(self.last_known_counts)
        
        if verbose:
            total_platforms = len(platforms) + len(missing_methods)
            cached_count = sum(1 for is_fresh in fresh_fetches.values() if not is_fresh)
            console.print(Panel(f"[bold green]Successfully fetched from {working_count}/{total_platforms} platforms[/bold green] ([cyan]{working_count} fresh[/cyan], [yellow]{cached_count} cached[/yellow])", expand=False))
        
        return results, messages, fresh_fetches, fetch_times


def main():
    """Main function to fetch and display statistics."""
    # Ensure configuration is up to date before proceeding
    with console.status("[bold blue]Configuring handles from handles.json...[/bold blue]", spinner="dots"):
        try:
            import subprocess
            result = subprocess.run([sys.executable, 'scripts/configure_handles.py'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                console.print(Panel(f"[red]ERROR: configure_handles failed: {result.stdout}\nCannot continue with invalid handles.json[/red]", border_style="red", expand=False))
                console.print(Panel("[red]Please fix the syntax error in handles.json and try again.[/red]", border_style="red", expand=False))
                return  # Exit main function
            elif result.stdout.strip():
                console.print(Panel(f"[green][OK] {result.stdout.strip()}[/green]", border_style="green", expand=False))
            # Reload configuration after configure_handles potentially updated it
            with console.status("[bold blue]Reloading configuration...[/bold blue]", spinner="dots"):
                import importlib
                import src
                importlib.reload(src)
                import src.data_manager
                importlib.reload(src.data_manager)
                # Re-import the updated config variables
                from src import USER_CONFIG, MAX_REASONABLE_COUNT, USER_AGENT
                globals()['USER_CONFIG'] = USER_CONFIG
                globals()['MAX_REASONABLE_COUNT'] = MAX_REASONABLE_COUNT  
                globals()['USER_AGENT'] = USER_AGENT
        except Exception as e:
            console.print(Panel(f"[yellow]WARNING: configure_handles or config reload failed: {e}\nContinuing with existing configuration...[/yellow]", border_style="yellow", expand=False))
    
    fetcher = PlatformStats()
    stats, messages, fresh_fetches, fetch_times = fetcher.fetch_all_stats()
    console.rule("[bold magenta]SUMMARY OF PROBLEM SOLVING STATISTICS[/bold magenta]", style="magenta")
    from rich import box
    table = Table(show_header=True, header_style="bold blue", box=box.SIMPLE, show_lines=True, padding=(0,1))
    table.add_column("[cyan]Platform[/cyan]", style="bold cyan", justify="left")
    table.add_column("[green]Count[/green]", style="bold green", justify="right")
    table.add_column("[yellow]Source[/yellow]", style="yellow", justify="center")
    table.add_column("[blue]Time[/blue]", style="cyan", justify="right")
    table.add_column("[white]Status/Reason[/white]", style="dim", justify="left")
    total = 0
    for platform, count in stats.items():
        fetch_time = fetch_times.get(platform, 0)
        # Format time nicely
        if fetch_time < 1.0:
            time_str = f"{fetch_time*1000:.0f}ms"
        else:
            time_str = f"{fetch_time:.1f}s"
        
        if count is not None:
            source = "[bold green][FRESH][/bold green]" if fresh_fetches.get(platform, False) else "[yellow][CACHED][/yellow]"
            reason = messages.get(platform, '')
            table.add_row(f"[bold]{platform}[/bold]", f"[bold]{count}[/bold]", source, f"[cyan]{time_str}[/cyan]", reason)
            total += count
        else:
            reason = messages.get(platform, 'Unknown reason')
            table.add_row(f"[bold]{platform}[/bold]", "-", "[red][FAILED][/red]", f"[cyan]{time_str}[/cyan]", f"[red]Failed to fetch[/red] - {reason}")
    console.print(table)
    console.print(Panel(f"[bold green]TOTAL:[/bold green] [bold yellow]{total} problems[/bold yellow]", border_style="green", expand=False))
    fresh_count = sum(1 for is_fresh in fresh_fetches.values() if is_fresh)
    cached_count = sum(1 for is_fresh in fresh_fetches.values() if not is_fresh)
    console.print(Panel(f"[cyan]Fresh:[/cyan] [bold]{fresh_count}[/bold]   [yellow]Cached:[/yellow] [bold]{cached_count}[/bold]", border_style="cyan", expand=False))
    
    # Check for slow platforms and provide suggestions
    slow_threshold = 10.0  # 10 seconds threshold for "slow"
    slow_platforms = [(platform, time) for platform, time in fetch_times.items() if time >= slow_threshold]
    if slow_platforms:
        slow_platforms.sort(key=lambda x: x[1], reverse=True)  # Sort by time descending
        slow_list = ", ".join([f"{platform} ({time:.1f}s)" for platform, time in slow_platforms[:3]])  # Top 3 slowest
        console.print(Panel(f"[yellow][SLOW PLATFORMS][/yellow] {slow_list} took unusually long to fetch.\n"
                           f"Consider updating these manually if you're not actively solving there - no need to check daily!\n"
                           f"Use: [cyan]python scripts/manual_update.py[/cyan]", 
                           border_style="yellow", expand=False))
    
    # Persist stats for README updater and repo tracking
    DataManager.save_stats(stats)

    # Update README after fetching (useful for scheduled automation)
    try:
        console.print(Panel("[bold blue]Updating README.md...[/bold blue]", border_style="blue", expand=False))
        import subprocess
        import os
        env = os.environ.copy()
        env['PYTHONPATH'] = os.getcwd()
        result = subprocess.run([sys.executable, 'scripts/update_readme.py'], 
                              timeout=30, cwd=os.getcwd(), env=env)
        if result.returncode != 0:
            console.print(Panel("[yellow]WARNING: README update may have failed (check output above)[/yellow]", border_style="yellow", expand=False))
        else:
            console.print(Panel("[green][OK] README updated successfully![/green]", border_style="green", expand=False))
    except Exception as e:
        console.print(Panel(f"[yellow]WARNING: README update skipped/failed: {e}[/yellow]", border_style="yellow", expand=False))

    # Check and adjust schedule based on solving activity
    try:
        console.print(Panel("[bold blue]Checking if schedule adjustment is needed...[/bold blue]", border_style="blue", expand=False))
        import subprocess
        result = subprocess.run([sys.executable, 'scripts/check_and_adjust_schedule.py'], 
                              timeout=30)
        if result.returncode != 0:
            console.print(Panel("[yellow]WARNING: Schedule check may have failed (check output above)[/yellow]", border_style="yellow", expand=False))
    except Exception as e:
        console.print(Panel(f"[yellow]Note: Schedule check skipped: {e}[/yellow]", border_style="yellow", expand=False))

    return stats


if __name__ == "__main__":
    main()
