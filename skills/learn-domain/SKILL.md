---
name: learn-domain
description: Use when the user asks to "learn", "study", "入门", "上手", "学习路径", "怎么学", "推荐学习路线", or mentions wanting a structured learning guide for any technology domain. Works with any domain — observability, AI agents, LLM, Kubernetes, Rust, etc. Produces a structured Chinese learning guide with concept dependency graph, tiered learning path, resource recommendations, and practical project suggestions.
allowed-tools: WebSearch, WebFetch, Read, Write, Glob, TodoWrite
argument-hint: "[话题] [--level beginner|intermediate] [--project <项目描述>] [--lang zh|en]"
---

# 技术领域学习指南生成器

为任意技术领域生成结构化学习指南，解决"不知道该学什么、按什么顺序学、哪些资源靠谱"的问题。产出一份中文 Markdown 学习指南，概念名称附英文原文。

## 参数

解析 `$ARGUMENTS`：
- **话题**：必填，技术领域名称（如"可观测"、"Kubernetes"、"Rust"）。空参数 = 报错，必须询问用户想学什么领域。
- **--level beginner|intermediate**：可选，指定起点层级。默认：根据用户上下文自动判断（新手选 beginner，有基础选 intermediate）。
- **--project <项目描述>**：可选，用户有具体项目目标时，反向推导必须学的概念。
- **--lang zh|en**：可选，输出语言。默认 `zh`（中文为主 + 英文术语）。

## 关键词生成

根据用户话题，生成双语术语对照表的关键词。如果用户用语是中文，推断对应的英文术语；如果是英文，推断中文。示例：用户说"可观测" → 推断 "Observability, LLM monitoring, distributed tracing"。

## 工作流

严格按以下 5 步顺序执行。不得跳过步骤。

### 步骤 1：准备与领域骨架

创建 TodoWrite 清单：
```
- [ ] 步骤 1：领域骨架生成
- [ ] 步骤 2：WebSearch 定向补充资源
- [ ] 步骤 3：引用 landscape 报告热点
- [ ] 步骤 4：实战项目建议生成
- [ ] 步骤 5：渲染学习指南
```

用自身知识生成领域骨架，包含以下四个部分（**不使用 WebSearch，纯知识输出**）：

**a) 领域全景**：一句话定义该领域是什么 + 核心子方向列表（3-6 个）。每个子方向用一句话描述。

**b) 术语对照表**：列出该领域 10-20 个核心术语，每条包含中文、英文、一句话释义。释义必须准确简洁，不是泛泛描述。

**c) 概念依赖图**：用 Markdown 树状层级格式表示概念之间的依赖关系。每个概念标注层级标签 `[基础]`、`[核心]`、`[进阶]` 和一句话简释（如 `← 单次操作记录`）。

层级标签规则：
- `[基础]`：概念依赖图中最底层、无前置依赖的概念。目标：能读懂该领域的文章和对话。
- `[核心]`：依赖图中间层、有 1-2 个前置的概念。目标：能独立完成该领域的常规项目。
- `[进阶]`：依赖图顶层、多个前置的概念 + 当前热点。目标：能做技术决策、理解前沿趋势。

如果用户提供了 `--project` 参数：从项目目标反向推导，标注哪些概念是"必须学"（项目直接依赖），哪些是"可选学"（了解即可），在依赖图中用 `⚡` 标记必须学的概念。

**d) 分级概念列表**：将概念依赖图中的概念按层级分组，形成三个学习层级的概念清单。计算每层估计天数（基础层按每个概念约 1-2 天，核心层约 2-3 天，进阶层约 3-5 天）。

### 步骤 2：WebSearch 定向补充

为每个学习层级搜索入门资源。**精准搜索，不做大规模采集**。

**搜索计划**（每层 1-2 次搜索，取前 5 条）：

| 目标 | 搜索关键词 |
|------|-----------|
| 基础资源 | `<话题英文> beginner tutorial guide introduction` |
| 核心资源 | `<话题英文> best practices production practical guide` |
| 进阶资源 | `<话题英文> advanced deep dive architecture internals` |
| 中文资源 | `<话题中文> 入门 教程 实践 最佳实践` |
| 避坑指南 | `<话题英文> common mistakes pitfalls misconceptions` |

