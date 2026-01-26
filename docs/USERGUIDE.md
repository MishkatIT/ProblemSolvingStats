# User Guide: Problem Solving Statistics Tracker

## Overview

The Problem Solving Statistics Tracker is a comprehensive tool that automatically tracks and displays your competitive programming progress across 12+ platforms. It fetches statistics from various competitive programming websites and generates a beautiful, automatically updated GitHub README showcasing your achievements.

## Features

### 🚀 Automated Tracking
- **Daily Updates**: Automatically fetches latest statistics every day
- **Multi-Platform Support**: Tracks progress on 13 competitive programming platforms
- **Smart Scheduling**: Adapts update frequency based on your solving activity
- **GitHub Actions Integration**: Runs automatically in your GitHub repository

### 📊 Rich Statistics Display
- **Interactive Tables**: Sortable statistics table with progress bars
- **Visual Progress Indicators**: Color-coded progress badges for each platform
- **Platform Logos**: Official favicons for easy platform identification
- **Real-time Updates**: Shows last update times and modes (Automatic/Manual)

### 🛠️ Flexible Update Methods
- **Automatic Mode**: Uses APIs and web scraping for reliable data fetching
- **Manual Mode**: Interactive script for platforms that need manual input
- **Fallback System**: Uses last known good values when automatic fetching fails
- **Configuration Management**: Easy setup and reconfiguration of usernames

## Supported Platforms

| Platform | Method | Status | Auto Update |
|----------|--------|--------|-------------|
| Codeforces | API + Web Scraping | ✅ Active | Yes |
| AtCoder | API + Web Scraping | ✅ Active | Yes |
| CodeChef | Web Scraping | ✅ Active | Yes |
| LightOJ | Web Scraping | ✅ Active | Yes |
| Toph | Web Scraping | ✅ Active | Yes |
| VJudge | Web Scraping | ✅ Active | Yes |
| UVa | API + Web Scraping | ✅ Active | Yes |
| SPOJ | Web Scraping | ✅ Active | No |
| HackerRank | Web Scraping | ✅ Active | No |
| HackerEarth | Web Scraping | ✅ Active | Yes |
| LeetCode | GraphQL API + Web Scraping | ✅ Active | Yes |
| CSES | Web Scraping | ✅ Active | No |
| Kattis | Web Scraping | ✅ Active | Yes |
| CSAcademy | Web Scraping | ✅ Active | Optional |
| Toki | Web Scraping | ✅ Active | Optional |

## Quick Start

### 1. Fork the Repository

```bash
# Visit https://github.com/MishkatIT/ProblemSolvingStats
# Click "Fork" in the top-right corner
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ProblemSolvingStats.git
cd ProblemSolvingStats
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. run bat

.\spark.bat


### 5. Enable GitHub Actions

1. Go to your repository's **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. Your stats will update automatically every day!

## Detailed Usage

### Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `auto_update.py` | Fetch stats from all platforms automatically | Daily updates, GitHub Actions |
| `manual_update.py` | Interactive manual statistics input | When automatic fetching fails |
| `change_display_name.py` | Change profile display names | Personalizing README appearance |
| `update_readme.py` | Generate/update README with current stats | After fetching new data |
| `manage_handle.py` | Add, edit, or delete platform handles | Setting up or changing usernames |
| `sync_profiles.py` | Sync handles from URLs to configuration | After updating handles.json |
| `check_and_adjust_schedule.py` | Adjust GitHub Actions schedule based on activity | Automated workflow management |
| `known_platforms.py` | Display known platform URL templates | Reference for supported platforms |

### Windows Batch File (`spark.bat`)

For Windows users, we've created a convenient batch file that simplifies running all scripts.

**Features:**
- Interactive menu system
- Automatic virtual environment management
- Dependency checking and installation
- One-click access to all functionality
- Beginner-friendly interface

**Usage:**
```cmd
# Double-click spark.bat in Windows Explorer, or:
spark.bat
# or
.\spark.bat
```

**What it does automatically:**
- Creates Python virtual environment if needed
- Activates the virtual environment
- Installs/updates all required dependencies
- Provides a numbered menu to choose any script
- Handles environment cleanup on exit

**Menu Options:**
1. **Auto Update** - Run `auto_update.py`
2. **Manual Update** - Run `manual_update.py`
3. **Add or Delete Handles** - Run `manage_handle.py`
4. **Change Display Name** - Run `change_display_name.py`
5. **Update README** - Run `update_readme.py`
6. **Install Dependencies** - Update Python packages
7. **Exit** - Close the batch file

> 💡 **Recommended for:** Windows users, beginners, or anyone who wants a simplified experience without command-line knowledge.

This is the main script that fetches statistics from all supported platforms.

**Features:**
- Uses APIs when available for accuracy
- Falls back to web scraping when APIs fail
- Handles rate limiting and timeouts gracefully
- Updates `data/stats.json` and `data/last_known_counts.json`
- Automatically calls `update_readme.py` to refresh the display

**Usage:**
```bash
python scripts/auto_update.py
```

**Output includes:**
- Progress indicators for each platform
- Success/failure status
- Fallback notifications
- Summary statistics

### Manual Updates (`manual_update.py`)

Use this when automatic fetching fails for specific platforms or when you want to input statistics manually.

**Features:**
- Interactive prompts for each platform
- Validates input ranges
- Updates last known counts with manual mode
- Useful for platforms without reliable APIs

**Usage:**
```bash
python scripts/manual_update.py
```

**When to use:**
- Platform websites are down
- API rate limits exceeded
- New platforms not yet supported
- Verification of automatic results

### README Updates (`update_readme.py`)

Generates the beautiful statistics display in your README.md.

**Features:**
- Creates sortable statistics table
- Generates progress badges
- Updates timestamps and metadata
- Handles platform logos and colors
- Creates summary sections

**Usage:**
```bash
# Update with current stats
python scripts/update_readme.py

