# Statistics Update Guide

This directory contains scripts to help you update the problem-solving statistics in the README.md file.

## Methods to Update Statistics

### Method 1: Automatic Update (Recommended for local machines)

If you have internet access, you can run the automatic update script:

```bash
python3 update_stats.py
```

This will:
1. Fetch current statistics from all 12 platforms
2. Display a summary
3. Save the results to `stats.json`

Then update the README:

```bash
python3 update_readme.py
```

### Method 2: Manual Update

If automatic fetching doesn't work (e.g., due to network restrictions), use the manual input script:

```bash
python3 manual_update.py
```

This will:
1. Prompt you to visit each platform
2. Ask you to enter the current solve count
3. Save the results to `stats.json`
4. Optionally update README.md automatically

### Method 3: GitHub Actions (Automated Weekly Updates)

The repository now includes a GitHub Actions workflow that can automatically update statistics weekly.

To enable it:
1. The workflow file is already created at `.github/workflows/update-stats.yml`
2. Go to your repository on GitHub
3. Click on "Actions" tab
4. Enable workflows if not already enabled
5. The workflow will run every Sunday at midnight UTC
6. You can also trigger it manually from the Actions tab

## How to Manually Visit Each Platform

Here are the direct links to check current solve counts:

1. **Codeforces**: https://codeforces.com/profile/MishkatIT
   - Look for "problem" count on the profile page

2. **LeetCode**: https://leetcode.com/MishkatIT/
   - Check the "Solved" count on the profile

3. **Vjudge**: https://vjudge.net/user/MishkatIT
   - Look for "Solved" problems count

4. **AtCoder**: https://atcoder.jp/users/MishkatIT
   - Check the number of "AC" (Accepted) submissions

5. **CodeChef**: https://www.codechef.com/users/MishkatIT
   - Look for "Problems Solved" on the profile

6. **CSES**: https://cses.fi/user/165802/
   - Check tasks solved count

7. **Toph**: https://toph.co/u/MishkatIT
   - Look for "solved" count

8. **LightOJ**: https://lightoj.com/user/mishkatit
   - Check "Solved" problems

9. **SPOJ**: https://www.spoj.com/users/mishkatit/
   - Look for "Problems solved"

10. **HackerRank**: https://www.hackerrank.com/MishkatIT
    - Check "challenges solved"

11. **UVa**: https://uhunt.onlinejudge.org/id/1615470
    - Look for total accepted submissions

12. **HackerEarth**: https://www.hackerearth.com/@MishkatIT
    - Check problems solved count

## Files Description

- `update_stats.py` - Automatic statistics fetcher (requires internet access)
- `manual_update.py` - Interactive script for manual input
- `update_readme.py` - Updates README.md with statistics from stats.json
- `.github/workflows/update-stats.yml` - GitHub Actions workflow for automation

## Troubleshooting

### Automatic fetching fails
- Check your internet connection
- Some platforms may have rate limiting or anti-bot measures
- Use manual update method as a fallback

### README update doesn't work
- Ensure stats.json exists and contains valid data
- Check that README.md hasn't been modified in a way that breaks the patterns
- Manually verify the changes if needed

## Quick Start

For the fastest update, if you're on a machine with internet access:

```bash
# One-line update
python3 update_stats.py && python3 update_readme.py && git add README.md && git commit -m "Update statistics" && git push
```

Or use manual input:

```bash
python3 manual_update.py
```
