#!/usr/bin/env python3
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote

USER, LIMIT = "awaae001", 7
SKIP = {"hyb-oyqq", "jiuci18/st_cardplus"}
BEGIN, END = "<!-- BEGIN GENERATED -->", "<!-- END GENERATED -->"
README = Path(__file__).with_name("README.md")

def gh(*args):
    out = subprocess.run(["gh", *args], capture_output=True, text=True, check=True).stdout
    return json.loads(out)

def count(query):
    return gh("api", f"search/commits?q={quote(query)}&per_page=1")["total_count"]

def total_stars():
    stars, page = 0, 1
    while True:
        repos = gh("api", f"users/{USER}/repos?per_page=100&page={page}")
        stars += sum(r["stargazers_count"] for r in repos if not r["fork"])
        if len(repos) < 100:
            return stars
        page += 1

search = (f'query{{search(query:"author:{USER} is:merged sort:created-desc",type:ISSUE,first:60)'
          "{nodes{...on PullRequest{number title mergedAt repository{nameWithOwner}}}}}")
prs = sorted(gh("api", "graphql", "-f", f"query={search}")["data"]["search"]["nodes"],
             key=lambda p: p["mergedAt"], reverse=True)

rows = []
for p in prs:
    repo = p["repository"]["nameWithOwner"]
    if repo in SKIP or repo.split("/")[0] in SKIP:
        continue
    rows.append(f"#{p['number']:<5} {p['title']}  - {repo}")
    if len(rows) == LIMIT:
        break

total = count(f"author:{USER}")
recent = count(f"author:{USER} committer-date:>{date.today() - timedelta(days=30)}")
stars = total_stars()

text = README.read_text()
begin = text.index(BEGIN) + len(BEGIN)
README.write_text(f"""{text[:begin]}
```shell
$ gh pr list --author={USER} --state=merged -{len(rows)}
{chr(10).join(rows)}
```
Total commits {total:,} | 30 days {recent:,} | Total stars {stars:,}

<sub>记得用 `python3 update.py` 更新 README，上次是 {date.today()}。</sub>
{text[text.index(END):]}""")
