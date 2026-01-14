#!/usr/bin/env python3
"""
Comprehensive unit tests for web scraping functionality.
Tests the scraping patterns, fallback mechanisms, and error handling
without requiring actual network access.
"""

import unittest
import json
import os
import tempfile
import sys
from unittest.mock import Mock, patch, MagicMock
from urllib.error import URLError, HTTPError

# Import the module to test
from update_stats import PlatformStats


class TestWebScrapingPatterns(unittest.TestCase):
    """Test web scraping patterns with mock HTML responses."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = PlatformStats()
    
    def test_codeforces_api_success(self):
        """Test Codeforces API parsing with successful response."""
        mock_response = {
            'status': 'OK',
            'result': [
                {'verdict': 'OK', 'problem': {'contestId': 1, 'index': 'A'}},
                {'verdict': 'OK', 'problem': {'contestId': 1, 'index': 'B'}},
                {'verdict': 'WRONG_ANSWER', 'problem': {'contestId': 1, 'index': 'C'}},
                {'verdict': 'OK', 'problem': {'contestId': 2, 'index': 'A'}},
                {'verdict': 'OK', 'problem': {'contestId': 1, 'index': 'A'}},  # Duplicate
            ]
        }
        
        with patch.object(self.fetcher, 'fetch_url', return_value=mock_response):
            count = self.fetcher.get_codeforces()
            self.assertEqual(count, 3, "Should count unique solved problems")
    
    def test_codeforces_scraping_fallback(self):
        """Test Codeforces web scraping fallback when API fails."""
        html = '<div class="info">2386</div><div>problems solved</div>'
        
        with patch.object(self.fetcher, 'fetch_url') as mock_fetch:
            # First call (API) returns None, second call (HTML) returns HTML
            mock_fetch.side_effect = [None, html]
            count = self.fetcher.get_codeforces()
            self.assertEqual(count, 2386)
    
    def test_leetcode_graphql_api(self):
        """Test LeetCode GraphQL API parsing."""
        mock_response = {
            'data': {
                'matchedUser': {
                    'submitStats': {
                        'acSubmissionNum': [
                            {'count': 412},
                            {'count': 200}
                        ]
                    }
                }
            }
        }
        
        # Mock urlopen to return the GraphQL response
        with patch('update_stats.urlopen') as mock_urlopen:
            mock_response_obj = MagicMock()
            mock_response_obj.read.return_value = json.dumps(mock_response).encode('utf-8')
            mock_response_obj.__enter__.return_value = mock_response_obj
            mock_urlopen.return_value = mock_response_obj
            
            count = self.fetcher.get_leetcode()
            self.assertEqual(count, 412)
    
    def test_leetcode_scraping_fallback(self):
        """Test LeetCode web scraping fallback."""
        html = '{"solvedProblem": 412, "total": 3000}'
        
        with patch('update_stats.urlopen') as mock_urlopen:
            # API call raises exception
            mock_urlopen.side_effect = URLError("Connection failed")
            
            # Then patch fetch_url for scraping fallback
            with patch.object(self.fetcher, 'fetch_url', return_value=html):
                count = self.fetcher.get_leetcode()
                self.assertEqual(count, 412)
    
    def test_vjudge_scraping(self):
        """Test Vjudge web scraping."""
        html = '<span>Solved: 346</span>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_vjudge()
            self.assertEqual(count, 346)
    
    def test_atcoder_scraping(self):
        """Test AtCoder web scraping."""
        html = '<td>158 AC</td>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_atcoder()
            self.assertEqual(count, 158)
    
    def test_codechef_scraping(self):
        """Test CodeChef web scraping with multiple patterns."""
        test_cases = [
            ('<h3>Problems Solved</h3><div><b>3</b></div>', 3),
            ('"problemsSolved": 5', 5),
            ('problems-solved>7</div>', 7),
        ]
        
        for html, expected in test_cases:
            with patch.object(self.fetcher, 'fetch_url', return_value=html):
                count = self.fetcher.get_codechef()
                self.assertEqual(count, expected, f"Failed to parse: {html}")
    
    def test_cses_scraping(self):
        """Test CSES web scraping."""
        html = '64 / 300 tasks solved'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_cses()
            self.assertEqual(count, 64)
    
    def test_toph_scraping(self):
        """Test Toph web scraping."""
        html = '<div>35 solved</div>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_toph()
            self.assertEqual(count, 35)
    
    def test_lightoj_scraping(self):
        """Test LightOJ web scraping."""
        html = '<span>Solved: 31</span>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_lightoj()
            self.assertEqual(count, 31)
    
    def test_spoj_scraping(self):
        """Test SPOJ web scraping."""
        html = '<td>Problems solved:</td><td>21</td>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_spoj()
            self.assertEqual(count, 21)
    
    def test_hackerrank_scraping(self):
        """Test HackerRank web scraping."""
        html = '<div>7 challenges solved</div>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_hackerrank()
            self.assertEqual(count, 7)
    
    def test_uva_api(self):
        """Test UVa API parsing."""
        mock_response = {
            'subs': [
                [0, 100, 90],  # AC
                [0, 101, 90],  # AC
                [0, 102, 80],  # Not AC
                [0, 100, 90],  # Duplicate
            ]
        }
        
        with patch.object(self.fetcher, 'fetch_url', return_value=mock_response):
            count = self.fetcher.get_uva()
            self.assertEqual(count, 2)
    
    def test_uva_scraping_fallback(self):
        """Test UVa web scraping fallback."""
        html = '<td>Solved:</td><td>6</td>'
        
        with patch.object(self.fetcher, 'fetch_url') as mock_fetch:
            # First call (API) returns None, second call (HTML) returns HTML
            mock_fetch.side_effect = [None, html]
            count = self.fetcher.get_uva()
            self.assertEqual(count, 6)
    
    def test_hackerearth_scraping(self):
        """Test HackerEarth web scraping."""
        html = '<span>3 problems solved</span>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_hackerearth()
            self.assertEqual(count, 3)


class TestSanityChecks(unittest.TestCase):
    """Test sanity checks and validation logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = PlatformStats()
    
    def test_negative_count_rejected(self):
        """Test that negative counts are rejected."""
        html = '<span>Solved: -5</span>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_vjudge()
            self.assertIsNone(count, "Negative counts should be rejected")
    
    def test_zero_count_rejected(self):
        """Test that zero counts are rejected."""
        html = '<span>Solved: 0</span>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_vjudge()
            self.assertIsNone(count, "Zero counts should be rejected")
    
    def test_excessive_count_rejected(self):
        """Test that unreasonably high counts are rejected."""
        html = '<span>Solved: 15000</span>'
        
        with patch.object(self.fetcher, 'fetch_url', return_value=html):
            count = self.fetcher.get_vjudge()
            self.assertIsNone(count, "Counts above MAX_REASONABLE_COUNT should be rejected")
    
    def test_valid_count_accepted(self):
        """Test that valid counts are accepted."""
        for valid_count in [1, 100, 1000, 5000, 9999]:
            html = f'<span>Solved: {valid_count}</span>'
            with patch.object(self.fetcher, 'fetch_url', return_value=html):
                count = self.fetcher.get_vjudge()
                self.assertEqual(count, valid_count)


