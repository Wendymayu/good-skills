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
