#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from typing import Any


def http_get_json(url: str, token: str | None, retries: int = 3) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "profile-automation-agent",
    }
    if token:
        headers["Authorization"] = "Bearer " + token

    for attempt in range(1, retries + 1):
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            if err.code < 500:
                raise
            if attempt == retries:
                raise
        except Exception:
            if attempt == retries:
                raise
        time.sleep(attempt * 2)

    return []


def summarize_events(events: list[dict[str, Any]], window_days: int) -> dict[str, Any]:
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=window_days)
    recent_events = []
    for event in events:
        created_at = event.get("created_at")
        if not created_at:
            continue
        timestamp = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        if timestamp >= cutoff:
            recent_events.append(event)

    repo_counter: Counter[str] = Counter()
    commits = 0
    prs_opened = 0
    issues_opened = 0

    highlights: list[str] = []
    for event in recent_events:
        repo_name = event.get("repo", {}).get("name", "unknown")
        repo_counter[repo_name] += 1
        event_type = event.get("type", "")

        if event_type == "PushEvent":
            commits += len(event.get("payload", {}).get("commits", []))
        elif event_type == "PullRequestEvent" and event.get("payload", {}).get("action") == "opened":
            prs_opened += 1
            pr_title = event.get("payload", {}).get("pull_request", {}).get("title")
            if pr_title:
                highlights.append(f"Opened PR: {pr_title} ({repo_name})")
        elif event_type == "IssuesEvent" and event.get("payload", {}).get("action") == "opened":
            issues_opened += 1

    for repo, count in repo_counter.most_common(3):
        highlights.append(f"{count} public activities in {repo}")

    return {
        "window_days": window_days,
        "total_events": len(recent_events),
        "commits": commits,
        "pull_requests_opened": prs_opened,
        "issues_opened": issues_opened,
        "top_repositories": [
            {"name": repo, "activity_count": count}
            for repo, count in repo_counter.most_common(5)
        ],
        "highlights": highlights[:8],
    }


def summarize_repositories(repos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = []
    for repo in repos[:4]:
        summaries.append(
            {
                "name": repo.get("name", ""),
                "description": repo.get("description") or "No description",
                "html_url": repo.get("html_url", ""),
                "stargazers_count": repo.get("stargazers_count", 0),
                "updated_at": repo.get("updated_at", ""),
            }
        )
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and summarize GitHub profile activity")
    parser.add_argument("--username", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--window-days", type=int, default=7)
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    events_url = f"https://api.github.com/users/{args.username}/events/public?per_page=100"
    repos_url = f"https://api.github.com/users/{args.username}/repos?sort=updated&per_page=10"

    payload: dict[str, Any] = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "username": args.username,
        "event_summary": {
            "window_days": args.window_days,
            "total_events": 0,
            "commits": 0,
            "pull_requests_opened": 0,
            "issues_opened": 0,
            "top_repositories": [],
            "highlights": ["No public GitHub events found in the selected time window."],
        },
        "project_highlights": [],
    }

    try:
        events = http_get_json(events_url, token)
        repos = http_get_json(repos_url, token)
        payload["event_summary"] = summarize_events(events, args.window_days)
        payload["project_highlights"] = summarize_repositories(repos)
    except Exception:
        payload["event_summary"]["highlights"] = [
            "Unable to retrieve GitHub activity this run; existing profile content was retained.",
            "Activity API call failed; workflow will retry in the next scheduled run.",
        ]

    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
