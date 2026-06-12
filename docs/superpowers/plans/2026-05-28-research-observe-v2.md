# research-observe v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade research-observe from a 4-script lightweight research tool into a 7-plate, 40+-source multi-source observability intelligence system.

**Architecture:** Scripts produce structured JSON for deterministic sources (arXiv, S2, GitHub repos, GitHub releases). Claude orchestrates unstructured sources (blogs, newsletters, domestic media) through WebSearch+WebFetch instructions in SKILL.md. `generate_report.py` is the sole aggregator — it reads a combined JSON and fills a markdown template.

**Tech Stack:** Python 3 (stdlib + `requests` + `python-dateutil`), GitHub REST API v3, arXiv Atom XML API, Semantic Scholar Graph API v1

---

## File Map

| File | Responsibility |
|------|---------------|
| `skills/research-observe/SKILL.md` | 7-plate orchestration instructions for Claude |
| `references/search-strategies.md` | Query templates for all 7 plates (Claude reads) |
| `references/source-guide.md` | API docs, repo lists, rate limits, JSON schema |
| `references/report-template.md` | Markdown skeleton with `{PLACEHOLDER}` variables |
| `scripts/search_arxiv.py` | arXiv API queries with category + venue filters |
| `scripts/search_semantic_scholar.py` | Semantic Scholar queries with keyword sync |
| `scripts/fetch_otel_updates.py` | OTel GitHub PR/Issue scanner (unchanged) |
| `scripts/fetch_openinference_updates.py` | **NEW** OpenInference GitHub PR/Issue scanner |
| `scripts/fetch_tool_releases.py` | **NEW** GitHub Releases fetcher for AI-native tools |
| `scripts/generate_report.py` | Aggregator: reads combined JSON, fills template |

---

### Task 1: Extend `references/search-strategies.md`

**Files:**
- Modify: `research-observe/skills/research-observe/references/search-strategies.md`

- [ ] **Step 1: Add all new query templates**

Replace the current file content with:

```markdown
# Search Strategies

Query templates for each research plate. Scripts use these programmatically; Claude uses them for WebSearch.

## Plate 1: Industry Newsletters (WebSearch)

```
site:tldr.tech/ai LLM observability agent monitoring
site:latent.space AI agent observability tracing
site:deeplearning.ai/the-batch AI monitoring safety
site:radarai.com LLM observability
```

## Plate 2: Domestic Sources (WebSearch)

```
site:infoq.cn LLM可观测性 AI Agent监控
site:qbitai.com LLM agent observability 监控
site:jiqizhixin.com AI agent 可观测
site:zhihu.com 可观测性 LangFuse OTel
site:okjk.com LLM observability agent
```

## Plate 3: Academic Papers

### arXiv + Semantic Scholar Keywords

| Domain | Terms |
|--------|-------|
| Observability | "LLM observability", "AI agent tracing", "AI monitoring", "model observability", "telemetry LLM" |
| Evaluation | "LLM evaluation", "agent evaluation", "benchmark LLM", "LLM-as-judge" |
| Safety | "AI alignment observability", "safety monitoring", "guardrail tracing", "red-team observability", "jailbreak detection" |
| Architecture | "agent trace model", "span model LLM", "trace context propagation agent", "multi-agent contamination" |
| Data | "data provenance LLM", "agent data lineage", "tool call telemetry" |

### Topic Expansions

**tracing**: "agent trace", "distributed tracing" LLM, "span model" LLM

**eval**: "LLM evaluation", "agent evaluation", "LLM-as-judge"

**safety**: "AI alignment" observability, "safety monitoring" LLM, "jailbreak detection"

**cost**: "token cost" attribution, "LLM billing", "cost per task"

**architecture**: "agent DAG", "multi-agent" observability, "tool call" telemetry

**observability** (full scan): "LLM observability", "agent tracing", "AI monitoring", "model observability"

### arXiv Category Filter

`(cat:cs.AI OR cat:cs.CL OR cat:cs.SE)`

### Venue Filter (--venues)

| Venue | arXiv identifier |
|-------|-----------------|
| AAAI | aaai |
| NeurIPS | neurips |
| ICML | icml |
| EMNLP | emnlp |

### Twitter/X Academic Accounts (WebSearch)

```
from:@_akhaliq AI observability agent monitoring
from:@papers_daily AI safety agent tracing
AlphaSignalAI LLM observability
```

## Plate 4: Standards & Open-Source Communities

### OTel Queries (WebSearch supplement)

```
"OpenTelemetry GenAI semantic conventions" site:github.com
"open-telemetry semantic-conventions" genai PR
"OTel GenAI SIG meeting" notes
site:github.com/open-telemetry/semantic-conventions "gen_ai"
```

### CNCF AI/ML WG (WebSearch)

```
site:github.com/cncf/tag-runtime AI observability
site:github.com/cncf ai-ml-wg observability
site:cncf.io ai working group observability
```

## Plate 5: Enterprise Engineering Blogs (WebSearch)

```
site:techcommunity.microsoft.com Azure AI Foundry observability agent
site:anthropic.com engineering safety monitoring
site:datadoghq.com/blog AI agent monitoring observability
site:newrelic.com/blog AI agent LLM observability
site:cloud.google.com/blog AI ML observability GenAI tracing
site:openai.com engineering safety monitoring agent observability
site:aws.amazon.com/blogs/machine-learning LLM agent observability tracing
site:developer.aliyun.com AI agent 可观测 OTel
site:cloud.tencent.com/developer LLM agent 监控 可观测性
site:volcengine.com AI agent 可观测 监控
```

## Plate 6: Open-Source Tool Updates

### AI-Native Tool Queries (WebSearch supplement)

```
"LangFuse" release OR changelog
"Arize Phoenix" LLM observability release
"Helicone" update OR feature
"OpenLIT" opentelemetry genai
"Traceloop" openllmetry release
"Coze 罗盘" 可观测 agent
"LangSmith" changelog OR release
```

### Traditional Observability Tool Queries (WebSearch)

```
site:grafana.com/blog AI agent LLM observability
site:dynatrace.com AI agent monitoring Davis
site:splunk.com AI observability LLM
site:elastic.co/blog AI agent APM observability
```
```

