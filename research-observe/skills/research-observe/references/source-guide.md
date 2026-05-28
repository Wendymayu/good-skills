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
