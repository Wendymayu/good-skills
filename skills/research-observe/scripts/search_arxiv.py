#!/usr/bin/env python3
"""Search arXiv for papers on LLM/AI agent observability."""

import argparse
import json
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
from dateutil.parser import parse as parse_date

ARXIV_API = "http://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}

CATEGORY_FILTER = "(cat:cs.AI OR cat:cs.CL OR cat:cs.SE)"

TOPIC_TERMS = {
    "tracing": ['"agent trace"', '"distributed tracing" LLM', '"span model" LLM'],
    "eval": ['"LLM evaluation"', '"agent evaluation"', '"LLM-as-judge"'],
    "safety": ['"AI alignment" observability', '"safety monitoring" LLM', '"jailbreak detection"', '"safety guardrail"'],
    "cost": ['"token cost" attribution', '"LLM billing"', '"cost per task"'],
    "architecture": ['"agent DAG"', '"multi-agent" observability', '"tool call" telemetry', '"multi-agent contamination"'],
    "observability": ['"LLM observability"', '"agent tracing"', '"AI monitoring"', '"model observability"', '"data provenance" LLM', '"agent monitoring"'],
}


def build_query(topic: str, venues: list[str] | None = None) -> str:
    if topic in TOPIC_TERMS:
        terms = TOPIC_TERMS[topic]
    else:
        terms = [f'"{topic}"']

    query_parts = " OR ".join(f"ti:{t}" for t in terms)
    query = f"({query_parts}) AND {CATEGORY_FILTER}"

    if venues:
        venue_terms = " OR ".join(f'all:"{v}"' for v in venues)
        query = f"({query}) AND ({venue_terms})"

    return query


def search_arxiv(query: str, max_results: int, retries: int = 2) -> list[dict]:
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": max_results,
        "start": 0,
    }

    for attempt in range(retries + 1):
        try:
            resp = requests.get(ARXIV_API, params=params, timeout=30)
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            if attempt < retries:
                time.sleep(3)
            else:
                return [{"error": f"arXiv API request failed: {e}"}]

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as e:
        return [{"error": f"Failed to parse arXiv XML: {e}"}]

    results = []
    for entry in root.findall("atom:entry", NS):
        title_el = entry.find("atom:title", NS)
        if title_el is None:
            continue
        title = " ".join(title_el.text.split())

        published_el = entry.find("atom:published", NS)
        published = ""
        if published_el is not None and published_el.text:
            try:
                published = parse_date(published_el.text).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                published = published_el.text[:10]

        authors = []
        for author_el in entry.findall("atom:author", NS):
            name_el = author_el.find("atom:name", NS)
            if name_el is not None and name_el.text:
                authors.append(name_el.text.strip())

        summary_el = entry.find("atom:summary", NS)
        summary = ""
        if summary_el is not None and summary_el.text:
            summary = " ".join(summary_el.text.split())

        url = ""
        for link_el in entry.findall("atom:link", NS):
            if link_el.get("title") == "html":
                url = link_el.get("href", "")
                break
        if not url:
            id_el = entry.find("atom:id", NS)
            if id_el is not None and id_el.text:
                url = id_el.text.strip()

        categories = [
            c.get("term", "")
            for c in entry.findall("atom:category", NS)
            if c.get("term")
        ]

        results.append({
            "title": title,
            "authors": authors,
            "summary": summary,
            "keywords": categories,
            "published": published,
            "url": url,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Search arXiv for LLM observability papers")
    parser.add_argument("--topic", required=True, help="Search topic")
    parser.add_argument("--since", required=True, help="Date filter (YYYY-MM-DD)")
    parser.add_argument("--deep", action="store_true", help="Fewer results with full abstracts")
    parser.add_argument("--venues", nargs="*", default=None,
                        help="Filter by venue name (e.g., AAAI NeurIPS ICML EMNLP)")
    args = parser.parse_args()

    max_results = 5 if args.deep else 15
    query = build_query(args.topic, args.venues)

    results = search_arxiv(query, max_results)

    since_date = args.since
    if since_date:
        filtered = []
        for r in results:
            if isinstance(r, dict) and "error" not in r:
                if r.get("published", "") >= since_date:
                    if not args.deep and len(r.get("summary", "")) > 200:
                        r["summary"] = r["summary"][:197] + "..."
                    filtered.append(r)
            else:
                filtered.append(r)
        results = filtered

    sys.stdout.buffer.write(json.dumps(results, indent=2, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