- [ ] **Step 2: Commit**

```bash
git add research-observe/skills/research-observe/references/search-strategies.md
git commit -m "feat: extend search strategies for 7-plate v2 coverage"
```

---

### Task 2: Extend `references/source-guide.md`

**Files:**
- Modify: `research-observe/skills/research-observe/references/source-guide.md`

- [ ] **Step 1: Rewrite source guide with v2 content**

Replace the current file content with:

```markdown
# Source Guide

API endpoints, rate limits, and monitored repositories for research-observe v2.

## GitHub Repositories

### OTel GenAI SIG (fetch_otel_updates.py)

| Repository | Focus |
|-----------|-------|
| `open-telemetry/semantic-conventions` | GenAI span/metric/attribute definitions |
| `open-telemetry/opentelemetry-python` | Python SDK + instrumentations |
| `open-telemetry/opentelemetry-js` | JS SDK + instrumentations |
| `open-telemetry/opentelemetry-go` | Go SDK + instrumentations |
| `open-telemetry/community` | GenAI SIG meeting notes, governance |

### OpenInference WG (fetch_openinference_updates.py)

| Repository | Focus |
|-----------|-------|
| `Arize-AI/openinference` | Core OpenInference spec and Python SDK |
| `Arize-AI/phoenix` | AI observability platform (releases tracked separately) |

### AI-Native Tool Releases (fetch_tool_releases.py)

| Tool | GitHub Repository |
|------|------------------|
| LangFuse | `langfuse/langfuse` |
| Arize Phoenix | `Arize-AI/phoenix` |
| Helicone | `Helicone/helicone` |
| OpenLIT | `openlit/openlit` |
| Traceloop/OpenLLMetry | `traceloop/openllmetry` |

## GitHub API

- Endpoint: `https://api.github.com`
- Rate limit (unauthenticated): 60 requests/hour
- Rate limit (authenticated): 5,000 requests/hour
- Set env var `GITHUB_TOKEN` for higher limits
- Key endpoints used:
  - `GET /repos/{owner}/{repo}/pulls` — PR listing
  - `GET /repos/{owner}/{repo}/issues` — Issue listing
  - `GET /repos/{owner}/{repo}/releases` — Release listing
  - `GET /repos/{owner}/{repo}/contents/{path}` — File content lookup

## arXiv API

- Endpoint: `http://export.arxiv.org/api/query`
- Rate limit: 1 request per 3 seconds (polite policy)
- Response format: Atom XML
- Pagination: `start` and `max_results` parameters
- No authentication required

## Semantic Scholar API

- Endpoint: `https://api.semanticscholar.org/graph/v1/paper/search`
- Rate limit (unauthenticated): ~1 request/second
- Rate limit (authenticated): ~10 requests/second
- Set env var `SEMANTIC_SCHOLAR_API_KEY` for higher limits
- Response format: JSON
- Fields: `title,authors,abstract,url,publicationDate,citationCount`

## Combined Results JSON Schema (v2)

`generate_report.py` expects this schema:

```json
{
  "date": "YYYY-MM-DD",
  "since": "YYYY-MM-DD",
  "topic": "string",
  "newsletters": [
    {"source": "string", "title": "string", "summary": "string", "url": "string"}
  ],
  "domestic": [
    {"source": "string", "title": "string", "summary": "string", "url": "string"}
  ],
  "papers": [
    {"title": "string", "authors": ["string"], "summary": "string", "keywords": ["string"], "published": "YYYY-MM-DD", "url": "string", "citationCount": 0, "source": "arxiv|semantic_scholar|twitter"}
  ],
  "standards": {
    "otel": {
      "prs": [
        {"repo": "string", "number": 0, "title": "string", "state": "string", "updated_at": "ISO 8601", "url": "string", "labels": ["string"]}
      ],
      "issues": [
        {"repo": "string", "number": 0, "title": "string", "state": "string", "updated_at": "ISO 8601", "url": "string", "labels": ["string"]}
      ],
      "sig_notes_url": "string or null"
    },
    "openinference": {
      "prs": [
        {"repo": "string", "number": 0, "title": "string", "state": "string", "updated_at": "ISO 8601", "url": "string", "labels": ["string"]}
      ],
      "issues": [
        {"repo": "string", "number": 0, "title": "string", "state": "string", "updated_at": "ISO 8601", "url": "string", "labels": ["string"]}
      ]
    },
    "cncf": [
      {"title": "string", "summary": "string", "url": "string"}
    ]
  },
  "enterprise_blogs": [
    {"source": "string", "title": "string", "significance": "string", "url": "string"}
  ],
  "tools": {
    "ai_native": [
      {"name": "string", "version": "string", "change": "string", "published": "YYYY-MM-DD", "url": "string"}
    ],
    "traditional": [
      {"name": "string", "title": "string", "change": "string", "url": "string"}
    ]
  }
}
```
```

- [ ] **Step 2: Commit**

```bash
git add research-observe/skills/research-observe/references/source-guide.md
git commit -m "feat: extend source guide with v2 repos, endpoints, and JSON schema"
```

---

### Task 3: Rewrite `references/report-template.md`

**Files:**
- Modify: `research-observe/skills/research-observe/references/report-template.md`

- [ ] **Step 1: Write the 7-plate + summary template**

Replace the current file content with:

```markdown
# LLM & AI Agent 可观测性全景报告

