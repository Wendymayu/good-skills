# research-observe

A Claude Code skill for researching LLM and AI Agent observability. Collects and synthesizes the latest dynamics across OTel community, academic papers, open-source tooling, and engineering practices into a structured markdown report with original source links.

## Install

```bash
>claude 
>plugin add /path/to/good-skills/research-observe
```

## Usage

```
/research-observe                        # Full landscape scan (last 30 days)
/research-observe tracing                # Focus on agent tracing
/research-observe eval --since 2026-05-01 # Eval topic, since May 1
/research-observe safety --deep          # Detailed analysis on safety
```

### Arguments

| Argument | Description |
|----------|-------------|
| `topic` | Focus area: tracing, eval, safety, cost, architecture, or custom |
| `--since YYYY-MM-DD` | Filter results after this date (default: 30 days ago) |
| `--deep` | Fewer results (5/source) with full abstracts |

### Periodic Scanning

Pair with `/loop` for automated weekly scans:

```
/loop 24h /research-observe --since $(date -d '7 days ago' +%Y-%m-%d)
```

## Info Sources

| Priority | Source | Method |
|----------|--------|--------|
| 1 (highest) | OTel GenAI semantic conventions, SIG activity | `fetch_otel_updates.py` + WebSearch |
| 2 | arXiv papers (cs.AI, cs.CL, cs.SE) | `search_arxiv.py` |
| 2 | Semantic Scholar papers | `search_semantic_scholar.py` |
| 3 | Open-source tools (LangFuse, Phoenix, Helicone, etc.) | WebSearch |
| 3 | Engineering blogs & migration stories | WebSearch + WebFetch |

## Dependencies

```bash
pip install requests python-dateutil
```

Set `GITHUB_TOKEN` env var for higher GitHub API rate limits (optional).
Set `SEMANTIC_SCHOLAR_API_KEY` env var for higher S2 rate limits (optional).
