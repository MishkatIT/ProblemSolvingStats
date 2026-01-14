# Statistics Update Tools - README

This directory contains multiple tools and scripts to help update the problem-solving statistics in README.md.

## 🚨 Important: Environment Limitation

The automated statistics fetcher (`update_stats.py`) cannot access external websites from the GitHub Actions environment due to network restrictions. However, multiple alternative solutions are provided.

## 📝 Available Tools

### 1. quick_update.py ⭐ RECOMMENDED
**Fastest and most reliable method**

- Edit the `CURRENT_STATS` dictionary in the file
- Run `python3 quick_update.py`
- Automatically updates README.md
- No external dependencies needed

### 2. manual_update.py
**Interactive terminal interface**

- Run `python3 manual_update.py`
- Provides interactive prompts for each platform
- Guides you through the update process step-by-step

### 3. update_stats.py + update_readme.py
**Automatic fetching (when network available)**

- `update_stats.py` - Attempts to fetch from all platforms automatically
- `update_readme.py` - Updates README.md from stats.json
- Works only with unrestricted internet access

### 4. GitHub Actions Workflow
**Automated weekly updates**

- Location: `.github/workflows/update-stats.yml`
- Runs every Sunday at midnight UTC
- Can be triggered manually from Actions tab
- Attempts automatic fetching and updates

## 📚 Documentation Files

- **HOW_TO_UPDATE.md** - Quick start guide (read this first!)
- **UPDATE_GUIDE.md** - Comprehensive guide with all methods
- **COUNTS_TEMPLATE.md** - Simple template to fill in counts
- **This file** - Overview of all tools

## 🎯 Quick Start

### For immediate update:

1. Open `quick_update.py` in a text editor
2. Visit each platform URL (listed in the file)
3. Update the numbers in `CURRENT_STATS = {}`
4. Run: `python3 quick_update.py`
5. Review: `git diff README.md`
6. Commit: `git add README.md quick_update.py && git commit -m "Update statistics"`
7. Push: `git push`

### For interactive update:

```bash
python3 manual_update.py
```

## 🔄 Update Workflow

```
Visit platforms → Get counts → Update stats → Run script → Commit → Push
```

## ⚙️ How It Works

1. **Collection**: Stats are collected manually or automatically
2. **Storage**: Stats are saved to `stats.json` (ignored by git)
3. **Update**: `update_readme.py` updates README.md using regex patterns
4. **Preservation**: All formatting, emojis, and structure are preserved

## 🛠️ Technical Details

- All scripts are Python 3.12+ compatible
- No external dependencies required
- Updates:
  - Last updated date badge
  - Total solved badge
  - Individual platform counts
  - Progress percentages
  - Achievement breakdown chart
  - Key highlights section

## 📋 Platform List

1. Codeforces - https://codeforces.com/profile/MishkatIT
2. LeetCode - https://leetcode.com/MishkatIT/
3. Vjudge - https://vjudge.net/user/MishkatIT
4. AtCoder - https://atcoder.jp/users/MishkatIT
5. CodeChef - https://www.codechef.com/users/MishkatIT
6. CSES - https://cses.fi/user/165802/
7. Toph - https://toph.co/u/MishkatIT
8. LightOJ - https://lightoj.com/user/mishkatit
9. SPOJ - https://www.spoj.com/users/mishkatit/
10. HackerRank - https://www.hackerrank.com/MishkatIT
11. UVa - https://uhunt.onlinejudge.org/id/1615470
12. HackerEarth - https://www.hackerearth.com/@MishkatIT

## 🐛 Troubleshooting

- **Script fails**: Check Python version (3.12+ recommended)
- **README not updating**: Ensure stats.json is valid JSON
- **Formatting issues**: Don't manually edit README patterns
- **Network errors**: Use manual update methods

## 📞 Support

For detailed instructions, see:
- `HOW_TO_UPDATE.md` for step-by-step guide
- `UPDATE_GUIDE.md` for troubleshooting
- `COUNTS_TEMPLATE.md` for a simple fill-in template

---

**Note**: These tools were created to facilitate easy statistics updates since automated web scraping is not reliable due to environment and network restrictions.
