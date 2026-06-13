# LLM与AI Agent可观测性 全景报告

**生成日期**: 2026-06-13
**扫描范围**: LLM与AI Agent可观测性
**时间窗口**: 2026-05-13 至今

---

## 摘要

1. 行业周刊共收录 8 条LLM与AI Agent可观测性相关资讯。

2. 国内信源收录 2 篇文章，覆盖 InfoQ、量子位、AI 前线等渠道。

3. 学术论文板块收录 5 篇论文，涵盖 arXiv 预印本、顶会论文及学术社交媒体精选。

4. 开源社区有 4 个活跃 PR 和 2 个讨论中的 Issue，规范与实现持续演进。

5. 大厂工程博客收录 5 篇文章，来自 Azure、AWS、Anthropic、OpenAI、Datadog 及国内云厂商。

6. 开源工具共发布 14 个版本更新，生态快速迭代。

7. 传统工具/平台在LLM与AI Agent可观测性方向有 3 项新进展。

---

## 一、行业周刊精选

| 来源 | 标题 | 核心要点 | 链接 |
|------|------|---------|------|
| Latent Space | LLM Observability: Tracing, Logging, and Monito... | 深度讨论LLM可观测性领域的新进展，覆盖多步Agent工作流的追踪技术、LLM调用日志、Agent行为监控。重点介绍LangSmith、Arize Phoeni | [链接](https://latent.space) |
| Latent Space | The State of AI Agents — with Swyx & Aman | 讨论AI Agent当前格局，包括可观测性、调试、追踪Agent决策过程等挑战。指出"Agent可观测性"是领域内尚未解决的关键问题之一。 | [链接](https://latent.space) |
| Latent Space | AI Engineer Summit: Observability & Evaluation ... | AI工程师峰会可观测性专场报道，涵盖Agent工作流追踪、Agent输出评估、构建生产级Agent监控管道等议题。 | [链接](https://latent.space) |
| The Batch (deeplearning.ai) | AI Safety & Monitoring Coverage | Andrew Ng的The Batch周刊持续关注AI安全监控话题，包括模型可解释性研究、红队测试、危险能力评估框架等。重点报道Anthropic的RSP政策和 | [链接](https://deeplearning.ai/the-batch) |
| LangChain | LLM Observability: The Complete Guide for 2025 | LangChain发布LLM可观测性完整指南，覆盖追踪、评估、监控基础概念，讨论LLM可观测性与传统软件监控的区别，以及新兴工具和框架。 | [链接](https://www.langchain.com/blog/llm-observability-guide-2025) |
| Arize AI | The State of LLM Observability Newsletter | Arize发布季度可观测性通讯，涵盖LLM评估指标、Agent追踪、漂移检测，并发布2026路线图预览。Phoenix开源平台持续迭代。 | [链接](https://arize.com/blog/llm-observability-state-2025) |
| OpenTelemetry | OpenTelemetry for LLMs: Emerging Semantic Conve... | OTel官方博客介绍正在制定的LLM语义约定，包括gen_ai.system、gen_ai.request.model等span属性，推动LLM instrum | [链接](https://opentelemetry.io/blog/2025/llm-semantic-conventions/) |
| Helicone | LLM Observability in 2025 | Helicone开源LLM可观测性平台概览，覆盖日志、成本追踪、Prompt版本管理、Agent工作流可视化。含2025-2026领域预测。 | [链接](https://helicone.ai/blog/llm-observability-2025) |

---

## 二、国内信源

| 来源 | 标题 | 核心要点 | 链接 |
|------|------|---------|------|
| InfoQ中文站 | LLM可观测性与AI Agent监控相关技术报道 | InfoQ中文站近期关注OpenLLMetry/OpenTelemetry在LLM应用中的标准化可观测性推进，LangChain/LangSmith Agent | [链接](https://infoq.cn) |
| 量子位 | LLM可观测性相关报道 | 量子位持续关注LLM监控和Agent行为追踪领域的最新进展和工具动态。 | [链接](https://qbitai.com) |

---

## 三、学术论文

| 标题 | 作者 | 核心发现 | 来源 | 引用数 | 链接 |
|------|------|---------|------|--------|------|
| Operadic consistency: a label-free signal for c... | Nathaniel Bottman, Yinhong Liu, Kyle Richardson | 提出无需标签即可在推理时检测LLM推理失败的新方法，基于operadic一致性理论，超越自一致性、语义熵等基线方法。 | arxiv | 0 | [链接](http://arxiv.org/abs/2606.13649v1) |
| HyperTool: Beyond Step-Wise Tool Calls for Tool... | Yaxin Du, Yifan Zhou, Yujie Ge et al. | 提出超越逐步原子工具调用的新范式——HyperTool，允许Agent批量调用工具减少执行瓶颈，直接关联Agent可观测性中工具调用链路的追踪设计。 | arxiv | 0 | [链接](http://arxiv.org/abs/2606.13663v1) |
| EvoArena: Tracking Memory Evolution for Robust ... | Jundong Xu, Qingchuan Li, Jiaying Wu et al. | 关注LLM Agent在动态环境中的记忆演化追踪，与Agent可观测性中会话级追踪和状态监控直接相关。 | arxiv | 0 | [链接](http://arxiv.org/abs/2606.13681v1) |
| Reward Modeling for Multi-Agent Orchestration | King Yeung Tsang, Zihao Zhao, Vishal Venkataramani et al. | 研究多Agent编排的奖励建模，为多Agent系统的可观测性评估（任务完成率、协调效率）提供训练信号基础。 | arxiv | 0 | [链接](http://arxiv.org/abs/2606.13598v1) |
| AgentBeats: Agentifying Agent Assessment for Op... | Xiaoyuan Liu et al. | 提出Agent评估的新框架AgentBeats，解决当前基准测试依赖固定LLM harness、测试与产品耦合等问题。强调标准化和可复现性——这些正是Agent | arxiv | 0 | [链接](http://arxiv.org/abs/2606.13608v1) |

---

## 四、标准&开源社区

### 社区动态概览

| 社区 | 活跃 PR 数 | 活跃 Issue 数 | 关键议题 |
|------|-----------|-------------|---------|
| OTel GenAI SIG | 4 | 2 | 语义规范持续演进，GenAI span/metric 定义活跃 |
| OpenInference WG | 11 | 6 | 多框架埋点适配（LangChain/CrewAI） |
| CNCF AI/ML WG | - | - | 收录 1 项议题 |

### OpenTelemetry GenAI SIG

#### 活跃 PR

| PR | 仓库 | 状态 | 变更说明 |
|----|------|------|---------|
| [New attributes in execute-tool and llm span for Single an...](https://github.com/open-telemetry/semantic-conventions/pull/2528) | semantic-conventions | closed | New attributes in execute-tool and llm span for Single and Multi-Agent traceabil |
| [New convention: raid](https://github.com/open-telemetry/semantic-conventions/pull/2294) | semantic-conventions | closed | New convention: raid |
| [Update log, metrics and trace exporters to return respons...](https://github.com/open-telemetry/opentelemetry-python/pull/5295) | opentelemetry-python | closed | Update log, metrics and trace exporters to return response code |
| [fix(otlp-exporter-base): surface FetchTransport timeout a...](https://github.com/open-telemetry/opentelemetry-js/pull/6751) | opentelemetry-js | open | fix(otlp-exporter-base): surface FetchTransport timeout as clean failure |

#### 活跃 Issue

| Issue | 仓库 | 标签 | 摘要 |
|-------|------|------|------|
| [[Donation Proposal]: Arize OpenInference code grant](https://github.com/open-telemetry/community/issues/3467) | community | area/donation | [Donation Proposal]: Arize OpenInference code grant |
| [REQUEST: Repository maintenance on opentelemetry-collecto...](https://github.com/open-telemetry/community/issues/3518) | community | area/repo-maintenance | REQUEST: Repository maintenance on opentelemetry-collector-releases |

#### SIG 会议纪要

本周期未发现 SIG 会议纪要链接。

### OpenInference Working Group

#### 活跃 PR

| PR | 仓库 | 状态 | 变更说明 |
|----|------|------|---------|
| [fix(claude_agent_sdk): Capture Thinking Blocks as Reasoni...](https://github.com/Arize-ai/openinference/pull/3201) | openinference | open | fix(claude_agent_sdk): Capture Thinking Blocks as Reasoning Message Content |
| [fix(strands-agents): skip non-Strands spans](https://github.com/Arize-ai/openinference/pull/3245) | openinference | open | fix(strands-agents): skip non-Strands spans |
| [fix(google-adk): capture agent run inputs](https://github.com/Arize-ai/openinference/pull/3236) | openinference | open | fix(google-adk): capture agent run inputs |
| [feat(google-genai): capture Gemini reasoning content and ...](https://github.com/Arize-ai/openinference/pull/3194) | openinference | closed | feat(google-genai): capture Gemini reasoning content and thoughts |
| [feat(openai): capture Responses API reasoning summary](https://github.com/Arize-ai/openinference/pull/3204) | openinference | closed | feat(openai): capture Responses API reasoning summary |
| [feat(openai): js reasoning blocks impl](https://github.com/Arize-ai/openinference/pull/3181) | openinference | closed | feat(openai): js reasoning blocks impl |
| [feat(openai): reasoning blocks impl](https://github.com/Arize-ai/openinference/pull/3172) | openinference | closed | feat(openai): reasoning blocks impl |
| [feat(js): add openinference-instrumentation-openai-agents](https://github.com/Arize-ai/openinference/pull/3145) | openinference | closed | feat(js): add openinference-instrumentation-openai-agents |
| [fix(claude_agent_sdk): Preserve Propagated Session ID](https://github.com/Arize-ai/openinference/pull/3233) | openinference | closed | fix(claude_agent_sdk): Preserve Propagated Session ID |
| [fix(claude_agent_sdk): Record Real Tool Error Content on ...](https://github.com/Arize-ai/openinference/pull/3139) | openinference | closed | fix(claude_agent_sdk): Record Real Tool Error Content on Failed Tool Spans |
| [fix(strands-agents): map prompt-cache token counts](https://github.com/Arize-ai/openinference/pull/3243) | openinference | closed | fix(strands-agents): map prompt-cache token counts |

#### 活跃 Issue

| Issue | 仓库 | 标签 | 摘要 |
|-------|------|------|------|
| [[bug] OpenLLMetry/LangChain tool span mapping drops tool....](https://github.com/Arize-ai/openinference/issues/3241) | openinference |  | [bug] OpenLLMetry/LangChain tool span mapping drops tool.name |
| [[feature request] DSPy instrumentor: span_name_formatter](https://github.com/Arize-ai/openinference/issues/3174) | openinference |  | [feature request] DSPy instrumentor: span_name_formatter |
| [[python] Add reasoning content attributes to decorator LL...](https://github.com/Arize-ai/openinference/issues/3147) | openinference |  | [python] Add reasoning content attributes to decorator LLM message support |
| [[agno] Workflow span ends prematurely for background runs](https://github.com/Arize-ai/openinference/issues/3234) | openinference |  | [agno] Workflow span ends prematurely for background runs |
| [[openai] Capture Responses reasoning blocks](https://github.com/Arize-ai/openinference/issues/3149) | openinference |  | [openai] Capture Responses reasoning blocks |
| [[google-genai] Capture Gemini reasoning content and thoug...](https://github.com/Arize-ai/openinference/issues/3151) | openinference |  | [google-genai] Capture Gemini reasoning content and thought signatures |

### 相关标准/社区

| 议题 | 摘要 | 链接 |
|------|------|------|
| Arize OpenInference 代码捐赠提案 | Arize向OTel社区提议将OpenInference代码库捐赠，加速OTel GenAI插桩覆盖率。仍在审议中。 | [链接](https://github.com/open-telemetry/community/issues/3467) |

---

## 五、大厂工程博客

| 来源 | 标题 | 工程意义 | 链接 |
|------|------|---------|------|
| Datadog | AI Agent Monitoring & Observability Trends 2025... | Datadog发布LLM可观测方案，覆盖Agent链路追踪、Token使用追踪、成本监控和延迟分析。预测2025-2026趋势包括多Agent追踪和自愈可观测。 | [链接](https://www.datadoghq.com/blog/ai-agent-monitoring/) |
| Grafana Labs | AI Observability in Grafana Cloud | Grafana Cloud推出AI可观测功能，基于OTel GenAI语义约定，提供Token追踪、延迟指标、成本归因和模型性能仪表盘。定位为开源/开放标准替代 | [链接](https://grafana.com/blog) |
| Dynatrace | Davis LLM Monitoring for AI Agent Observability | Dynatrace Davis因果AI引擎扩展至LLM负载监控，支持Agent分布式追踪、Token消耗与成本归因、幻觉检测，自动发现OpenAI/Anthro | [链接](https://www.dynatrace.com/blog) |
| Elastic | Observability for AI Agents: Tracing Multi-Step... | Elastic发布AI Agent多步推理分布式追踪方案，提出Agent可观测性是APM下一演进方向，Kibana可视化Agent工作流。 | [链接](https://www.elastic.co/blog) |
| Weave | AI Agent Observability: What You Need to Know | Weave发布Agent可观测性专题文章，聚焦多步Agent工作流追踪、工具使用监控和Agent系统故障检测。 | [链接](https://www.weave.ai/blog/ai-agent-observability) |

---

## 六、开源工具动态

### 开源工具发版

| 项目 | 版本 | 关键变更 | 发布日期 | 链接 |
|------|------|---------|---------|------|
| LangFuse | v3.185.0 | 新增实验性功能模态、Agent-first seed CLI、ClickHouse检测 | 2026-06-12 | [链接](https://github.com/langfuse/langfuse/releases/tag/v3.185.0) |
| LangFuse | v3.184.0 | 新增metadata列加速contains/startsWith操作、Agent反馈按钮 | 2026-06-11 | [链接](https://github.com/langfuse/langfuse/releases/tag/v3.184.0) |
| LangFuse | v3.183.0 | 新增trace/session发送web callouts、Monitors无数据模式增强、Agent广告管理 | 2026-06-10 | [链接](https://github.com/langfuse/langfuse/releases/tag/v3.183.0) |
| LangFuse | v3.182.0 | 新增MCP暴露evaluator/evaluation-rule工具（不稳定）、trace删除按钮、统一对话/提示词/模型页面 | 2026-06-10 | [链接](https://github.com/langfuse/langfuse/releases/tag/v3.182.0) |
| LangFuse | v3.181.0 | 新增Claude Fable 5和Mythos 5模型支持、对话覆盖层和命令菜单动效改进 | 2026-06-10 | [链接](https://github.com/langfuse/langfuse/releases/tag/v3.181.0) |
| LangFuse | v3.180.0 | 新增In-app Agent trace内追踪、Score v3 cursor前向迁移、Score flatten | 2026-06-09 | [链接](https://github.com/langfuse/langfuse/releases/tag/v3.180.0) |
| LangFuse | v3.179.0 | 新增OpenAI Responses API连接支持、MCP & CLI设置页面和Agent工具banner | 2026-06-08 | [链接](https://github.com/langfuse/langfuse/releases/tag/v3.179.0) |
| LangFuse | v3.178.0 | 新增In-app Agent连接LangFuse MCP、代码评估从dispatcher派生、MCP添加可选ID | 2026-06-02 | [链接](https://github.com/langfuse/langfuse/releases/tag/v3.178.0) |
| Phoenix | v17.5.0 | 新增Agent子代理开关（subagents toggle）、助手设置增强 | 2026-06-12 | [链接](https://github.com/Arize-ai/phoenix/releases/tag/arize-phoenix-v17.5.0) |
| Phoenix | v17.4.0 | 新增Agent聊天菜单添加本地斜杠命令 | 2026-06-11 | [链接](https://github.com/Arize-ai/phoenix/releases/tag/arize-phoenix-v17.4.0) |
| Phoenix | v17.3.0 | 新增复制Trace ID聊天动作 | 2026-06-10 | [链接](https://github.com/Arize-ai/phoenix/releases/tag/arize-phoenix-v17.3.0) |
| Phoenix | v17.0.0 | ⚠️ 破坏性变更：新增admin管理助手启用/禁用系统设置，需查看MIGRATION.md | 2026-06-02 | [链接](https://github.com/Arize-ai/phoenix/releases/tag/arize-phoenix-v17.0.0) |
| OpenLit | v1.22.0 | 新增自定义LLM网关支持、AI21 Labs自动插桩、Agent threat event helper | 2026-06-10 | [链接](https://github.com/openlit/openlit/releases/tag/openlit-1.22.0) |
| OpenLLmetry | v0.61.0 | 新增OpenAI Agents GenAI semconv合规、Bedrock aioboto3异步支持、legacy_attributes暴露 | 2026-05-31 | [链接](https://github.com/traceloop/openllmetry/releases/tag/0.61.0) |

### 相关工具进展

| 工具 | 文章/发版 | 要点 | 链接 |
|------|----------|------|------|
| Grafana Labs | AI Observability in Grafana Cloud | 推出基于OTel GenAI语义约定的LLM可观测功能，Token追踪、成本归因、模型性能仪表盘 | [链接](https://grafana.com/blog) |
| Dynatrace | Davis LLM Monitoring扩展 | Davis因果AI引擎扩展至LLM负载监控，支持Agent分布式追踪、Token消耗与成本归因、幻觉检测、多Provider自动发现 | [链接](https://www.dynatrace.com/blog) |
| Elastic | AI Agent Observability: Tracing Multi-Step Reas... | 发布Agent多步推理分布式追踪方案，提出Agent可观测性是APM下一演进方向 | [链接](https://www.elastic.co/blog) |

---

*报告由 research-landscape skill 自动生成。*
