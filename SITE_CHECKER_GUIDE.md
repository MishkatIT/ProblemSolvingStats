# 🔍 Site Checker Guide

## Overview

The `check_sites.py` script is a diagnostic tool that helps you verify which competitive programming platforms are responding correctly and validate problem counts. This is essential for troubleshooting when automatic fetching fails.

## Features

✅ **Check All Platforms** - Quickly verify which sites are working  
✅ **Check Specific Sites** - Get detailed status for individual platforms  
✅ **Validate Counts** - Compare fetched counts against expected values  
✅ **JSON Output** - Machine-readable output for automation  
✅ **Clear Diagnostics** - Understand why a platform might be failing  

## Installation

No installation needed! The script uses the same dependencies as `update_stats.py`.

```bash
chmod +x check_sites.py
```

## Usage

### 1. Check All Platforms

This shows the status of all 12 platforms at once:

```bash
python3 check_sites.py --check-all
```

**Output Example:**
```
======================================================================
PLATFORM STATUS CHECK
======================================================================
Platform        Status     Count      Details
----------------------------------------------------------------------
Codeforces      ✓ OK       2386       Successfully fetched 2386 problems
LeetCode        ✓ OK       412        Successfully fetched 412 problems
Vjudge          ✗ FAIL     N/A        Returned None or invalid count
...
----------------------------------------------------------------------

Summary:
  Working platforms: 10/12
  Failing platforms: 2/12

  ✓ Working: Codeforces, LeetCode, AtCoder, ...
  ✗ Failing: Vjudge, CodeChef

  Total problems from working platforms: 3500
======================================================================
```

### 2. Check a Specific Site

Get detailed information about a single platform:

```bash
python3 check_sites.py --site codeforces
python3 check_sites.py --site leetcode
python3 check_sites.py --site atcoder
```

**Available platforms:**
- `codeforces` - Codeforces
- `leetcode` - LeetCode
- `vjudge` - Vjudge
- `atcoder` - AtCoder
- `codechef` - CodeChef
- `cses` - CSES
- `toph` - Toph
- `lightoj` - LightOJ
- `spoj` - SPOJ
- `hackerrank` - HackerRank
- `uva` - UVa Online Judge
- `hackerearth` - HackerEarth

**Output Example:**
```
======================================================================
CHECKING: Codeforces
======================================================================
Fetching statistics from Codeforces... ✓

Status: SUCCESS
Problems Solved: 2386

The platform is responding correctly.
======================================================================
```

**Failure Output:**
```
======================================================================
CHECKING: LeetCode
======================================================================
Fetching statistics from LeetCode... ✗

Status: FAILED
Problems Solved: N/A

The platform did not return a valid count.
This could be due to:
  - Network connectivity issues
  - Platform API/website changes
  - Rate limiting or access restrictions
======================================================================
```

### 3. Validate Counts

Compare fetched counts against expected values stored in `stats.json`:

```bash
python3 check_sites.py --validate
```

**Prerequisites:** You need a `stats.json` file with baseline counts.

**Output Example:**
```
======================================================================
VALIDATION REPORT
======================================================================
Platform        Expected   Actual     Status
----------------------------------------------------------------------
Codeforces      2386       2386       ✓ Match
LeetCode        412        415        ⚠ Diff (+3)
Vjudge          346        346        ✓ Match
AtCoder         158        N/A        ✗ Fetch Failed
...
----------------------------------------------------------------------

⚠ Some platforms have differences or failures.
  This may indicate:
  - New problems were solved
  - Platform API issues
  - Network connectivity problems
======================================================================
```

### 4. JSON Output

Get machine-readable output for automation:

```bash
python3 check_sites.py --check-all --json
python3 check_sites.py --site codeforces --json
```

**Output Example:**
```json
{
  "working": ["Codeforces", "LeetCode", "AtCoder"],
  "failing": ["Vjudge", "CodeChef"],
  "counts": {
    "Codeforces": 2386,
    "LeetCode": 412,
    "Vjudge": null,
    ...
  }
}
```

## Common Use Cases

### Troubleshooting Failed Updates

When `update_stats.py` fails, use `check_sites.py` to identify the problem:

