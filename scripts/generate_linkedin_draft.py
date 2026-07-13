#!/usr/bin/env python3
import argparse
import datetime as dt
import json
from pathlib import Path


def to_bullets(items: list[str], fallback: str) -> str:
    if not items:
        return f"- {fallback}"
    return "\n".join(f"- {item}" for item in items)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LinkedIn weekly draft from profile and activity data")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--activity", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    activity = json.loads(Path(args.activity).read_text(encoding="utf-8"))
    event_summary = activity.get("event_summary", {})

    today = dt.date.today().isoformat()
    highlights = event_summary.get("highlights", [])

    draft = f"""# LinkedIn Draft - {today}

Status: Draft (Human approval required before publishing)

This week, I continued my focus on strategic delivery and transformation leadership.

## Weekly Metrics ({event_summary.get('window_days', 7)}-day window)
- Public GitHub activities: {event_summary.get('total_events', 0)}
- Commits: {event_summary.get('commits', 0)}
- PRs opened: {event_summary.get('pull_requests_opened', 0)}
- Issues opened: {event_summary.get('issues_opened', 0)}

## Key Highlights
{to_bullets(highlights, 'Consolidated planning and portfolio execution practices across ongoing initiatives.')}

## What I’m Building Momentum On
{to_bullets(profile.get('professional_focus', []), 'Driving measurable business outcomes through delivery governance.')}

I’m always happy to connect with professionals working on PMO excellence, agile transformation, and value-driven program delivery.

#ProjectManagement #PMO #DigitalTransformation #Agile #Leadership
"""

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(draft, encoding="utf-8")


if __name__ == "__main__":
    main()
