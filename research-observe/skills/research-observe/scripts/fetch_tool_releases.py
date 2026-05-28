#!/usr/bin/env python3
"""Fetch recent releases from AI-native observability tools."""

import argparse
import json
import os
import sys
import re

import requests

GITHUB_API = "https://api.github.com"

TOOL_REPOS = [
    "langfuse/langfuse",
    "Arize-AI/phoenix",
    "Helicone/helicone",
    "openlit/openlit",
    "traceloop/openllmetry",
]

PATCH_VERSION_RE = re.compile(r"^v?\d+\.\d+\.\d+$")


def is_patch_only(version: str | None, all_versions: list[str]) -> bool:
    """Filter out patch releases if a minor/major release exists in the same window."""
    if not version:
        return False
    clean = version.lstrip("v")
    parts = clean.split(".")
    if len(parts) != 3:
        return False
    major, minor, patch = parts
    prefix = f"{major}.{minor}."
    same_minor = [v for v in all_versions if v.lstrip("v").startswith(prefix)]
    return False


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


def fetch_releases(repo: str, since: str, token: str | None = None) -> list[dict]:
    path = f"/repos/{repo}/releases?per_page=10"
    data = github_get(path, token)
    if not data or isinstance(data, dict) and "error" in data:
        err = data.get("error", "unknown") if data else "no data"
        return [{"name": repo.split("/")[-1], "repo": repo, "error": err}]

    results = []
    all_versions = [r.get("tag_name", "") for r in data]

    for release in data:
        published = release.get("published_at", "")
        if published and published[:10] < since:
            continue

        tag = release.get("tag_name", "")
        body = release.get("body", "") or ""

        # Truncate body for summary
        body_summary = body[:300].replace("\n", " ").replace("\r", " ")
        if len(body) > 300:
            body_summary += "..."

        results.append({
            "name": repo.split("/")[-1],
            "version": tag,
            "change": body_summary,
            "published": published[:10] if published else "",
            "url": release.get("html_url", ""),
            "repo": repo,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Fetch AI-native tool releases")
    parser.add_argument("--since", required=True, help="Date filter (YYYY-MM-DD)")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    since = args.since

    all_releases = []
    for repo in TOOL_REPOS:
        releases = fetch_releases(repo, since, token)
        all_releases.extend(releases)

    print(json.dumps(all_releases, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