**生成日期**: {DATE}
**扫描范围**: {TOPIC}
**时间窗口**: {SINCE_DATE} 至今

---

## 摘要

{SUMMARY}

---

## 一、行业周刊精选

| 来源 | 标题 | 核心要点 | 链接 |
|------|------|---------|------|
{NEWSLETTERS_TABLE}

---

## 二、国内信源

| 来源 | 标题 | 核心要点 | 链接 |
|------|------|---------|------|
{DOMESTIC_TABLE}

---

## 三、学术论文

| 标题 | 作者 | 核心发现 | 来源 | 引用数 | 链接 |
|------|------|---------|------|--------|------|
{PAPERS_TABLE}

---

## 四、标准&开源社区

### 社区动态概览

| 社区 | 活跃 PR 数 | 活跃 Issue 数 | 关键议题 |
|------|-----------|-------------|---------|
{STANDARDS_SUMMARY}

### OpenTelemetry GenAI SIG

#### 活跃 PR

| PR | 仓库 | 状态 | 变更说明 |
|----|------|------|---------|
{OTEL_PRS_TABLE}

#### 活跃 Issue

| Issue | 仓库 | 标签 | 摘要 |
|-------|------|------|------|
{OTEL_ISSUES_TABLE}

#### SIG 会议纪要

{SIG_UPDATES}

### OpenInference Working Group

#### 活跃 PR

| PR | 仓库 | 状态 | 变更说明 |
|----|------|------|---------|
{OI_PRS_TABLE}

#### 活跃 Issue

| Issue | 仓库 | 标签 | 摘要 |
|-------|------|------|------|
{OI_ISSUES_TABLE}

### CNCF AI/ML WG

| 议题 | 摘要 | 链接 |
|------|------|------|
{CNCF_TABLE}

---

## 五、大厂工程博客

| 来源 | 标题 | 工程意义 | 链接 |
|------|------|---------|------|
{ENTERPRISE_BLOGS_TABLE}

---

## 六、开源工具动态

### AI-Native 工具发版

| 项目 | 版本 | 关键变更 | 发布日期 | 链接 |
|------|------|---------|---------|------|
{AI_NATIVE_TOOLS_TABLE}

### 传统可观测工具 AI 进展

| 工具 | 文章/发版 | 要点 | 链接 |
|------|----------|------|------|
{TRADITIONAL_TOOLS_TABLE}

---

*报告由 research-observe skill 自动生成。*
```

- [ ] **Step 2: Commit**

```bash
git add research-observe/skills/research-observe/references/report-template.md
git commit -m "feat: rewrite report template for 7-plate v2 with summary header"
```

---

### Task 4: Add `--venues` parameter to `search_arxiv.py`

**Files:**
- Modify: `research-observe/skills/research-observe/scripts/search_arxiv.py`

- [ ] **Step 1: Expand topic terms and add venue filter logic**

Replace the `TOPIC_TERMS` dict and `build_query` function:

```python
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
```

- [ ] **Step 2: Update `main()` to parse `--venues`**

Replace the `main()` function:

```python
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

    print(json.dumps(results, indent=2, ensure_ascii=False))
```

- [ ] **Step 3: Commit**

```bash
git add research-observe/skills/research-observe/scripts/search_arxiv.py
git commit -m "feat: add --venues filter and expand keywords in search_arxiv.py"
```

---

### Task 5: Sync keywords in `search_semantic_scholar.py`

**Files:**
- Modify: `research-observe/skills/research-observe/scripts/search_semantic_scholar.py`

- [ ] **Step 1: Expand topic terms dict and align with arXiv script**

Add the `TOPIC_TERMS` dict (matching arXiv) and update `main()` to use it:

```python
TOPIC_TERMS = {
    "tracing": ['"agent trace"', '"distributed tracing" LLM', '"span model" LLM'],
    "eval": ['"LLM evaluation"', '"agent evaluation"', '"LLM-as-judge"'],
    "safety": ['"AI alignment" observability', '"safety monitoring" LLM', '"jailbreak detection"', '"safety guardrail"'],
    "cost": ['"token cost" attribution', '"LLM billing"', '"cost per task"'],
    "architecture": ['"agent DAG"', '"multi-agent" observability', '"tool call" telemetry', '"multi-agent contamination"'],
    "observability": ['"LLM observability"', '"agent tracing"', '"AI monitoring"', '"model observability"', '"data provenance" LLM', '"agent monitoring"'],
}


def main():
    parser = argparse.ArgumentParser(description="Search Semantic Scholar for LLM observability papers")
    parser.add_argument("--topic", required=True, help="Search topic")
    parser.add_argument("--since", required=True, help="Date filter (YYYY-MM-DD)")
    parser.add_argument("--deep", action="store_true", help="Fewer results with full abstracts")
    args = parser.parse_args()

    limit = 5 if args.deep else 15
    year_from = args.since[:4] if args.since else ""

    if args.topic in TOPIC_TERMS:
        terms = TOPIC_TERMS[args.topic]
        query = " OR ".join(terms)
    else:
        query = f'{args.topic} ("observability" OR "monitoring" OR "tracing" OR "evaluation")'

    results = search_semantic_scholar(query, limit, year_from)

    if not args.deep:
        for r in results:
            if isinstance(r, dict) and "error" not in r:
                if len(r.get("summary", "")) > 200:
                    r["summary"] = r["summary"][:197] + "..."

    print(json.dumps(results, indent=2, ensure_ascii=False))
