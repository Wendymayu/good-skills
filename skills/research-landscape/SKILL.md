---
name: research-landscape
description: Use when the user asks to "research", "scan", "check updates", "what's new in", "latest developments in", or mentions any technology topic they want a landscape scan of. Works with any domain — AI agent evaluation, LLM observability, microservices, Kubernetes security, etc. Produces a structured Chinese report with summaries and original source links across 7 plates.
allowed-tools: WebSearch, WebFetch, Bash(python *), Bash(pip install *), Read, Write, Grep, Glob, TodoWrite
argument-hint: "[话题] [--since YYYY-MM-DD] [--deep]"
---

# 技术领域全景观测

采集、综合、报告任意技术领域的最新进展。产出一份结构化的中文 Markdown 报告，保留原文标题，中文摘要。文章/博客/论文标题必须保留原文语言，只有摘要部分用中文。

## 参数

解析 `$ARGUMENTS`：
- **话题**：任意技术领域，中文或英文均可（如"可观测"、"AI agent evaluation"、"微服务治理"、"Kubernetes"）。需将话题翻译为每个板块合适的搜索关键词。空参数 = 报错，必须询问用户想扫描什么话题。
- **--since YYYY-MM-DD**：筛选该日期之后的结果。默认：今天往前推 30 天。
- **--deep**：深度模式，每信源 5 条结果，含完整摘要。默认：广度模式，每信源 15 条。

## 关键词生成

根据用户话题，为每个板块生成双语（中文+英文）搜索关键词。如果用户用语本身就是领域术语则直接使用；否则推断最相关的学术/行业术语。示例：用户说"可观测" → 英文关键词"LLM observability"、"AI agent tracing"、"OTel GenAI"；中文关键词"可观测性"、"链路追踪"、"Agent监控"。

## 前置条件

首次使用前运行：
```bash
pip install requests python-dateutil
```

可选：设置 `GITHUB_TOKEN` 环境变量以提高 GitHub API 速率限制（推荐）。
可选：设置 `SEMANTIC_SCHOLAR_API_KEY` 环境变量以提高 S2 API 速率限制。

## 采集工作流

必须严格按以下板块顺序执行（从"可看可不看"到"必须关注"）。不得跳过板块，不得调换顺序。

### 步骤 1：准备

创建 TodoWrite 清单：
```
- [ ] 板块一：行业周刊精选（WebSearch + WebFetch）
- [ ] 板块二：国内信源（WebSearch + WebFetch）
- [ ] 板块三：学术论文（search_arxiv.py + search_semantic_scholar.py + WebSearch）
- [ ] 板块四：标准&开源社区（WebSearch + WebFetch）
- [ ] 板块五：大厂工程博客（WebSearch + WebFetch）
- [ ] 板块六：开源工具动态（WebSearch + WebFetch）
- [ ] 聚合 JSON 并生成报告（generate_report.py）
```

计算 `--since` 日期。默认：今天减 30 天。
生成话题的双语搜索关键词。

### 步骤 2：板块一 — 行业周刊精选

用 WebSearch 在以下 4 个周刊归档站搜索话题相关内容：
- `site:tldr.tech/ai <话题关键词>`
- `site:latent.space <话题关键词>`
- `site:deeplearning.ai/the-batch <话题关键词>`
- `site:radarai.com <话题关键词>`

每个源 WebFetch 前 2 条结果。提取标题（原文）、3 句中文摘要、URL。只保留与话题相关的条目。记录为 `{source, title, summary, url}`。

### 步骤 3：板块二 — 国内信源

用 WebSearch 在以下 5 个国内站点搜索：
- `site:infoq.cn <中文话题关键词>`
- `site:qbitai.com <话题关键词>`
- `site:jiqizhixin.com <话题关键词>`
- `site:zhihu.com <中文话题关键词>`
- `site:okjk.com <话题关键词>`

每个源 WebFetch 前 2 条结果。提取标题（原文）、3 句中文摘要、URL。优先 InfoQ 和 AI前线（有编辑审稿）。记录为 `{source, title, summary, url}`。

### 步骤 4：板块三 — 学术论文

**并行**运行以下两个 Bash 命令（同一轮次）：

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-landscape/scripts/search_arxiv.py" --topic "<话题>" --since <日期> [--deep]
```

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-landscape/scripts/search_semantic_scholar.py" --topic "<话题>" --since <日期> [--deep]
```

