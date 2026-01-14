#!/usr/bin/env python3
"""
Script to fetch and update problem-solving statistics from various competitive programming platforms.
Author: MishkatIT
"""

import re
import json
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import datetime


class PlatformStats:
    """Class to handle fetching statistics from different platforms."""
    
    def __init__(self):
        self.stats = {}
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
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
            url = "https://codeforces.com/profile/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Look for problem count in profile
                match = re.search(r'(\d+)\s+problem', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting Codeforces stats: {e}")
        return None
    
    def get_leetcode(self):
        """Fetch LeetCode statistics."""
        try:
            # LeetCode GraphQL API
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
            print(f"Error getting LeetCode stats: {e}")
        return None
    
    def get_vjudge(self):
        """Fetch Vjudge statistics."""
        try:
            url = "https://vjudge.net/user/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Look for solved count
                match = re.search(r'Solved[:\s]*(\d+)', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
                # Alternative pattern
                match = re.search(r'<a[^>]*>(\d+)</a>[^<]*Solved', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting Vjudge stats: {e}")
        return None
    
    def get_atcoder(self):
        """Fetch AtCoder statistics."""
        try:
            url = "https://atcoder.jp/users/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Look for AC count
                match = re.search(r'(\d+)\s+AC', html)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting AtCoder stats: {e}")
        return None
    
    def get_codechef(self):
        """Fetch CodeChef statistics."""
        try:
            url = "https://www.codechef.com/users/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Look for problems solved
                match = re.search(r'Problems\s+Solved[^>]*>.*?(\d+)', html, re.IGNORECASE | re.DOTALL)
                if match:
                    return int(match.group(1))
                match = re.search(r'(\d+)[^<]*Problems', html)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting CodeChef stats: {e}")
        return None
    
    def get_cses(self):
        """Fetch CSES statistics."""
        try:
            url = "https://cses.fi/user/165802/"
            html = self.fetch_url(url)
            if html:
                # Look for tasks solved
                match = re.search(r'(\d+)\s+/\s+\d+\s+task', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting CSES stats: {e}")
        return None
    
    def get_toph(self):
        """Fetch Toph statistics."""
        try:
            url = "https://toph.co/u/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Look for solved count
                match = re.search(r'(\d+)\s+solved', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting Toph stats: {e}")
        return None
    
    def get_lightoj(self):
        """Fetch LightOJ statistics."""
        try:
            url = "https://lightoj.com/user/mishkatit"
            html = self.fetch_url(url)
            if html:
                # Look for solved problems
                match = re.search(r'Solved[:\s]*(\d+)', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting LightOJ stats: {e}")
        return None
    
    def get_spoj(self):
        """Fetch SPOJ statistics."""
        try:
            url = "https://www.spoj.com/users/mishkatit/"
            html = self.fetch_url(url)
            if html:
                # Look for problems solved
                match = re.search(r'Problems\s+solved[:\s]*(\d+)', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting SPOJ stats: {e}")
        return None
    
    def get_hackerrank(self):
        """Fetch HackerRank statistics."""
        try:
            url = "https://www.hackerrank.com/MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Look for challenges solved
                match = re.search(r'(\d+)\s+challenges?\s+solved', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting HackerRank stats: {e}")
        return None
    
    def get_uva(self):
        """Fetch UVa statistics."""
        try:
            # uhunt API
            url = "https://uhunt.onlinejudge.org/api/subs-user/1615470"
            data = self.fetch_url(url, use_api=True)
            if data:
                solved = set()
                for sub in data.get('subs', []):
                    if len(sub) > 2 and sub[2] == 90:  # 90 is AC verdict
                        solved.add(sub[1])  # problem ID
                return len(solved)
        except Exception as e:
            print(f"Error getting UVa stats: {e}")
        return None
    
    def get_hackerearth(self):
        """Fetch HackerEarth statistics."""
        try:
            url = "https://www.hackerearth.com/@MishkatIT"
            html = self.fetch_url(url)
            if html:
                # Look for problems solved
                match = re.search(r'(\d+)\s+problem', html, re.IGNORECASE)
                if match:
                    return int(match.group(1))
        except Exception as e:
            print(f"Error getting HackerEarth stats: {e}")
        return None
    
    def fetch_all_stats(self):
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
        
        print("Fetching statistics from all platforms...\n")
        results = {}
        
        for platform, fetch_func in platforms.items():
            print(f"Fetching {platform}...", end=' ')
            try:
                count = fetch_func()
                if count is not None:
                    results[platform] = count
                    print(f"✓ {count} problems")
                else:
                    print("✗ Failed")
                    results[platform] = None
            except Exception as e:
                print(f"✗ Error: {e}")
                results[platform] = None
        
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
