# Changelog

## [Unreleased]

### Added
- **Persistent count tracking**: Added `last_known_counts.json` to store the last successfully fetched count and date for each platform
- **Smart fallback mechanism**: When a platform fails to fetch, the system automatically uses the last known count
- **Date annotations**: Platforms using stale data now show "(last updated: YYYY-MM-DD)" in the README
- **Improved CodeChef scraping**: Multiple regex patterns to handle different HTML structures on CodeChef's website
- **Manual update tracking**: Both `manual_update.py` and `quick_update.py` now save update dates

### Changed
- `update_stats.py`: Enhanced PlatformStats class with methods for loading/saving last known counts
- `update_readme.py`: Now shows date annotations for platforms using last known counts
- `manual_update.py`: Added date tracking for manual updates
- `quick_update.py`: Added date tracking for quick updates
- `.gitignore`: Added `last_known_counts.json` to keep it local only

### Fixed
- CodeChef problem count now correctly falls back to last known count when scraping fails
- Better error handling with specific exception types instead of bare `except:` clauses
- Removed redundant file existence checks before try-except blocks

### Technical Details

#### Persistent Count Storage
The system now maintains a `last_known_counts.json` file with the following structure:
```json
{
  "counts": {
    "Codeforces": 2470,
    "LeetCode": 393,
    ...
  },
  "dates": {
    "Codeforces": "2026-01-14",
    "LeetCode": "2026-01-14",
    ...
  }
}
```

#### Fallback Behavior
When automatic fetching fails:
1. System attempts to scrape/fetch the platform data
2. If fetch fails, system loads last known count from `last_known_counts.json`
3. README is updated with the count and a date annotation showing when it was last updated
4. Platforms with today's date don't show the annotation (considered "fresh")

#### Manual Updates
When using `manual_update.py` or `quick_update.py`:
1. User provides the current counts
2. System saves counts to `stats.json`
3. System saves counts and current date to `last_known_counts.json`
4. README is updated with fresh counts (no date annotations)

This ensures that manual updates are also tracked with proper dates.