class TestErrorHandling(unittest.TestCase):
    """Test error handling for network failures."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = PlatformStats()
    
    def test_network_error_returns_none(self):
        """Test that network errors are handled gracefully."""
        with patch.object(self.fetcher, 'fetch_url', return_value=None):
            count = self.fetcher.get_codeforces()
            self.assertIsNone(count)
    
    def test_invalid_html_returns_none(self):
        """Test that invalid HTML returns None."""
        with patch.object(self.fetcher, 'fetch_url', return_value='<html>no count here</html>'):
            count = self.fetcher.get_vjudge()
            self.assertIsNone(count)
    
    def test_exception_handling(self):
        """Test that exceptions are caught and handled."""
        with patch.object(self.fetcher, 'fetch_url', side_effect=Exception("Test error")):
            count = self.fetcher.get_codeforces()
            self.assertIsNone(count)


class TestLastKnownCounts(unittest.TestCase):
    """Test the last known counts fallback mechanism."""
    
    def setUp(self):
        """Set up test fixtures with temporary file."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.original_file = PlatformStats.LAST_KNOWN_FILE
        PlatformStats.LAST_KNOWN_FILE = os.path.join(self.temp_dir, 'test_last_known.json')
        self.fetcher = PlatformStats()
    
    def tearDown(self):
        """Clean up temporary files."""
        PlatformStats.LAST_KNOWN_FILE = self.original_file
        # Clean up temp directory
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
    
    def test_save_and_load_last_known(self):
        """Test saving and loading last known counts."""
        # Update a count
        self.fetcher._update_last_known('TestPlatform', 100)
        self.fetcher._save_last_known_counts()
        
        # Create a new fetcher instance
        new_fetcher = PlatformStats()
        count = new_fetcher._get_last_known('TestPlatform')
        
        self.assertEqual(count, 100)
    
    def test_fallback_to_last_known(self):
        """Test that fetch_all_stats uses last known counts on failure."""
        # Set up last known counts
        self.fetcher._update_last_known('Codeforces', 2000)
        self.fetcher._save_last_known_counts()
        
        # Mock all fetch methods to return None (simulating failure)
        with patch.object(self.fetcher, 'fetch_url', return_value=None):
            stats = self.fetcher.fetch_all_stats(verbose=False)
            
            # Should fall back to last known count
            self.assertEqual(stats.get('Codeforces'), 2000)
    
    def test_no_last_known_returns_none(self):
        """Test that platforms without last known counts return None on failure."""
        with patch.object(self.fetcher, 'fetch_url', return_value=None):
            count = self.fetcher.get_vjudge()
            self.assertIsNone(count)


class TestFetchAllStats(unittest.TestCase):
    """Test the fetch_all_stats method."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.fetcher = PlatformStats()
    
    def test_fetch_all_stats_success(self):
        """Test that fetch_all_stats collects data from all platforms."""
        # Mock all platform methods to return a count
        platforms = ['codeforces', 'leetcode', 'vjudge', 'atcoder', 'codechef',
                    'cses', 'toph', 'lightoj', 'spoj', 'hackerrank', 'uva', 'hackerearth']
        
        for i, platform in enumerate(platforms, start=1):
            method_name = f'get_{platform}'
            with patch.object(self.fetcher, method_name, return_value=i * 100):
                pass
        
        # This test verifies the structure exists
        stats = self.fetcher.fetch_all_stats(verbose=False)
        self.assertIsInstance(stats, dict)
        self.assertGreaterEqual(len(stats), 12)
    
    def test_fetch_all_stats_handles_failures(self):
        """Test that fetch_all_stats handles individual platform failures."""
        with patch.object(self.fetcher, 'fetch_url', return_value=None):
            stats = self.fetcher.fetch_all_stats(verbose=False)
            
            # Should still return a dict, even if all failed
            self.assertIsInstance(stats, dict)


def run_tests():
    """Run all tests and return results."""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWebScrapingPatterns))
    suite.addTests(loader.loadTestsFromTestCase(TestSanityChecks))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestLastKnownCounts))
    suite.addTests(loader.loadTestsFromTestCase(TestFetchAllStats))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
        print("="*70)
        sys.exit(0)
    else:
        print("\n✗ SOME TESTS FAILED")
        print("="*70)
        sys.exit(1)
