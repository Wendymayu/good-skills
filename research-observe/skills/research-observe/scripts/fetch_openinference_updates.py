#!/usr/bin/env python3
"""Fetch recent OpenInference Working Group activity relevant to GenAI observability."""

import argparse
import json
import os
import sys

import requests

GITHUB_API = "https://api.github.com"

REPOS = [
    "Arize-AI/openinference",
]

GENAI_KEYWORDS = [
    "genai", "gen-ai", "generative ai", "gen_ai",
    "llm", "large language model",
    "ai", "artificial intelligence",
    "semantic-convention", "semconv",
    "instrumentation", "tracing", "span",
    "langchain", "crewai", "agent",
]


def github_get(path: str, token: str | None = None) -> dict | list | None:
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


def main():
    parser = argparse.ArgumentParser(description="Fetch OpenInference WG GenAI community updates")
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

    output = {
        "prs": all_prs,
        "issues": all_issues,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
