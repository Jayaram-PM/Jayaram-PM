#!/usr/bin/env python3
import argparse
import json
import os
import urllib.error
import urllib.request


def publish_to_linkedin(text: str, access_token: str, person_urn: str) -> None:
    url = "https://api.linkedin.com/v2/ugcPosts"
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status not in (200, 201):
            raise RuntimeError(f"LinkedIn publish failed with status {response.status}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish a LinkedIn draft when API credentials are available")
    parser.add_argument("--draft", required=True)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    draft_text = open(args.draft, "r", encoding="utf-8").read()

    if not args.publish:
        print("Publish flag not set; skipping LinkedIn publish.")
        return

    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN")

    if not access_token or not person_urn:
        print("LinkedIn API credentials are not configured. Draft remains for manual review/posting.")
        return

    try:
        publish_to_linkedin(draft_text, access_token, person_urn)
        print("LinkedIn draft published successfully.")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LinkedIn API request failed: {error.code} {body}") from error


if __name__ == "__main__":
    main()