然后 WebSearch 搜索 Twitter/X 学术账号：
```
from:@_akhaliq <话题关键词>
from:@papers_daily <话题关键词>
```

所有论文条目设置 `source` 字段为 `arxiv`、`semantic_scholar` 或 `twitter`。去重由 `generate_report.py` 自动处理。

### 步骤 5：板块四 — 标准&开源社区

WebSearch 搜索与话题相关的标准/社区组织：
- `site:github.com/cncf <话题关键词>`
- `site:github.com/open-telemetry <话题关键词>`（仅可观测性话题）
- `<话题> standards community SIG working group`

对每个相关社区，WebFetch 会议纪要、提案或规范文档。PR/Issue 记录为 `{repo, number, title, state, url}`，社区内容记录为 `{title, summary, url}`。

如果话题有知名的社区仓库（如可观测性有 OTel），可运行 `references/source-guide.md` 中列出的 fetch 脚本获取结构化数据。

### 步骤 6：板块五 — 大厂工程博客

用 WebSearch 在以下 10 个博客源搜索话题相关内容：

**海外云**：`site:techcommunity.microsoft.com <话题>`、`site:cloud.google.com/blog <话题>`、`site:aws.amazon.com/blogs/machine-learning <话题>`
**模型厂商**：`site:anthropic.com <话题>`、`site:openai.com <话题>`
**监控平台**：`site:datadoghq.com/blog <话题>`、`site:newrelic.com/blog <话题>`
**国内云**：`site:developer.aliyun.com <中文话题>`、`site:cloud.tencent.com/developer <中文话题>`、`site:volcengine.com <中文话题>`

每批 3-4 条查询。每条命中 WebFetch 验证相关性。提取标题（原文）、3-5 句中文工程意义摘要、URL。记录为 `{source, title, significance, url}`。

### 步骤 7：板块六 — 开源工具动态

WebSearch 搜索与话题相关的开源工具：
- 搜索 `<话题> open source tools GitHub releases`
- 对每个发现的工具，搜索 `site:github.com/<org>/<repo> releases`

如果话题有知名工具仓库（如可观测性有 LangFuse），可运行 `references/source-guide.md` 中列出的 `fetch_tool_releases.py`。

WebSearch 搜索传统/成熟工具在该话题方向的进展。

发版数据记录为 `{name, version, change, published, url, repo}`，一般工具更新记录为 `{name, title, change, url}`。

### 错误恢复与降级策略

每个数据源独立失败，不要中断整体流程。但不要轻易放弃——按以下降级策略逐层尝试：

**WebSearch 失败降级**：
1. 先用 `site:xxx <关键词>` 精确搜索
2. 如果 site: 搜索无结果或返回合成摘要 → **去掉 site: 限制**，改用 `<关键词> <话题>` 泛搜
3. 如果泛搜仍无结果 → 换用中文关键词搜一遍，再换用英文关键词搜一遍
4. 以上全部失败才输出"本期无更新"

**WebFetch 失败降级**：
1. 先尝试 WebFetch 抓取页面内容
2. 如果 WebFetch 被安全策略阻止 → **直接用 WebSearch 返回的摘要**做内容提取，不依赖 WebFetch
3. 如果 WebSearch 摘要也不够具体 → 标记该条目为"仅标题+链接，无详细摘要"

**脚本 API 失败降级**：
1. arXiv API 429 → 等待 5 秒后重试一次
2. Semantic Scholar 空结果 → 换用更宽泛的关键词重试一次（去掉引号精确匹配）
3. GitHub API 403 → 提醒用户设置 GITHUB_TOKEN，但不中断流程
4. 脚本输出 `{"error": "..."}` 条目则排除，不纳入报告

**整板块无数据**：输出"本期无更新"，并在报告末尾的"限制说明"部分列出失败原因和建议的手动补充方式。

### 步骤 8：聚合并生成报告

1. 将所有采集数据合并为 JSON：

```json
{
  "date": "<今天>",
  "since": "<起始日期>",
  "topic": "<话题>",
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

2. 写入临时文件，然后运行：

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/research-landscape/scripts/generate_report.py" \
  --input <JSON文件路径> \
  --template "${CLAUDE_PLUGIN_ROOT}/skills/research-landscape/references/report-template.md" \
  --topic "<话题>" \
  --since <日期>
```

