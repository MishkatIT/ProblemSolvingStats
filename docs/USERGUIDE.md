# User Guide: Problem Solving Statistics Tracker

## Overview

The Problem Solving Statistics Tracker is a comprehensive tool that automatically tracks and displays your competitive programming progress across 15 platforms. It fetches statistics from various competitive programming websites and generates a beautiful, automatically updated GitHub README showcasing your achievements.

## Features

### 🚀 Automated Tracking
- **Daily Updates**: Automatically fetches latest statistics every day
- **Multi-Platform Support**: Tracks progress on 15 competitive programming platforms
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

| Platform | Method | Status |
|----------|--------|--------|
| Codeforces | API + Web Scraping | ✅ Active |
| AtCoder | API + Web Scraping | ✅ Active |
| CodeChef | Web Scraping | ✅ Active |
| LightOJ | Web Scraping | ✅ Active |
| Toph | Web Scraping | ✅ Active |
| VJudge | Web Scraping | ✅ Active |
| UVa | API + Web Scraping | ✅ Active |
| SPOJ | Web Scraping | ✅ Active |
| HackerRank | Web Scraping | ✅ Active |
| HackerEarth | Web Scraping | ✅ Active |
| LeetCode | GraphQL API + Web Scraping | ✅ Active |
| CSES | Web Scraping | ✅ Active |
| Kattis | Web Scraping | ✅ Active |
| CSAcademy | Web Scraping | ✅ Active |
| Toki | Web Scraping | ✅ Active |

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

### 3. Configure Your Usernames

#### Option A: Using URLs (Recommended)

Add your profile URLs to `config/handles.json`:

```json
[
  "https://codeforces.com/profile/YourUsername",
  "https://atcoder.jp/users/YourUsername",
  "https://www.codechef.com/users/YourUsername",
  "https://vjudge.net/user/YourUsername",
  "https://toph.co/u/YourUsername"
]
```

Then run the configuration script:

```bash
python scripts/configure_handles.py
```

#### Option B: Manual Configuration

Edit `src/config.json` directly:

```json
{
  "USER_CONFIG": {
    "Codeforces": "YourUsername",
    "AtCoder": "YourUsername",
    "CodeChef": "YourUsername"
  }
}
```

### 4. Test the Setup

```bash
# Run automatic update
python scripts/auto_update.py

# Or run manual update for specific platforms
python scripts/manual_update.py
```

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
| `update_readme.py` | Generate/update README with current stats | After fetching new data |
| `configure_handles.py` | Setup and manage platform usernames | Initial setup, adding platforms |

### Automatic Updates (`auto_update.py`)

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

### Configuration Management (`configure_handles.py`)

Manages platform usernames and settings.

**Features:**
- Parses URLs to extract usernames
- Validates platform formats
- Updates configuration files
- Handles multiple URL formats
- Provides configuration summary

**Usage:**
```bash
python scripts/configure_handles.py
```

## Configuration Files

### `src/config.json`

Central configuration file containing:

```json
{
  "USER_CONFIG": {
    "PlatformName": "YourUsername"
  },
  "PLATFORM_URL_TEMPLATES": {
    "PlatformName": "https://example.com/user/{username}"
  },
  "PLATFORM_LOGOS": {
    "PlatformName": ["https://favicon.url", true]
  },
  "PLATFORM_COLORS": ["color1", "color2", ...],
  "ALL_PLATFORMS": ["Platform1", "Platform2", ...]
}
```

### `handles.json`

Simple list of profile URLs for easy configuration:

```json
[
  "https://codeforces.com/profile/YourUsername",
  "https://atcoder.jp/users/YourUsername",
  "https://www.codechef.com/users/YourUsername"
]
```

### `data/stats.json`

Current statistics data:

```json
{
  "Codeforces": 3465,
  "AtCoder": 317,
  "CodeChef": 371
}
```

### `last_known_counts.json`

Historical data with timestamps and modes:

```json
{
  "counts": {
    "Codeforces": 3465,
    "AtCoder": 317
  },
  "dates": {
    "Codeforces": "2026-01-23",
    "AtCoder": "2026-01-23"
  },
  "modes": {
    "Codeforces": "automatic",
    "AtCoder": "automatic"
  }
}
```

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

1. Runs daily at 11:35 PM BDT
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
# Re-run configuration
python scripts/configure_handles.py

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
    - cron: '35 17 * * *'  # 11:35 PM BDT
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

## Support

- **Issues**: [GitHub Issues](https://github.com/MishkatIT/ProblemSolvingStats/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MishkatIT/ProblemSolvingStats/discussions)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.</content>
<parameter name="filePath">d:\ProblemSolvingStats\USERGUIDE.md