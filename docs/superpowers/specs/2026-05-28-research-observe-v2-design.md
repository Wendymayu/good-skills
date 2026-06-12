# research-observe v2: 多源全景观测情报系统

## 概述

将 research-observe 技能从当前的"4 脚本 + WebSearch 泛搜"轻量研究工具升级为覆盖 7 大板块、40+ 信源的**多源定向采集 + 智能聚合**系统。一份全量报告，摘要写在开头，全中文呈现，文章/博客标题保留原文。

## 报告结构

最终报告 `research-observe-report-YYYY-MM-DD.md` 按以下顺序排列（从"可看可不看"到"必须关注"）：

1. **摘要** — 本次扫描的数据总览 + 3-5 条关键趋势（中文，约 300 字）
2. **行业周刊精选** — 快速扫描，知道圈子在聊什么
3. **国内信源** — 国内视角，落地参考
4. **学术论文** — 前沿但落地有距离
5. **标准&开源社区** — 最核心，规范级的决策依据
6. **大厂工程博客** — 实践经验 + 云平台方案，部分可直接借鉴
7. **开源工具动态** — 可直接接入的工具

### 报告生成参数

- 默认采集窗口：过去 30 天
- 支持 `--since YYYY-MM-DD` 灵活指定（周采集/月采集）
- 支持 `--topic` 聚焦特定方向（tracing/eval/safety/architecture/cost）
- 支持 `--deep` 切换深度模式

## 架构设计

```
┌─────────────────────────────────────────────────┐
│                  SKILL.md (编配层)                │
│  解析参数 → 并行采集7大板块 → 聚合JSON → 生成报告   │
└─────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                  ▼
   定向脚本(5个)     WebSearch+WebFetch   RSS/API 抓取
   arXiv/S2/OTe    大厂博客/周刊/国内    工具GitHub Releases
   l/OpenInference/                     / 官方博客
   工具Releases
```

**核心原则**：脚本负责结构化数据（JSON in/out），Claude 负责非结构化源的判断和摘要。

## 各板块详细设计

### 板块一：行业周刊精选

**信源**：TLDR AI、Latent Space、The Batch (deeplearning.ai)、RadarAI Weekly

**采集方式**：
- WebSearch 定向搜索各周刊归档站，筛选过去 30 天内容
- WebFetch 提取标题、核心摘要（3 句以内中文）、URL
- Claude 做二次筛选，只保留与 LLM 可观测性/AI Agent 监控相关内容

**查询模板**（`references/search-strategies.md`）：
- `site:tldr.tech/ai + LLM observability agent monitoring`
- `site:latent.space + AI agent observability tracing`
- `site:deeplearning.ai/the-batch + AI monitoring safety`
- `site:radarai.com + LLM observability`

**输出**：表格 — 来源 | 标题（原文）| 核心要点 | 链接

**采集成本**：WebSearch × 4 + WebFetch × ~8 篇

---

### 板块二：国内信源

**信源**：InfoQ 中文站、量子位、AI 前线、知乎（AI 技术圈）、即刻

**采集方式**：
- 每源定向搜索，30 天内内容
- WebFetch 提取内容，Claude 提取标题（保留原文）、3 句核心中文摘要、URL
- 优先 InfoQ 中文和 AI 前线（有编辑审稿），知乎和即刻做信号筛选

**查询模板**：
- `site:infoq.cn + LLM可观测性 AI Agent监控`
- `site:qbitai.com + LLM agent observability 监控`
- `site:jiqizhixin.com + AI agent 可观测`
- `site:zhihu.com + 可观测性 LangFuse OTel`
- `site:okjk.com + LLM observability agent`

**输出**：表格 — 来源 | 标题（原文）| 核心要点 | 链接

**采集成本**：WebSearch × 5 + WebFetch × ~10 篇

---

### 板块三：学术论文

**信源**：arXiv 预印本、顶会论文（AAAI/NeurIPS/ICML/EMNLP）、Twitter/X 学术号（`@_akhaliq`、`@papers_daily`）

**arXiv 采集**（修改 `search_arxiv.py`）：
- 扩展关键词：`LLM Observability`、`AI Agent Tracing`、`Safety Guardrail`、`Multi-Agent Contamination`、`agent eval`、`data provenance`、`agent monitoring`
- 新增 `--venues` 参数，支持按顶会名称过滤（AAAI/NeurIPS/ICML/EMNLP）
- 默认 30 天窗口

**Semantic Scholar 采集**（`search_semantic_scholar.py`）：
- 同步关键词列表
- 获取 citationCount，与 arXiv 按标题去重（保留高引用版本）

**Twitter/X 学术号**（SKILL.md 指令）：
- WebSearch `from:@_akhaliq OR from:@papers_daily AI observability agent monitoring`
- 提取论文链接和讨论热度，取前 5 条有意义推荐

**输出**：表格 — 标题（原文）| 作者 | 核心发现（中文摘要）| 来源 | 引用数 | 链接

**采集成本**：`search_arxiv.py` × 1 + `search_semantic_scholar.py` × 1 + WebSearch × 1 + WebFetch × ~3

---

### 板块四：标准&开源社区

**信源**：OpenTelemetry GenAI SIG、OpenInference WG (Arize)、CNCF AI/ML WG

**OTel GenAI SIG**（`fetch_otel_updates.py`，无改动）：
- 监控 5 个 open-telemetry 仓库中 GenAI 相关 PR/Issue
- 附带 SIG 会议纪要链接
- 关键词：`genai`、`gen-ai`、`llm`、`ai`、`semantic-convention`、`instrumentation`

**OpenInference WG**（新增 `fetch_openinference_updates.py`）：
- 监控 `openinference` GitHub org 的 spec/semantic-conventions 仓库
- 抓取 GenAI 埋点规范、多框架适配（LangChain/CrewAI）相关 PR/Issue
- 同一套关键词过滤逻辑

