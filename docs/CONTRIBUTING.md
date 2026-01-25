# Contributing to ProblemSolvingStats

First off, thank you for considering contributing to ProblemSolvingStats! It's people like you that make this project better for everyone.

## 🎯 Ways to Contribute

There are many ways you can contribute to this project:

- 🐛 Report bugs
- 💡 Suggest new features or improvements
- 📝 Improve documentation
- 🔧 Fix bugs or implement features
- 🌐 Add support for new platforms
- ✨ Improve code quality

## 🚀 Getting Started

### 1. Fork the Repository

1. Visit [MishkatIT/ProblemSolvingStats](https://github.com/MishkatIT/ProblemSolvingStats)
2. Click the **Fork** button in the top-right corner
3. GitHub will create a copy in your account

### 2. Set Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ProblemSolvingStats.git
cd ProblemSolvingStats

# Add upstream remote
git remote add upstream https://github.com/MishkatIT/ProblemSolvingStats.git

# Install dependencies
pip install -r requirements.txt

# Verify everything works
python scripts/auto_update.py
```

### 3. Create a Branch

Always create a new branch for your work:

```bash
# For new features
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b fix/your-bug-fix

# For documentation
git checkout -b docs/your-documentation-update
```

## 📝 Coding Guidelines

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose
- Add comments for complex logic

### Example Function Style

```python
def calculate_percentage(solved, total):
    """Calculate percentage for progress bar.
    
    Args:
        solved: Number of problems solved
        total: Total number of problems
        
    Returns:
        Percentage as float rounded to 1 decimal place
    """
    if total == 0:
        return 0.0
    return round((solved / total) * 100, 1)
```

### Module Organization

The project uses a well-organized folder structure:

```
ProblemSolvingStats/
├── scripts/                    # Executable scripts
│   ├── auto_update.py         # Main statistics fetcher
│   ├── manual_update.py       # Manual input script
│   ├── change_display_name.py # Display name customization
│   ├── update_readme.py       # README generator
│   └── check_and_adjust_schedule.py # Schedule management
├── config/                     # Configuration files
│   └── handles.json           # User profile URLs
├── data/                       # Data files
│   ├── stats.json             # Current statistics
│   └── last_known_counts.json # Historical data
├── docs/                       # Documentation
│   ├── README.md              # Main documentation
│   ├── USERGUIDE.md           # Detailed user guide
│   ├── CHANGELOG.md           # Version history
│   └── CONTRIBUTING.md        # Contribution guidelines
├── src/                        # Shared modules
│   ├── __init__.py            # Package initialization
│   ├── config.json            # Configuration constants
│   ├── data_manager.py        # JSON file operations
│   └── utils.py               # Shared utility functions
├── .github/                    # GitHub configuration
│   └── workflows/
│       └── update-stats.yml   # GitHub Actions workflow
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── .venv/                      # Virtual environment (optional)
```

When adding new code:
- **Scripts** → Add to `scripts/` folder
- **Configurations** → Add to `src/config.json` or `config/` folder
- **Data files** → Add to `data/` folder
- **Documentation** → Add to `docs/` folder
- **Utilities** → Add to `src/utils.py`
- **Data operations** → Add to `src/data_manager.py`

## 🔄 Making Changes

### Before You Start

1. **Sync your fork** with upstream:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

### While Working

1. **Write clean, documented code**
2. **Test your changes thoroughly**
3. **Keep commits focused and atomic**
4. **Write clear commit messages**

### Commit Message Format

```
Type: Brief description (50 chars or less)

More detailed explanation if needed (wrap at 72 chars).
- Bullet points for multiple changes
- Keep it clear and concise

Fixes #123 (if applicable)
```

**Types:**
- `Add:` - New feature or functionality
- `Fix:` - Bug fix
- `Docs:` - Documentation changes
- `Refactor:` - Code refactoring
- `Test:` - Adding or updating tests
- `Style:` - Code style changes (formatting, etc.)
- `Chore:` - Maintenance tasks

### Examples

```bash
git commit -m "Add: Support for CodeForces API v2"
git commit -m "Fix: Handle network timeout in LeetCode scraper"
git commit -m "Docs: Update installation instructions"
git commit -m "Refactor: Extract common scraping logic to utils"
```

## 🧪 Testing

Before submitting your pull request:

1. **Test all scripts work**:
   ```bash
   python scripts/auto_update.py
   python scripts/update_readme.py
   python scripts/manual_update.py
   ```

2. **Check imports**:
   ```bash
   python -c "import sys; sys.path.insert(0, 'src'); import scripts.auto_update; print('OK')"
   python -c "import sys; sys.path.insert(0, 'src'); import scripts.update_readme; print('OK')"
   python -c "import sys; sys.path.insert(0, 'src'); import scripts.manual_update; print('OK')"
   ```

3. **Verify no syntax errors**:
   ```bash
   python -m py_compile scripts/auto_update.py
   python -m py_compile scripts/update_readme.py
   python -m py_compile scripts/manual_update.py
   ```

## 📤 Submitting Your Changes

### 1. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 2. Create a Pull Request

1. Go to your fork on GitHub
2. Click **Compare & pull request**
3. Fill out the PR template:
   - Clear title describing the change
   - Detailed description of what changed and why
   - Reference any related issues
   - List any breaking changes

### 3. PR Review Process

- A maintainer will review your PR
- Address any feedback or requested changes
- Once approved, your PR will be merged!

## 🐛 Reporting Bugs

### Before Submitting a Bug Report

1. **Check existing issues** - Someone may have already reported it
2. **Try the latest version** - The bug might be fixed
3. **Gather information** - Error messages, environment details, steps to reproduce

### Bug Report Template

When creating an issue, include:

```markdown
**Description:**
A clear description of the bug

**Steps to Reproduce:**
1. Run command X
2. See error Y

**Expected Behavior:**
What you expected to happen

**Actual Behavior:**
What actually happened

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10]
- Dependencies: [output of `pip freeze`]

