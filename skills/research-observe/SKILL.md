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

### Error Resilience

Each data source fails independently don't halt the workflow. If a script outputs `{"error": "..."}` entries, exclude them from the final report. If WebSearch returns no results or WebFetch fails for a source, skip it and continue. If an entire plate yields no usable data, render it as "本期无更新" in Chinese. Never retry a failed source more than once.

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
/loop 168h /good-skills:research-observe --since $(date -d '7 days ago' +%%Y-%%m-%%d)
```
