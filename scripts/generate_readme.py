#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- N/A"


def render_badges(badges: list[str]) -> str:
    return " ".join(f"![badge]({badge})" for badge in badges)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate profile README from structured data")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--activity", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    activity = json.loads(Path(args.activity).read_text(encoding="utf-8"))

    event_summary = activity.get("event_summary", {})
    highlights = event_summary.get("highlights", [])
    top_repos = event_summary.get("top_repositories", [])
    project_highlights = activity.get("project_highlights", [])

    top_repo_lines = [
        f"- **{repo['name']}** — {repo['activity_count']} activities"
        for repo in top_repos
        if repo.get("name")
    ] or ["- No activity captured this week."]

    project_lines = [
        f"- [{repo.get('name')}]({repo.get('html_url')}) — {repo.get('description')} (⭐ {repo.get('stargazers_count', 0)})"
        for repo in project_highlights
        if repo.get("name") and repo.get("html_url")
    ] or ["- Project highlights will appear after the next successful activity sync."]

    markdown = f"""# Hi, I'm {profile['name']} 👋

### {profile['headline']}
### {profile['tagline']}

{profile['summary']}

{render_badges(profile.get('badges', []))}

---

## 🧠 Core Skills

{bullets(profile.get('skills', []))}

---

## 📜 Certifications

{bullets(profile.get('certifications', []))}

---

## 🎓 Education

{bullets(profile.get('education', []))}

---

## 📊 Weekly GitHub Activity ({event_summary.get('window_days', 7)}-day window)

- Public events: **{event_summary.get('total_events', 0)}**
- Commits tracked: **{event_summary.get('commits', 0)}**
- PRs opened: **{event_summary.get('pull_requests_opened', 0)}**
- Issues opened: **{event_summary.get('issues_opened', 0)}**

### Highlights
{bullets(highlights)}

### Top Repositories This Week
{chr(10).join(top_repo_lines)}

---

## 🚀 Pinned Project Summaries

{chr(10).join(project_lines)}

---

## 🚀 Professional Focus

{bullets(profile.get('professional_focus', []))}

---

## 🤝 Let’s Connect

- 📧 Email: **{profile['email']}**
- 💼 LinkedIn: **[{profile['linkedin'].split('/')[-1] or 'LinkedIn'}]({profile['linkedin']})**
- 📍 Location: **{profile['location']}**

---

_This README is maintained automatically by profile automation agents._
"""

    Path(args.output).write_text(markdown, encoding="utf-8")


if __name__ == "__main__":
    main()