**Error Messages:**
```
Paste any error messages or stack traces here
```

**Additional Context:**
Any other relevant information
```

## 💡 Suggesting Features

We love new ideas! When suggesting a feature:

1. **Check existing issues** - It might already be planned
2. **Describe the use case** - Why is this feature needed?
3. **Provide examples** - Show how it would work
4. **Consider alternatives** - Are there other ways to achieve this?

### Feature Request Template

```markdown
**Feature Description:**
Clear description of the proposed feature

**Problem It Solves:**
What problem does this address?

**Proposed Solution:**
How would this feature work?

**Alternatives Considered:**
Other ways this could be implemented

**Additional Context:**
Screenshots, mockups, or examples
```

## 🌐 Adding New Platforms

Want to add a new competitive programming platform? Great! Here's how:

### 1. Update Configuration

Edit `src/config.json`:

```json
{
  "USER_CONFIG": {
    "NewPlatform": "YourUsername"
  },
  "PLATFORM_URL_TEMPLATES": {
    "NewPlatform": "https://newplatform.com/user/{username}"
  },
  "ALL_PLATFORMS": [
    "NewPlatform"
  ]
}
```

# Add to PLATFORM_URL_TEMPLATES
PLATFORM_URL_TEMPLATES = {
    # ... existing platforms
    'NewPlatform': 'https://newplatform.com/profile/{username}',
}

# Add to PLATFORM_LOGOS
PLATFORM_LOGOS = {
    # ... existing platforms
    'NewPlatform': ('https://newplatform.com/favicon.ico', True),
}

# Add to PLATFORM_COLORS
PLATFORM_COLORS = {
    # ... existing platforms
    'NewPlatform': 'blue',
}

# Add to ALL_PLATFORMS
ALL_PLATFORMS = [
    'Codeforces', 'LeetCode', # ... existing platforms
    'NewPlatform'
]
```

**Note:** The configuration is now in JSON format in `src/config.json`. The above Python syntax is for reference - use JSON format when editing the actual file.

### 2. Implement Fetcher

Add to `auto_update.py` in the `PlatformStats` class:

```python
def get_newplatform(self):
    """Fetch NewPlatform statistics."""
    try:
        # Try API first if available
        url = f"https://api.newplatform.com/users/{USER_CONFIG['NewPlatform']}"
        data = self.fetch_url(url, use_api=True)
        if data:
            return data.get('solved_count')
        
        # Fallback to web scraping
        url = f"https://newplatform.com/profile/{USER_CONFIG['NewPlatform']}"
        html = self.fetch_url(url)
        if html:
            patterns = [
                r'Solved:\s*(\d+)',
                r'"solvedCount":\s*(\d+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                    if 0 < count < MAX_REASONABLE_COUNT:
                        return count
    except Exception as e:
        print(f"  Error getting NewPlatform stats: {e}")
    return None
```

### 3. Register the Fetcher

Add to the `platforms` dictionary in `fetch_all_stats()`:

```python
platforms = {
    # ... existing platforms
    'NewPlatform': self.get_newplatform,
}
```

### 4. Test Your Implementation

```bash
python scripts/auto_update.py
```

## 📖 Documentation

Good documentation is crucial! When contributing:

- Update README.md if you add features
- Add docstrings to new functions/classes
- Update CHANGELOG.md with your changes
- Consider adding examples

## ❓ Questions?

- Open an issue with the `question` label
- Check existing documentation in README.md
- Review closed issues for similar questions

## 🙏 Thank You!

Your contributions make this project better. Whether it's a bug report, feature suggestion, or code contribution, every bit helps!

---

**Happy Contributing!** 🎉
