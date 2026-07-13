#!/usr/bin/env python3
import argparse
from pathlib import Path


def assert_contains(content: str, marker: str) -> None:
    if marker not in content:
        raise ValueError(f"Expected marker not found: {marker}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated profile automation outputs")
    parser.add_argument("--readme", required=True)
    parser.add_argument("--linkedin-draft", required=True)
    args = parser.parse_args()

    readme = Path(args.readme).read_text(encoding="utf-8")
    draft = Path(args.linkedin_draft).read_text(encoding="utf-8")

    if len(readme.strip()) < 300:
        raise ValueError("README output is unexpectedly short")

    for marker in [
        "## 🧠 Core Skills",
        "## 📊 Weekly GitHub Activity",
        "## 🚀 Pinned Project Summaries",
        "## 🤝 Let’s Connect",
    ]:
        assert_contains(readme, marker)

    assert_contains(draft, "Status: Draft")
    assert_contains(draft, "Human approval required")


if __name__ == "__main__":
    main()