```bash
# 1. Check which sites are working
python3 check_sites.py --check-all

# 2. Test specific failing platforms
python3 check_sites.py --site vjudge
python3 check_sites.py --site codechef

# 3. Use working platforms to update manually
python3 quick_update.py
```

### Verifying New Counts

After solving new problems, verify the counts were fetched correctly:

```bash
# 1. Run a full check
python3 check_sites.py --check-all

# 2. If counts look good, save them
python3 update_stats.py  # This saves to stats.json

# 3. Update README
python3 update_readme.py
```

### Regular Health Checks

Set up a cron job or GitHub Action to regularly check platform health:

```bash
# Check all platforms and output to JSON
python3 check_sites.py --check-all --json > platform_status.json
```

## Understanding Failure Reasons

### Network Connectivity Issues
```
Error: <urlopen error [Errno -5] No address associated with hostname>
```
**Solution:** Check your internet connection or firewall settings.

### API Changes
```
Status: FAILED
The platform did not return a valid count.
```
**Solution:** The platform may have changed their API or HTML structure. Update the parsing logic in `update_stats.py`.

### Rate Limiting
```
Error: HTTP Error 429: Too Many Requests
```
**Solution:** Wait a few minutes before trying again. Consider adding delays between requests.

### Authentication Required
```
Error: HTTP Error 403: Forbidden
```
**Solution:** The platform may require authentication. Check if login is needed.

## Integration with Other Scripts

### With update_stats.py

```bash
# Check what will work before running full update
python3 check_sites.py --check-all

# If some platforms fail, you can still proceed with working ones
python3 update_stats.py
```

### With quick_update.py

```bash
# Check current counts
python3 check_sites.py --check-all

# Manually update quick_update.py with the working counts
nano quick_update.py

# Run the update
python3 quick_update.py
```

### With validation workflow

```bash
# 1. Establish baseline
python3 check_sites.py --check-all --json > baseline.json

# 2. Later, validate against baseline
python3 check_sites.py --validate

# 3. Check differences
python3 check_sites.py --check-all
```

## Advanced Usage

### Scripting and Automation

```bash
#!/bin/bash
# Check if Codeforces is working before updating

RESULT=$(python3 check_sites.py --site codeforces --json)
COUNT=$(echo $RESULT | jq -r '.codeforces')

if [ "$COUNT" != "null" ]; then
    echo "✓ Codeforces working: $COUNT problems"
    # Proceed with update
else
    echo "✗ Codeforces failed, skipping update"
    exit 1
fi
```

### Monitoring Multiple Platforms

```bash
# Check specific platforms you care about most
for site in codeforces leetcode atcoder; do
    echo "Checking $site..."
    python3 check_sites.py --site $site
    echo ""
done
```

## Tips and Best Practices

1. **Run --check-all first** - Always start with a full check to see the overall status
2. **Use --site for debugging** - When a specific platform fails, use --site for detailed diagnostics
3. **Keep stats.json updated** - Regularly update your baseline for accurate validation
4. **Check before commits** - Run validation before committing README updates
5. **Document failures** - If a platform consistently fails, document it for future reference

## Troubleshooting

### Script Won't Run

```bash
# Make sure it's executable
chmod +x check_sites.py

# Check Python version (needs 3.6+)
python3 --version

# Run with full path if needed
python3 /full/path/to/check_sites.py --check-all
```

### All Platforms Failing

This usually means:
- No internet connection
- Firewall blocking external requests
- Running in restricted environment (like GitHub Actions without proper permissions)

**Solution:** Try running locally or check network settings.

### Incorrect Counts

If counts seem wrong:
1. Visit the platform directly to verify
2. Check if API/HTML structure changed
3. Update parsing logic in `update_stats.py`
4. Test with `python3 check_sites.py --site <platform>`

## Related Documentation

- **update_stats.py** - Main script for fetching statistics
- **quick_update.py** - Fast manual update method
- **manual_update.py** - Interactive update tool
- **update_readme.py** - Update README with new counts

## Support

If you encounter issues:
1. Run `python3 check_sites.py --check-all` to diagnose
2. Check the error messages for specific platforms
3. Try fetching from working platforms only
4. Use manual update methods as fallback

---

**Happy checking! 🚀**
