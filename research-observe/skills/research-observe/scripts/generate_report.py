#!/usr/bin/env python3
"""Generate a structured markdown report from combined research results."""

import argparse
import json
import sys
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path


def title_similarity(a: str, b: str) -> float:
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    return SequenceMatcher(None, " ".join(sorted(tokens_a)), " ".join(sorted(tokens_b))).ratio()


def deduplicate_papers(arxiv_papers: list[dict], s2_papers: list[dict]) -> list[dict]:
    """Deduplicate papers across arXiv and Semantic Scholar by title similarity."""
    merged = list(arxiv_papers)
    for s2 in s2_papers:
        is_dup = False
        for existing in merged:
            if title_similarity(s2.get("title", ""), existing.get("title", "")) > 0.7:
                # Merge: prefer entry with more metadata
                if s2.get("citationCount", 0) > existing.get("citationCount", 0):
                    existing.update(s2)
                is_dup = True
                break
        if not is_dup:
            merged.append(s2)
    return merged


def render_prs_table(prs: list[dict]) -> str:
    if not prs:
        return "*No GenAI-related PRs found in the specified period.*"
    lines = []
    for pr in prs:
        if "error" in pr:
            lines.append(f"| Error | {pr.get('repo', '')} | - | {pr['error']} |")
            continue
        title = pr.get("title", "")
        url = pr.get("url", "")
        repo = pr.get("repo", "").replace("open-telemetry/", "")
        state = pr.get("state", "")
        # Truncate title for table readability
        short_title = title if len(title) <= 60 else title[:57] + "..."
        lines.append(f"| [{short_title}]({url}) | {repo} | {state} | {title[:80]} |")
    return "\n".join(lines)


def render_issues_table(issues: list[dict]) -> str:
    if not issues:
        return "*No GenAI-related issues found in the specified period.*"
    lines = []
    for issue in issues:
        title = issue.get("title", "")
        url = issue.get("url", "")
        repo = issue.get("repo", "").replace("open-telemetry/", "")
        labels = ", ".join(issue.get("labels", []))
        short_title = title if len(title) <= 60 else title[:57] + "..."
        lines.append(f"| [{short_title}]({url}) | {repo} | {labels} | {title[:80]} |")
    return "\n".join(lines)


def render_papers_table(papers: list[dict]) -> str:
    if not papers:
        return "*No academic papers found for the specified topic and period.*"
    lines = []
    for p in papers:
        title = p.get("title", "")
        authors = ", ".join(p.get("authors", [])[:3])
        if len(p.get("authors", [])) > 3:
            authors += " et al."
        summary = p.get("summary", "")
        url = p.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {short_title} | {authors} | {summary[:80]} | [Link]({url}) |")
    return "\n".join(lines)


def render_tools_table(tools: list[dict]) -> str:
    if not tools:
        return "*No notable tool updates found.*"
    lines = []
    for t in tools:
        name = t.get("name", "")
        change = t.get("change", "")
        stars = t.get("stars")
        stars_str = str(stars) if stars else "-"
        url = t.get("url", "")
        lines.append(f"| {name} | {change[:60]} | {stars_str} | [GitHub]({url}) |")
    return "\n".join(lines)


def render_engineering_table(engineering: list[dict]) -> str:
    if not engineering:
        return "*No engineering blog posts found.*"
    lines = []
    for e in engineering:
        title = e.get("title", "")
        source = e.get("source", "")
        takeaway = e.get("takeaway", "")
        url = e.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {short_title} | {source} | {takeaway[:80]} | [Read]({url}) |")
    return "\n".join(lines)


def generate_trend_insights(data: dict) -> str:
    """Generate a brief trend summary from the collected data."""
    observations = []

    pr_count = len([p for p in data.get("otel", {}).get("prs", []) if "error" not in p])
    if pr_count > 0:
        observations.append(f"OTel GenAI semantic conventions continue evolving with {pr_count} active PRs in the monitoring window.")

    paper_count = len(data.get("arxiv", [])) + len(data.get("semantic_scholar", []))
    if paper_count > 0:
        observations.append(f"Academic activity remains strong with {paper_count} papers published on LLM/AI observability topics.")

    tool_count = len(data.get("tools", []))
    if tool_count > 0:
        observations.append(f"The open-source tooling ecosystem shows {tool_count} notable updates, indicating rapid iteration across the board.")

    if not observations:
        return "Limited activity detected in this monitoring window. Consider expanding the date range or topic scope."

    return " ".join(observations)