总计约 5 次搜索，每层最多 5 条资源。

**资源提取规则**：
- 每条资源记录 `{title, reason, url}`
- `reason` 是一句话推荐理由（为什么这篇适合该层级的学习者）
- URL 必须是文章级链接（路径深度 ≥ 1），不能是首页
- 如果 WebSearch 返回合成摘要而非具体 URL → 标记 `[链接暂缺，请搜索 <关键词>]`
- 搜索失败不阻塞——骨架输出仍然完整

**避坑指南补充**：WebSearch 搜索 1 次 `<话题英文> common mistakes pitfalls misconceptions`，提取 1-2 条社区反馈的常见坑。与 Claude 知识生成的避坑合并（去重）。

### 步骤 3：引用 landscape 报告热点

检查当前工作目录是否存在 `research-landscape-report-*.md` 文件：

```bash
Glob: research-landscape-report-*.md
```

**如果存在**：读取该文件，提取"七、趋势点评"部分的内容，作为"当前热点"板块的数据来源。引用时注明来源报告的日期。

**如果不存在**：输出以下提示文字：
```
建议运行 /good-skills:research-landscape {话题} 补充当前行业热点和最新动态。
```

### 步骤 4：实战项目建议

根据话题 + 用户 `--project` 参数（如有），生成 2-3 个实战项目建议。

**项目建议规则**：
- 项目从易到难排列
- 每个项目必须明确标注：难度（⭐/⭐⭐/⭐⭐⭐）、学到的核心概念列表、估计时间
- 如果用户提供了 `--project`：第一个项目建议应直接对齐用户的项目目标，标注"直接对齐你的项目目标"
- 项目建议应具体可执行（如"用 OpenTelemetry SDK 给一个 Flask API 添加 tracing"），不是泛泛的"做一个项目"

### 步骤 5：渲染学习指南

1. 将所有采集数据合并：

```
{
  "date": "<今天>",
  "topic": "<话题>",
  "level": "<层级>",
  "domain_overview": "<领域全景文字>",
  "terminology_table": "<术语对照表 Markdown>",
  "concept_dependency_graph": "<概念依赖图文字>",
  "beginner_days": "<基础天数>",
  "beginner_concepts": "<基础概念列表>",
  "beginner_resources": "<基础资源表格>",
  "core_days": "<核心天数>",
  "core_concepts": "<核心概念列表>",
  "core_resources": "<核心资源表格>",
  "advanced_days": "<进阶天数>",
  "advanced_concepts": "<进阶概念列表>",
  "advanced_resources": "<进阶资源表格>",
  "project_table": "<实战项目表格>",
  "current_hotspots": "<热点文字>",
  "pitfall_guide": "<避坑指南文字>"
}
```

2. 用步骤 1-4 生成的数据填充模板中的所有 `{PLACEHOLDER}` 变量。

3. 写入 Markdown 文件，命名为 `learn-domain-guide-{话题}-{日期}.md`。

4. 读取生成的指南并呈现给用户。说明文件路径。

5. 标记所有 TodoWrite 条目为完成。

## 常见错误

- **跳过步骤** — 所有 5 个步骤必须执行，即使某些步骤无数据也要输出占位提示。
- **用 WebSearch 生成概念依赖图** — 概念依赖图必须由 Claude 知识生成，不依赖 WebSearch。
- **翻译概念名称** — 概念必须保留原文语言（英文术语保留英文），中文摘要附在后面。
- **使用首页级 URL** — 每条资源的 URL 必须指向具体文章页面，不是网站首页。
- **忽略 --project 参数** — 如果用户提供了项目目标，必须反向推导必须学的概念并在依赖图中标注 ⚡。
- **省略避坑指南** — 避坑指南是必输出板块，不可跳过。

## 与 research-landscape 的协作

两个 skill 独立运行但可配合使用：
- **先 landscape 再 learn-domain**：landscape 提供当前热点，learn-domain 自动引用其趋势点评作为"当前热点"板块。
- **单独使用 learn-domain**：如果无 landscape 报告，"当前热点"板块输出建议运行 landscape 的提示文字。
- **不合并**：learn-domain 不作为 landscape 的子功能，两者是独立 skill。
