#!/usr/bin/env python3
"""Rewrite the generated block in README.md. Needs gh logged in."""

import json
import subprocess
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

USER = "awaae001"
SKIP_OWNERS = {"hyb-oyqq"}
SKIP_REPOS = {"jiuci18/st_cardplus"}
BEGIN, END = "<!-- BEGIN GENERATED -->", "<!-- END GENERATED -->"
README = Path(__file__).with_name("README.md")


def gh(*args):
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def recent_prs(n=7):
    prs = gh("search", "prs", "--author", USER, "--merged",
             "--sort", "created", "--order", "desc", "--limit", "60",
             "--json", "number,title,repository")
    rows = []
    for p in prs:
        repo = p["repository"]["nameWithOwner"]
        if repo in SKIP_REPOS or repo.split("/")[0] in SKIP_OWNERS:
            continue
        rows.append(f"#{p['number']:<5} {p['title']}  - {repo}")
        if len(rows) == n:
            break
    return rows


def count(query):
    return gh("api", f"search/commits?q={quote(query)}&per_page=1")["total_count"]


def block():
    rows = recent_prs()
    total = count(f"author:{USER}")
    recent = count(f"author:{USER} committer-date:>{date.today() - timedelta(days=365)}")
    return f"""```console
$ gh pr list --author={USER} --state=merged -{len(rows)}
{chr(10).join(rows)}
```

Total commits {total:,} | Last year {recent:,}"""


text = README.read_text()
begin = text.index(BEGIN) + len(BEGIN)
README.write_text(f"{text[:begin]}\n{block()}\n{text[text.index(END):]}")
