---
name: research-observe
description: This skill should be used when the user asks to "research observability", "scan LLM monitoring", "check OTel GenAI updates", "find agent tracing papers", "what's new in LLM observability", or mentions "LLM observability", "AI agent monitoring", "OTel GenAI", "agent eval", "AI safety observability". Produces a structured report with summaries and original source links.
allowed-tools: WebSearch, WebFetch, Bash(python *), Bash(pip install *), Read, Write, Grep, Glob, TodoWrite
argument-hint: "[topic] [--since YYYY-MM-DD] [--deep]"
---

# Researching LLM and AI Agent Observability

Collect, synthesize, and report on the latest dynamics in the LLM/AI Agent observability domain. Produce a structured markdown report preserving all original source links.

Priority order: **(1) OTel community > (2) Academic research > (3) Engineering practices**.

## Arguments

Parse `$ARGUMENTS` for:
- **topic**: Focus area (e.g., "tracing", "eval", "safety"). Empty = full landscape scan.
- **--since YYYY-MM-DD**: Filter results after this date. Default: 30 days before today.
- **--deep**: Fewer items (5 per source) with detailed analysis per item. Default: broader scan (15 per source).

## Prerequisites

Run once before first use:
```bash
pip install requests python-dateutil
```

## Research Workflow

### Step 1: Prepare

Create a TodoWrite checklist:
```
- [ ] OTel community dynamics
- [ ] Academic papers (arXiv + Semantic Scholar)
- [ ] Open-source tooling updates
- [ ] Engineering practices and blog posts
- [ ] Synthesize and generate report
```

Compute the `--since` date. If not provided by the user, calculate today minus 30 days.

Determine search topic. If not provided, use a broad set of terms from `references/search-strategies.md`.

### Step 2: OTel Community (Highest Priority)

1. Run the OTel fetcher:
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/fetch_otel_updates.py" --since <DATE>
```
Capture JSON output. This scans 5 open-telemetry GitHub repos for GenAI-related PRs, issues, and SIG meeting notes.

2. Search the web for recent OTel GenAI SIG activity using queries from `references/search-strategies.md` section "OTel Queries".

3. If any SIG meeting notes URL is discovered, use WebFetch to extract key decisions and action items.

### Step 3: Academic Papers

Run both search scripts **in parallel** (two separate Bash calls in the same turn):

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/search_arxiv.py" --topic "<TOPIC>" --since <DATE> [--deep]
```

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/search_semantic_scholar.py" --topic "<TOPIC>" --since <DATE> [--deep]
```

Each outputs a JSON array of paper entries. Save each output to a temp file.

If `--deep` is set, each returns up to 5 results with full abstracts. Otherwise up to 15 with one-liner summaries.

### Step 4: Open-Source Tooling Updates

Use WebSearch for each tool category from `references/search-strategies.md` section "Tool Queries". Run 2-3 queries per turn to avoid overwhelming the tool.

For each result, record: project name, notable change or release, star count if visible, original link.

### Step 5: Engineering Practices and Blog Posts

1. Use WebSearch with queries from `references/search-strategies.md` section "Engineering Queries".

2. For the top 2-3 results per query, use WebFetch to verify relevance and extract key takeaways.

3. Record: article title, source (company/blog), key takeaway, original link.

### Step 6: Synthesize and Generate Report

1. Read all collected JSON outputs and WebSearch/WebFetch notes.

2. Build a combined JSON structure matching the schema expected by `generate_report.py` (see `references/source-guide.md`).

3. Write the combined JSON to a temp file, then run:
```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/scripts/generate_report.py" \
  --input combined_results.json \
  --template "${CLAUDE_PLUGIN_ROOT}/skills/research-observe/references/report-template.md" \
  --topic "<TOPIC>"
```

4. Read the generated report file and present it to the user. Mention the file path for future reference.

5. Mark the final TodoWrite item complete.

## Quick Reference

| Phase | Action | Tool |
|-------|--------|------|
| OTel Community | `fetch_otel_updates.py` + WebSearch | Bash, WebSearch, WebFetch |
| Academic Papers | `search_arxiv.py` + `search_semantic_scholar.py` | Bash (parallel) |
| Open-Source Tools | WebSearch per tool | WebSearch |
| Engineering Blogs | WebSearch + WebFetch top results | WebSearch, WebFetch |
| Report | `generate_report.py` | Bash, Read |

## Common Mistakes

- Skipping OTel community phase — this is the highest-priority source; always run it first.
- Running academic search scripts serially — launch both in parallel for efficiency.
- Discarding source links — every item in the report MUST include an original URL.
- Forgetting `--since` default — always compute the 30-day window if the user does not specify.
- Omitting pip install on first run — scripts depend on `requests` and `python-dateutil`.
- Flooding WebSearch with all tool queries at once — batch into groups of 2-3 per turn.

## Integration with /loop

Pair with `/loop` for periodic landscape scanning:
```
/loop 24h /research-observe --since $(date -d '7 days ago' +%%Y-%%m-%%d)
```
Each invocation is independent; the report is a snapshot, not incremental.

## Additional Resources

### Reference Files

Consult for detailed query templates and API documentation:
- **`references/search-strategies.md`** — Search query templates for WebSearch, arXiv, and Semantic Scholar
- **`references/source-guide.md`** — API endpoints, rate limits, monitored GitHub repos
- **`references/report-template.md`** — Report markdown skeleton with section placeholders