3. 读取生成的报告文件并呈现给用户。说明文件路径。

4. **基于报告数据撰写趋势点评**，追加到报告末尾。这一步是必须的，不可跳过。点评需覆盖：

   **a) 研究热点**（2-3 条）：从学术论文和社区 Issue/PR 中提炼当前最活跃的研究方向。每条热点用一句话概括，附上支撑数据来源（如"本期 X 篇论文聚焦 Y 方向，OpenInference 有 Z 个相关 PR"）。

   **b) 工程趋势**（2-3 条）：从工具发版、大厂博客、标准社区中提炼工程落地方向。关注：哪些工具正在快速迭代、哪些标准正在成形、哪些厂商正在布局。

   **c) 跨板块交叉洞察**（1-2 条）：发现不同板块之间的关联信号——如学术论文提出的概念正好对应某个工具的新发版功能、标准社区的讨论方向与大厂的博客方向一致等。这些交叉信号往往比单一板块的发现更有决策价值。

   **d) 值得关注的风险/盲区**（1 条）：指出本次扫描中发现的潜在风险（如某工具突然大幅改版有 breaking change、某标准提案悬而未决导致生态不确定性）或数据盲区（如某些板块本期数据缺失需要手动补充）。

   点评风格：**简洁、有观点、有数据支撑**，不是泛泛的"领域在快速发展"。每条点评控制在 50-100 字中文。

5. 标记所有 TodoWrite 条目为完成。

## 快速参考

| 板块 | 动作 | 工具 |
|------|------|------|
| 一、周刊 | WebSearch ×4 + WebFetch ×~8 | WebSearch, WebFetch |
| 二、国内 | WebSearch ×5 + WebFetch ×~10 | WebSearch, WebFetch |
| 三、论文 | search_arxiv.py + search_semantic_scholar.py + WebSearch | Bash（并行）, WebSearch |
| 四、社区 | WebSearch + WebFetch（按话题适配） | WebSearch, WebFetch |
| 五、博客 | WebSearch ×10 + WebFetch ×~15 | WebSearch, WebFetch |
| 六、工具 | WebSearch + WebFetch（按话题适配） | WebSearch, WebFetch |
| 报告 | generate_report.py | Bash, Read |

## 常见错误

- 跳过板块 — 所有 7 个板块必须执行，即使某些板块无数据也要输出"本期无更新"。
- 翻译标题 — 标题必须保留原文语言，只有摘要用中文。
- 忘记 `--since` 默认值 — 始终计算 30 天窗口。
- 学术脚本串行运行 — 必须并行启动以提高效率。
- **使用首页/域名级 URL** — 每条记录的 URL 必须指向**具体文章页面**（如 `https://datadoghq.com/blog/monitoring-ai-agents/`），不是网站首页（如 `https://datadoghq.com/blog`）。如果 WebSearch 返回的只有域名，必须用更具体的查询或 WebFetch 获取文章级链接。无法获取具体 URL 的条目应标记为"链接暂缺"而非用首页代替。
- 跳过国内信源（板块二） — 此板块捕获中文视角，不可省略。
- 只用英文关键词 — 必须同时生成中文和英文关键词以全面覆盖。
- 板块四/六不按话题适配 — 标准社区和工具仓库因领域不同而异；不要为非可观测性话题硬编码可观测性专用仓库。

## URL 质量规则

**核心要求**：报告中的每一条链接必须是**文章级 URL**，能让读者直接跳转到原文。

**获取流程**：
1. WebSearch 返回具体文章 URL → 直接使用 ✅
2. WebSearch 只返回域名/首页 → 用 `<话题关键词> <文章标题关键词>` 做更精确的泛搜，获取文章级 URL
3. 泛搜仍无具体 URL → WebFetch 尝试抓取该源站的文章列表页，从列表中提取文章链接
4. 以上全部失败 → 条目标记 `[链接暂缺，请访问 <源站首页> 查阅]`，不用首页 URL 假装是文章链接

**验证标准**：URL 路径必须包含至少一层深度（如 `/blog/xxx`、`/article/xxx`、`/p/xxx`），不能只是 `/` 或 `/blog`。

## /loop 定期扫描

配合 `/loop` 实现定时自动扫描：
```
/loop 168h /good-skills:research-landscape <话题> --since $(date -d '7 days ago' +%%Y-%%m-%%d)
```