def main():
    parser = argparse.ArgumentParser(description="Generate LLM observability research report")
    parser.add_argument("--input", required=True, help="Path to combined results JSON")
    parser.add_argument("--template", required=True, help="Path to report template markdown")
    parser.add_argument("--topic", required=True, help="Research topic for the report title")
    args = parser.parse_args()

    input_path = Path(args.input)
    template_path = Path(args.template)

    if not input_path.exists():
        print(json.dumps({"error": f"Input file not found: {input_path}"}))
        sys.exit(1)

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(json.dumps({"error": f"Failed to read input: {e}"}))
        sys.exit(1)

    if not template_path.exists():
        # Use built-in template if file not found
        template = DEFAULT_TEMPLATE
    else:
        template = template_path.read_text(encoding="utf-8")

    # Deduplicate papers
    arxiv_papers = [p for p in data.get("arxiv", []) if isinstance(p, dict) and "error" not in p]
    s2_papers = [p for p in data.get("semantic_scholar", []) if isinstance(p, dict) and "error" not in p]
    papers = deduplicate_papers(arxiv_papers, s2_papers)

    # Sort papers by date descending
    papers.sort(key=lambda p: p.get("published", ""), reverse=True)

    otel = data.get("otel", {})
    today = datetime.now().strftime("%Y-%m-%d")

    # Fill template
    report = template
    report = report.replace("{DATE}", today)
    report = report.replace("{TOPIC}", args.topic)
    report = report.replace("{SINCE_DATE}", args.since if hasattr(args, "since") else "N/A")
    report = report.replace("{TREND_INSIGHTS}", generate_trend_insights(data))
    report = report.replace("{OTEL_PRS_TABLE}", render_prs_table(otel.get("prs", [])))
    report = report.replace("{OTEL_ISSUES_TABLE}", render_issues_table(otel.get("issues", [])))

    sig_url = otel.get("sig_notes_url")
    sig_text = f"[GenAI SIG Meeting Notes]({sig_url})" if sig_url else "No SIG meeting notes found in this period."
    report = report.replace("{SIG_UPDATES}", sig_text)

    report = report.replace("{PAPERS_TABLE}", render_papers_table(papers))
    report = report.replace("{TOOLS_TABLE}", render_tools_table(data.get("tools", [])))
    report = report.replace("{ENGINEERING_TABLE}", render_engineering_table(data.get("engineering", [])))

    # Write report
    report_filename = f"research-observe-report-{today}.md"
    report_path = Path(report_filename)
    report_path.write_text(report, encoding="utf-8")

    print(f"Report written to: {report_path.absolute()}")


DEFAULT_TEMPLATE = """# LLM Observability Landscape Report

**Date**: {DATE}
**Topic**: {TOPIC}
**Scope**: Since {SINCE_DATE}

---

## Trend Insights

{TREND_INSIGHTS}

---

## OTel Community Dynamics

### Active PRs

| PR | Repo | Status | Key Change |
|----|------|--------|------------|
{OTEL_PRS_TABLE}

### Notable Issues

| Issue | Repo | Labels | Summary |
|-------|------|--------|---------|
{OTEL_ISSUES_TABLE}

### GenAI SIG Updates

{SIG_UPDATES}

---

## Academic Papers

| Paper | Authors | Key Insight | Link |
|-------|---------|-------------|------|
{PAPERS_TABLE}

---

## Open-Source Tool Updates

| Project | Notable Change | Stars | Link |
|---------|---------------|-------|------|
{TOOLS_TABLE}

---

## Engineering Practices

| Article | Source | Key Takeaway | Link |
|---------|--------|-------------|------|
{ENGINEERING_TABLE}

---

*Report generated by research-observe skill.*
"""


if __name__ == "__main__":
    main()
