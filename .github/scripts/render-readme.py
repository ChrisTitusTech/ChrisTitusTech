"""Render profile sections with small GitHub queries and bounded retries.

README.gtpl retains its historical name; its four comment markers are replaced
literally, so repository descriptions are never executed as template code.
"""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import urlencode


QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      commitContributionsByRepository(maxRepositories: 100) {
        repository { nameWithOwner url description isPrivate }
        contributions(last: 1) { nodes { occurredAt } }
      }
    }
  }
}
"""


def api(arguments):
    for attempt in range(3):
        try:
            result = subprocess.run(
                ["gh", "api", *arguments],
                check=True, capture_output=True, text=True, timeout=60,
            )
            data = json.loads(result.stdout)
            if isinstance(data, dict) and data.get("errors"):
                raise ValueError("GitHub returned GraphQL errors")
            return data
        except (subprocess.SubprocessError, ValueError, KeyError, TypeError):
            if attempt == 2:
                raise RuntimeError("GitHub query failed after 3 attempts") from None
            print("GitHub query failed; retrying", file=sys.stderr)
            time.sleep(5 * (attempt + 1))


def recent_contributions(entries, login):
    entries = [entry for entry in entries
               if not entry["repository"]["isPrivate"]
               and entry["repository"]["nameWithOwner"].lower() != f"{login}/{login}".lower()
               and entry["contributions"]["nodes"]]
    entries.sort(key=lambda entry: entry["contributions"]["nodes"][0]["occurredAt"],
                 reverse=True)
    return [repo_line(entry["repository"]["nameWithOwner"],
                      entry["repository"]["url"], entry["repository"]["description"])
            for entry in entries[:5]]


def clean(value):
    return " ".join((value or "").splitlines())


def repo_line(name, url, description):
    return f"- [{name}]({url}) - {clean(description)}"


def render(template, sections):
    for name in sections:
        if template.count("{{ /* " + name + " */ }}") != 1:
            raise ValueError(f"Expected exactly one {name} marker")
    # One pass prevents substituted repository text from being interpreted again.
    return re.sub(r"\{\{ /\* (RECENT_[A-Z_]+) \*/ \}\}",
                  lambda match: "\n" + "\n".join(sections[match[1]]), template)


def sections(login):
    data = api(["graphql", "-f", f"query={QUERY}", "-f", f"login={login}"])
    entries = data["data"]["user"]["contributionsCollection"]["commitContributionsByRepository"]
    result = {"RECENT_CONTRIBUTIONS": recent_contributions(entries, login)}
    repos = []
    page = 1
    while len(repos) < 5:
        batch = api([f"users/{login}/repos?sort=created&direction=desc&per_page=100&page={page}"])
        repos.extend(repo for repo in batch if not repo["fork"] and not repo["private"]
                     and repo["full_name"].lower() != f"{login}/{login}".lower())
        if len(batch) < 100:
            break
        page += 1
    result["RECENT_REPOS"] = [repo_line(repo["full_name"], repo["html_url"], repo["description"])
                              for repo in repos[:5]]
    query = urlencode({"q": f"type:pr author:{login} is:public -repo:{login}/{login}",
                       "sort": "created", "order": "desc", "per_page": 5})
    pulls = api([f"search/issues?{query}"])
    if pulls.get("incomplete_results"):
        raise RuntimeError("GitHub returned incomplete pull-request results")
    result["RECENT_PULL_REQUESTS"] = [
        f'- [{clean(pr["title"])}]({pr["html_url"]}) on '
        f'[{pr["repository_url"].split("/repos/", 1)[1]}]'
        f'(https://github.com/{pr["repository_url"].split("/repos/", 1)[1]})'
        for pr in pulls["items"]]
    stars = api([f"users/{login}/starred?sort=created&direction=desc&per_page=5"])
    result["RECENT_STARS"] = [repo_line(repo["full_name"], repo["html_url"], repo["description"])
                              for repo in stars if not repo["private"]]
    return result


if __name__ == "__main__":
    login = os.environ["GITHUB_REPOSITORY_OWNER"]
    template = Path(sys.argv[1]).read_text()
    Path(sys.argv[2]).write_text(render(template, sections(login)))
