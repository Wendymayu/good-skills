#!/usr/bin/env python3
"""Fetch recent OpenTelemetry community activity relevant to GenAI observability."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import requests

GITHUB_API = "https://api.github.com"

REPOS = [
    "open-telemetry/semantic-conventions",
    "open-telemetry/opentelemetry-python",
    "open-telemetry/opentelemetry-js",
    "open-telemetry/opentelemetry-go",
    "open-telemetry/community",
]

GENAI_KEYWORDS = [
    "genai", "gen-ai", "generative ai", "gen_ai",
    "llm", "large language model",
    "ai", "artificial intelligence",
    "semantic-convention", "semconv",
    "instrumentation",
]


def github_get(path: str, token: str | None = None) -> dict | None:
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    try:
        resp = requests.get(f"{GITHUB_API}{path}", headers=headers, timeout=30)
        if resp.status_code == 403:
            return {"error": "GitHub API rate limit exceeded. Set GITHUB_TOKEN env var for higher limits."}
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        return {"error": f"GitHub API request failed: {e}"}


def is_genai_related(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in GENAI_KEYWORDS)


def fetch_prs(repo: str, since: str, token: str | None = None) -> list[dict]:
    path = f"/repos/{repo}/pulls?state=all&sort=updated&direction=desc&per_page=20"
    data = github_get(path, token)
    if not data or isinstance(data, dict) and "error" in data:
        err = data.get("error", "unknown") if data else "no data"
        return [{"repo": repo, "error": err}]

    results = []
    for pr in data:
        updated = pr.get("updated_at", "")
        if updated and updated[:10] < since:
            continue
        title = pr.get("title", "")
        if not is_genai_related(title):
            continue

        results.append({
            "repo": repo,
            "number": pr.get("number"),
            "title": title,
            "state": pr.get("state", ""),
            "updated_at": updated,
            "url": pr.get("html_url", ""),
            "labels": [l.get("name", "") for l in pr.get("labels", [])],
        })

    return results


def fetch_issues(repo: str, since: str, token: str | None = None) -> list[dict]:
    path = f"/repos/{repo}/issues?state=all&sort=updated&direction=desc&per_page=20"
    data = github_get(path, token)
    if not data or isinstance(data, dict) and "error" in data:
        return []

    results = []
    for issue in data:
        # Skip PRs (they appear in issues endpoint too)
        if "pull_request" in issue:
            continue
        updated = issue.get("updated_at", "")
        if updated and updated[:10] < since:
            continue
        title = issue.get("title", "")
        if not is_genai_related(title):
            continue

        results.append({
            "repo": repo,
            "number": issue.get("number"),
            "title": title,
            "state": issue.get("state", ""),
            "updated_at": updated,
            "url": issue.get("html_url", ""),
            "labels": [l.get("name", "") for l in issue.get("labels", [])],
        })

    return results


def fetch_sig_notes(token: str | None = None) -> str | None:
    """Try to locate GenAI SIG meeting notes in the community repo."""
    # Try common paths
    paths_to_try = [
        "/repos/open-telemetry/community/contents/sig/gen-ai",
        "/repos/open-telemetry/community/contents/sig/genai",
        "/repos/open-telemetry/community/contents/sigs/gen-ai",
    ]
    for path in paths_to_try:
        data = github_get(path, token)
        if data and isinstance(data, list):
            for item in data:
                name = item.get("name", "").lower()
                if "meeting" in name or "notes" in name:
                    return item.get("html_url", "")

    # Fallback: search issues with gen-ai label
    path = "/repos/open-telemetry/community/issues?labels=gen-ai&per_page=5&sort=updated&direction=desc"
    data = github_get(path, token)
    if data and isinstance(data, list) and len(data) > 0:
        return data[0].get("html_url", "")

    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch OTel GenAI community updates")
    parser.add_argument("--since", required=True, help="Date filter (YYYY-MM-DD)")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    since = args.since

    all_prs = []
    all_issues = []

    for repo in REPOS:
        prs = fetch_prs(repo, since, token)
        all_prs.extend(prs)

        issues = fetch_issues(repo, since, token)
        all_issues.extend(issues)

    sig_url = fetch_sig_notes(token)

    output = {
        "prs": all_prs,
        "issues": all_issues,
        "sig_notes_url": sig_url,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
