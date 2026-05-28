# Source Guide

API endpoints, rate limits, and monitored repositories.

## GitHub Repositories (Monitored by fetch_otel_updates.py)

| Repository | Focus |
|-----------|-------|
| `open-telemetry/semantic-conventions` | GenAI span/metric/attribute definitions |
| `open-telemetry/opentelemetry-python` | Python SDK + instrumentations (bedrock, openai, etc.) |
| `open-telemetry/opentelemetry-js` | JS SDK + instrumentations |
| `open-telemetry/opentelemetry-go` | Go SDK + instrumentations |
| `open-telemetry/community` | GenAI SIG meeting notes, governance, OTEPs |

## GenAI SIG Meeting Notes

Location in community repo: `sig/gen-ai/meetings/` (path may vary).

Fallback: Search issues with label `gen-ai` in the community repo, or check the SIG's README for a meeting notes link.

## arXiv API

- Endpoint: `http://export.arxiv.org/api/query`
- Rate limit: 1 request per 3 seconds (polite policy)
- Response format: Atom XML
- Pagination: `start` and `max_results` parameters
- No authentication required

## Semantic Scholar API

- Endpoint: `https://api.semanticscholar.org/graph/v1/paper/search`
- Rate limit (unauthenticated): ~1 request/second (100 requests/5 minutes)
- Rate limit (authenticated): ~10 requests/second
- Set env var `SEMANTIC_SCHOLAR_API_KEY` for higher limits
- Response format: JSON
- Fields: `title,authors,abstract,url,publicationDate,citationCount`

## GitHub API

- Endpoint: `https://api.github.com`
- Rate limit (unauthenticated): 60 requests/hour
- Rate limit (authenticated): 5,000 requests/hour
- Set env var `GITHUB_TOKEN` for higher limits
- Response format: JSON
- Key endpoints used:
  - `GET /repos/{owner}/{repo}/pulls` — open PRs
  - `GET /repos/{owner}/{repo}/issues` — open issues
  - `GET /repos/{owner}/{repo}/contents/{path}` — file content (SIG notes)

## Combined Results JSON Schema

The `generate_report.py` script expects this schema:

```json
{
  "otel": {
    "prs": [
      {
        "repo": "string",
        "number": "int",
        "title": "string",
        "state": "string",
        "updated_at": "ISO 8601",
        "url": "string",
        "labels": ["string"]
      }
    ],
    "issues": [
      {
        "repo": "string",
        "number": "int",
        "title": "string",
        "state": "string",
        "updated_at": "ISO 8601",
        "url": "string",
        "labels": ["string"]
      }
    ],
    "sig_notes_url": "string or null"
  },
  "arxiv": [
    {
      "title": "string",
      "authors": ["string"],
      "summary": "string",
      "keywords": ["string"],
      "published": "YYYY-MM-DD",
      "url": "string"
    }
  ],
  "semantic_scholar": [
    {
      "title": "string",
      "authors": ["string"],
      "summary": "string",
      "keywords": ["string"],
      "published": "YYYY-MM-DD",
      "url": "string",
      "citationCount": "int"
    }
  ],
  "tools": [
    {
      "name": "string",
      "change": "string",
      "stars": "int or null",
      "url": "string"
    }
  ],
  "engineering": [
    {
      "title": "string",
      "source": "string",
      "takeaway": "string",
      "url": "string"
    }
  ]
}
```