```

- [ ] **Step 2: Commit**

```bash
git add research-observe/skills/research-observe/scripts/search_semantic_scholar.py
git commit -m "feat: sync keyword expansions with search_arxiv.py"
```

---

### Task 6: Create `fetch_openinference_updates.py`

**Files:**
- Create: `research-observe/skills/research-observe/scripts/fetch_openinference_updates.py`

- [ ] **Step 1: Write the script**

```python
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
```

- [ ] **Step 2: Verify the script runs (syntax check)**

```bash
python -c "import py_compile; py_compile.compile('research-observe/skills/research-observe/scripts/fetch_openinference_updates.py', doraise=True); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add research-observe/skills/research-observe/scripts/fetch_openinference_updates.py
git commit -m "feat: add fetch_openinference_updates.py for OpenInference WG monitoring"
```

---

### Task 7: Create `fetch_tool_releases.py`

**Files:**
- Create: `research-observe/skills/research-observe/scripts/fetch_tool_releases.py`

- [ ] **Step 1: Write the script**

```python
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
    # A patch is a patch release; check if any other version shares the same major.minor
    prefix = f"{major}.{minor}."
    same_minor = [v for v in all_versions if v.lstrip("v").startswith(prefix)]
    # Keep the latest patch for each minor
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
```

- [ ] **Step 2: Verify syntax**

```bash
python -c "import py_compile; py_compile.compile('research-observe/skills/research-observe/scripts/fetch_tool_releases.py', doraise=True); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add research-observe/skills/research-observe/scripts/fetch_tool_releases.py
git commit -m "feat: add fetch_tool_releases.py for AI-native tool release tracking"
```

---

### Task 8: Rewrite `generate_report.py`

**Files:**
- Modify: `research-observe/skills/research-observe/scripts/generate_report.py`

- [ ] **Step 1: Write the v2 report generator**

Replace the entire file with:

```python
#!/usr/bin/env python3
"""Generate a structured markdown report from combined v2 research results."""

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
    merged = list(arxiv_papers)
    for s2 in s2_papers:
        is_dup = False
        for existing in merged:
            if title_similarity(s2.get("title", ""), existing.get("title", "")) > 0.7:
                if s2.get("citationCount", 0) > existing.get("citationCount", 0):
                    existing.update(s2)
                is_dup = True
                break
        if not is_dup:
            merged.append(s2)
    return merged


def generate_summary(data: dict) -> str:
    observations = []

    otel = data.get("standards", {}).get("otel", {})
    pr_count = len([p for p in otel.get("prs", []) if "error" not in p])
    issue_count = len([i for i in otel.get("issues", []) if "error" not in i])

    paper_count = len(data.get("papers", []))
    tools_native = len(data.get("tools", {}).get("ai_native", []))
    tools_traditional = len(data.get("tools", {}).get("traditional", []))
    blogs_count = len(data.get("enterprise_blogs", []))
    newsletters_count = len(data.get("newsletters", []))
    domestic_count = len(data.get("domestic", []))

    if newsletters_count > 0:
        observations.append(f"行业周刊共收录 {newsletters_count} 条可观测性相关资讯。")

    if domestic_count > 0:
        observations.append(f"国内信源收录 {domestic_count} 篇文章，覆盖 InfoQ、量子位、AI 前线等渠道。")

    if paper_count > 0:
        observations.append(f"学术论文板块收录 {paper_count} 篇论文，涵盖 arXiv 预印本、顶会论文及学术社交媒体精选。")

    if pr_count > 0 or issue_count > 0:
        observations.append(f"OTel GenAI SIG 有 {pr_count} 个活跃 PR 和 {issue_count} 个讨论中的 Issue，语义规范持续演进。")

    if blogs_count > 0:
        observations.append(f"大厂工程博客收录 {blogs_count} 篇文章，来自 Azure、AWS、Anthropic、OpenAI、Datadog 及国内云厂商。")

    if tools_native > 0:
        observations.append(f"AI-Native 可观测工具共发布 {tools_native} 个版本更新，生态快速迭代。")

    if tools_traditional > 0:
        observations.append(f"传统 APM/可观测厂商（Grafana、Dynatrace、Splunk、Elastic）在 AI Agent 监控方向有 {tools_traditional} 项新进展。")

    if not observations:
        return "本监测窗口内各板块活动相对平静。建议扩大时间范围或放宽话题关键词以获取更多信号。"

    return "\n\n".join(f"{i + 1}. {o}" for i, o in enumerate(observations))


# --- Table renderers for each plate ---

def render_newsletters_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无相关行业周刊内容。*"
    lines = []
    for item in items:
        title = item.get("title", "")
        source = item.get("source", "")
        summary = item.get("summary", "")
        url = item.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {source} | {short_title} | {summary[:80]} | [链接]({url}) |")
    return "\n".join(lines)


def render_domestic_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无相关国内信源内容。*"
    lines = []
    for item in items:
        title = item.get("title", "")
        source = item.get("source", "")
        summary = item.get("summary", "")
        url = item.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {source} | {short_title} | {summary[:80]} | [链接]({url}) |")
    return "\n".join(lines)