**CNCF AI/ML WG**（SKILL.md 指令）：
- WebSearch `site:github.com/cncf/tag-runtime AI observability` / `site:github.com/cncf ai-ml-wg`
- WebFetch 提取会议纪要、白皮书、提案中可观测性相关内容

**输出**：每个子社区独立表格，前置汇总表

**采集成本**：`fetch_otel_updates.py` × 1 + `fetch_openinference_updates.py` × 1（新建）+ WebSearch × 1 + WebFetch × ~3

---

### 板块五：大厂工程博客

**信源**（10 个）：

| 分类 | 信源 |
|------|------|
| 海外云 | Microsoft Azure AI Foundry、Google Cloud AI Blog、AWS ML Blog |
| 模型厂商 | Anthropic Engineering、OpenAI Engineering |
| 监控平台 | Datadog AI、New Relic AI |
| 国内云 | 阿里云开发者社区、腾讯云开发者社区、火山引擎开发者社区 |

**采集方式**：
- 每源一个定向 WebSearch，过去 30 天
- WebFetch 提取标题（保留原文）、正文核心观点（3-5 句中文摘要）、URL

**查询模板**：
- `site:techcommunity.microsoft.com + Azure AI Foundry observability agent`
- `site:anthropic.com + engineering safety monitoring`
- `site:datadoghq.com/blog + AI agent monitoring observability`
- `site:newrelic.com/blog + AI agent LLM observability`
- `site:cloud.google.com/blog + AI ML observability GenAI tracing`
- `site:openai.com + engineering safety monitoring agent observability`
- `site:aws.amazon.com/blogs/machine-learning + LLM agent observability tracing`
- `site:developer.aliyun.com + AI agent 可观测 OTel`
- `site:cloud.tencent.com/developer + LLM agent 监控 可观测性`
- `site:volcengine.com + AI agent 可观测 监控`

**输出**：表格 — 来源 | 标题（原文）| 工程意义（中文摘要）| 链接

**采集成本**：WebSearch × 10 + WebFetch × ~15 篇

---

### 板块六：开源工具动态

**AI-Native 工具**（新增 `fetch_tool_releases.py`）：

| 工具 | GitHub 仓库 |
|------|------------|
| LangFuse | `langfuse/langfuse` |
| Arize Phoenix | `Arize-AI/phoenix` |
| Helicone | `Helicone/helicone` |
| OpenLIT | `openlit/openlit` |
| Traceloop/OpenLLMetry | `traceloop/openllmetry` |
| Coze 罗盘 | WebSearch（不开源）|

- 调用 GitHub API 获取近 30 天 Releases
- 过滤 patch 版本，只保留 minor/major release
- 输出 JSON: `[{name, version, published, body_summary, url, repo}]`

**传统可观测工具 AI 进展**（SKILL.md 指令）：

| 工具 | 搜索范围 |
|------|---------|
| Grafana Labs | `site:grafana.com/blog + AI agent LLM observability` |
| Dynatrace | `site:dynatrace.com + AI agent monitoring Davis` |
| Splunk | `site:splunk.com + AI observability LLM` |
| Elastic | `site:elastic.co/blog + AI agent APM observability` |
| Datadog | 已在板块五覆盖 |
| New Relic | 已在板块五覆盖 |

LangSmith（不开源）通过 WebSearch `site:docs.smith.langchain.com changelog` / `site:blog.langchain.dev langsmith` 获取发版日志。

**输出**：两个子表 — "AI-Native 工具发版"和"传统可观测工具 AI 进展"

**采集成本**：`fetch_tool_releases.py` × 1 + WebSearch × 6 + WebFetch × ~8

---

## 文件改动清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `skills/research-observe/SKILL.md` | 重写 | 7 板块编配指令，~3,000 词 |
| `references/search-strategies.md` | 扩展 | 新增周刊/国内/大厂/传统工具查询模板 |
| `references/source-guide.md` | 扩展 | 新增 API 端点、受监控仓库、速率限制 |
| `references/report-template.md` | 重写 | 7 板块 + 摘要首页模板 |
| `scripts/search_arxiv.py` | 修改 | 新增 `--venues` 顶会筛选、扩展关键词列表 |
| `scripts/search_semantic_scholar.py` | 微调 | 同步关键词列表 |
| `scripts/fetch_otel_updates.py` | 不变 | 现有实现满足需求 |
| `scripts/fetch_openinference_updates.py` | **新增** | 监控 openinference org 仓库 PR/Issue |
| `scripts/fetch_tool_releases.py` | **新增** | 6 个 AI-Native 工具 GitHub Releases 抓取 |
| `scripts/generate_report.py` | 重写 | 7 板块模板变量 + 摘要页生成 + 子表渲染 |

## 技术约束

- **语言**：Python 3，依赖 `requests` + `python-dateutil`，其余用 stdlib
- **错误处理**：每个数据源独立失败不阻塞整体流程，错误在 JSON 中以 `{"error": "..."}` 输出
- **去重**：arXiv 与 Semantic Scholar 按标题相似度 > 70% 去重（`difflib.SequenceMatcher`），保留 citationCount 高的条目
- **速率限制**：GitHub API 未认证 60 req/h，认证 5000 req/h；Semantic Scholar 单 IP 1 req/s（无 API key）或 10 req/s（有 API key）
- **报告语言**：全中文，文章/博客/论文标题保留原文

## 集成方式

- `/research-observe` — 全景观测横切面（30 天默认）
- `/research-observe --since 2026-05-21` — 周采集模式
- `/research-observe tracing --deep` — 聚焦特定话题深度扫描
- 配合 `/loop` 实现定时自动扫描
