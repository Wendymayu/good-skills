# Search Strategies

Query templates for each research phase. Scripts use these programmatically; Claude uses them for WebSearch.

## OTel Queries (WebSearch)

```
"OpenTelemetry GenAI semantic conventions" site:github.com
"open-telemetry semantic-conventions" genai PR 2026
"OTel GenAI SIG meeting" notes 2026
site:github.com/open-telemetry/semantic-conventions "gen_ai"
"opentelemetry genai instrumentation" release OR changelog 2026
```

## Academic Queries

### Core Terms

| Domain | Terms |
|--------|-------|
| Observability | "LLM observability", "agent tracing", "AI monitoring", "model observability", "telemetry LLM" |
| Evaluation | "LLM evaluation", "agent evaluation", "benchmark LLM", "LLM-as-judge" |
| Safety | "AI alignment observability", "safety monitoring", "guardrail tracing", "red-team observability" |
| Architecture | "agent trace model", "span model LLM", "trace context propagation agent" |

### Topic Expansions

When the user specifies a topic, expand the core terms:

**tracing**: add "distributed tracing", "span model", "trace context", "W3C trace context agent"

**eval**: add "evaluation framework", "automated eval pipeline", "LLM benchmark suite"

**safety**: add "safety layer monitoring", "constitutional AI observability", "jailbreak detection telemetry"

**cost**: add "token cost attribution", "LLM billing observability", "cost per task tracing"

**architecture**: add "agent DAG trace", "multi-agent observability", "tool call telemetry"

### arXiv Category Filter

Always combine topic terms with: `(cat:cs.AI OR cat:cs.CL OR cat:cs.SE)`

Example full query: `ti:"agent trace" AND (cat:cs.AI OR cat:cs.CL)`

## Tool Queries (WebSearch)

Run one query per tool:

```
"LangFuse" release OR changelog 2026
"Arize Phoenix" LLM observability 2026
"Helicone" update OR feature 2026
"OpenLIT" opentelemetry genai 2026
"Traceloop" opentelemetry LLM 2026
"Lilypad" LLM observability 2026
"Dynatrace AI" observability 2026
"Langfuse" star count github 2026
```

## Engineering Queries (WebSearch)

```
"LLM observability" migration OR "case study" 2026
"AI agent monitoring" production OR retrospective 2026
"LLM cost latency quality" trade-off observability 2026
"opentelemetry LLM" production experience OR lessons 2026
"agent tracing" architecture OR design 2026
```