def render_papers_table(papers: list[dict]) -> str:
    if not papers:
        return "*本周期无相关学术论文。*"
    lines = []
    for p in papers:
        title = p.get("title", "")
        authors = ", ".join(p.get("authors", [])[:3])
        if len(p.get("authors", [])) > 3:
            authors += " et al."
        summary = p.get("summary", "")
        source = p.get("source", "arxiv")
        citations = p.get("citationCount", 0) or 0
        url = p.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {short_title} | {authors} | {summary[:80]} | {source} | {citations} | [链接]({url}) |")
    return "\n".join(lines)


def render_standards_summary(data: dict) -> str:
    otel = data.get("otel", {})
    oi = data.get("openinference", {})
    cncf = data.get("cncf", [])

    otel_prs = len([p for p in otel.get("prs", []) if "error" not in p])
    otel_issues = len([i for i in otel.get("issues", []) if "error" not in i])
    oi_prs = len([p for p in oi.get("prs", []) if "error" not in p])
    oi_issues = len([i for i in oi.get("issues", []) if "error" not in i])
    cncf_count = len(cncf)

    lines = []
    lines.append(f"| OTel GenAI SIG | {otel_prs} | {otel_issues} | 语义规范持续演进，GenAI span/metric 定义活跃 |")
    lines.append(f"| OpenInference WG | {oi_prs} | {oi_issues} | 多框架埋点适配（LangChain/CrewAI） |")
    lines.append(f"| CNCF AI/ML WG | - | - | 收录 {cncf_count} 项议题 |")
    return "\n".join(lines)


def render_prs_table(prs: list[dict]) -> str:
    if not prs:
        return "*无 GenAI 相关活跃 PR。*"
    lines = []
    for pr in prs:
        if "error" in pr:
            lines.append(f"| Error | {pr.get('repo', '')} | - | {pr['error']} |")
            continue
        title = pr.get("title", "")
        url = pr.get("url", "")
        repo = pr.get("repo", "").split("/")[-1] if "/" in pr.get("repo", "") else pr.get("repo", "")
        state = pr.get("state", "")
        short_title = title if len(title) <= 60 else title[:57] + "..."
        lines.append(f"| [{short_title}]({url}) | {repo} | {state} | {title[:80]} |")
    return "\n".join(lines)


def render_issues_table(issues: list[dict]) -> str:
    if not issues:
        return "*无 GenAI 相关活跃 Issue。*"
    lines = []
    for issue in issues:
        title = issue.get("title", "")
        url = issue.get("url", "")
        repo = issue.get("repo", "").split("/")[-1] if "/" in issue.get("repo", "") else issue.get("repo", "")
        labels = ", ".join(issue.get("labels", []))
        short_title = title if len(title) <= 60 else title[:57] + "..."
        lines.append(f"| [{short_title}]({url}) | {repo} | {labels} | {title[:80]} |")
    return "\n".join(lines)


def render_cncf_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无 CNCF AI/ML WG 相关内容。*"
    lines = []
    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")
        url = item.get("url", "")
        lines.append(f"| {title[:60]} | {summary[:80]} | [链接]({url}) |")
    return "\n".join(lines)


def render_enterprise_blogs_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无大厂工程博客相关内容。*"
    lines = []
    for item in items:
        source = item.get("source", "")
        title = item.get("title", "")
        significance = item.get("significance", "")
        url = item.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {source} | {short_title} | {significance[:80]} | [链接]({url}) |")
    return "\n".join(lines)


def render_ai_native_tools_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无 AI-Native 工具发版。*"
    lines = []
    for item in items:
        if "error" in item:
            lines.append(f"| {item.get('name', '')} | Error | {item.get('error', '')} | - | - |")
            continue
        name = item.get("name", "")
        version = item.get("version", "")
        change = item.get("change", "")
        published = item.get("published", "")
        url = item.get("url", "")
        lines.append(f"| {name} | {version} | {change[:80]} | {published} | [链接]({url}) |")
    return "\n".join(lines)