# Update with specific source (for automation)
python scripts/update_readme.py --source automatic
```

### Handle Management (`manage_handle.py`)

Interactive script for managing your platform handles and usernames.

**Features:**
- Add new platform handles
- Edit existing usernames
- Delete unused handles
- Validate handle formats
- Update configuration automatically

**Usage:**
```bash
python scripts/manage_handle.py
```

**When to use:**
- Setting up the project for the first time
- Adding support for new platforms
- Changing usernames on existing platforms
- Removing platforms you no longer use

### Profile Synchronization (`sync_profiles.py`)

Synchronizes handle configurations from `config/handles.json` to the main configuration files.

**Features:**
- Parses URLs to extract usernames
- Updates `src/config.json` with new handles
- Maintains display name consistency
- Validates platform support

**Usage:**
```bash
python scripts/sync_profiles.py
```

**When to use:**
- After manually editing `config/handles.json`
- When adding new handles via URLs
- Ensuring configuration consistency

### Schedule Adjustment (`check_and_adjust_schedule.py`)

Automatically adjusts GitHub Actions workflow schedule based on solving activity.

**Features:**
- Monitors solving activity over time
- Switches from daily to monthly updates when inactive
- Resumes daily updates when activity returns
- Updates workflow files automatically

**Usage:**
```bash
python scripts/check_and_adjust_schedule.py
```

**When to use:**
- As part of automated workflows
- To optimize GitHub Actions usage
- When activity patterns change

### Known Platforms Reference (`known_platforms.py`)

Displays information about supported platforms and URL templates.

**Features:**
- Lists all known platform templates
- Shows URL generation patterns
- Helps with handle configuration
- Reference for platform support

**Usage:**
```bash
python scripts/known_platforms.py
```

**When to use:**
- Checking platform availability
- Understanding URL formats
- Adding new platform support

## Configuration Files

### `src/config.json`

Central configuration file containing:

```json
{
  "USER_CONFIG": {
    "Codeforces": "YourUsername",
    "LeetCode": "YourUsername",
    "CodeChef": "YourUsername"
  },
  "PROFILE_DISPLAY_NAMES": {
    "Codeforces": "🏆 Competitive Programmer",
    "LeetCode": "💻 Algorithm Expert",
    "CodeChef": "👨‍🍳 CodeChef Master"
  },
  "PLATFORM_URL_TEMPLATES": {
    "Codeforces": "https://codeforces.com/profile/{username}",
    "LeetCode": "https://leetcode.com/u/{username}/",
    "CodeChef": "https://www.codechef.com/users/{username}"
  },
  "PLATFORM_LOGOS": {
    "Codeforces": ["https://www.google.com/s2/favicons?domain=codeforces.com&sz=16", true],
    "LeetCode": ["https://www.google.com/s2/favicons?domain=leetcode.com&sz=16", true],
    "CodeChef": ["https://www.google.com/s2/favicons?domain=www.codechef.com&sz=16", true]
  },
  "PLATFORM_COLORS": ["AA0000", "FF3333", "FF7777", "FFBB55", "FFCC88", "FF88FF", "D499FF", "AAAAFF", "90C3DD", "77DDBB", "77EE99", "77FF77", "CCCCCC"],
  "ALL_PLATFORMS": ["AtCoder", "CSES", "CodeChef", "Codeforces", "HackerEarth", "HackerRank", "Kattis", "LeetCode", "LightOJ", "SPOJ", "Toph", "UVa", "VJudge"],
  "LAST_KNOWN_FILE": "data/last_known_counts.json",
  "STATS_FILE": "data/stats.json",
  "README_FILE": "docs/README.md",
  "MAX_REASONABLE_COUNT": 20000,
  "BDT_TIMEZONE_hours": 6,
  "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

### `handles.json`

Canonical mapping of profile URLs for easy configuration (stored in `config/handles.json`):

```json
{
  "urls": {
    "Codeforces": "https://codeforces.com/profile/YourUsername",
    "LeetCode": "https://leetcode.com/u/YourUsername/",
    "CodeChef": "https://www.codechef.com/users/YourUsername",
    "AtCoder": "https://atcoder.jp/users/YourUsername",
    "CSES": "https://cses.fi/user/YourUsername/",
    "VJudge": "https://vjudge.net/user/YourUsername",
    "Toph": "https://toph.co/u/YourUsername",
    "LightOJ": "https://lightoj.com/user/YourUsername",
    "SPOJ": "https://www.spoj.com/users/YourUsername",
    "HackerRank": "https://www.hackerrank.com/profile/YourUsername",
    "HackerEarth": "https://www.hackerearth.com/@YourUsername/",
    "Kattis": "https://open.kattis.com/users/YourUsername",
    "UVa": "https://uhunt.onlinejudge.org/id/YourUsername"
  }
}
```

### `data/stats.json`

Current statistics data structure:

```json
{
  "Codeforces": "solved_count",
  "LeetCode": "solved_count",
  "AtCoder": "solved_count",
  "...": "..."
}
```

*Note: Contains solved problem counts for all 13 supported platforms.*

### `last_known_counts.json`

Historical data structure with timestamps and modes:

```json
{
  "counts": {
    "Codeforces": "solved_count",
    "LeetCode": "solved_count",
    "AtCoder": "solved_count",
    "...": "..."
  },
  "dates": {
    "Codeforces": "YYYY-MM-DD",
    "LeetCode": "YYYY-MM-DD",
    "AtCoder": "YYYY-MM-DD",
    "...": "..."
  },
  "modes": {
    "Codeforces": "automatic_or_manual",
    "LeetCode": "automatic_or_manual",
    "AtCoder": "automatic_or_manual",
    "...": "..."
  }
}
```

*Note: Contains historical data for all 13 supported platforms.*

## Customization Options

### Profile Display Names

You can customize how your profile names appear in the README table by editing the `PROFILE_DISPLAY_NAMES` section in `src/config.json`:

```json
{
  "PROFILE_DISPLAY_NAMES": {
    "Codeforces": "🏆 Competitive Programmer",
    "LeetCode": "💻 Algorithm Expert",
    "AtCoder": "🎌 Speed Coder",
    "CodeChef": "👨‍🍳 CodeChef Master"
  }
}
```

**What it changes:**
- The **"👤 Profile"** column in your README will show custom names instead of usernames
- URLs remain the same (pointing to your actual profiles)
- Display names are independent of your actual usernames

**How to apply:**
1. Edit `src/config.json` and modify `PROFILE_DISPLAY_NAMES`
2. Run `python scripts/update_readme.py` to update the README

**Example Result:**
```markdown
<td><a href="https://codeforces.com/profile/YourUsername">🏆 Competitive Programmer</a></td>
```

## GitHub Actions Setup

### Workflow Configuration

The repository includes a GitHub Actions workflow (`.github/workflows/update-stats.yml`) that:

1. Runs daily at 10:35 PM BDT (16:35 UTC)
2. Executes `auto_update.py`
3. Commits changes back to the repository
4. Adapts schedule based on solving activity

### Schedule Adjustment

The system automatically adjusts update frequency:

- **Active Mode**: Daily updates when you're actively solving
- **Inactive Mode**: Monthly updates after 90 days without solves
- **Recovery**: Immediately switches back to daily when activity resumes

## Troubleshooting

### Common Issues

#### 1. Platform Fetching Fails

**Symptoms:** Script shows "Failed" for specific platforms

**Solutions:**
```bash
# Try manual update for failed platforms
python scripts/manual_update.py

# Check if platform website is accessible
curl -I https://platform-website.com
```

#### 2. GitHub Actions Not Running

**Symptoms:** No automatic updates in repository

**Solutions:**
1. Go to repository **Actions** tab
2. Enable workflows if disabled
3. Check workflow run logs for errors
4. Verify repository secrets if needed

#### 3. README Not Updating

**Symptoms:** Statistics don't appear in README

**Solutions:**
```bash
# Run manual README update
python scripts/update_readme.py

# Check if data/stats.json exists and has data
cat data/stats.json
```

#### 4. Configuration Errors

**Symptoms:** "Platform not found" or username errors

**Solutions:**
```bash
# For manual display name setup:
# 1. Edit src/config.json
# 2. Modify the PROFILE_DISPLAY_NAMES section
# 3. Add entries like: "PlatformName": "Your Custom Display Name"
# 4. Run: python scripts/update_readme.py

# Verify config.json is valid JSON
python -m json.tool src/config.json
```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Set environment variable for debug output
export DEBUG_STATS=1
python scripts/auto_update.py
```

### Platform-Specific Issues

#### Codeforces
- Ensure username is correct (case-sensitive)
- Check if profile is public

#### AtCoder
- Username is case-sensitive
- API may have rate limits

#### Web Scraping Platforms
- May fail if website layout changes
- Use manual update as fallback

## Advanced Usage

### Custom Platform Support

To add a new platform:

1. Add configuration to `src/config.json`
2. Implement fetch method in `PlatformStats` class
3. Update `ALL_PLATFORMS` list
4. Test with both automatic and manual modes

### API Integration

For platforms with APIs:

```python
def get_platform_name(self):
    try:
        # Try API first
        url = f"https://api.platform.com/user/{self.user_config['PlatformName']}"
        data = self.fetch_url(url, use_api=True)
        return data['solved_count']
    except:
        # Fallback to web scraping
        return self.scrape_platform_name()
```

### Custom Scheduling

Modify `.github/workflows/update-stats.yml`:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # 00:00 UTC (6:00 AM BDT)
  workflow_dispatch:        # Manual trigger
```

## Contributing

### Adding New Platforms

1. Fork the repository
2. Add platform configuration
3. Implement fetch logic
4. Test thoroughly
5. Submit pull request

### Improving Existing Platforms

- Update regex patterns for web scraping
- Add API support where possible
- Improve error handling
- Enhance documentation

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to functions
- Include type hints where helpful
- Test changes before submitting

## FAQ

### Q: How often does it update?
A: Daily by default, but adapts based on your solving activity.

### Q: What if a platform's website changes?
A: The system uses multiple fallback methods and manual override options.

### Q: Can I add my own platforms?
A: Yes, the code is designed to be extensible.

### Q: Does it work with private profiles?
A: No, profiles must be public for web scraping to work.

### Q: How much does it cost?
A: Completely free - uses GitHub Actions free tier.

### Q: Can I customize the appearance?
A: Yes, modify the templates in `update_readme.py`.

### Q: Is there an easy way to run this on Windows?
A: Yes! Use `spark.bat` - it provides an interactive menu and handles everything automatically.

### Q: What platforms are currently supported?
A: 12+ platforms: Codeforces, AtCoder, CodeChef, LeetCode, LightOJ, Toph, VJudge, UVa, SPOJ, HackerRank, HackerEarth, CSES, and Kattis.

## Support

- **Issues**: [GitHub Issues](https://github.com/MishkatIT/ProblemSolvingStats/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MishkatIT/ProblemSolvingStats/discussions)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

ThThis project is licensed under the MIT License - see the [LICENSE](/LICENSE)
