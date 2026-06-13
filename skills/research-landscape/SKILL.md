---
name: research-landscape
description: Use when the user asks to "research", "scan", "check updates", "what's new in", "latest developments in", or mentions any technology topic they want a landscape scan of. Works with any domain — AI agent evaluation, LLM observability, microservices, Kubernetes security, etc. Produces a structured Chinese report with summaries and original source links across 7 plates.
allowed-tools: WebSearch, WebFetch, Bash(python *), Bash(pip install *), Read, Write, Grep, Glob, TodoWrite
argument-hint: "[topic] [--since YYYY-MM-DD] [--deep]"
---

# Research Landscape Scan

Collect, synthesize, and report on the latest developments in any technology domain. Produce a structured markdown report in Chinese with original source links. Article/blog/paper titles MUST be preserved in their original language; only summaries are Chinese.

## Arguments

Parse `$ARGUMENTS` for:
- **topic**: Any domain the user specifies — Chinese or English (e.g., "可观测", "AI agent evaluation", "微服务治理", "Kubernetes"). You must translate the topic into appropriate search keywords for each plate. Empty = error, ask the user what topic they want.
- **--since YYYY-MM-DD**: Filter results after this date. Default: 30 days before today.
- **--deep**: Fewer items (5 per source) with detailed analysis. Default: broader scan (15 per source).

## Keyword Generation

For each plate, generate search keywords in BOTH Chinese and English based on the user's topic. Use the user's exact words if they match domain terminology; otherwise infer the most relevant academic/industry terms. Example mapping for "可观测": English keywords → "LLM observability", "AI agent tracing", "OTel GenAI"; Chinese keywords → "可观测性", "链路追踪", "Agent监控".

## Prerequisites

Run once before first use:
```bash
pip install requests python-dateutil
```

Set `GITHUB_TOKEN` env var for higher GitHub API rate limits (optional but recommended).
Set `SEMANTIC_SCHOLAR_API_KEY` env var for higher S2 rate limits (optional).

## Research Workflow

MUST follow this exact plate order (from browsable to must-read). Do NOT skip plates. Do NOT reorder plates.

### Step 1: Prepare

Create a TodoWrite checklist:
```
- [ ] Plate 1: Industry newsletters (WebSearch + WebFetch)
- [ ] Plate 2: Domestic sources (WebSearch + WebFetch)
- [ ] Plate 3: Academic papers (search_arxiv.py + search_semantic_scholar.py + WebSearch)
- [ ] Plate 4: Standards & open-source communities (WebSearch + WebFetch)
- [ ] Plate 5: Enterprise engineering blogs (WebSearch + WebFetch)
- [ ] Plate 6: Open-source tool updates (search_arxiv.py for tool papers + WebSearch + WebFetch)
- [ ] Aggregate JSON and generate report (generate_report.py)
```

Compute `--since` date. Default: today minus 30 days.
Generate bilingual search keywords for the topic.

### Step 2: Plate 1 — Industry Newsletters

Use WebSearch with topic-adapted queries on these 4 newsletter archive sites:
- `site:tldr.tech/ai <topic keywords>`
- `site:latent.space <topic keywords>`
- `site:deeplearning.ai/the-batch <topic keywords>`
- `site:radarai.com <topic keywords>`

For each source, WebFetch the top 2 results. Extract title (original language), 3-sentence Chinese summary, and URL. Only keep items related to the user's topic. Record as `{source, title, summary, url}`.

### Step 3: Plate 2 — Domestic Sources

Use WebSearch with topic-adapted queries on these 5 domestic sites:
- `site:infoq.cn <Chinese topic keywords>`
- `site:qbitai.com <topic keywords>`
- `site:jiqizhixin.com <topic keywords>`
- `site:zhihu.com <Chinese topic keywords>`
- `site:okjk.com <topic keywords>`

For each source, WebFetch the top 2 results. Extract title (original), 3-sentence Chinese summary, URL. Prioritize InfoQ and AI前线 for editorial quality. Record as `{source, title, summary, url}`.

### Step 4: Plate 3 — Academic Papers

Run these in **parallel** (two Bash calls in the same turn):

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-landscape/scripts/search_arxiv.py" --topic "<TOPIC>" --since <DATE> [--deep]
```

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-landscape/scripts/search_semantic_scholar.py" --topic "<TOPIC>" --since <DATE> [--deep]
```

Then use WebSearch for Twitter/X academic accounts:
```
from:@_akhaliq <topic keywords>
from:@papers_daily <topic keywords>
```