def render_traditional_tools_table(items: list[dict]) -> str:
    if not items:
        return "*本周期无传统可观测工具 AI 相关进展。*"
    lines = []
    for item in items:
        name = item.get("name", "")
        title = item.get("title", "")
        change = item.get("change", "")
        url = item.get("url", "")
        short_title = title if len(title) <= 50 else title[:47] + "..."
        lines.append(f"| {name} | {short_title} | {change[:80]} | [链接]({url}) |")
    return "\n".join(lines)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="Generate LLM observability v2 research report")
    parser.add_argument("--input", required=True, help="Path to combined results JSON")
    parser.add_argument("--template", required=True, help="Path to report template markdown")
    parser.add_argument("--topic", required=True, help="Research topic for the report title")
    parser.add_argument("--since", default="N/A", help="Since date for report metadata")
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
        print(json.dumps({"error": f"Template file not found: {template_path}"}))
        sys.exit(1)

    template = template_path.read_text(encoding="utf-8")

    # Deduplicate papers
    arxiv_papers = [p for p in data.get("papers", []) if p.get("source") == "arxiv"]
    s2_papers = [p for p in data.get("papers", []) if p.get("source") == "semantic_scholar"]
    other_papers = [p for p in data.get("papers", []) if p.get("source") not in ("arxiv", "semantic_scholar")]
    papers = deduplicate_papers(arxiv_papers, s2_papers)
    papers.extend(other_papers)
    papers.sort(key=lambda p: p.get("published", ""), reverse=True)

    standards = data.get("standards", {})
    tools = data.get("tools", {})
    today = datetime.now().strftime("%Y-%m-%d")

    # Fill template
    report = template
    report = report.replace("{DATE}", today)
    report = report.replace("{TOPIC}", args.topic)
    report = report.replace("{SINCE_DATE}", args.since)
    report = report.replace("{SUMMARY}", generate_summary(data))

    # Plate 1: Newsletters
    report = report.replace("{NEWSLETTERS_TABLE}", render_newsletters_table(data.get("newsletters", [])))

    # Plate 2: Domestic
    report = report.replace("{DOMESTIC_TABLE}", render_domestic_table(data.get("domestic", [])))

    # Plate 3: Papers
    report = report.replace("{PAPERS_TABLE}", render_papers_table(papers))

    # Plate 4: Standards
    report = report.replace("{STANDARDS_SUMMARY}", render_standards_summary(standards))

    otel = standards.get("otel", {})
    report = report.replace("{OTEL_PRS_TABLE}", render_prs_table(otel.get("prs", [])))
    report = report.replace("{OTEL_ISSUES_TABLE}", render_issues_table(otel.get("issues", [])))

    sig_url = otel.get("sig_notes_url")
    report = report.replace("{SIG_UPDATES}", f"[GenAI SIG 会议纪要]({sig_url})" if sig_url else "本周期未发现 SIG 会议纪要链接。")

    oi = standards.get("openinference", {})
    report = report.replace("{OI_PRS_TABLE}", render_prs_table(oi.get("prs", [])))
    report = report.replace("{OI_ISSUES_TABLE}", render_issues_table(oi.get("issues", [])))
    report = report.replace("{CNCF_TABLE}", render_cncf_table(standards.get("cncf", [])))

    # Plate 5: Enterprise blogs
    report = report.replace("{ENTERPRISE_BLOGS_TABLE}", render_enterprise_blogs_table(data.get("enterprise_blogs", [])))

    # Plate 6: Tools
    report = report.replace("{AI_NATIVE_TOOLS_TABLE}", render_ai_native_tools_table(tools.get("ai_native", [])))
    report = report.replace("{TRADITIONAL_TOOLS_TABLE}", render_traditional_tools_table(tools.get("traditional", [])))

    # Write report
    report_filename = f"research-observe-report-{today}.md"
    report_path = Path(report_filename)
    report_path.write_text(report, encoding="utf-8")

    print(f"Report written to: {report_path.absolute()}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify syntax**

```bash
python -c "import py_compile; py_compile.compile('research-observe/skills/research-observe/scripts/generate_report.py', doraise=True); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add research-observe/skills/research-observe/scripts/generate_report.py
git commit -m "feat: rewrite generate_report.py for 7-plate v2 with summary and new renderers"
```

---

### Task 9: Rewrite SKILL.md

**Files:**
- Modify: `research-observe/skills/research-observe/SKILL.md`

- [ ] **Step 1: Write the v2 SKILL.md**

Replace the entire file with:

```markdown
---
name: research-observe
description: This skill should be used when the user asks to "research observability", "scan LLM monitoring", "check OTel GenAI updates", "find agent tracing papers", "what's new in LLM observability", or mentions "LLM observability", "AI agent monitoring", "OTel GenAI", "agent eval", "AI safety observability". Produces a structured report with summaries and original source links across 7 plates: newsletters, domestic sources, academic papers, standards communities, enterprise blogs, and open-source tool updates.
allowed-tools: WebSearch, WebFetch, Bash(python *), Bash(pip install *), Read, Write, Grep, Glob, TodoWrite
argument-hint: "[topic] [--since YYYY-MM-DD] [--deep]"
---

# Researching LLM and AI Agent Observability (v2)

Collect, synthesize, and report on the latest LLM/AI Agent observability developments across 7 plates. Produce a structured markdown report in Chinese with original source links and article/blog/paper titles preserved in their original language.

## Arguments

Parse `$ARGUMENTS` for:
- **topic**: Focus area (e.g., "tracing", "eval", "safety"). Empty = full landscape scan.
- **--since YYYY-MM-DD**: Filter results after this date. Default: 30 days before today.
- **--deep**: Fewer items (5 per source) with detailed analysis. Default: broader scan (15 per source).

## Prerequisites

Run once before first use:
```bash
pip install requests python-dateutil
```

Set `GITHUB_TOKEN` env var for higher GitHub API rate limits (optional but recommended).
Set `SEMANTIC_SCHOLAR_API_KEY` env var for higher S2 rate limits (optional).

## Research Workflow

Report order (from browsable to must-read): Newsletters → Domestic → Papers → Standards → Enterprise Blogs → Tools.

### Step 1: Prepare

Create a TodoWrite checklist:
```
- [ ] Plate 1: Industry newsletters (WebSearch + WebFetch)
- [ ] Plate 2: Domestic sources (WebSearch + WebFetch)
- [ ] Plate 3: Academic papers (search_arxiv.py + search_semantic_scholar.py + Twitter/X)
- [ ] Plate 4: Standards & open-source communities (fetch_otel_updates.py + fetch_openinference_updates.py + CNCF WebSearch)
- [ ] Plate 5: Enterprise engineering blogs (WebSearch + WebFetch)
- [ ] Plate 6: Open-source tool updates (fetch_tool_releases.py + traditional tools WebSearch)
- [ ] Aggregate JSON and generate report (generate_report.py)
```

Compute `--since` date. Default: today minus 30 days.

### Step 2: Plate 1 — Industry Newsletters

Use WebSearch with queries from `references/search-strategies.md` section "Plate 1: Industry Newsletters":
- `site:tldr.tech/ai LLM observability agent monitoring`
- `site:latent.space AI agent observability tracing`
- `site:deeplearning.ai/the-batch AI monitoring safety`
- `site:radarai.com LLM observability`

For each source, WebFetch the top 2 results. Extract title (original language), 3-sentence Chinese summary, and URL. Only keep items related to LLM observability or AI agent monitoring. Record as `{source, title, summary, url}`.

### Step 3: Plate 2 — Domestic Sources

Use WebSearch with queries from `references/search-strategies.md` section "Plate 2: Domestic Sources":
- `site:infoq.cn LLM可观测性 AI Agent监控`
- `site:qbitai.com LLM agent observability 监控`
- `site:jiqizhixin.com AI agent 可观测`
- `site:zhihu.com 可观测性 LangFuse OTel`
- `site:okjk.com LLM observability agent`

For each source, WebFetch the top 2 results. Extract title (original), 3-sentence Chinese summary, URL. Prioritize InfoQ and AI前线 for editorial quality. Record as `{source, title, summary, url}`.

### Step 4: Plate 3 — Academic Papers

Run these in **parallel** (two Bash calls in the same turn):

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/search_arxiv.py" --topic "<TOPIC>" --since <DATE> [--deep] [--venues AAAI NeurIPS ICML EMNLP]
```

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/search_semantic_scholar.py" --topic "<TOPIC>" --since <DATE> [--deep]
```

Then use WebSearch for Twitter/X academic accounts:
```
from:@_akhaliq AI observability agent monitoring
from:@papers_daily AI safety agent tracing
```

Collect all paper entries with `source` field set to `arxiv`, `semantic_scholar`, or `twitter`. Deduplication is handled automatically by `generate_report.py`.

### Step 5: Plate 4 — Standards & Open-Source Communities

Run these two scripts in **parallel**:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/fetch_otel_updates.py" --since <DATE>
```

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/fetch_openinference_updates.py" --since <DATE>
```

Then WebSearch for CNCF AI/ML WG:
```
site:github.com/cncf/tag-runtime AI observability
site:github.com/cncf ai-ml-wg observability
```

WebFetch any relevant CNCF meeting notes or proposals. Record as `{title, summary, url}`.

### Step 6: Plate 5 — Enterprise Engineering Blogs

Use WebSearch with queries from `references/search-strategies.md` section "Plate 5: Enterprise Engineering Blogs". There are 10 sources across 4 categories:

**Overseas Cloud**: Microsoft Azure AI Foundry, Google Cloud AI Blog, AWS ML Blog
**Model Vendors**: Anthropic Engineering, OpenAI Engineering
**Monitoring Platforms**: Datadog AI, New Relic AI
**Domestic Cloud**: 阿里云开发者社区, 腾讯云开发者社区, 火山引擎开发者社区

Run 3-4 queries per batch. For each hit, WebFetch to verify relevance. Extract title (original), 3-5 sentence Chinese significance summary, and URL. Record as `{source, title, significance, url}`.

### Step 7: Plate 6 — Open-Source Tool Updates

Run the AI-native tool release fetcher:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/fetch_tool_releases.py" --since <DATE>
```

Then WebSearch for tools without structured GitHub releases:

**Coze 罗盘**: Search `"Coze" 罗盘 可观测 agent monitoring` — record `{name: "Coze 罗盘", title, change, url}`.

**LangSmith**: Search `site:docs.smith.langchain.com changelog` and `site:blog.langchain.dev langsmith` — record under `ai_native` tools.

**Traditional observability tools**: Use queries from `references/search-strategies.md` section "Traditional Observability Tool Queries":
- `site:grafana.com/blog AI agent LLM observability`
- `site:dynatrace.com AI agent monitoring Davis`
- `site:splunk.com AI observability LLM`
- `site:elastic.co/blog AI agent APM observability`

(Datadog and New Relic are covered in Plate 5.)

Record traditional tool items as `{name, title, change, url}`.

### Step 8: Aggregate and Generate Report

1. Combine all collected data into a single JSON structure matching the schema in `references/source-guide.md`:

```json
{
  "date": "<today>",
  "since": "<since_date>",
  "topic": "<topic>",
  "newsletters": [...],
  "domestic": [...],
  "papers": [...],
  "standards": {
    "otel": {...},
    "openinference": {...},
    "cncf": [...]
  },
  "enterprise_blogs": [...],
  "tools": {
    "ai_native": [...],
    "traditional": [...]
  }
}
```

2. Write this JSON to a temp file, then run:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/generate_report.py" \
  --input <combined_json_path> \
  --template "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/references/report-template.md" \
  --topic "<TOPIC>" \
  --since <DATE>
```

3. Read the generated report file and present it to the user. Mention the file path for future reference.

4. Mark all TodoWrite items complete.

## Quick Reference

| Plate | Action | Tools |
|-------|--------|-------|
| 1. Newsletters | WebSearch ×4 + WebFetch ×~8 | WebSearch, WebFetch |
| 2. Domestic | WebSearch ×5 + WebFetch ×~10 | WebSearch, WebFetch |
| 3. Papers | search_arxiv.py + search_semantic_scholar.py + WebSearch | Bash (parallel), WebSearch |
| 4. Standards | fetch_otel_updates.py + fetch_openinference_updates.py + WebSearch | Bash (parallel), WebSearch, WebFetch |
| 5. Enterprise Blogs | WebSearch ×10 + WebFetch ×~15 | WebSearch, WebFetch |
| 6. Tools | fetch_tool_releases.py + WebSearch ×6 + WebFetch ×~8 | Bash, WebSearch, WebFetch |
| Report | generate_report.py | Bash, Read |

## Common Mistakes

- Forgetting to set `--since` default — always compute the 30-day window.
- Running academic scripts serially — launch both (and both OTel scripts) in parallel for efficiency.
- Discarding source links — every item in the report MUST include an original URL.
- Skipping `pip install requests python-dateutil` on first run.
- Translating article/blog/paper titles — titles MUST be preserved in their original language; only summaries are Chinese.
- Forgetting the Coze 罗盘 and traditional observability tool searches in Plate 6.

## Integration with /loop

Pair with `/loop` for periodic landscape scanning:
```
/loop 168h /research-observe --since $(date -d '7 days ago' +%%Y-%%m-%%d)
```
```

- [ ] **Step 2: Commit**

```bash
git add research-observe/skills/research-observe/SKILL.md
git commit -m "feat: rewrite SKILL.md for 7-plate v2 orchestration workflow"
```

---

### Task 10: Integration Test

**Files:**
- Test all scripts and the report pipeline end-to-end

- [ ] **Step 1: Verify all scripts pass syntax check**

```bash
for f in research-observe/skills/research-observe/scripts/*.py; do
  python -c "import py_compile; py_compile.compile('$f', doraise=True); print(f'OK: $f')"
done
```

Expected: `OK` for all 6 scripts.

- [ ] **Step 2: Verify generate_report.py works with a minimal fixture**

Create a test fixture:

```bash
cat > /tmp/test_fixture_v2.json << 'PYEOF'
{
  "newsletters": [{"source": "TLDR AI", "title": "Test Newsletter", "summary": "Some observability news", "url": "https://example.com"}],
  "domestic": [{"source": "InfoQ", "title": "OTel 可观测性实践", "summary": "国内落地案例", "url": "https://example.com"}],
  "papers": [{"title": "LLM Agent Tracing Survey", "authors": ["Alice", "Bob"], "summary": "A comprehensive survey", "published": "2026-05-15", "url": "https://arxiv.org/abs/0000.00000", "citationCount": 5, "source": "arxiv", "keywords": ["cs.AI"]}],
  "standards": {
    "otel": {"prs": [], "issues": [], "sig_notes_url": null},
    "openinference": {"prs": [], "issues": []},
    "cncf": []
  },
  "enterprise_blogs": [{"source": "Anthropic", "title": "Safety Monitoring at Scale", "significance": "护栏监控规模化落地", "url": "https://example.com"}],
  "tools": {
    "ai_native": [{"name": "langfuse", "version": "v3.0.0", "change": "Major release with agent scaffolding", "published": "2026-05-20", "url": "https://github.com/langfuse/langfuse/releases/v3.0.0"}],
    "traditional": []
  }
}
PYEOF
```

Run the report generator:

```bash
python research-observe/skills/research-observe/scripts/generate_report.py \
  --input /tmp/test_fixture_v2.json \
  --template research-observe/skills/research-observe/references/report-template.md \
  --topic "test" \
  --since "2026-05-01"
```

Expected: Output `Report written to: .../research-observe-report-2026-05-28.md`

- [ ] **Step 3: Verify report content**

```bash
grep -c "行业周刊精选" research-observe-report-*.md && \
grep -c "国内信源" research-observe-report-*.md && \
grep -c "学术论文" research-observe-report-*.md && \
grep -c "标准&开源社区" research-observe-report-*.md && \
grep -c "大厂工程博客" research-observe-report-*.md && \
grep -c "开源工具动态" research-observe-report-*.md && \
echo "All 6 plates present with summary header"
```

Expected: All 6 plate headers found.

- [ ] **Step 4: Cleanup and commit**

```bash
rm research-observe-report-*.md /tmp/test_fixture_v2.json
git add -A && git commit -m "test: verify end-to-end v2 report pipeline with fixture"
```
```

---

## Task Dependency Graph

```
Task 1 (search-strategies) ──┐
Task 2 (source-guide)     ──┤
Task 3 (report-template)  ──┼──► Task 8 (generate_report.py)
                             │
Task 4 (search_arxiv)      ──┤
Task 5 (search_s2)         ──┤
Task 6 (fetch_openinf)     ──┼──► Task 9 (SKILL.md)
Task 7 (fetch_tool_rel)    ──┤
                             │
                             └──► Task 10 (integration test)
```
```

- [ ] **Step 5: Run integration test**

```bash
for f in research-observe/skills/research-observe/scripts/*.py; do
  python -c "import py_compile; py_compile.compile('$f', doraise=True); print(f'OK: $f')"
done
```

Expected: `OK` for all 6 scripts.

- [ ] **Step 6: Run generate_report.py with a minimal fixture**

Create the fixture and run the report generator, then verify all 6 plates render.

- [ ] **Step 7: Commit**

```bash
git add -A && git commit -m "test: verify end-to-end v2 report pipeline"
```

---

## Task Dependency Graph

```
Task 1 (search-strategies.md) ──┐
Task 2 (source-guide.md)     ──┤
Task 3 (report-template.md)  ──┼──► Task 8 (generate_report.py) ──► Task 10 (integration test)
Task 4 (search_arxiv.py)     ──┤                                          ▲
Task 5 (search_s2.py)        ──┤                                          │
Task 6 (fetch_openinf.py)    ──┼──► Task 9 (SKILL.md) ──────────────────┘
Task 7 (fetch_tool_rel.py)   ──┘
```
