#!/usr/bin/env python3
"""Search Semantic Scholar for papers on LLM/AI agent observability."""

import argparse
import json
import os
import sys
import time

import requests

S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_FIELDS = "title,authors,abstract,url,publicationDate,citationCount"


def search_semantic_scholar(query: str, limit: int, year_from: str, retries: int = 2) -> list[dict]:
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    headers = {}
    if api_key:
        headers["x-api-key"] = api_key

    year_filter = f"{year_from}-" if year_from else ""
    params = {
        "query": query,
        "fields": S2_FIELDS,
        "limit": limit,
        "year": year_filter,
    }

    for attempt in range(retries + 1):
        try:
            time.sleep(1.1)  # Respect rate limit for unauthenticated use
            resp = requests.get(S2_API, params=params, headers=headers, timeout=30)
            if resp.status_code == 429:
                wait = int(resp.headers.get("Retry-After", "5"))
                time.sleep(wait)
                continue
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            if attempt < retries:
                time.sleep(3)
            else:
                return [{"error": f"Semantic Scholar API request failed: {e}"}]

    data = resp.json()
    results = []
    for paper in data.get("data", []):
        authors = [a.get("name", "") for a in paper.get("authors", []) if a.get("name")]
        abstract = paper.get("abstract", "") or ""
        pub_date = paper.get("publicationDate", "") or ""

        results.append({
            "title": paper.get("title", ""),
            "authors": authors,
            "summary": abstract,
            "keywords": [],
            "published": pub_date[:10] if pub_date else "",
            "url": paper.get("url", ""),
            "citationCount": paper.get("citationCount", 0) or 0,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Search Semantic Scholar for LLM observability papers")
    parser.add_argument("--topic", required=True, help="Search topic")
    parser.add_argument("--since", required=True, help="Date filter (YYYY-MM-DD)")
    parser.add_argument("--deep", action="store_true", help="Fewer results with full abstracts")
    args = parser.parse_args()

    limit = 5 if args.deep else 15
    year_from = args.since[:4] if args.since else ""

    # Build query with observability context
    query = args.topic
    broader_terms = ["LLM observability", "agent tracing", "AI monitoring", "model observability"]
    if args.topic.lower() not in ("observability", "monitoring"):
        query = f'{args.topic} ("observability" OR "monitoring" OR "tracing" OR "evaluation")'

    results = search_semantic_scholar(query, limit, year_from)

    # Trim abstracts for non-deep mode
    if not args.deep:
        for r in results:
            if isinstance(r, dict) and "error" not in r:
                if len(r.get("summary", "")) > 200:
                    r["summary"] = r["summary"][:197] + "..."

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