Collect all paper entries with `source` field set to `arxiv`, `semantic_scholar`, or `twitter`. Deduplication is handled by `generate_report.py`.

### Step 5: Plate 4 — Standards & Open-Source Communities

WebSearch for standards/community bodies relevant to the topic. For general tech topics, search:
- `site:github.com/cncf <topic keywords>`
- `site:github.com/open-telemetry <topic keywords>` (if observability-related)
- `<topic> standards community SIG working group`

For each relevant community found, WebFetch meeting notes, proposals, or spec documents. Record PRs/issues as `{repo, number, title, state, url}` and community items as `{title, summary, url}`.

If the topic has specific well-known community repos (e.g., OTel for observability), you may run fetch scripts from `references/source-guide.md` for structured data.

### Step 6: Plate 5 — Enterprise Engineering Blogs

Use WebSearch on these 10 blog sources with topic-adapted queries:

**Overseas Cloud**: `site:techcommunity.microsoft.com <topic>`, `site:cloud.google.com/blog <topic>`, `site:aws.amazon.com/blogs/machine-learning <topic>`
**Model Vendors**: `site:anthropic.com <topic>`, `site:openai.com <topic>`
**Monitoring Platforms**: `site:datadoghq.com/blog <topic>`, `site:newrelic.com/blog <topic>`
**Domestic Cloud**: `site:developer.aliyun.com <Chinese topic>`, `site:cloud.tencent.com/developer <Chinese topic>`, `site:volcengine.com <Chinese topic>`

Run 3-4 queries per batch. For each hit, WebFetch to verify relevance. Extract title (original), 3-5 sentence Chinese significance summary, and URL. Record as `{source, title, significance, url}`.

### Step 7: Plate 6 — Open-Source Tool Updates

WebSearch for open-source tools relevant to the topic:
- Search `<topic> open source tools GitHub releases 2025 2026`
- For each tool found, search `site:github.com/<org>/<repo> releases`

If the topic has well-known tool repos (e.g., LangFuse for observability), you may run `fetch_tool_releases.py` with repos from `references/source-guide.md`.

WebSearch for traditional/established tools' progress in this topic area.

Record as `{name, version, change, published, url, repo}` for release data, or `{name, title, change, url}` for general tool updates.

### Error Resilience

Each data source fails independently — do NOT halt the workflow. If a script outputs `{"error": "..."}` entries, exclude them from the final report. If WebSearch returns no results or WebFetch fails for a source, skip it and continue. If an entire plate yields no usable data, render it as "本期无更新" in Chinese. Never retry a failed source more than once.

### Step 8: Aggregate and Generate Report

1. Combine all collected data into a single JSON structure:

```json
{
  "date": "<today>",
  "since": "<since_date>",
  "topic": "<topic>",
  "newsletters": [...],
  "domestic": [...],
  "papers": [...],
  "standards": [...],
  "enterprise_blogs": [...],
  "tools": {
    "releases": [...],
    "general": [...]
  }
}
```

2. Write this JSON to a temp file, then run:

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-landscape/scripts/generate_report.py" \
  --input <combined_json_path> \
  --template "${CLAUDE_PLUGIN_ROOT}/skills/research-landscape/references/report-template.md" \
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
| 4. Standards | WebSearch + WebFetch (topic-adapted) | WebSearch, WebFetch |
| 5. Enterprise Blogs | WebSearch ×10 + WebFetch ×~15 | WebSearch, WebFetch |
| 6. Tools | WebSearch + WebFetch (topic-adapted) | WebSearch, WebFetch |
| Report | generate_report.py | Bash, Read |

## Common Mistakes

- Skipping plates — ALL 7 plates MUST be attempted, even if some yield no data.
- Translating titles — titles MUST be preserved in their original language; only summaries are Chinese.
- Forgetting `--since` default — always compute the 30-day window.
- Running academic scripts serially — launch both in parallel for efficiency.
- Discarding source links — every item MUST include an original URL.
- Skipping domestic sources (Plate 2) — this plate captures Chinese perspectives and must not be omitted.
- Using only English keywords — always generate BOTH Chinese and English keywords for comprehensive coverage.
- Not adapting Plate 4/6 to the topic — standards communities and tool repos vary by domain; do NOT hardcode observability-specific repos for a different topic.

## Integration with /loop

Pair with `/loop` for periodic landscape scanning:
```
/loop 168h /good-skills:research-landscape <topic> --since $(date -d '7 days ago' +%%Y-%%m-%%d)
```
