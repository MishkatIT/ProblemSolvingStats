#!/usr/bin/env python
"""
Known platform URL templates and domains for handle configuration.
This file contains templates for generating profile URLs from usernames.
"""

# Known platform URL templates
# Format: platform_name: template_with_{username}_placeholder
PLATFORM_URL_TEMPLATES = {
    "Codeforces": "https://codeforces.com/profile/{username}",
    "LeetCode": "https://leetcode.com/u/{username}/",
    "CodeChef": "https://www.codechef.com/users/{username}",
    "AtCoder": "https://atcoder.jp/users/{username}",
    "CSES": "https://cses.fi/user/{username}/",
    "HackerEarth": "https://www.hackerearth.com/@{username}/",
    "HackerRank": "https://www.hackerrank.com/profile/{username}",
    "LightOJ": "https://lightoj.com/user/{username}",
    "Toph": "https://toph.co/u/{username}",
    "UVa": "https://uhunt.onlinejudge.org/id/{username}",
    "VJudge": "https://vjudge.net/user/{username}",
    "SPOJ": "https://www.spoj.com/users/{username}",
    "CSAcademy": "https://csacademy.com/user/{username}",
    "Kattis": "https://open.kattis.com/users/{username}",
    "Toki": "https://tlx.toki.id/profiles/{username}",
    "DMOJ": "https://dmoj.ca/user/{username}",
    "Timus": "https://acm.timus.ru/author.aspx?id={username}",
    "TopCoder": "https://www.topcoder.com/members/{username}",
    "OmegaUp": "https://omegaup.com/profile/{username}/",
    "Beecrowd": "https://www.beecrowd.com.br/judge/en/profile/{username}",
    "POJ": "http://poj.org/userstatus?user_id={username}",
    "ZOJ": "https://zoj.pintia.cn/user/{username}",
    "HDU": "http://acm.hdu.edu.cn/userstatus.php?user={username}",
    "FZU": "http://acm.fzu.edu.cn/user.php?uname={username}",
    "SGU": "http://acm.sgu.ru/teaminfo.php?id={username}",
    "AOJ": "https://judge.u-aizu.ac.jp/onlinejudge/user.jsp?id={username}",
    "Yukicoder": "https://yukicoder.me/users/{username}",
    "ProjectEuler": "https://projecteuler.net/profile/{username}.png",
    "COJ": "https://coj.uci.cu/user/useraccount.xhtml?username={username}",
    "InfoArena": "https://www.infoarena.ro/utilizator/{username}",
    "KTH": "https://www.kth.se/profile/{username}/",
    "MSU": "https://acm.msu.ru/user/{username}",
    "WCIPEG": "https://wcipeg.com/user/{username}",
    "COCI": "https://hsin.hr/coci/user.php?username={username}",
    "BOI": "https://boi.cses.fi/users/{username}",
    "IOI": "https://ioinformatics.org/user/{username}",
    "CodeJam": "https://codejam.googleapis.com/scoreboard/{username}",
    "HackerCup": "https://www.facebook.com/hackercup/user/{username}",
    "AtCoderABC": "https://atcoder.jp/users/{username}?contestType=algo",
    "CodeforcesGym": "https://codeforces.com/profile/{username}?gym=true",
    "LeetCodeCN": "https://leetcode.cn/u/{username}/",
    "NowCoder": "https://ac.nowcoder.com/acm/contest/profile/{username}",
    "Luogu": "https://www.luogu.com.cn/user/{username}",
    "LibreOJ": "https://loj.ac/user/{username}",
    "UniversalOJ": "https://uoj.ac/user/profile/{username}",
    "QDUOJ": "https://qduoj.com/user/{username}"
}

# List of all supported platforms
ALL_PLATFORMS = list(PLATFORM_URL_TEMPLATES.keys())

# Known domains for platform detection
# Format: domain: platform_name
KNOWN_DOMAINS = {
    "codeforces.com": "Codeforces",
    "leetcode.com": "LeetCode",
    "codechef.com": "CodeChef",
    "atcoder.jp": "AtCoder",
    "cses.fi": "CSES",
    "hackerearth.com": "HackerEarth",
    "hackerrank.com": "HackerRank",
    "lightoj.com": "LightOJ",
    "toph.co": "Toph",
    "uhunt.onlinejudge.org": "UVa",
    "vjudge.net": "VJudge",
    "spoj.com": "SPOJ",
    "csacademy.com": "CSAcademy",
    "open.kattis.com": "Kattis",
    "tlx.toki.id": "Toki",
    "dmoj.ca": "DMOJ",
    "acm.timus.ru": "Timus",
    "topcoder.com": "TopCoder",
    "omegaup.com": "OmegaUp",
    "beecrowd.com.br": "Beecrowd",
    "poj.org": "POJ",
    "zoj.pintia.cn": "ZOJ",
    "acm.hdu.edu.cn": "HDU",
    "acm.fzu.edu.cn": "FZU",
    "acm.sgu.ru": "SGU",
    "judge.u-aizu.ac.jp": "AOJ",
    "yukicoder.me": "Yukicoder",
    "projecteuler.net": "ProjectEuler",
    "coj.uci.cu": "COJ",
    "infoarena.ro": "InfoArena",
    "kth.se": "KTH",
    "acm.msu.ru": "MSU",
    "wcipeg.com": "WCIPEG",
    "hsin.hr": "COCI",
    "boi.cses.fi": "BOI",
    "ioinformatics.org": "IOI",
    "codejam.googleapis.com": "CodeJam",
    "facebook.com": "HackerCup",
    "leetcode.cn": "LeetCodeCN",
    "nowcoder.com": "NowCoder",
    "luogu.com.cn": "Luogu",
    "loj.ac": "LibreOJ",
    "uoj.ac": "UniversalOJ",
    "qduoj.com": "QDUOJ"
}

def get_template_for_platform(platform):
    """Get URL template for a platform."""
    return PLATFORM_URL_TEMPLATES.get(platform)

def get_platform_for_domain(domain):
    """Get platform name for a domain."""
    return KNOWN_DOMAINS.get(domain)

def generate_url_from_template(platform, username):
    """Generate URL using platform template."""
    template = get_template_for_platform(platform)
    if template:
        return template.replace('{username}', username)
    return f"https://{platform.lower()}.com/{username}"  # Fallback